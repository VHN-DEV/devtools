#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Tìm file trùng lặp dựa trên hash (MD5/SHA256)

Mục đích: Phát hiện và xóa file trùng lặp để tiết kiệm dung lượng
Lý do: Dọn dẹp ổ đĩa, tối ưu không gian lưu trữ
"""

import os
import sys
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

# Thêm thư mục cha vào sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    print_header, format_size, get_user_input, confirm_action,
    ProgressBar, log_info, log_error, setup_logger, safe_delete, normalize_path
)


def get_file_hash(file_path: str, hash_algo: str = 'md5', chunk_size: int = 8192) -> Optional[str]:
    """
    Tính hash của file
    
    Args:
        file_path: Đường dẫn file
        hash_algo: Thuật toán hash (md5, sha1, sha256)
        chunk_size: Kích thước chunk đọc file (bytes)
    
    Returns:
        str: Hash string hoặc None nếu lỗi
    
    Giải thích:
    - Đọc file theo chunk để tránh tràn RAM với file lớn
    - Hash từng chunk và cập nhật vào hasher
    - Trả về hex digest
    """
    # Chọn thuật toán hash
    if hash_algo == 'md5':
        hasher = hashlib.md5()
    elif hash_algo == 'sha1':
        hasher = hashlib.sha1()
    elif hash_algo == 'sha256':
        hasher = hashlib.sha256()
    else:
        hasher = hashlib.md5()
    
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError, PermissionError) as e:
        log_error(f"Lỗi đọc file {file_path}: {e}")
        return None


def get_file_hash_with_size(args: Tuple[str, int, str]) -> Tuple[str, Optional[str], int]:
    """
    Wrapper function cho multiprocessing
    
    Args:
        args: tuple (file_path, size, hash_algo)
    
    Returns:
        tuple: (file_path, hash, size)
    
    Giải thích:
    - Wrapper để dùng với ProcessPoolExecutor
    - Trả về cả path và hash và size
    """
    file_path, size, hash_algo = args
    file_hash = get_file_hash(file_path, hash_algo)
    return file_path, file_hash, size


class DuplicateFinder:
    """
    Class tìm file trùng lặp
    
    Mục đích: Tập trung logic tìm duplicate, dễ mở rộng
    """
    
    def __init__(self, folder_path: str, recursive: bool = True, 
                 min_size: int = 0, hash_algo: str = 'md5'):
        """
        Khởi tạo DuplicateFinder
        
        Args:
            folder_path: Thư mục cần quét
            recursive: Có quét thư mục con không
            min_size: Kích thước tối thiểu (bytes)
            hash_algo: Thuật toán hash
        """
        self.folder_path = Path(folder_path).resolve()
        self.recursive = recursive
        self.min_size = min_size
        self.hash_algo = hash_algo
        self.file_count = 0
    
    def find_by_size_first(self, use_multiprocessing: bool = True) -> Dict[str, List[Tuple[str, int]]]:
        """
        Tìm duplicate bằng cách filter theo size trước
        
        Args:
            use_multiprocessing: Có dùng multiprocessing không
        
        Returns:
            dict: {hash: [(file_path, size), ...]}
        
        Giải thích:
        - Bước 1: Group files theo size
        - Bước 2: Chỉ hash các file có size trùng nhau
        - Tối ưu hơn so với hash tất cả file
        """
        log_info(f"Bắt đầu quét thư mục: {self.folder_path}")
        
        # Bước 1: Group theo size
        print("🔍 Bước 1: Quét và group theo kích thước...\n")
        size_dict = defaultdict(list)
        
        if self.recursive:
            for root, dirs, files in os.walk(self.folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        
                        if size < self.min_size:
                            continue
                        
                        size_dict[size].append(file_path)
                        self.file_count += 1
                        
                        if self.file_count % 100 == 0:
                            print(f"   Đã quét {self.file_count} file...", end='\r')
                    
                    except (OSError, PermissionError):
                        pass
        else:
            for file in os.listdir(self.folder_path):
                file_path = os.path.join(self.folder_path, file)
                if os.path.isfile(file_path):
                    try:
                        size = os.path.getsize(file_path)
                        
                        if size < self.min_size:
                            continue
                        
                        size_dict[size].append(file_path)
                        self.file_count += 1
                    
                    except (OSError, PermissionError):
                        pass
        
        print(f"   Đã quét {self.file_count} file.       ")
        
        # Lọc chỉ lấy size có nhiều hơn 1 file (potential duplicates)
        potential_duplicates = {s: files for s, files in size_dict.items() if len(files) > 1}
        
        if not potential_duplicates:
            print("\n✅ Không có file nào có cùng kích thước!")
            return {}
        
        # Đếm số file cần hash
        files_to_hash = sum(len(files) for files in potential_duplicates.values())
        print(f"\n🔍 Bước 2: Tìm thấy {files_to_hash} file có cùng kích thước")
        print(f"   Đang tính hash...\n")
        
        log_info(f"Tìm thấy {files_to_hash} file potential duplicate")
        
        # Bước 2: Hash các file có cùng size
        hash_dict = defaultdict(list)
        
        if use_multiprocessing and files_to_hash > 5:
            # Sử dụng multiprocessing
            progress = ProgressBar(files_to_hash, prefix="Tính hash:")
            
            # Chuẩn bị tasks
            tasks = []
            for size, file_paths in potential_duplicates.items():
                for file_path in file_paths:
                    tasks.append((file_path, size, self.hash_algo))
            
            # Xử lý song song
            import multiprocessing
            max_workers = min(multiprocessing.cpu_count(), files_to_hash)
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(get_file_hash_with_size, task) for task in tasks]
                
                for future in as_completed(futures):
                    try:
                        file_path, file_hash, size = future.result()
                        
                        if file_hash:
                            hash_dict[file_hash].append((file_path, size))
                        
                        progress.update()
                    
                    except Exception as e:
                        log_error(f"Lỗi khi hash: {e}")
                        progress.update()
            
            progress.finish()
        
        else:
            # Xử lý tuần tự
            progress = ProgressBar(files_to_hash, prefix="Tính hash:")
            
            for size, file_paths in potential_duplicates.items():
                for file_path in file_paths:
                    file_hash = get_file_hash(file_path, self.hash_algo)
                    if file_hash:
                        hash_dict[file_hash].append((file_path, size))
                    progress.update()
            
            progress.finish()
        
        # Lọc chỉ lấy hash có nhiều hơn 1 file (thực sự duplicate)
        duplicates = {h: files for h, files in hash_dict.items() if len(files) > 1}
        
        log_info(f"Tìm thấy {len(duplicates)} nhóm file trùng lặp")
        
        return duplicates
    
    def find_by_size_only(self) -> Dict[int, List[str]]:
        """
        Tìm duplicate chỉ dựa vào size (nhanh nhưng không chính xác)
        
        Returns:
            dict: {size: [file_paths]}
        
        Giải thích:
        - Chỉ so sánh size, không hash
        - Nhanh nhưng có thể false positive
        - Hữu ích cho quick scan
        """
        print("🔍 Đang quét file theo kích thước...\n")
        log_info("Quét theo size only")
        
        size_dict = defaultdict(list)
        
        if self.recursive:
            for root, dirs, files in os.walk(self.folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        
                        if size < self.min_size:
                            continue
                        
                        size_dict[size].append(file_path)
                        self.file_count += 1
                        
                        if self.file_count % 100 == 0:
                            print(f"   Đã quét {self.file_count} file...", end='\r')
                    
                    except (OSError, PermissionError):
                        pass
        else:
            for file in os.listdir(self.folder_path):
                file_path = os.path.join(self.folder_path, file)
                if os.path.isfile(file_path):
                    try:
                        size = os.path.getsize(file_path)
                        
                        if size < self.min_size:
                            continue
                        
                        size_dict[size].append(file_path)
                        self.file_count += 1
                    
                    except (OSError, PermissionError):
                        pass
        
        print(f"   Đã quét {self.file_count} file.       ")
        
        # Lọc chỉ lấy size có nhiều hơn 1 file
        duplicates = {s: files for s, files in size_dict.items() if len(files) > 1}
        
        return duplicates


def display_duplicates(duplicates: dict, by_hash: bool = True, limit: int = 20) -> Tuple[int, int]:
    """
    Hiển thị danh sách file trùng lặp
    
    Args:
        duplicates: Dictionary chứa duplicates
        by_hash: True = duplicates theo hash, False = theo size
        limit: Số nhóm tối đa hiển thị
    
    Returns:
        tuple: (total_duplicates, wasted_space)
    
    Giải thích:
    - Hiển thị từng nhóm duplicate
    - Tính toán dung lượng lãng phí
    - Giới hạn số nhóm hiển thị để không quá dài
    """
    if not duplicates:
        print("\n✅ Không tìm thấy file trùng lặp!")
        return 0, 0
    
    duplicate_groups = len(duplicates)
    total_duplicates = sum(len(files) - 1 for files in duplicates.values())
    wasted_space = 0
    
    print(f"\n{'='*60}")
    print(f"📊 Tìm thấy {duplicate_groups} nhóm file trùng lặp")
    print(f"{'='*60}\n")
    
    log_info(f"Tìm thấy {duplicate_groups} nhóm, {total_duplicates} file duplicate")
    
    for idx, (key, files) in enumerate(list(duplicates.items())[:limit], 1):
        # Kiểm tra files không rỗng
        if not files:
            continue
            
        if by_hash:
            # files là list của tuple (path, size)
            file_size = files[0][1]
            file_paths = [f[0] for f in files]
        else:
            # files là list của path, key là size
            file_size = key
            file_paths = files
        
        group_waste = file_size * (len(file_paths) - 1)
        wasted_space += group_waste
        
        print(f"Nhóm {idx}: {len(file_paths)} file ({format_size(file_size)}) - Lãng phí: {format_size(group_waste)}")
        
        if by_hash:
            print(f"   Hash: {key[:16]}...")
        
        for file_path in file_paths:
            print(f"   - {file_path}")
        
        print()
    
    if len(duplicates) > limit:
        remaining = len(duplicates) - limit
        print(f"... và {remaining} nhóm khác (dùng -a để hiển thị tất cả)\n")
    
    return total_duplicates, wasted_space


def save_report(duplicates: dict, output_file: str, by_hash: bool = True):
    """
    Lưu báo cáo file trùng lặp ra file
    
    Args:
        duplicates: Dictionary chứa duplicates
        output_file: Tên file output
        by_hash: True = duplicates theo hash
    
    Giải thích:
    - Xuất toàn bộ kết quả ra file text
    - Dễ xem lại và phân tích sau
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("  BÁO CÁO FILE TRÙNG LẶP\n")
        f.write("=" * 60 + "\n\n")
        
        duplicate_groups = len(duplicates)
        total_duplicates = sum(len(files) - 1 for files in duplicates.values())
        
        f.write(f"Tổng số nhóm trùng lặp: {duplicate_groups}\n")
        f.write(f"Tổng số file trùng lặp: {total_duplicates}\n\n")
        
        for idx, (key, files) in enumerate(duplicates.items(), 1):
            # Kiểm tra files không rỗng
            if not files:
                continue
                
            if by_hash:
                file_size = files[0][1]
                file_paths = [f[0] for f in files]
            else:
                file_size = key
                file_paths = files
            
            group_waste = file_size * (len(file_paths) - 1)
            
            f.write(f"\nNhóm {idx}: {len(file_paths)} file ({format_size(file_size)})\n")
            if by_hash:
                f.write(f"Hash: {key}\n")
            
            for file_path in file_paths:
                f.write(f"  - {file_path}\n")
    
    log_info(f"Đã lưu báo cáo: {output_file}")


