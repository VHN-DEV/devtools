#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Tạo các file font (TTF, OTF, WOFF, WOFF2)
Mục đích: Tạo font từ các nguồn hoặc convert giữa các format
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Thêm thư mục cha vào sys.path để import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import install_library


def print_header():
    """In header của tool"""
    print("=" * 60)
    print("  TOOL TẠO VÀ CHUYỂN ĐỔI FILE FONT")
    print("=" * 60)
    print()


def check_dependencies():
    """
    Kiểm tra các thư viện cần thiết
    
    Returns:
        bool: True nếu đủ dependencies
    """
    try:
        # Thử import fonttools
        import fontTools
        print("✅ Thư viện fonttools: OK")
    except ImportError:
        install_library(
            package_name="fonttools",
            install_command="pip install fonttools",
            library_display_name="fonttools"
        )
        return False
    
    try:
        # Thử import brotli (cho WOFF2)
        import brotli
        print("✅ Thư viện brotli: OK")
    except ImportError:
        print("⚠️  Thư viện brotli chưa được cài (cần cho WOFF2)")
        if install_library(
            package_name="brotli",
            install_command="pip install brotli",
            library_display_name="brotli"
        ):
            print("✅ Đã cài đặt brotli thành công!")
        else:
            print("⚠️  Tool vẫn có thể hoạt động nhưng không thể tạo WOFF2.")
    
    return True


def convert_font_format(input_path, output_path, output_format='woff'):
    """
    Chuyển đổi định dạng font
    
    Args:
        input_path: File font gốc (TTF, OTF)
        output_path: File font output
        output_format: Format đích (woff, woff2, ttf, otf)
    """
    try:
        from fontTools.ttLib import TTFont
        
        print(f"\n🔤 Đang chuyển đổi font...")
        print(f"   Format: {output_format.upper()}\n")
        
        # Load font
        font = TTFont(input_path)
        
        # Convert theo format
        if output_format.lower() == 'woff':
            font.flavor = 'woff'
        elif output_format.lower() == 'woff2':
            font.flavor = 'woff2'
        else:
            font.flavor = None  # TTF hoặc OTF
        
        # Save
        font.save(output_path)
        font.close()
        
        # So sánh kích thước
        original_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)
        ratio = (output_size / original_size) * 100
        
        print(f"\n✅ Chuyển đổi thành công!")
        print(f"   📄 File gốc: {format_size(original_size)}")
        print(f"   📄 File mới: {format_size(output_size)} ({ratio:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi chuyển đổi: {e}")
        return False


def get_font_info(font_path):
    """
    Lấy thông tin font
    
    Args:
        font_path: Đường dẫn file font
    
    Returns:
        dict: Thông tin font (name, family, style, version...)
    """
    try:
        from fontTools.ttLib import TTFont
        
        font = TTFont(font_path)
        
        info = {
            'family': 'Unknown',
            'style': 'Regular',
            'version': 'Unknown',
            'copyright': 'Unknown',
            'glyphs': len(font.getGlyphSet())
        }
        
        # Đọc thông tin từ 'name' table
        if 'name' in font:
            name_table = font['name']
            for record in name_table.names:
                if record.nameID == 1:  # Family name
                    info['family'] = record.toUnicode()
                elif record.nameID == 2:  # Subfamily/Style
                    info['style'] = record.toUnicode()
                elif record.nameID == 5:  # Version
                    info['version'] = record.toUnicode()
                elif record.nameID == 0:  # Copyright
                    info['copyright'] = record.toUnicode()
        
        font.close()
        return info
        
    except Exception as e:
        print(f"❌ Lỗi khi đọc thông tin font: {e}")
        return None


def display_font_info(font_path):
    """Hiển thị thông tin font"""
    print(f"\n🔤 Font: {os.path.basename(font_path)}")
    print("=" * 60)
    
    info = get_font_info(font_path)
    
    if not info:
        return
    
    print(f"Family: {info['family']}")
    print(f"Style: {info['style']}")
    print(f"Version: {info['version']}")
    print(f"Glyphs: {info['glyphs']}")
    print(f"Copyright: {info['copyright']}")
    print(f"Size: {format_size(os.path.getsize(font_path))}")
    print("=" * 60)


