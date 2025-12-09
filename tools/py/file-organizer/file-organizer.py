#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Sắp xếp file theo loại vào các thư mục tương ứng
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict


def print_header():
    print("=" * 60)
    print("  TOOL SAP XEP FILE THEO LOAI")
    print("=" * 60)
    print()


# Định nghĩa các loại file
FILE_CATEGORIES = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp', '.tiff'],
    'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
    'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'],
    'Code': ['.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.html', '.css', '.scss', '.ts', '.jsx', '.tsx'],
    'Executables': ['.exe', '.msi', '.apk', '.dmg', '.deb', '.rpm'],
    'Databases': ['.sql', '.db', '.sqlite', '.mdb', '.accdb'],
    'Fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
    'Others': []  # Các file không thuộc loại nào
}


def get_file_category(file_path):
    """Xác định loại file dựa trên extension"""
    ext = os.path.splitext(file_path)[1].lower()
    
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    
    return 'Others'


def organize_files(source_folder, destination_folder=None, mode='copy', by_extension=False):
    """
    Sắp xếp file
    
    Args:
        source_folder: Thư mục nguồn
        destination_folder: Thư mục đích (None = tạo trong source)
        mode: 'copy' hoặc 'move'
        by_extension: True = sắp xếp theo extension, False = sắp xếp theo category
    """
    source_path = Path(source_folder).resolve()
    
    if destination_folder:
        dest_path = Path(destination_folder).resolve()
    else:
        dest_path = source_path / "Organized"
    
    # Tạo thư mục đích
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Thống kê
    stats = defaultdict(int)
    total_files = 0
    
    print(f"\n📂 Thu muc nguon: {source_path}")
    print(f"📂 Thu muc dich: {dest_path}")
    print(f"🔄 Che do: {mode.upper()}")
    print(f"\n🚀 Bat dau sap xep...\n")
    
    # Lấy danh sách file
    files = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f))]
    
    for file in files:
        file_path = source_path / file
        
        try:
            if by_extension:
                # Sắp xếp theo extension
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    folder_name = ext[1:].upper()  # Bỏ dấu chấm
                else:
                    folder_name = "NO_EXTENSION"
            else:
                # Sắp xếp theo category
                folder_name = get_file_category(file)
            
            # Tạo thư mục category
            category_folder = dest_path / folder_name
            category_folder.mkdir(exist_ok=True)
            
            # Đường dẫn file đích
            dest_file = category_folder / file
            
            # Xử lý trùng tên
            counter = 1
            base_name = dest_file.stem
            extension = dest_file.suffix
            while dest_file.exists():
                dest_file = category_folder / f"{base_name}_{counter}{extension}"
                counter += 1
            
            # Copy hoặc Move
            if mode == 'copy':
                shutil.copy2(file_path, dest_file)
                action = "Copy"
            else:
                shutil.move(str(file_path), str(dest_file))
                action = "Move"
            
            print(f"✓ {action}: {file} → {folder_name}/")
            stats[folder_name] += 1
            total_files += 1
        
        except Exception as e:
            print(f"✗ Lỗi với {file}: {e}")
    
    # Thống kê
    print(f"\n{'='*60}")
    print(f"✅ Hoan thanh! Da xu ly {total_files} file")
    print(f"{'='*60}")
    print(f"\n📊 Thong ke theo loai:")
    
    for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   {category}: {count} file")


