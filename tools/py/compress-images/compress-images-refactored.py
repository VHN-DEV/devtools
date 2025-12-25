#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Nén và chỉnh sửa ảnh hàng loạt (Refactored)

Mục đích: Giảm dung lượng ảnh, resize, đổi format
Lý do: Tối ưu ảnh cho web, tiết kiệm dung lượng

Refactored using new tool base classes and patterns
"""

import os
import sys
import datetime
import argparse
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from concurrent.futures import ProcessPoolExecutor, as_completed

from utils import (
    BaseTool, InteractiveToolMixin, CLIToolMixin, ImageProcessingToolMixin,
    BatchProcessor, display_batch_results, collect_processing_results,
    print_header, format_size, ensure_directory_exists,
    log_info, log_error, install_missing_library
)

# Check PIL dependency
if not install_missing_library('PIL', display_name='Pillow'):
    sys.exit(1)

from PIL import Image


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
        if target_format == 'WEBP':
            save_kwargs['method'] = 6  # Tối ưu cho tốc độ
            # Tắt optimize cho WEBP khi có max_size_kb để tăng tốc độ
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


class ImageCompressionProcessor(BatchProcessor):
    """
    Custom batch processor for image compression
    """

    def __init__(self, **kwargs):
        # Set image-specific defaults
        kwargs.setdefault('file_extensions', ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff'])
        super().__init__(**kwargs)

        # Image-specific options
        self.quality = kwargs.get('quality', 70)
        self.optimize = kwargs.get('optimize', True)
        self.max_size_kb = kwargs.get('max_size_kb')
        self.convert_format = kwargs.get('convert_format')
        self.resize_width = kwargs.get('resize_width')
        self.resize_height = kwargs.get('resize_height')

    def process_single_file(self, file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Process a single image file

        Args:
            file_path: Path to image file

        Returns:
            tuple: (success, message, result_data)
        """
        # Generate output path
        if self.output_path:
            filename = os.path.basename(file_path)

            # Change extension if converting format
            if self.convert_format:
                name_without_ext = os.path.splitext(filename)[0]
                ext = self.convert_format.lower()
                if ext == "jpeg":
                    ext = "jpg"
                filename = f"{name_without_ext}.{ext}"

            output_file = self.output_path / filename
        else:
            # Same directory with _compressed suffix
            base_name = os.path.splitext(file_path)[0]
            ext = os.path.splitext(file_path)[1]
            if self.convert_format:
                ext = f".{self.convert_format.lower()}"
                if ext == ".jpeg":
                    ext = ".jpg"
            output_file = Path(f"{base_name}_compressed{ext}")

        # Compress the image
        success, message, old_size, new_size = compress_single_image(
            input_path=file_path,
            output_path=str(output_file),
            quality=self.quality,
            optimize=self.optimize,
            max_size_kb=self.max_size_kb,
            convert_format=self.convert_format,
            resize_width=self.resize_width,
            resize_height=self.resize_height
        )

        result_data = {
            'old_size': old_size,
            'new_size': new_size,
            'output_path': str(output_file)
        }

        return success, message, result_data