def delete_duplicates_interactive(duplicates: dict, by_hash: bool = True):
    """
    Xóa file trùng lặp với tương tác
    
    Args:
        duplicates: Dictionary chứa duplicates
        by_hash: True = duplicates theo hash
    
    Giải thích:
    - Cho phép người dùng chọn cách xóa
    - Xác nhận trước khi xóa
    - Logging từng file bị xóa
    """
    print("\n===== CHẾ ĐỘ XÓA TRÙNG LẶP =====")
    print("1. Giữ file đầu tiên, xóa các file còn lại")
    print("2. Giữ file mới nhất (theo modification time), xóa cũ hơn")
    print("3. Giữ file cũ nhất (theo modification time), xóa mới hơn")
    print("0. Không xóa")
    
    choice = get_user_input("Chọn (0-3)", default="0")
    
    if choice == "0":
        return
    
    files_to_delete = []
    
    for key, files in duplicates.items():
        if by_hash:
            file_paths = [f[0] for f in files]
        else:
            file_paths = files
        
        if choice == "1":
            # Giữ file đầu tiên
            files_to_delete.extend(file_paths[1:])
        
        elif choice == "2":
            # Giữ file mới nhất
            files_with_mtime = [(f, os.path.getmtime(f)) for f in file_paths]
            files_sorted = sorted(files_with_mtime, key=lambda x: x[1], reverse=True)
            files_to_delete.extend([f[0] for f in files_sorted[1:]])
        
        elif choice == "3":
            # Giữ file cũ nhất
            files_with_mtime = [(f, os.path.getmtime(f)) for f in file_paths]
            files_sorted = sorted(files_with_mtime, key=lambda x: x[1])
            files_to_delete.extend([f[0] for f in files_sorted[1:]])
    
    if not files_to_delete:
        print("Không có file nào để xóa.")
        return
    
    # Hiển thị preview
    print(f"\n⚠️  SẼ XÓA {len(files_to_delete)} FILE:")
    for i, file_path in enumerate(files_to_delete[:10], 1):
        print(f"   {i}. {file_path}")
    
    if len(files_to_delete) > 10:
        print(f"   ... và {len(files_to_delete) - 10} file khác")
    
    if not confirm_action(f"Bạn sắp xóa {len(files_to_delete)} file!", require_yes=True):
        print("❌ Đã hủy")
        return
    
    # Xóa files
    print(f"\n🗑️  Đang xóa...\n")
    progress = ProgressBar(len(files_to_delete), prefix="Xóa file:")
    
    deleted = 0
    errors = 0
    
    for file_path in files_to_delete:
        success, error = safe_delete(file_path)
        
        if success:
            deleted += 1
            log_info(f"Đã xóa: {file_path}")
        else:
            errors += 1
            log_error(f"Lỗi xóa {file_path}: {error}")
        
        progress.update()
    
    progress.finish()
    
    print(f"\n✅ Đã xóa {deleted}/{len(files_to_delete)} file")
    if errors > 0:
        print(f"❌ {errors} file gặp lỗi")
    
    log_info(f"Xóa hoàn thành: {deleted} thành công, {errors} lỗi")