def organize_by_date(source_folder, destination_folder=None, mode='copy', date_format='%Y-%m'):
    """
    Sắp xếp file theo ngày tháng (modification date)
    
    Args:
        date_format: 
            - '%Y-%m' → 2024-01
            - '%Y-%m-%d' → 2024-01-15
            - '%Y' → 2024
    """
    import datetime
    
    source_path = Path(source_folder).resolve()
    
    if destination_folder:
        dest_path = Path(destination_folder).resolve()
    else:
        dest_path = source_path / "Organized_by_Date"
    
    dest_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📂 Thu muc nguon: {source_path}")
    print(f"📂 Thu muc dich: {dest_path}")
    print(f"🔄 Che do: {mode.upper()}")
    print(f"\n🚀 Bat dau sap xep theo ngay...\n")
    
    stats = defaultdict(int)
    total_files = 0
    
    files = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f))]
    
    for file in files:
        file_path = source_path / file
        
        try:
            # Lấy modification time
            mod_time = os.path.getmtime(file_path)
            date = datetime.datetime.fromtimestamp(mod_time)
            
            # Tạo tên folder theo format
            folder_name = date.strftime(date_format)
            
            # Tạo thư mục date
            date_folder = dest_path / folder_name
            date_folder.mkdir(exist_ok=True)
            
            # Đường dẫn file đích
            dest_file = date_folder / file
            
            # Xử lý trùng tên
            counter = 1
            base_name = dest_file.stem
            extension = dest_file.suffix
            while dest_file.exists():
                dest_file = date_folder / f"{base_name}_{counter}{extension}"
                counter += 1
            
            # Copy hoặc Move
            if mode == 'copy':
                shutil.copy2(file_path, dest_file)
                action = "Copy"
            else:
                shutil.move(str(file_path), str(dest_file))
                action = "Move"
            
            print(f"✓ {action}: {file} → {folder_name}/")
            stats[folder_name] += 1
            total_files += 1
        
        except Exception as e:
            print(f"✗ Lỗi với {file}: {e}")
    
    # Thống kê
    print(f"\n{'='*60}")
    print(f"✅ Hoan thanh! Da xu ly {total_files} file")
    print(f"{'='*60}")
    print(f"\n📊 Thong ke theo thoi gian:")
    
    for period, count in sorted(stats.items()):
        print(f"   {period}: {count} file")


def main():
    print_header()
    
    # Nhập thư mục nguồn
    source_input = input("Nhap duong dan thu muc can sap xep: ").strip('"')
    if not source_input or not os.path.isdir(source_input):
        print("❌ Thu muc khong ton tai!")
        return
    
    # Chọn chế độ sắp xếp
    print("\n===== CHE DO SAP XEP =====")
    print("1. Theo loai file (Images, Videos, Documents, ...)")
    print("2. Theo duoi file (.jpg, .mp4, .pdf, ...)")
    print("3. Theo ngay thang (modification date)")
    
    organize_mode = input("\nChon che do (1-3): ").strip()
    
    # Hỏi thư mục đích
    dest_input = input("\nThu muc dich (Enter de tao thu muc 'Organized' trong thu muc nguon): ").strip('"')
    dest_folder = dest_input if dest_input else None
    
    # Copy hay Move
    print("\n===== HANH DONG =====")
    print("1. Copy (giu nguyen file goc)")
    print("2. Move (di chuyen file)")
    
    action_choice = input("\nChon (1-2): ").strip()
    action_mode = 'move' if action_choice == '2' else 'copy'
    
    # Xác nhận
    if action_mode == 'move':
        print("\n⚠️  CANH BAO: Che do MOVE se di chuyen file khoi vi tri goc!")
        confirm = input("Xac nhan? (Y/n): ").strip().lower()
        if confirm == 'n':
            print("❌ Da huy.")
            return
    
    # Thực hiện sắp xếp
    if organize_mode == "1":
        organize_files(source_input, dest_folder, action_mode, by_extension=False)
    
    elif organize_mode == "2":
        organize_files(source_input, dest_folder, action_mode, by_extension=True)
    
    elif organize_mode == "3":
        print("\n===== DINH DANG NGAY =====")
        print("1. Nam-Thang (2024-01)")
        print("2. Nam-Thang-Ngay (2024-01-15)")
        print("3. Chi nam (2024)")
        
        date_choice = input("\nChon (1-3): ").strip()
        
        date_formats = {
            "1": "%Y-%m",
            "2": "%Y-%m-%d",
            "3": "%Y"
        }
        
        date_format = date_formats.get(date_choice, "%Y-%m")
        organize_by_date(source_input, dest_folder, action_mode, date_format)
    
    else:
        print("❌ Lua chon khong hop le!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Da huy!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")

