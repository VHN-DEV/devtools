#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Nén và chỉnh sửa ảnh hàng loạt

Mục đích: Giảm dung lượng ảnh, resize, đổi format
Lý do: Tối ưu ảnh cho web, tiết kiệm dung lượng
"""

import os
import sys
import datetime
import argparse
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from concurrent.futures import ProcessPoolExecutor, as_completed

# Thêm thư mục cha vào sys.path để import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    print_header, format_size, get_user_input, confirm_action,
    get_file_list, ensure_directory_exists, ProgressBar, 
    log_info, log_error, setup_logger, normalize_path,
    install_library
)

# Kiểm tra thư viện PIL
try:
    from PIL import Image
except ImportError:
    install_library(
        package_name="Pillow",
        install_command="pip install Pillow",
        library_display_name="Pillow"
    )
    sys.exit(1)


def compress_single_image(
    input_path: str,
    output_path: str,
    quality: int = 70,
    optimize: bool = True,
    max_size_kb: Optional[int] = None,
    convert_format: Optional[str] = None,
    resize_width: Optional[int] = None,
    resize_height: Optional[int] = None
) -> Tuple[bool, str, int, int]:
    """
    Nén và xử lý một ảnh
    
    Args:
        input_path: Đường dẫn ảnh gốc
        output_path: Đường dẫn ảnh đầu ra
        quality: Chất lượng nén (1-100)
        optimize: Có optimize không
        max_size_kb: Dung lượng tối đa (KB)
        convert_format: Định dạng đích (jpg, png, webp)
        resize_width: Chiều rộng mới (None = giữ nguyên)
        resize_height: Chiều cao mới (None = giữ nguyên)
    
    Returns:
        tuple: (success, message, old_size, new_size)
    
    Giải thích:
    - Mở ảnh và xử lý resize nếu cần
    - Đổi format nếu cần
    - Nén với quality chỉ định
    - Nếu có max_size_kb, giảm dần quality cho đến khi đạt
    - Trả về kết quả và kích thước file
    """
    try:
        # Bước 1: Mở ảnh gốc
        img = Image.open(input_path)
        original_format = img.format
        old_size = os.path.getsize(input_path)
        
        # Bước 2: Resize nếu có yêu cầu
        if resize_width or resize_height:
            orig_w, orig_h = img.size
            
            # Kiểm tra kích thước hợp lệ (tránh division by zero)
            if orig_w == 0 or orig_h == 0:
                return False, f"Ảnh có kích thước không hợp lệ: {orig_w}x{orig_h}", old_size, old_size
            
            if resize_width and resize_height:
                # Resize theo đúng width & height nhập vào
                new_size = (resize_width, resize_height)
            elif resize_width:
                # Resize theo width, giữ tỷ lệ
                ratio = resize_width / orig_w
                new_size = (resize_width, int(orig_h * ratio))
            else:  # resize_height
                # Resize theo height, giữ tỷ lệ
                ratio = resize_height / orig_h
                new_size = (int(orig_w * ratio), resize_height)
            
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Bước 3: Xác định format đầu ra
        if convert_format:
            target_format = convert_format.upper()
            if target_format == "JPG":
                target_format = "JPEG"
            
            # Convert sang RGB nếu cần thiết cho JPEG hoặc WEBP (nếu không cần alpha)
            if target_format in ["JPEG", "WEBP"] and img.mode in ("RGBA", "LA", "P"):
                # Với WEBP, kiểm tra xem có alpha channel thực sự không
                if target_format == "WEBP" and img.mode == "RGBA":
                    # Kiểm tra xem alpha channel có trong suốt không
                    alpha = img.split()[3]
                    has_transparency = any(pixel < 255 for pixel in alpha.getdata())
                    
                    if not has_transparency:
                        # Không có transparency thực sự, convert sang RGB để nhanh hơn
                        img = img.convert("RGB")
                else:
                    # Tạo background trắng cho JPEG hoặc các mode khác
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = background
        else:
            target_format = original_format or "JPEG"
        
        # Bước 4: Đảm bảo thư mục đầu ra tồn tại
        ensure_directory_exists(os.path.dirname(output_path))
        
        # Bước 5: Lưu ảnh với nén
        save_kwargs = {
            'format': target_format,
            'optimize': optimize
        }
        
        # Thêm quality cho các format hỗ trợ
        if target_format in ['JPEG', 'WEBP']:
            save_kwargs['quality'] = quality
        
        # Tối ưu WEBP: thêm method parameter để tăng tốc độ
        # method: 0-6, 6 = nhanh nhất (ít nén), 0 = chậm nhất (nén tốt nhất)
        # Dùng method=6 để tăng tốc độ xử lý
        if target_format == 'WEBP':
            save_kwargs['method'] = 6  # Tối ưu cho tốc độ
            # Tắt optimize cho WEBP khi có max_size_kb để tăng tốc độ
            # (vì chúng ta đã tự động điều chỉnh quality rồi)
            if max_size_kb:
                save_kwargs['optimize'] = False
        
        img.save(output_path, **save_kwargs)
        
        # Bước 6: Nếu có max_size_kb, giảm dần quality (tối ưu hóa)
        if max_size_kb and target_format in ['JPEG', 'WEBP']:
            current_quality = quality
            max_size_bytes = max_size_kb * 1024
            current_size = os.path.getsize(output_path)
            
            # Nếu file đã nhỏ hơn yêu cầu, bỏ qua
            if current_size <= max_size_bytes:
                pass
            else:
                # Tối ưu: dùng binary search approach thay vì linear
                # Bước 1: Giảm nhanh quality với step lớn để tìm khoảng
                min_quality = 10
                max_quality = current_quality
                
                # Giảm nhanh với step 10-15 để tìm khoảng gần đúng
                while current_size > max_size_bytes and current_quality > min_quality:
                    current_quality = max(min_quality, current_quality - 15)
                    save_kwargs['quality'] = current_quality
                    img.save(output_path, **save_kwargs)
                    current_size = os.path.getsize(output_path)
                
                # Bước 2: Nếu vẫn chưa đạt, tinh chỉnh với step nhỏ hơn
                if current_size > max_size_bytes and current_quality > min_quality:
                    # Tìm quality tối ưu với step nhỏ hơn
                    while current_size > max_size_bytes and current_quality > min_quality:
                        current_quality = max(min_quality, current_quality - 5)
                        save_kwargs['quality'] = current_quality
                        img.save(output_path, **save_kwargs)
                        current_size = os.path.getsize(output_path)
        
        new_size = os.path.getsize(output_path)
        
        # Tính tỷ lệ nén
        reduction = ((old_size - new_size) / old_size) * 100 if old_size > 0 else 0
        
        message = f"{format_size(old_size)} → {format_size(new_size)} (-{reduction:.1f}%)"
        
        return True, message, old_size, new_size
        
    except Exception as e:
        return False, str(e), 0, 0


def batch_compress_images(
    input_dir: str,
    output_dir: str,
    quality: int = 70,
    optimize: bool = True,
    max_size_kb: Optional[int] = None,
    convert_format: Optional[str] = None,
    resize_width: Optional[int] = None,
    resize_height: Optional[int] = None,
    use_multiprocessing: bool = True,
    max_workers: Optional[int] = None
) -> Tuple[int, int, int, int, List[Dict]]:
    """
    Nén ảnh hàng loạt
    
    Args:
        input_dir: Thư mục chứa ảnh gốc
        output_dir: Thư mục đầu ra
        quality: Chất lượng nén
        optimize: Có optimize không
        max_size_kb: Dung lượng tối đa
        convert_format: Định dạng đích
        resize_width: Chiều rộng mới
        resize_height: Chiều cao mới
        use_multiprocessing: Có dùng multiprocessing không
        max_workers: Số workers (None = auto)
    
    Returns:
        tuple: (success_count, error_count, total_old_size, total_new_size, file_details)
        file_details: List các dict chứa thông tin chi tiết từng file
    
    Giải thích:
    - Quét tất cả ảnh trong thư mục
    - Xử lý song song với multiprocessing (nếu enabled)
    - Hiển thị progress bar
    - Trả về thống kê và danh sách chi tiết từng file
    """
    # Bước 1: Lấy danh sách ảnh
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff']
    image_files = get_file_list(
        input_dir,
        extensions=image_extensions,
        recursive=False  # Chỉ quét thư mục hiện tại
    )
    
    if not image_files:
        print("❌ Không tìm thấy ảnh nào!")
        return 0, 0, 0, 0, []
    
    print(f"📸 Tìm thấy {len(image_files)} ảnh\n")
    log_info(f"Bắt đầu nén {len(image_files)} ảnh")
    
    # Bước 2: Tạo thư mục đầu ra
    ensure_directory_exists(output_dir)
    
    # Bước 3: Chuẩn bị tasks
    tasks = []
    for img_path in image_files:
        filename = os.path.basename(img_path)
        
        # Đổi extension nếu convert format
        if convert_format:
            name_without_ext = os.path.splitext(filename)[0]
            ext = convert_format.lower()
            if ext == "jpeg":
                ext = "jpg"
            filename = f"{name_without_ext}.{ext}"
        
        output_path = os.path.join(output_dir, filename)
        
        tasks.append({
            'input_path': img_path,
            'output_path': output_path,
            'quality': quality,
            'optimize': optimize,
            'max_size_kb': max_size_kb,
            'convert_format': convert_format,
            'resize_width': resize_width,
            'resize_height': resize_height
        })
    
    # Bước 4: Xử lý ảnh
    success_count = 0
    error_count = 0
    total_old_size = 0
    total_new_size = 0
    file_details = []  # List để lưu thông tin chi tiết từng file
    
    progress = ProgressBar(len(tasks), prefix="Đang xử lý:")
    progress.update(0)  # Hiển thị progress bar ngay từ đầu
    
    if use_multiprocessing and len(tasks) > 1:
        # Xử lý song song với multiprocessing
        import multiprocessing
        if max_workers is None:
            max_workers = min(multiprocessing.cpu_count(), len(tasks))
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    compress_single_image,
                    task['input_path'],
                    task['output_path'],
                    task['quality'],
                    task['optimize'],
                    task['max_size_kb'],
                    task['convert_format'],
                    task['resize_width'],
                    task['resize_height']
                ): task for task in tasks
            }
            
            for future in as_completed(futures):
                task = futures[future]
                filename = os.path.basename(task['input_path'])
                
                try:
                    success, message, old_size, new_size = future.result()
                    
                    if success:
                        success_count += 1
                        total_old_size += old_size
                        total_new_size += new_size
                        # Lưu thông tin chi tiết
                        reduction = ((old_size - new_size) / old_size) * 100 if old_size > 0 else 0
                        file_details.append({
                            'filename': filename,
                            'old_size': old_size,
                            'new_size': new_size,
                            'reduction': reduction,
                            'status': 'success'
                        })
                        progress.update(message=f"✅ {filename}")
                        log_info(f"Nén thành công: {filename} - {message}")
                    else:
                        error_count += 1
                        file_details.append({
                            'filename': filename,
                            'old_size': old_size if old_size > 0 else os.path.getsize(task['input_path']) if os.path.exists(task['input_path']) else 0,
                            'new_size': 0,
                            'reduction': 0,
                            'status': 'error',
                            'error': message
                        })
                        progress.update(message=f"❌ {filename}: {message}")
                        log_error(f"Lỗi nén {filename}: {message}")
                
                except Exception as e:
                    error_count += 1
                    old_size_temp = os.path.getsize(task['input_path']) if os.path.exists(task['input_path']) else 0
                    file_details.append({
                        'filename': filename,
                        'old_size': old_size_temp,
                        'new_size': 0,
                        'reduction': 0,
                        'status': 'error',
                        'error': str(e)
                    })
                    progress.update(message=f"❌ {filename}: {str(e)}")
                    log_error(f"Exception khi nén {filename}: {str(e)}")
    else:
        # Xử lý tuần tự
        for task in tasks:
            filename = os.path.basename(task['input_path'])
            
            success, message, old_size, new_size = compress_single_image(
                task['input_path'],
                task['output_path'],
                task['quality'],
                task['optimize'],
                task['max_size_kb'],
                task['convert_format'],
                task['resize_width'],
                task['resize_height']
            )
            
            if success:
                success_count += 1
                total_old_size += old_size
                total_new_size += new_size
                # Lưu thông tin chi tiết
                reduction = ((old_size - new_size) / old_size) * 100 if old_size > 0 else 0
                file_details.append({
                    'filename': filename,
                    'old_size': old_size,
                    'new_size': new_size,
                    'reduction': reduction,
                    'status': 'success'
                })
                progress.update(message=f"✅ {filename}")
                log_info(f"Nén thành công: {filename} - {message}")
            else:
                error_count += 1
                file_details.append({
                    'filename': filename,
                    'old_size': old_size if old_size > 0 else os.path.getsize(task['input_path']) if os.path.exists(task['input_path']) else 0,
                    'new_size': 0,
                    'reduction': 0,
                    'status': 'error',
                    'error': message
                })
                progress.update(message=f"❌ {filename}: {message}")
                log_error(f"Lỗi nén {filename}: {message}")
    
    progress.finish()
    
    return success_count, error_count, total_old_size, total_new_size, file_details


def print_detailed_statistics(file_details: List[Dict]):
    """
    Hiển thị bảng thống kê chi tiết từng file ảnh đã nén
    
    Args:
        file_details: List các dict chứa thông tin chi tiết từng file
    
    Giải thích:
    - Sắp xếp theo tên file
    - Hiển thị dạng bảng với: tên file, dung lượng gốc, dung lượng mới, tỷ lệ giảm
    """
    if not file_details:
        return
    
    print(f"\n{'='*80}")
    print("📊 THỐNG KÊ CHI TIẾT TỪNG FILE ẢNH")
    print(f"{'='*80}\n")
    
    # Sắp xếp theo tên file
    sorted_details = sorted(file_details, key=lambda x: x['filename'].lower())
    
    # Tính độ rộng cột (giới hạn tối đa 50 ký tự để bảng không quá rộng)
    max_filename_len = max(len(d['filename']) for d in sorted_details)
    max_filename_len = min(max(max_filename_len, 25), 50)  # Tối thiểu 25, tối đa 50 ký tự
    
    # In header
    header = f"{'STT':<5} | {'Tên file':<{max_filename_len}} | {'Dung lượng gốc':<15} | {'Dung lượng mới':<15} | {'Tỷ lệ giảm':<12} | {'Trạng thái'}"
    print(header)
    print("-" * len(header))
    
    # In từng dòng
    for idx, detail in enumerate(sorted_details, 1):
        filename = detail['filename']
        # Rút ngắn tên file nếu quá dài
        if len(filename) > max_filename_len:
            filename = filename[:max_filename_len-3] + "..."
        
        old_size_str = format_size(detail['old_size'])
        new_size_str = format_size(detail['new_size']) if detail['status'] == 'success' else "N/A"
        
        if detail['status'] == 'success':
            reduction_str = f"-{detail['reduction']:.1f}%"
            status_str = "✅ Thành công"
        else:
            reduction_str = "N/A"
            error_msg = detail.get('error', 'Lỗi không xác định')
            # Rút ngắn thông báo lỗi để phù hợp với cột
            if len(error_msg) > 25:
                error_msg = error_msg[:22] + "..."
            status_str = f"❌ {error_msg}"
        
        row = f"{idx:<5} | {filename:<{max_filename_len}} | {old_size_str:<15} | {new_size_str:<15} | {reduction_str:<12} | {status_str}"
        print(row)
    
    print(f"\n{'='*80}\n")


def main_interactive():
    """
    Chế độ interactive (menu nhập liệu)
    
    Giải thích:
    - Hỏi người dùng từng thông số
    - Hiển thị kết quả chi tiết
    """
    print_header("TOOL NÉN VÀ CHỈNH SỬA ẢNH")
    
    # Nhập thư mục input
    print("💡 Mẹo: Bạn có thể kéo thả thư mục vào terminal để nhập đường dẫn")
    input_dir_raw = get_user_input("Nhập đường dẫn thư mục chứa ảnh")
    input_dir = normalize_path(input_dir_raw)
    
    if not os.path.isdir(input_dir):
        print(f"❌ Thư mục không tồn tại: {input_dir}")
        return
    
    print(f"✅ Đã chọn: {input_dir}\n")
    
    # Nhập thư mục output
    default_output = os.path.join(
        input_dir,
        f"compressed_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    output_dir_raw = get_user_input(
        "Nhập đường dẫn thư mục đầu ra (Enter để mặc định)",
        default=default_output
    )
    output_dir = normalize_path(output_dir_raw)
    
    # Quality
    quality_input = get_user_input("Nhập quality (1-100, mặc định 70)", default="70")
    try:
        quality = int(quality_input)
        quality = max(1, min(100, quality))
    except ValueError:
        quality = 70
    
    # Optimize
    optimize_input = get_user_input("Có bật optimize không? (Y/n, mặc định Yes)", default="y")
    optimize = optimize_input.lower() != "n"
    
    # Convert format
    convert_format = get_user_input(
        "Muốn đổi sang định dạng nào? (jpg, png, webp - Enter để giữ nguyên)",
        default=None
    )
    if convert_format and convert_format.lower() not in ['jpg', 'jpeg', 'png', 'webp', 'bmp']:
        print("⚠️  Format không hợp lệ, giữ nguyên format gốc")
        convert_format = None
    
    # Max size
    max_size_input = get_user_input("Nhập dung lượng tối đa mỗi ảnh (KB, Enter để bỏ qua)", default=None)
    max_size_kb = int(max_size_input) if max_size_input and max_size_input.isdigit() else None
    
    # Resize
    resize_w_input = get_user_input("Nhập chiều rộng (px, Enter để bỏ qua)", default=None)
    resize_width = int(resize_w_input) if resize_w_input and resize_w_input.isdigit() else None
    
    resize_h_input = get_user_input("Nhập chiều cao (px, Enter để bỏ qua)", default=None)
    resize_height = int(resize_h_input) if resize_h_input and resize_h_input.isdigit() else None
    
    # Multiprocessing
    use_mp = get_user_input("Sử dụng multiprocessing? (Y/n, mặc định Yes)", default="y")
    use_multiprocessing = use_mp.lower() != "n"
    
    # Xác nhận
    print("\n===== XÁC NHẬN CẤU HÌNH =====")
    print(f"📁 Thư mục đầu vào: {input_dir}")
    print(f"📁 Thư mục đầu ra: {output_dir}")
    print(f"🎨 Quality: {quality}")
    print(f"⚡ Optimize: {'Có' if optimize else 'Không'}")
    if convert_format:
        print(f"🔄 Format: {convert_format.upper()}")
    if max_size_kb:
        print(f"📊 Dung lượng tối đa: {max_size_kb} KB")
    if resize_width or resize_height:
        print(f"📏 Resize: {resize_width or 'auto'}x{resize_height or 'auto'} px")
    print(f"⚡ Multiprocessing: {'Có' if use_multiprocessing else 'Không'}")
    
    if not confirm_action("Bắt đầu xử lý?"):
        print("❌ Đã hủy")
        return
    
    # Xử lý
    print(f"\n🚀 Bắt đầu nén ảnh...\n")
    
    success, errors, old_size, new_size, file_details = batch_compress_images(
        input_dir, output_dir, quality, optimize, max_size_kb,
        convert_format, resize_width, resize_height, use_multiprocessing
    )
    
    # Hiển thị kết quả tổng quan
    print(f"\n{'='*60}")
    print(f"✅ Hoàn thành!")
    print(f"   - Thành công: {success} ảnh")
    print(f"   - Lỗi: {errors} ảnh")
    print(f"   - Dung lượng gốc: {format_size(old_size)}")
    print(f"   - Dung lượng mới: {format_size(new_size)}")
    if old_size > 0:
        reduction = ((old_size - new_size) / old_size) * 100
        print(f"   - Tiết kiệm: {format_size(old_size - new_size)} ({reduction:.1f}%)")
    print(f"   - Thư mục: {output_dir}")
    print(f"{'='*60}")
    
    # Hiển thị thống kê chi tiết từng file
    print_detailed_statistics(file_details)
    
    log_info(f"Hoàn thành nén: {success} thành công, {errors} lỗi")


def main_cli(args):
    """
    Chế độ CLI (command line arguments)
    
    Args:
        args: Arguments từ argparse
    
    Giải thích:
    - Chạy tool bằng command line
    - Hữu ích cho scripting và automation
    """
    # Validate input
    if not os.path.isdir(args.input):
        print(f"❌ Thư mục không tồn tại: {args.input}")
        return 1
    
    # Xử lý
    success, errors, old_size, new_size, file_details = batch_compress_images(
        args.input,
        args.output,
        args.quality,
        args.optimize,
        args.max_size,
        args.format,
        args.width,
        args.height,
        not args.no_multiprocessing
    )
    
    # Hiển thị kết quả ngắn gọn
    print(f"\n✅ {success} thành công, ❌ {errors} lỗi")
    if old_size > 0:
        reduction = ((old_size - new_size) / old_size) * 100
        print(f"💾 Tiết kiệm: {format_size(old_size - new_size)} ({reduction:.1f}%)")
    
    return 0 if errors == 0 else 1


def main():
    """
    Hàm main - điều phối giữa interactive và CLI mode
    
    Giải thích:
    - Nếu có arguments -> CLI mode
    - Nếu không -> Interactive mode
    """
    # Setup logger
    setup_logger('compress-images', log_to_console=False)
    
    # Tạo argument parser
    parser = argparse.ArgumentParser(
        description='Tool nén và chỉnh sửa ảnh hàng loạt',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  # Chế độ interactive
  python compress-images.py
  
  # Nén với quality 80
  python compress-images.py -i ./images -o ./output -q 80
  
  # Resize và convert sang WebP
  python compress-images.py -i ./images -o ./output -f webp -w 1920
  
  # Giới hạn dung lượng tối đa 500KB
  python compress-images.py -i ./images -o ./output --max-size 500
        """
    )
    
    parser.add_argument('-i', '--input', help='Thư mục chứa ảnh đầu vào')
    parser.add_argument('-o', '--output', help='Thư mục đầu ra')
    parser.add_argument('-q', '--quality', type=int, default=70, 
                       help='Chất lượng nén (1-100, mặc định: 70)')
    parser.add_argument('--no-optimize', dest='optimize', action='store_false',
                       help='Tắt optimization')
    parser.add_argument('-f', '--format', choices=['jpg', 'jpeg', 'png', 'webp'],
                       help='Đổi sang định dạng khác')
    parser.add_argument('--max-size', type=int, help='Dung lượng tối đa (KB)')
    parser.add_argument('-w', '--width', type=int, help='Chiều rộng mới (px)')
    parser.add_argument('-H', '--height', type=int, help='Chiều cao mới (px)')
    parser.add_argument('--no-multiprocessing', action='store_true',
                       help='Tắt multiprocessing')
    
    # Parse arguments
    args, unknown = parser.parse_known_args()
    
    # Nếu có -i thì dùng CLI mode
    if args.input:
        if not args.output:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output = os.path.join(args.input, f"compressed_{timestamp}")
        
        sys.exit(main_cli(args))
    else:
        # Interactive mode
        try:
            main_interactive()
        except KeyboardInterrupt:
            print("\n\n❌ Đã hủy!")
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            log_error(f"Exception: {e}", exc_info=True)


if __name__ == "__main__":
    main()