def create_font_subset(input_path, output_path, characters=None, unicode_ranges=None):
    """
    Tạo font subset (chỉ chứa một số ký tự)
    
    Args:
        input_path: Font gốc
        output_path: Font subset output
        characters: Danh sách ký tự cần giữ lại
        unicode_ranges: Danh sách Unicode ranges (vd: ['U+0020-007F', 'U+0100-017F'])
    """
    try:
        try:
            from fontTools.subset import Subsetter
        except ImportError:
            print("❌ Cần cài đặt fonttools với subset support!")
            print("\n💡 Cài đặt:")
            print(f"   {sys.executable} -m pip install fonttools")
            print("\n💡 Hoặc nếu đã cài, cần restart tool.")
            return False
        
        from fontTools.ttLib import TTFont
        
        print(f"\n✂️  Đang tạo font subset...")
        
        # Load font
        font = TTFont(input_path)
        
        # Tạo subsetter
        subsetter = Subsetter()
        
        # Thêm ký tự hoặc unicode ranges
        if characters:
            subsetter.populate(text=characters)
            print(f"   Ký tự: {len(characters)}")
        elif unicode_ranges:
            subsetter.populate(unicodes=unicode_ranges)
            print(f"   Unicode ranges: {', '.join(unicode_ranges)}")
        else:
            print("❌ Cần chỉ định ký tự hoặc unicode ranges!")
            font.close()
            return False
        
        # Subset font
        subsetter.subset(font)
        
        # Save
        font.save(output_path)
        font.close()
        
        # So sánh kích thước
        original_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)
        reduction = ((original_size - output_size) / original_size) * 100
        
        print(f"\n✅ Tạo subset thành công!")
        print(f"   📄 File gốc: {format_size(original_size)}")
        print(f"   📄 File subset: {format_size(output_size)}")
        print(f"   💯 Giảm: {reduction:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi tạo subset: {e}")
        return False


def format_size(size_bytes):
    """Format dung lượng dễ đọc"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def main():
    """Hàm chính - Menu font generator"""
    print_header()
    
    # Kiểm tra dependencies
    if not check_dependencies():
        print("\n💡 Sau khi cài đặt dependencies, chạy lại tool.")
        return
    
    print("\n===== CHỨC NĂNG =====")
    print("1. Chuyển đổi định dạng font (TTF/OTF → WOFF/WOFF2)")
    print("2. Xem thông tin font")
    print("3. Tạo font subset (chỉ chứa một số ký tự)")
    print("0. Thoát")
    
    choice = input("\nChọn chức năng (0-3): ").strip()
    
    if choice == "0":
        print("Thoát chương trình.")
        return
    
    elif choice == "1":
        # Convert font format
        print("\n===== CHUYỂN ĐỔI ĐỊNH DẠNG FONT =====")
        
        input_file = input("Nhập đường dẫn file font (TTF/OTF): ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        ext = Path(input_file).suffix.lower()
        if ext not in ['.ttf', '.otf']:
            print("⚠️  File không phải TTF hoặc OTF!")
            return
        
        display_font_info(input_file)
        
        print("\nĐịnh dạng output:")
        print("1. WOFF (Web Open Font Format)")
        print("2. WOFF2 (Web Open Font Format 2.0 - nén tốt hơn)")
        print("3. TTF (TrueType Font)")
        print("4. OTF (OpenType Font)")
        
        format_choice = input("\nChọn định dạng (1-4): ").strip()
        formats = {'1': 'woff', '2': 'woff2', '3': 'ttf', '4': 'otf'}
        output_format = formats.get(format_choice, 'woff')
        
        output_file = input("Tên file output (Enter để tự động): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}.{output_format}"
            )
        
        convert_font_format(input_file, output_file, output_format)
    
    elif choice == "2":
        # Font info
        print("\n===== THÔNG TIN FONT =====")
        
        input_file = input("Nhập đường dẫn file font: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        display_font_info(input_file)
    
    elif choice == "3":
        # Create font subset
        print("\n===== TẠO FONT SUBSET =====")
        
        input_file = input("Nhập đường dẫn file font: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        display_font_info(input_file)
        
        print("\nChọn phương thức:")
        print("1. Nhập danh sách ký tự")
        print("2. Nhập Unicode ranges")
        
        method_choice = input("\nChọn phương thức (1-2): ").strip()
        
        characters = None
        unicode_ranges = None
        
        if method_choice == "1":
            chars_input = input("Nhập danh sách ký tự (vd: 'Hello World' hoặc 'abc123'): ").strip()
            if chars_input:
                characters = chars_input
        
        elif method_choice == "2":
            ranges_input = input("Nhập Unicode ranges (vd: 'U+0020-007F,U+0100-017F'): ").strip()
            if ranges_input:
                unicode_ranges = [r.strip() for r in ranges_input.split(',')]
        
        if not characters and not unicode_ranges:
            print("❌ Cần nhập ký tự hoặc Unicode ranges!")
            return
        
        output_file = input("Tên file output (Enter để tự động): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            ext = Path(input_file).suffix
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}_subset{ext}"
            )
        
        create_font_subset(input_file, output_file, characters, unicode_ranges)
    
    else:
        print("❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
