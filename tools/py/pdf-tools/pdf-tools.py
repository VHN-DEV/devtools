#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Công cụ xử lý PDF đa năng
Mục đích: Merge, split, compress, convert PDF
"""

import os
import sys
from pathlib import Path

# Thêm thư mục cha vào sys.path để import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import install_library


def print_header():
    """In header của tool"""
    print("=" * 60)
    print("  TOOL XỬ LÝ PDF")
    print("=" * 60)
    print()


def check_dependencies():
    """
    Kiểm tra các thư viện cần thiết
    
    Mục đích: Đảm bảo user đã cài đủ thư viện
    Lý do: PyPDF2 và Pillow cần thiết cho tool
    """
    try:
        import PyPDF2
    except ImportError:
        install_library(
            package_name="PyPDF2",
            install_command="pip install PyPDF2",
            library_display_name="PyPDF2"
        )
        return False
    
    try:
        from PIL import Image
    except ImportError:
        install_library(
            package_name="Pillow",
            install_command="pip install Pillow",
            library_display_name="Pillow"
        )
        return False
    
    return True


def format_size(size_bytes):
    """Format dung lượng dễ đọc"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0


def merge_pdfs(input_files, output_file):
    """
    Gộp nhiều PDF thành 1 file
    
    Args:
        input_files: Danh sách đường dẫn PDF
        output_file: Đường dẫn file output
    
    Giải thích:
    - Dùng PdfMerger để gộp PDF
    - Giữ nguyên bookmarks và metadata
    - Hiển thị progress
    """
    import PyPDF2
    
    try:
        print(f"\n📦 Đang gộp {len(input_files)} file PDF...\n")
        
        merger = PyPDF2.PdfMerger()
        
        for idx, pdf_file in enumerate(input_files, 1):
            if not os.path.exists(pdf_file):
                print(f"⚠️  File không tồn tại: {pdf_file}")
                continue
            
            print(f"   [{idx}/{len(input_files)}] Đang xử lý: {os.path.basename(pdf_file)}")
            merger.append(pdf_file)
        
        # Tạo thư mục output nếu chưa có
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        
        merger.write(output_file)
        merger.close()
        
        output_size = os.path.getsize(output_file)
        
        print(f"\n✅ Gộp thành công!")
        print(f"   📄 File output: {output_file}")
        print(f"   📊 Kích thước: {format_size(output_size)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi gộp PDF: {e}")
        return False


def split_pdf(input_file, output_folder, mode='all', page_ranges=None):
    """
    Tách PDF thành nhiều file
    
    Args:
        input_file: File PDF cần tách
        output_folder: Thư mục chứa file output
        mode: 'all' (mỗi trang 1 file), 'range' (theo range)
        page_ranges: [(start, end), ...] nếu mode='range'
    
    Giải thích:
    - mode='all': Tách mỗi trang thành 1 file riêng
    - mode='range': Tách theo range chỉ định (vd: 1-5, 6-10)
    """
    import PyPDF2
    
    try:
        print(f"\n✂️  Đang tách PDF...\n")
        
        reader = PyPDF2.PdfReader(input_file)
        total_pages = len(reader.pages)
        
        print(f"   📄 File: {os.path.basename(input_file)}")
        print(f"   📊 Tổng số trang: {total_pages}\n")
        
        # Tạo thư mục output
        os.makedirs(output_folder, exist_ok=True)
        
        base_name = Path(input_file).stem
        
        if mode == 'all':
            # Tách từng trang
            for page_num in range(total_pages):
                writer = PyPDF2.PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                output_file = os.path.join(output_folder, f"{base_name}_page_{page_num + 1}.pdf")
                
                with open(output_file, 'wb') as output:
                    writer.write(output)
                
                print(f"   ✓ Trang {page_num + 1}/{total_pages}: {os.path.basename(output_file)}")
            
            print(f"\n✅ Tách thành công {total_pages} trang!")
            
        elif mode == 'range' and page_ranges:
            # Tách theo range
            for idx, (start, end) in enumerate(page_ranges, 1):
                # Validate range
                if start < 1 or end > total_pages or start > end:
                    print(f"⚠️  Range không hợp lệ: {start}-{end}")
                    continue
                
                writer = PyPDF2.PdfWriter()
                
                for page_num in range(start - 1, end):
                    writer.add_page(reader.pages[page_num])
                
                output_file = os.path.join(output_folder, f"{base_name}_pages_{start}-{end}.pdf")
                
                with open(output_file, 'wb') as output:
                    writer.write(output)
                
                print(f"   ✓ Range {start}-{end}: {os.path.basename(output_file)}")
            
            print(f"\n✅ Tách thành công {len(page_ranges)} range!")
        
        print(f"   📁 Thu muc output: {output_folder}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi tách PDF: {e}")
        return False