class CompressImagesTool(BaseTool, InteractiveToolMixin, CLIToolMixin, ImageProcessingToolMixin):
    """
    Compress Images tool using new base classes
    """

    def __init__(self, tool_file: str):
        super().__init__(tool_file)

        # Set tool dependencies
        self.set_dependencies({
            'PIL': {
                'import_name': 'PIL',
                'install_command': 'pip install Pillow',
                'display_name': 'Pillow (PIL)'
            }
        })

    def get_description(self) -> str:
        """Get tool description"""
        return "Nén và chỉnh sửa ảnh hàng loạt - Giảm dung lượng ảnh, resize, đổi format"

    def run_interactive(self) -> int:
        """
        Run tool in interactive mode

        Returns:
            int: Exit code
        """
        print_header("NÉN VÀ CHỈNH SỬA ẢNH")

        # Nhập thư mục input
        print("💡 Mẹo: Bạn có thể kéo thả thư mục vào terminal để nhập đường dẫn")
        input_dir = self.get_user_path("Nhập đường dẫn thư mục chứa ảnh")
        if not input_dir:
            return 1

        if not os.path.isdir(input_dir):
            print(f"❌ Thư mục không tồn tại: {input_dir}")
            return 1

        print(f"✅ Đã chọn: {input_dir}\n")

        # Nhập thư mục output
        default_output = os.path.join(input_dir, f"compressed_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        output_dir_raw = self.get_user_path(
            "Nhập đường dẫn thư mục đầu ra (Enter để mặc định)",
            default=default_output
        )
        output_dir = output_dir_raw or default_output

        # Quality
        quality_options = ["Thấp (50%)", "Trung bình (70%)", "Cao (90%)", "Tùy chỉnh"]
        quality_choice = self.get_user_choice("Chọn chất lượng nén:", quality_options, default=1)

        if quality_choice == 3:  # Tùy chỉnh
            quality = self.get_numeric_input("Nhập quality (1-100)", default=70, min_value=1, max_value=100)
        else:
            quality_map = [50, 70, 90]
            quality = quality_map[quality_choice] if quality_choice is not None else 70

        # Optimize
        optimize = self.get_boolean_input("Có bật optimize không? (Y/n)", default=True)

        # Convert format
        format_options = ["Giữ nguyên", "JPG", "PNG", "WebP"]
        format_choice = self.get_user_choice("Muốn đổi sang định dạng nào?", format_options, default=0)

        convert_format = None
        if format_choice and format_choice > 0:
            format_map = [None, "jpg", "png", "webp"]
            convert_format = format_map[format_choice]

        # Max size
        max_size_kb = self.get_numeric_input(
            "Nhập dung lượng tối đa mỗi ảnh (KB, Enter để bỏ qua)",
            min_value=1
        )

        # Resize
        resize_width = self.get_numeric_input(
            "Nhập chiều rộng (px, Enter để bỏ qua)",
            min_value=1
        )
        resize_height = self.get_numeric_input(
            "Nhập chiều cao (px, Enter để bỏ qua)",
            min_value=1
        )

        # Confirm
        print("
===== XÁC NHẬN CẤU HÌNH ====="        print(f"📁 Thư mục đầu vào: {input_dir}")
        print(f"📁 Thư mục đầu ra: {output_dir}")
        print(f"🎨 Quality: {quality}")
        print(f"⚡ Optimize: {'Có' if optimize else 'Không'}")
        if convert_format:
            print(f"🔄 Format: {convert_format.upper()}")
        if max_size_kb:
            print(f"📊 Dung lượng tối đa: {max_size_kb} KB")
        if resize_width or resize_height:
            print(f"📏 Resize: {resize_width or 'auto'}x{resize_height or 'auto'} px")

        if not self.get_user_confirmation("Bắt đầu xử lý?"):
            print("❌ Đã hủy")
            return 0

        # Setup processor
        processor = ImageCompressionProcessor(
            input_path=input_dir,
            output_path=output_dir,
            quality=quality,
            optimize=optimize,
            max_size_kb=max_size_kb,
            convert_format=convert_format,
            resize_width=resize_width,
            resize_height=resize_height
        )

        # Process files
        print(f"\n🚀 Bắt đầu nén ảnh...\n")
        results = self.process_files_batch(processor, show_progress=True)

        # Display results
        self.display_processing_results(results)

        return 0

    def setup_cli_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Setup CLI argument parser

        Args:
            parser: Argument parser to configure
        """
        # Add image processing arguments
        self.add_image_args(parser)

        # Add multiprocessing control
        parser.add_argument(
            '--no-multiprocessing',
            action='store_true',
            help='Tắt multiprocessing'
        )

    def run_cli(self, args: argparse.Namespace) -> int:
        """
        Run tool in CLI mode

        Args:
            args: Parsed CLI arguments

        Returns:
            int: Exit code
        """
        # Validate arguments
        if not self.validate_cli_inputs(args) or not self.validate_image_args(args):
            return 1

        # Setup processor
        processor = ImageCompressionProcessor(
            input_path=args.input,
            output_path=args.output,
            quality=args.quality,
            optimize=not getattr(args, 'no_optimize', False),
            max_size_kb=getattr(args, 'max_size', None),
            convert_format=getattr(args, 'format', None),
            resize_width=getattr(args, 'width', None),
            resize_height=getattr(args, 'height', None),
            use_multiprocessing=not getattr(args, 'no_multiprocessing', False)
        )

        # Process files
        results = self.process_files_batch(processor, show_progress=not getattr(args, 'quiet', False))

        if 'error' in results:
            print(f"❌ Lỗi: {results['error']}")
            return 1

        # Display summary for CLI
        stats = results.get('stats', {})
        if stats:
            success_count = stats.get('success_count', 0)
            error_count = stats.get('error_count', 0)

            print(f"\n✅ {success_count} thành công, ❌ {error_count} lỗi")

            if stats.get('total_input_size', 0) > 0:
                reduction = stats.get('compression_ratio', 0)
                saved = format_size(stats.get('space_saved', 0))
                print(f"💾 Tiết kiệm: {saved} ({reduction:.1f}%)")

        return 0 if stats.get('error_count', 0) == 0 else 1


def main():
    """Main entry point"""
    tool = CompressImagesTool(__file__)
    return tool.run()


if __name__ == "__main__":
    exit(main())