def main_interactive():
    """Chế độ interactive"""
    print_header("TOOL TÌM FILE TRÙNG LẶP")
    
    # Nhập thư mục
    print("💡 Mẹo: Bạn có thể kéo thả thư mục vào terminal để nhập đường dẫn")
    folder_input_raw = get_user_input("Nhập đường dẫn thư mục")
    folder_input = normalize_path(folder_input_raw)
    
    if not os.path.isdir(folder_input):
        print(f"❌ Thư mục không tồn tại: {folder_input}")
        return
    
    print(f"✅ Đã chọn: {folder_input}\n")
    
    # Tùy chọn
    recursive_input = get_user_input("Tìm trong tất cả thư mục con? (Y/n)", default="y")
    recursive = recursive_input.lower() != 'n'
    
    min_size_input = get_user_input("Kích thước file tối thiểu (KB, Enter để bỏ qua)", default="0")
    min_size = int(min_size_input) * 1024 if min_size_input.isdigit() else 0
    
    # Chọn phương pháp
    print("\n===== PHƯƠNG PHÁP TÌM =====")
    print("1. Theo hash (MD5) - Chính xác nhưng chậm")
    print("2. Theo hash (SHA256) - Chính xác hơn MD5")
    print("3. Theo kích thước - Nhanh nhưng không chính xác")
    
    method = get_user_input("Chọn phương pháp (1-3)", default="1")
    
    # Multiprocessing
    use_mp = get_user_input("Sử dụng multiprocessing? (Y/n)", default="y")
    use_multiprocessing = use_mp.lower() != 'n'
    
    # Tạo finder
    if method in ["1", "2"]:
        hash_algo = 'md5' if method == "1" else 'sha256'
        finder = DuplicateFinder(folder_input, recursive, min_size, hash_algo)
        duplicates = finder.find_by_size_first(use_multiprocessing)
        
        total_duplicates, wasted_space = display_duplicates(duplicates, by_hash=True)
        
        if duplicates:
            print(f"{'='*60}")
            print(f"💾 Tổng dung lượng lãng phí: {format_size(wasted_space)}")
            print(f"{'='*60}")
    
    elif method == "3":
        finder = DuplicateFinder(folder_input, recursive, min_size)
        duplicates = finder.find_by_size_only()
        
        total_duplicates, wasted_space = display_duplicates(duplicates, by_hash=False)
        
        if duplicates:
            print(f"{'='*60}")
            print(f"💾 Ước tính dung lượng lãng phí: {format_size(wasted_space)}")
            print(f"⚠️  Lưu ý: Phương pháp này chỉ dựa trên kích thước, có thể không chính xác 100%")
            print(f"{'='*60}")
    
    else:
        print("❌ Lựa chọn không hợp lệ!")
        return
    
    if not duplicates:
        return
    
    # Lưu báo cáo
    save_input = get_user_input("\nLưu báo cáo ra file? (y/N)", default="n")
    if save_input.lower() == 'y':
        output_file = "duplicate_report.txt"
        save_report(duplicates, output_file, by_hash=(method in ["1", "2"]))
        print(f"✅ Đã lưu báo cáo: {output_file}")
    
    # Xóa file trùng lặp
    delete_input = get_user_input("\nXóa file trùng lặp? (y/N)", default="n")
    if delete_input.lower() == 'y':
        delete_duplicates_interactive(duplicates, by_hash=(method in ["1", "2"]))