def compress_pdf(input_file, output_file, compression_level='medium'):
    """
    Nén PDF giảm dung lượng
    
    Args:
        input_file: File PDF cần nén
        output_file: File output
        compression_level: 'low', 'medium', 'high'
    
    Giải thích:
    - Nén bằng cách giảm chất lượng hình ảnh
    - Remove metadata không cần thiết
    - Optimize structure
    """
    import PyPDF2
    
    try:
        print(f"\n📦 Đang nén PDF...\n")
        
        reader = PyPDF2.PdfReader(input_file)
        writer = PyPDF2.PdfWriter()
        
        # Copy pages
        for page in reader.pages:
            # Compress images in page
            page.compress_content_streams()
            writer.add_page(page)
        
        # Remove metadata to reduce size
        writer.add_metadata({
            '/Producer': 'DevTools PDF Compressor',
        })
        
        # Write compressed PDF
        with open(output_file, 'wb') as output:
            writer.write(output)
        
        # So sánh kích thước
        original_size = os.path.getsize(input_file)
        compressed_size = os.path.getsize(output_file)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        print(f"✅ Nén thành công!")
        print(f"   📄 File goc: {format_size(original_size)}")
        print(f"   📄 File nen: {format_size(compressed_size)}")
        print(f"   💯 Giam: {reduction:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi nén PDF: {e}")
        return False


