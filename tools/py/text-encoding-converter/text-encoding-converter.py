#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Chuyển đổi encoding của file text
"""

import os
import sys
from pathlib import Path

# Thêm thư mục cha vào sys.path để import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import install_library

# Thử import chardet
try:
    import chardet
except ImportError:
    chardet = None


def print_header():
    print("=" * 60)
    print("  TOOL CHUYỂN ĐỔI ENCODING")
    print("=" * 60)
    print()


def detect_encoding(file_path):
    """
    Phát hiện encoding của file
    
    Returns:
        tuple: (encoding, confidence)
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'], result['confidence']
    except Exception as e:
        return None, 0


def convert_encoding(file_path, source_encoding, target_encoding, backup=True):
    """
    Chuyển đổi encoding của file
    
    Args:
        file_path: Đường dẫn file
        source_encoding: Encoding nguồn
        target_encoding: Encoding đích
        backup: Có backup file gốc không
    
    Returns:
        bool: Thành công hay không
    """
    try:
        # Đọc file với encoding nguồn
        with open(file_path, 'r', encoding=source_encoding, errors='ignore') as f:
            content = f.read()
        
        # Backup nếu cần
        if backup:
            backup_path = str(file_path) + '.bak'
            with open(backup_path, 'w', encoding=source_encoding) as f:
                with open(file_path, 'r', encoding=source_encoding, errors='ignore') as original:
                    f.write(original.read())
        
        # Ghi lại với encoding đích
        with open(file_path, 'w', encoding=target_encoding, newline='\n') as f:
            f.write(content)
        
        return True
    
    except Exception as e:
        print(f"   ❌ Lỗi: {e}")
        return False