def main_cli(args):
    """Chế độ CLI"""
    hash_algo = 'sha256' if args.sha256 else 'md5'
    
    finder = DuplicateFinder(
        args.directory,
        recursive=not args.no_recursive,
        min_size=args.min_size * 1024 if args.min_size else 0,
        hash_algo=hash_algo
    )
    
    if args.size_only:
        duplicates = finder.find_by_size_only()
        by_hash = False
    else:
        duplicates = finder.find_by_size_first(not args.no_multiprocessing)
        by_hash = True
    
    display_duplicates(duplicates, by_hash, limit=1000 if args.all else 20)
    
    if args.output:
        save_report(duplicates, args.output, by_hash)
        print(f"✅ Đã lưu báo cáo: {args.output}")


def main():
    """Hàm main"""
    setup_logger('duplicate-finder', log_to_console=False)
    
    parser = argparse.ArgumentParser(description='Tool tìm file trùng lặp')
    parser.add_argument('directory', nargs='?', help='Thư mục cần quét')
    parser.add_argument('--sha256', action='store_true', help='Dùng SHA256 thay vì MD5')
    parser.add_argument('--size-only', action='store_true', help='Chỉ so sánh theo size')
    parser.add_argument('--min-size', type=int, help='Kích thước tối thiểu (KB)')
    parser.add_argument('--no-recursive', action='store_true', help='Không quét thư mục con')
    parser.add_argument('--no-multiprocessing', action='store_true', help='Tắt multiprocessing')
    parser.add_argument('-o', '--output', help='File output cho báo cáo')
    parser.add_argument('-a', '--all', action='store_true', help='Hiển thị tất cả kết quả')
    
    args = parser.parse_args()
    
    if args.directory:
        main_cli(args)
    else:
        try:
            main_interactive()
        except KeyboardInterrupt:
            print("\n\n❌ Đã hủy!")
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            log_error(f"Exception: {e}", exc_info=True)


if __name__ == "__main__":
    main()