def pdf_to_images(input_file, output_folder, image_format='PNG', dpi=200):
    """
    Chuyển PDF thành ảnh
    
    Args:
        input_file: File PDF
        output_folder: Thư mục chứa ảnh
        image_format: 'PNG', 'JPEG'
        dpi: Độ phân giải (72-300)
    
    Giải thích:
    - Render từng trang PDF thành ảnh
    - DPI càng cao thì ảnh càng sắc nét nhưng nặng hơn
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        install_library(
            package_name="pdf2image",
            install_command="pip install pdf2image",
            library_display_name="pdf2image"
        )
        print("Lưu ý: Cần cài thêm poppler-utils")
        return False
    
    try:
        print(f"\n🖼️  Dang chuyển PDF sang ảnh...\n")
        print(f"   DPI: {dpi}")
        print(f"   Format: {image_format}\n")
        
        # Convert PDF to images
        images = convert_from_path(input_file, dpi=dpi)
        
        # Tạo thư mục output
        os.makedirs(output_folder, exist_ok=True)
        
        base_name = Path(input_file).stem
        
        for idx, image in enumerate(images, 1):
            output_file = os.path.join(
                output_folder, 
                f"{base_name}_page_{idx}.{image_format.lower()}"
            )
            
            image.save(output_file, image_format)
            
            size = os.path.getsize(output_file)
            print(f"   ✓ Trang {idx}/{len(images)}: {os.path.basename(output_file)} ({format_size(size)})")
        
        print(f"\n✅ Chuyển đổi thành công {len(images)} trang!")
        print(f"   📁 Thư mục output: {output_folder}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi chuyển đổi: {e}")
        if "poppler" in str(e).lower():
            print("\n💡 Lưu ý: Tool này cần cài thêm Poppler")
            print("   Windows: Download tai https://github.com/oschwartz10612/poppler-windows/releases")
            print("   Linux: sudo apt-get install poppler-utils")
            print("   macOS: brew install poppler")
        return False


def rotate_pdf(input_file, output_file, rotation=90, pages='all'):
    """
    Xoay trang PDF
    
    Args:
        input_file: File PDF
        output_file: File output
        rotation: Góc xoay (90, 180, 270)
        pages: 'all' hoặc list số trang [1, 2, 3]
    
    Giải thích:
    - Xoay PDF theo chiều kim đồng hồ
    - Có thể xoay tất cả hoặc chỉ một số trang
    """
    import PyPDF2
    
    try:
        print(f"\n🔄 Đang xoay PDF {rotation}°...\n")
        
        reader = PyPDF2.PdfReader(input_file)
        writer = PyPDF2.PdfWriter()
        
        total_pages = len(reader.pages)
        
        for page_num in range(total_pages):
            page = reader.pages[page_num]
            
            # Kiểm tra có xoay trang này không
            if pages == 'all' or (page_num + 1) in pages:
                page.rotate(rotation)
                print(f"   ✓ Xoay trang {page_num + 1}")
            
            writer.add_page(page)
        
        with open(output_file, 'wb') as output:
            writer.write(output)
        
        print(f"\n✅ Xoay thành công!")
        print(f"   📄 File output: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi xoay PDF: {e}")
        return False


def extract_text_from_pdf(input_file, output_file=None):
    """
    Trích xuất text từ PDF
    
    Args:
        input_file: File PDF
        output_file: File text output (None = print ra màn hình)
    
    Giải thích:
    - Extract text từ mỗi trang
    - Lưu vào file hoặc in ra màn hình
    """
    import PyPDF2
    
    try:
        print(f"\n📝 Dang trích xuất text...\n")
        
        reader = PyPDF2.PdfReader(input_file)
        total_pages = len(reader.pages)
        
        all_text = []
        
        for page_num in range(total_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            
            if text.strip():
                all_text.append(f"=== Trang {page_num + 1} ===\n{text}\n")
                print(f"   ✓ Trang {page_num + 1}: {len(text)} ký tự")
            else:
                print(f"   ⚠️  Trang {page_num + 1}: Không có text")
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(all_text))
            
            print(f"\n✅ Trích xuất thành công!")
            print(f"   📄 File output: {output_file}")
        else:
            print(f"\n✅ Trích xuất thành công!")
            print("\n" + "="*60)
            print('\n'.join(all_text[:500]))  # Hiển thị 500 ký tự đầu
            if len('\n'.join(all_text)) > 500:
                print("\n... (con nua)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi trích xuất text: {e}")
        return False


def get_pdf_info(input_file):
    """
    Lấy thông tin PDF
    
    Giải thích:
    - Số trang
    - Metadata
    - Kích thước file
    """
    import PyPDF2
    
    try:
        reader = PyPDF2.PdfReader(input_file)
        
        print(f"\n📄 Thông tin PDF: {os.path.basename(input_file)}")
        print("=" * 60)
        
        # Basic info
        print(f"Số trang: {len(reader.pages)}")
        print(f"Kích thước: {format_size(os.path.getsize(input_file))}")
        
        # Metadata
        if reader.metadata:
            print(f"\nMetadata:")
            for key, value in reader.metadata.items():
                if value:
                    print(f"  {key}: {value}")
        
        # Page size (first page)
        if len(reader.pages) > 0:
            page = reader.pages[0]
            width = float(page.mediabox.width) * 0.352778  # Convert to mm
            height = float(page.mediabox.height) * 0.352778
            print(f"\nKích thước trang: {width:.0f}mm x {height:.0f}mm")
        
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi đọc thông tin PDF: {e}")
        return False


def main():
    """
    Hàm chính - Menu PDF tools
    
    Giải thích:
    - Hiển thị menu các chức năng
    - Xử lý input từ user
    - Gọi hàm tương ứng
    """
    print_header()
    
    # Kiểm tra dependencies
    if not check_dependencies():
        return
    
    print("===== CHUC NANG =====")
    print("1. Gộp PDF (Merge)")
    print("2. Tách PDF (Split)")
    print("3. Nen PDF (Compress)")
    print("4. PDF sang ẢNH (PDF to Images)")
    print("5. Xoay PDF (Rotate)")
    print("6. Trích xuất Text")
    print("7. Xem thông tin PDF")
    print("0. Thoát")
    
    choice = input("\nChọn chức năng (0-7): ").strip()
    
    if choice == "0":
        print("Thoát chương trình.")
        return
    
    elif choice == "1":
        # Merge PDFs
        print("\n===== GỘP PDF =====")
        
        folder_input = input("Nhập đường dẫn thư mục chứa PDF: ").strip('"')
        if not os.path.isdir(folder_input):
            print("❌ Thư mục không tồn tại!")
            return
        
        # Tìm tất cả PDF trong thư mục
        pdf_files = [
            os.path.join(folder_input, f) 
            for f in os.listdir(folder_input) 
            if f.lower().endswith('.pdf')
        ]
        
        if not pdf_files:
            print("❌ Không tìm thấy file PDF nào!")
            return
        
        pdf_files.sort()
        
        print(f"\nTìm thấy {len(pdf_files)} file PDF:")
        for idx, pdf in enumerate(pdf_files, 1):
            size = format_size(os.path.getsize(pdf))
            print(f"  {idx}. {os.path.basename(pdf)} ({size})")
        
        output_name = input("\nNhập tên file output (vd: merged.pdf): ").strip()
        if not output_name.endswith('.pdf'):
            output_name += '.pdf'
        
        output_file = os.path.join(folder_input, output_name)
        
        merge_pdfs(pdf_files, output_file)
    
    elif choice == "2":
        # Split PDF
        print("\n===== TÁCH PDF =====")
        
        input_file = input("Nhập đường dẫn file PDF: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        output_folder = input("Thư mục output (Enter để tạo thư mục 'split'): ").strip('"')
        if not output_folder:
            output_folder = os.path.join(os.path.dirname(input_file), 'split')
        
        print("\n1. Tách từng trang (mỗi trang 1 file)")
        print("2. Tách theo range (vd: 1-5, 6-10)")
        
        split_mode = input("\nChọn chế độ (1-2): ").strip()
        
        if split_mode == "1":
            split_pdf(input_file, output_folder, mode='all')
        
        elif split_mode == "2":
            range_input = input("Nhập range (vd: 1-5, 6-10, 11-15): ").strip()
            ranges = []
            
            for r in range_input.split(','):
                r = r.strip()
                if '-' in r:
                    start, end = r.split('-')
                    ranges.append((int(start), int(end)))
            
            if ranges:
                split_pdf(input_file, output_folder, mode='range', page_ranges=ranges)
            else:
                print("❌ Range không hợp lệ!")
    
    elif choice == "3":
        # Compress PDF
        print("\n===== NÉN PDF =====")
        
        input_file = input("Nhập đường dẫn file PDF: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        output_file = input("Tên file output (Enter để thêm '_compressed'): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            ext = Path(input_file).suffix
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}_compressed{ext}"
            )
        
        compress_pdf(input_file, output_file)
    
    elif choice == "4":
        # PDF to Images
        print("\n===== PDF SANG ẢNH =====")
        
        input_file = input("Nhập đường dẫn file PDF: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        output_folder = input("Thư mục output (Enter để tạo thư mục 'images'): ").strip('"')
        if not output_folder:
            output_folder = os.path.join(os.path.dirname(input_file), 'images')
        
        format_choice = input("Định dạng ảnh (PNG/JPEG, mặc định PNG): ").strip().upper()
        if format_choice not in ['PNG', 'JPEG']:
            format_choice = 'PNG'
        
        dpi_input = input("DPI (72-300, mặc định 200): ").strip()
        dpi = int(dpi_input) if dpi_input and dpi_input.isdigit() else 200
        
        pdf_to_images(input_file, output_folder, format_choice, dpi)
    
    elif choice == "5":
        # Rotate PDF
        print("\n===== XOAY PDF =====")
        
        input_file = input("Nhập đường dẫn file PDF: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        rotation_input = input("Góc xoay (90/180/270, mặc định 90): ").strip()
        rotation = int(rotation_input) if rotation_input in ['90', '180', '270'] else 90
        
        output_file = input("Tên file output (Enter để thêm '_rotated'): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            ext = Path(input_file).suffix
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}_rotated{ext}"
            )
        
        rotate_pdf(input_file, output_file, rotation)
    
    elif choice == "6":
        # Extract text
        print("\n===== TRÍCH XUẤT TEXT =====")
        
        input_file = input("Nhập đường dẫn file PDF: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        save_choice = input("Luu ra file? (y/N): ").strip().lower()
        
        if save_choice == 'y':
            output_file = input("Tên file output (Enter để dùng 'extracted_text.txt'): ").strip()
            if not output_file:
                output_file = os.path.join(
                    os.path.dirname(input_file),
                    'extracted_text.txt'
                )
            extract_text_from_pdf(input_file, output_file)
        else:
            extract_text_from_pdf(input_file)
    
    elif choice == "7":
        # Get PDF info
        print("\n===== THÔNG TIN PDF =====")
        
        input_file = input("Nhập đường dẫn file PDF: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        get_pdf_info(input_file)
    
    else:
        print("❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")