def convert_folder(folder_path, source_encoding, target_encoding, file_extensions, recursive=True, backup=True):
    """Chuyển đổi tất cả file trong thư mục"""
    
    converted_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"\n🔄 Bắt đầu chuyển đổi...\n")
    
    if recursive:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if not file_extensions or any(file.lower().endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    
                    # Detect encoding nếu source là 'auto'
                    if source_encoding.lower() == 'auto':
                        detected, confidence = detect_encoding(file_path)
                        if detected and confidence > 0.7:
                            actual_source = detected
                            print(f"📄 {file} (detect: {detected}, {confidence:.0%})")
                        else:
                            print(f"⚠️  {file} - Khong phat hien duoc encoding, bo qua")
                            skipped_count += 1
                            continue
                    else:
                        actual_source = source_encoding
                        print(f"📄 {file}")
                    
                    # Convert
                    success = convert_encoding(file_path, actual_source, target_encoding, backup)
                    
                    if success:
                        print(f"   ✓ {actual_source} → {target_encoding}")
                        converted_count += 1
                    else:
                        error_count += 1
    else:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        for file in files:
            if not file_extensions or any(file.lower().endswith(ext) for ext in file_extensions):
                file_path = os.path.join(folder_path, file)
                
                if source_encoding.lower() == 'auto':
                    detected, confidence = detect_encoding(file_path)
                    if detected and confidence > 0.7:
                        actual_source = detected
                        print(f"📄 {file} (detect: {detected}, {confidence:.0%})")
                    else:
                        print(f"⚠️  {file} - Khong phat hien duoc encoding, bo qua")
                        skipped_count += 1
                        continue
                else:
                    actual_source = source_encoding
                    print(f"📄 {file}")
                
                success = convert_encoding(file_path, actual_source, target_encoding, backup)
                
                if success:
                    print(f"   ✓ {actual_source} → {target_encoding}")
                    converted_count += 1
                else:
                    error_count += 1
    
    return converted_count, skipped_count, error_count


def detect_mode(folder_path, file_extensions, recursive=True):
    """Chế độ chỉ phát hiện encoding"""
    
    print(f"\n🔍 Đang phát hiện encoding...\n")
    
    encoding_stats = {}
    
    if recursive:
        files_to_check = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if not file_extensions or any(file.lower().endswith(ext) for ext in file_extensions):
                    files_to_check.append(os.path.join(root, file))
    else:
        files_to_check = [
            os.path.join(folder_path, f) 
            for f in os.listdir(folder_path) 
            if os.path.isfile(os.path.join(folder_path, f))
            and (not file_extensions or any(f.lower().endswith(ext) for ext in file_extensions))
        ]
    
    for file_path in files_to_check:
        encoding, confidence = detect_encoding(file_path)
        
        if encoding:
            print(f"📄 {os.path.basename(file_path)}")
            print(f"   Encoding: {encoding} (confidence: {confidence:.0%})")
            
            if encoding not in encoding_stats:
                encoding_stats[encoding] = 0
            encoding_stats[encoding] += 1
        else:
            print(f"⚠️  {os.path.basename(file_path)} - Không phát hiện được")
    
    # Thống kê
    print(f"\n{'='*60}")
    print(f"📊 Thống kê encoding:")
    for enc, count in sorted(encoding_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   {enc}: {count} file")
    print(f"{'='*60}")


def main():
    print_header()
    
    # Kiểm tra thư viện chardet
    global chardet
    if chardet is None:
        if install_library(
            package_name="chardet",
            install_command="pip install chardet",
            library_display_name="chardet"
        ):
            import chardet
        else:
            return
    
    # Nhập thư mục
    folder_input = input("Nhập đường dẫn thư mục: ").strip('"')
    if not folder_input or not os.path.isdir(folder_input):
        print("❌ Thư mục không tồn tại!")
        return
    
    # Loại file
    ext_input = input("Chỉ xử lý file có đuôi (vd: .txt .py .js - Enter để xử lý tất cả): ").strip()
    file_extensions = [ext.strip() for ext in ext_input.split()] if ext_input else []
    
    # Đệ quy
    recursive_input = input("Xử lý tất cả thư mục con? (Y/n): ").strip().lower()
    recursive = recursive_input != 'n'
    
    # Chế độ
    print("\n===== CHẾ ĐỘ =====")
    print("1. Phát hiện encoding (không thay đổi file)")
    print("2. Chuyển đổi encoding")
    
    mode = input("\nChọn chế độ (1-2): ").strip()
    
    if mode == "1":
        detect_mode(folder_input, file_extensions, recursive)
    
    elif mode == "2":
        print("\n===== ENCODING NGUỒN =====")
        print("Nhập encoding nguồn (vd: utf-8, windows-1252, iso-8859-1)")
        print("Hoặc nhập 'auto' để tự động phát hiện")
        source_enc = input("\nEncoding nguồn: ").strip() or "auto"
        
        print("\n===== ENCODING ĐÍCH =====")
        print("Các encoding phổ biến:")
        print("  - utf-8 (khuyên dùng)")
        print("  - utf-16")
        print("  - windows-1252 (Windows Western)")
        print("  - iso-8859-1 (Latin-1)")
        target_enc = input("\nEncoding đích: ").strip() or "utf-8"
        
        # Backup
        backup_input = input("\nTạo backup file gốc (.bak)? (Y/n): ").strip().lower()
        backup = backup_input != 'n'
        
        # Xác nhận
        print(f"\n⚠️  CẢNH BÁO: Bạn sắp thay đổi encoding của nhiều file!")
        print(f"   Từ: {source_enc}")
        print(f"   Sang: {target_enc}")
        if backup:
            print(f"   Backup: Có")
        
        confirm = input("\nXác nhận? (YES để xác nhận): ")
        
        if confirm == "YES":
            converted, skipped, errors = convert_folder(
                folder_input, 
                source_enc, 
                target_enc, 
                file_extensions, 
                recursive, 
                backup
            )
            
            print(f"\n{'='*60}")
            print(f"✅ Hoàn thành!")
            print(f"   - Chuyển đổi thành công: {converted} file")
            print(f"   - Bỏ qua: {skipped} file")
            print(f"   - Lỗi: {errors} file")
            print(f"{'='*60}")
        else:
            print("❌ Đã hủy.")
    
    else:
        print("❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")

