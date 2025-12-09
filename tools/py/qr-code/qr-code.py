#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Tạo và Giải mã QR Code

Mục đích: Tạo QR code từ nội dung và giải mã QR code từ ảnh
Lý do: Marketing, thanh toán, chia sẻ link, quét mã hàng loạt
"""

import os
import sys
import time
import argparse
import contextlib
import shutil
import csv
import json
import re
from pathlib import Path
from typing import List, Tuple, Optional, TYPE_CHECKING, Dict
from datetime import datetime

# Import Image cho type hint (nếu có)
if TYPE_CHECKING:
    from PIL import Image

# Thêm thư mục cha vào sys.path để import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import (
    print_header, get_user_input, confirm_action,
    ensure_directory_exists, log_info, log_error, normalize_path,
    install_library
)
from utils.colors import Colors

# ==================== QR CODE GENERATOR ====================

# Kiểm tra thư viện tạo QR code
try:
    import qrcode
    from PIL import Image
    QRCODE_GEN_AVAILABLE = True
except ImportError:
    QRCODE_GEN_AVAILABLE = False
    qrcode = None  # Set to None nếu không có
    Image = None  # Set to None nếu không có

# Kiểm tra thư viện giải mã QR code
try:
    import cv2
    import numpy as np
    from pyzbar.pyzbar import decode
    QRCODE_DECODE_AVAILABLE = True
except ImportError:
    QRCODE_DECODE_AVAILABLE = False

# OCR tùy chọn
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Clipboard (tùy chọn)
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    pyperclip = None  # Set to None nếu không có

# CSV/JSON processing
CSV_AVAILABLE = True  # Built-in module


# ==================== HÀM TẠO QR CODE ====================

def create_qr_code(
    data: str,
    output_path: str,
    size: int = 10,
    border: int = 4,
    error_correction: str = "M",
    fill_color: str = "black",
    back_color: str = "white",
    box_size: Optional[int] = None,
    add_logo: Optional[str] = None,
    logo_size_ratio: float = 0.3
) -> Tuple[bool, str]:
    """Tạo QR code từ dữ liệu"""
    if not QRCODE_GEN_AVAILABLE:
        return False, "Thiếu thư viện qrcode. Cài đặt: pip install qrcode[pil]"
    
    # Import qrcode module vào local scope để tránh UnboundLocalError
    import qrcode as qr_module
    
    try:
        qr = qr_module.QRCode(
            version=1,
            error_correction=get_error_correction_level(error_correction),
            box_size=box_size if box_size is not None else size,
            border=border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(
            fill_color=fill_color,
            back_color=back_color
        )
        
        if add_logo and os.path.exists(add_logo):
            img = add_logo_to_qr(img, add_logo, logo_size_ratio)
        
        ensure_directory_exists(os.path.dirname(output_path) if os.path.dirname(output_path) else ".")
        
        # Xác định định dạng từ extension
        output_ext = os.path.splitext(output_path)[1].lower()
        
        # Hỗ trợ nhiều định dạng ảnh
        if output_ext in ['.png', '.PNG']:
            img.save(output_path, 'PNG', optimize=True)
        elif output_ext in ['.jpg', '.jpeg', '.JPG', '.JPEG']:
            # Chuyển sang RGB nếu cần (JPG không hỗ trợ transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            img.save(output_path, 'JPEG', quality=95, optimize=True)
        elif output_ext in ['.svg', '.SVG']:
            # SVG cần xử lý đặc biệt - tạo QR dạng vector
            try:
                # Import SVG factory từ module đã import
                import qrcode.image.svg as svg_module
                
                if os.path.exists(output_path):
                    os.remove(output_path)
                
                # Sử dụng qr_module để tránh xung đột
                factory = svg_module.SvgPathImage
                qr_svg_obj = qr_module.QRCode(
                    version=1,
                    error_correction=get_error_correction_level(error_correction),
                    box_size=box_size if box_size is not None else size,
                    border=border,
                    image_factory=factory
                )
                qr_svg_obj.add_data(data)
                qr_svg_obj.make(fit=True)
                img_svg = qr_svg_obj.make_image(fill_color=fill_color, back_color=back_color)
                img_svg.save(open(output_path, 'wb'))
            except Exception as svg_error:
                # Fallback: lưu PNG thay vì SVG nếu lỗi
                output_path_png = output_path.replace('.svg', '.png').replace('.SVG', '.png')
                img.save(output_path_png, 'PNG', optimize=True)
                message = f"Không thể lưu SVG, đã lưu PNG: {output_path_png}"
                file_size = os.path.getsize(output_path_png)
                return True, f"{message} ({file_size / 1024:.1f} KB)"
        elif output_ext in ['.bmp', '.BMP']:
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(output_path, 'BMP')
        elif output_ext in ['.tiff', '.tif', '.TIFF', '.TIF']:
            img.save(output_path, 'TIFF', compression='lzw')
        else:
            # Mặc định lưu PNG nếu không nhận diện được extension
            if not output_ext:
                output_path = output_path + '.png'
            else:
                output_path = os.path.splitext(output_path)[0] + '.png'
            img.save(output_path, 'PNG', optimize=True)
        
        file_size = os.path.getsize(output_path)
        message = f"Đã tạo QR code: {output_path} ({file_size / 1024:.1f} KB)"
        return True, message
        
    except Exception as e:
        return False, f"Lỗi: {str(e)}"


def get_error_correction_level(level: str) -> int:
    """Chuyển đổi mức sửa lỗi từ string sang constant"""
    if not QRCODE_GEN_AVAILABLE:
        return 1  # Default ERROR_CORRECT_M
    
    # Import vào local scope để tránh UnboundLocalError
    import qrcode as qr_module
    
    level_map = {
        'L': qr_module.constants.ERROR_CORRECT_L,  # ~7%
        'M': qr_module.constants.ERROR_CORRECT_M,  # ~15%
        'Q': qr_module.constants.ERROR_CORRECT_Q,  # ~25%
        'H': qr_module.constants.ERROR_CORRECT_H,  # ~30%
    }
    return level_map.get(level.upper(), qr_module.constants.ERROR_CORRECT_M)


def add_logo_to_qr(qr_img: "Image.Image", logo_path: str, size_ratio: float = 0.3) -> "Image.Image":
    """Thêm logo vào giữa QR code"""
    try:
        logo = Image.open(logo_path)
        qr_width, qr_height = qr_img.size
        logo_size = int(min(qr_width, qr_height) * size_ratio)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        logo_with_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 0))
        logo_with_bg.paste(logo, (0, 0), logo if logo.mode == 'RGBA' else None)
        
        if qr_img.mode != 'RGBA':
            qr_img = qr_img.convert('RGBA')
        
        pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
        qr_img.paste(logo_with_bg, pos, logo_with_bg)
        
        return qr_img.convert('RGB')
        
    except Exception as e:
        log_error(f"Không thể thêm logo: {e}")
        return qr_img


def parse_color(color_str: str) -> str:
    """Parse màu từ hex hoặc tên màu"""
    color_str = color_str.strip()
    
    if color_str.startswith('#'):
        return color_str
    
    color_names = {
        'black': '#000000',
        'white': '#FFFFFF',
        'red': '#FF0000',
        'green': '#00FF00',
        'blue': '#0000FF',
        'yellow': '#FFFF00',
        'orange': '#FFA500',
        'purple': '#800080',
    }
    
    return color_names.get(color_str.lower(), color_str)


# ==================== QR CODE TYPES GENERATION ====================

def create_wifi_qr(ssid: str, password: str, security: str = "WPA", hidden: bool = False) -> str:
    """Tạo dữ liệu QR code cho WiFi"""
    security_map = {
        "WPA": "WPA",
        "WPA2": "WPA2",
        "WEP": "WEP",
        "nopass": "nopass"
    }
    sec = security_map.get(security.upper(), "WPA")
    hidden_str = "true" if hidden else "false"
    return f"WIFI:T:{sec};S:{ssid};P:{password};H:{hidden_str};;"


def create_email_qr(email: str, subject: str = "", body: str = "") -> str:
    """Tạo dữ liệu QR code cho Email"""
    params = [f"mailto:{email}"]
    if subject:
        params.append(f"subject={subject}")
    if body:
        params.append(f"body={body}")
    return "&".join(params)


def create_sms_qr(phone: str, message: str = "") -> str:
    """Tạo dữ liệu QR code cho SMS"""
    if message:
        return f"sms:{phone}?body={message}"
    return f"sms:{phone}"


def create_phone_qr(phone: str) -> str:
    """Tạo dữ liệu QR code cho số điện thoại"""
    return f"tel:{phone}"


def create_vcard_qr(name: str, phone: str = "", email: str = "", org: str = "", 
                    url: str = "", address: str = "") -> str:
    """Tạo dữ liệu QR code cho vCard"""
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{name}"]
    if phone:
        lines.append(f"TEL:{phone}")
    if email:
        lines.append(f"EMAIL:{email}")
    if org:
        lines.append(f"ORG:{org}")
    if url:
        lines.append(f"URL:{url}")
    if address:
        lines.append(f"ADR:;;{address};;;")
    lines.append("END:VCARD")
    return "\n".join(lines)


def create_location_qr(latitude: float, longitude: float, altitude: float = 0) -> str:
    """Tạo dữ liệu QR code cho vị trí địa lý"""
    return f"geo:{latitude},{longitude},{altitude}"


def create_url_qr(url: str) -> str:
    """Tạo dữ liệu QR code cho URL"""
    if not url.startswith(('http://', 'https://')):
        return f"https://{url}"
    return url


# ==================== HÀM GIẢI MÃ QR CODE ====================

def decode_safe(pil_img):
    """Giải mã barcode bằng pyzbar, ẩn cảnh báo stderr"""
    with contextlib.redirect_stderr(open(os.devnull, 'w')):
        return decode(pil_img)


def enhance_contrast_and_sharpness(img):
    """Tăng tương phản bằng CLAHE và làm nét ảnh"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    return sharpened


def auto_crop_barcode(image_cv):
    """Phát hiện vùng có khả năng chứa mã vạch"""
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    grad = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    grad = cv2.convertScaleAbs(grad)
    
    _, thresh = cv2.threshold(grad, 225, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    closed = cv2.erode(closed, None, iterations=4)
    closed = cv2.dilate(closed, None, iterations=4)
    
    contours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    
    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    return image_cv[y:y + h, x:x + w]


def enhance_image(img):
    """Làm nét ảnh mạnh hơn"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    
    blurred = cv2.GaussianBlur(resized, (9, 9), 10.0)
    unsharp = cv2.addWeighted(resized, 1.5, blurred, -0.5, 0)
    denoised = cv2.fastNlMeansDenoising(unsharp, None, h=15, templateWindowSize=7, searchWindowSize=21)
    
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)


def try_decode_with_rotation(pil_img, angle_list=[90, 180, 270]):
    """Thử xoay ảnh ở các góc và decode lại"""
    for angle in angle_list:
        rotated = pil_img.rotate(angle, expand=True)
        barcodes = decode_safe(rotated)
        if barcodes:
            return barcodes
    return []


def decode_with_ocr(image_path):
    """Dùng OCR để đọc text từ ảnh (nếu có pytesseract)"""
    if not OCR_AVAILABLE:
        return []
    
    try:
        ocr_text = pytesseract.image_to_string(Image.open(image_path))
        import re
        text = ocr_text.upper().replace('\n', ' ').replace('\r', ' ').strip()
        text = re.sub(r'[^A-Z0-9]', ' ', text)
        candidates = re.findall(r'\b[A-Z0-9]{8,20}\b', text)
        return list(set(candidates))
    except Exception:
        return []


def process_image(image_path: Path) -> Tuple[List, Optional[str], str]:
    """Xử lý từng ảnh để giải mã barcode/QR code"""
    if not QRCODE_DECODE_AVAILABLE:
        return [], None, "Thiếu thư viện. Cài đặt: pip install opencv-python pyzbar pillow numpy"
    
    try:
        image_pil = Image.open(image_path)
        barcodes = decode_safe(image_pil)
        if barcodes and any(b.data.strip() for b in barcodes):
            return barcodes, "pyzbar", "Thành công từ ảnh gốc"
        
        image_cv = cv2.imread(str(image_path))
        if image_cv is None:
            return [], None, "Không thể đọc ảnh"
        
        cropped = auto_crop_barcode(image_cv)
        if cropped is not None:
            enhanced = enhance_contrast_and_sharpness(cropped)
            temp_path = str(image_path) + ".temp.jpg"
            cv2.imwrite(temp_path, enhanced)
            
            try:
                image_pil_cropped = Image.open(temp_path)
                barcodes = decode_safe(image_pil_cropped)
                if barcodes:
                    os.remove(temp_path)
                    return barcodes, "pyzbar", "Thành công sau crop + enhance"
                
                barcodes = try_decode_with_rotation(image_pil_cropped)
                if barcodes:
                    os.remove(temp_path)
                    return barcodes, "pyzbar", "Thành công sau xoay"
                
                enhanced_strong = enhance_image(cropped)
                cv2.imwrite(temp_path, enhanced_strong)
                image_pil_fallback = Image.open(temp_path)
                barcodes = decode_safe(image_pil_fallback)
                if barcodes:
                    os.remove(temp_path)
                    return barcodes, "pyzbar", "Thành công sau enhance mạnh"
                
                os.remove(temp_path)
            except Exception:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        barcodes = try_decode_with_rotation(image_pil)
        if barcodes:
            return barcodes, "pyzbar", "Thành công sau xoay ảnh gốc"
        
        if OCR_AVAILABLE:
            ocr_result = decode_with_ocr(image_path)
            if ocr_result:
                class DummyBarcode:
                    def __init__(self, data): 
                        self.data = data.encode('utf-8') if isinstance(data, str) else data
                return [DummyBarcode(data) for data in ocr_result], "ocr", "Đọc được bằng OCR"
        
        return [], None, "Không tìm thấy barcode"
        
    except Exception as e:
        return [], None, f"Lỗi: {e}"


def process_directory(directory: Path, move_success: bool = True):
    """Xử lý toàn bộ thư mục"""
    start_time = time.time()
    total_ok = 0
    total_nok = 0
    total_files = 0
    
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    for ext in extensions:
        total_files += len(list(directory.rglob(f'*{ext}')))
        total_files += len(list(directory.rglob(f'*{ext.upper()}')))
    
    if total_files == 0:
        print(Colors.warning("⚠️  Không tìm thấy file ảnh nào!"))
        return
    
    ok_dir = directory / 'ok'
    if move_success:
        ok_dir.mkdir(exist_ok=True)
    
    log_path = directory / 'result.txt'
    summary_path = directory / 'results.txt'
    
    with open(log_path, 'w', encoding='utf-8') as log_file, \
         open(summary_path, 'w', encoding='utf-8') as summary_file:
        
        summary_file.write(f"Kết quả quét barcode/QR code\n")
        summary_file.write(f"{'='*70}\n\n")
        
        for ext in extensions:
            for file_path in directory.rglob(f'*{ext}'):
                if 'ok' in str(file_path) or '.temp' in str(file_path):
                    continue
                
                print(f"\r{Colors.muted(f'Đang xử lý: {file_path.name:<50}')}", end='', flush=True)
                
                barcodes, method, status = process_image(file_path)
                
                if barcodes:
                    decoded_data = ", ".join([b.data.decode('utf-8', errors='ignore') for b in barcodes])
                    log_line = f"{file_path.name} → OK | {decoded_data} | Method: {method}"
                    
                    log_file.write(log_line + "\n")
                    summary_file.write(log_line + "\n")
                    
                    if move_success:
                        try:
                            shutil.move(str(file_path), str(ok_dir / file_path.name))
                        except Exception:
                            pass
                    
                    total_ok += 1
                    print(f"\r{Colors.success('✓')} {file_path.name}")
                else:
                    log_line = f"{file_path.name} → NOK | {status}"
                    log_file.write(log_line + "\n")
                    total_nok += 1
        
        total = total_ok + total_nok
        percent_ok = round((total_ok / total * 100), 2) if total > 0 else 0
        elapsed = round(time.time() - start_time, 2)
        
        summary = f"""
{'='*70}
Tổng kết:
  - Tổng số ảnh: {total}
  - Thành công: {total_ok} ({percent_ok}%)
  - Thất bại: {total_nok} ({100 - percent_ok:.2f}%)
  - Thời gian: {elapsed} giây
{'='*70}
"""
        summary_file.write(summary)
        log_file.write(summary)
        
        print(summary)


def process_directory_with_export(directory: Path, output_format: str = "txt", 
                                  move_success: bool = True):
    """Xử lý thư mục và export kết quả ra JSON/CSV"""
    start_time = time.time()
    results = []
    total_ok = 0
    total_nok = 0
    
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    ok_dir = directory / 'ok'
    if move_success:
        ok_dir.mkdir(exist_ok=True)
    
    for ext in extensions:
        for file_path in directory.rglob(f'*{ext}'):
            if 'ok' in str(file_path) or '.temp' in str(file_path):
                continue
            
            print(f"\r{Colors.muted(f'Đang xử lý: {file_path.name:<50}')}", end='', flush=True)
            
            barcodes, method, status = process_image(file_path)
            
            if barcodes:
                decoded_data = [b.data.decode('utf-8', errors='ignore') for b in barcodes]
                result = {
                    'filename': file_path.name,
                    'path': str(file_path),
                    'status': 'OK',
                    'data': decoded_data[0] if len(decoded_data) == 1 else decoded_data,
                    'method': method,
                    'timestamp': datetime.now().isoformat()
                }
                results.append(result)
                
                if move_success:
                    try:
                        shutil.move(str(file_path), str(ok_dir / file_path.name))
                    except Exception:
                        pass
                
                total_ok += 1
                print(f"\r{Colors.success('✓')} {file_path.name}")
            else:
                result = {
                    'filename': file_path.name,
                    'path': str(file_path),
                    'status': 'FAILED',
                    'data': None,
                    'method': None,
                    'error': status,
                    'timestamp': datetime.now().isoformat()
                }
                results.append(result)
                total_nok += 1
    
    # Export results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_format.lower() == 'json':
        output_file = directory / f'qr_results_{timestamp}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total': total_ok + total_nok,
                    'success': total_ok,
                    'failed': total_nok,
                    'success_rate': f"{(total_ok / (total_ok + total_nok) * 100):.2f}%" if (total_ok + total_nok) > 0 else "0%",
                    'elapsed_time': f"{round(time.time() - start_time, 2)} seconds"
                },
                'results': results
            }, f, ensure_ascii=False, indent=2)
        print(Colors.success(f"\n✅ Đã export JSON: {output_file}"))
    
    elif output_format.lower() == 'csv':
        output_file = directory / f'qr_results_{timestamp}.csv'
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        print(Colors.success(f"\n✅ Đã export CSV: {output_file}"))
    
    # Always write text summary
    summary_file = directory / f'results_{timestamp}.txt'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Kết quả quét QR code\n{'='*70}\n\n")
        for result in results:
            if result['status'] == 'OK':
                f.write(f"{result['filename']} → OK | {result['data']} | Method: {result['method']}\n")
            else:
                f.write(f"{result['filename']} → FAILED | {result.get('error', 'Unknown error')}\n")
        
        total = total_ok + total_nok
        percent_ok = round((total_ok / total * 100), 2) if total > 0 else 0
        elapsed = round(time.time() - start_time, 2)
        f.write(f"\n{'='*70}\n")
        f.write(f"Tổng số ảnh: {total}\n")
        f.write(f"Thành công: {total_ok} ({percent_ok}%)\n")
        f.write(f"Thất bại: {total_nok} ({100 - percent_ok:.2f}%)\n")
        f.write(f"Thời gian: {elapsed} giây\n")
    
    print(f"\n✅ Đã lưu kết quả: {summary_file}")


def decode_from_webcam():
    """Đọc QR code từ webcam"""
    if not QRCODE_DECODE_AVAILABLE:
        print(Colors.error("❌ Cần cài đặt: pip install opencv-python pyzbar pillow numpy"))
        return
    
    print_header("ĐỌC QR CODE TỪ WEBCAM", width=70)
    print(Colors.primary("  📹 QUÉT QR CODE TỪ CAMERA"))
    print()
    print(Colors.warning("⚠️  Nhấn 'q' để thoát"))
    print()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(Colors.error("❌ Không thể mở camera!"))
        return
    
    print(Colors.success("✅ Camera đã sẵn sàng. Đưa QR code vào khung hình..."))
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Decode QR code
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            barcodes = decode_safe(Image.fromarray(gray))
            
            if barcodes:
                for barcode in barcodes:
                    data = barcode.data.decode('utf-8')
                    print(f"\n{Colors.success('✅ Tìm thấy:')} {Colors.primary(data)}")
                    
                    if confirm_action("Lưu kết quả vào file?"):
                        output_file = f"webcam_qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(data)
                        print(Colors.success(f"✅ Đã lưu: {output_file}"))
                    
                    if not confirm_action("Tiếp tục quét?"):
                        cap.release()
                        cv2.destroyAllWindows()
                        return
                    # Tiếp tục quét tự động
            
            # Hiển thị frame với text hướng dẫn
            cv2.putText(frame, "Press 'q' to quit", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('QR Code Scanner - Press Q to quit', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print(Colors.warning("\n⚠️  Đã dừng bởi người dùng"))
    finally:
        cap.release()
        cv2.destroyAllWindows()


def batch_generate_from_csv(csv_path: str, output_dir: str, 
                           size: int = 10, border: int = 4, 
                           error_correction: str = "M"):
    """Tạo QR code hàng loạt từ file CSV"""
    if not QRCODE_GEN_AVAILABLE:
        print(Colors.error("❌ Cần cài đặt: pip install qrcode[pil]"))
        return
    
    csv_path_normalized = normalize_path(csv_path)
    output_dir_normalized = normalize_path(output_dir)
    
    if not os.path.exists(csv_path_normalized):
        print(Colors.error(f"❌ File CSV không tồn tại: {csv_path}"))
        return
    
    ensure_directory_exists(output_dir_normalized)
    
    print(f"\n📖 Đọc file CSV: {csv_path}")
    print(f"💾 Thư mục output: {output_dir}")
    
    success_count = 0
    error_count = 0
    
    try:
        with open(csv_path_normalized, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Kiểm tra các cột cần thiết
            if 'data' not in reader.fieldnames and 'content' not in reader.fieldnames:
                print(Colors.error("❌ CSV phải có cột 'data' hoặc 'content'"))
                return
            
            data_column = 'data' if 'data' in reader.fieldnames else 'content'
            filename_column = 'filename' if 'filename' in reader.fieldnames else None
            
            for idx, row in enumerate(reader, 1):
                data = row[data_column].strip()
                if not data:
                    continue
                
                # Tạo tên file
                if filename_column and row.get(filename_column):
                    filename = row[filename_column].strip()
                else:
                    # Tạo tên từ data (giới hạn 50 ký tự)
                    safe_name = re.sub(r'[^\w\-_.]', '_', data[:50])
                    filename = f"qr_{idx:04d}_{safe_name}.png"
                
                output_path = os.path.join(output_dir_normalized, filename)
                
                # Tùy chỉnh từ CSV nếu có
                qr_size = int(row.get('size', size))
                qr_border = int(row.get('border', border))
                qr_error = row.get('error_correction', error_correction).upper()
                fill_color = parse_color(row.get('fill_color', 'black'))
                back_color = parse_color(row.get('back_color', 'white'))
                
                print(f"\r{Colors.muted(f'Đang tạo: {filename:<50}')}", end='', flush=True)
                
                success, message = create_qr_code(
                    data=data,
                    output_path=output_path,
                    size=qr_size,
                    border=qr_border,
                    error_correction=qr_error,
                    fill_color=fill_color,
                    back_color=back_color
                )
                
                if success:
                    success_count += 1
                    print(f"\r{Colors.success('✓')} {filename}")
                else:
                    error_count += 1
                    print(f"\r{Colors.error('✗')} {filename} - {message}")
        
        print(f"\n\n{'='*70}")
        print(f"✅ Thành công: {success_count}")
        print(f"❌ Lỗi: {error_count}")
        print(f"{'='*70}")
        
    except Exception as e:
        print(Colors.error(f"\n❌ Lỗi khi đọc CSV: {e}"))


def batch_generate_from_text(text_path: str, output_dir: str, 
                             size: int = 10, border: int = 4):
    """Tạo QR code hàng loạt từ file text (mỗi dòng = 1 QR code)"""
    if not QRCODE_GEN_AVAILABLE:
        print(Colors.error("❌ Cần cài đặt: pip install qrcode[pil]"))
        return
    
    text_path_normalized = normalize_path(text_path)
    output_dir_normalized = normalize_path(output_dir)
    
    if not os.path.exists(text_path_normalized):
        print(Colors.error(f"❌ File text không tồn tại: {text_path}"))
        return
    
    ensure_directory_exists(output_dir_normalized)
    
    success_count = 0
    error_count = 0
    
    try:
        with open(text_path_normalized, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f, 1):
                data = line.strip()
                if not data or data.startswith('#'):  # Bỏ qua dòng trống và comment
                    continue
                
                safe_name = re.sub(r'[^\w\-_.]', '_', data[:50])
                filename = f"qr_{idx:04d}_{safe_name}.png"
                output_path = os.path.join(output_dir_normalized, filename)
                
                print(f"\r{Colors.muted(f'Đang tạo: {filename:<50}')}", end='', flush=True)
                
                success, message = create_qr_code(
                    data=data,
                    output_path=output_path,
                    size=size,
                    border=border
                )
                
                if success:
                    success_count += 1
                    print(f"\r{Colors.success('✓')} {filename}")
                else:
                    error_count += 1
                    print(f"\r{Colors.error('✗')} {filename}")
        
        print(f"\n\n{'='*70}")
        print(f"✅ Thành công: {success_count}")
        print(f"❌ Lỗi: {error_count}")
        print(f"{'='*70}")
        
    except Exception as e:
        print(Colors.error(f"\n❌ Lỗi khi đọc file: {e}"))


# ==================== INTERACTIVE MODES ====================

def mode_generate():
    """Chế độ tạo QR code"""
    print_header("TẠO QR CODE", width=70)
    print(Colors.primary("  📱 TẠO QR CODE TỪ TEXT/URL"))
    print()
    
    if not QRCODE_GEN_AVAILABLE:
        install_library(
            package_name="qrcode[pil]",
            install_command="pip install qrcode[pil]",
            library_display_name="qrcode"
        )
        return
    
    while True:
        data = get_user_input("Nhập nội dung cần tạo QR code (text, URL, etc.): ")
        if data:
            break
        print(Colors.error("❌ Vui lòng nhập nội dung!"))
    
    print("\n📤 Định dạng file (PNG, JPG, SVG, BMP, TIFF):")
    print("  - PNG: Chất lượng cao, hỗ trợ transparency (mặc định)")
    print("  - JPG: File nhỏ hơn, không transparency")
    print("  - SVG: Vector, có thể scale không giới hạn")
    print("  - BMP, TIFF: Định dạng ảnh khác")
    
    default_output = "qr_code.png"
    output_path_raw = get_user_input(
        "Nhập đường dẫn file lưu (Enter để mặc định: qr_code.png): ",
        default=default_output
    )
    output_path = normalize_path(output_path_raw)
    
    # Đảm bảo có extension
    if not os.path.splitext(output_path)[1]:
        output_path = output_path + '.png'
    
    print("\n⚙️  Tùy chỉnh QR Code:")
    
    size_input = get_user_input("Kích thước box (mặc định 10): ", default="10")
    try:
        box_size = int(size_input)
    except ValueError:
        box_size = 10
    
    border_input = get_user_input("Độ dày border (mặc định 4): ", default="4")
    try:
        border = int(border_input)
    except ValueError:
        border = 4
    
    error_input = get_user_input(
        "Mức sửa lỗi (L/M/Q/H, mặc định M): ",
        default="M"
    )
    error_correction = error_input.upper() if error_input.upper() in ['L', 'M', 'Q', 'H'] else 'M'
    
    fill_color_input = get_user_input(
        "Màu mã QR (black, #000000, hoặc tên màu, mặc định black): ",
        default="black"
    )
    fill_color = parse_color(fill_color_input)
    
    back_color_input = get_user_input(
        "Màu nền (white, #FFFFFF, hoặc tên màu, mặc định white): ",
        default="white"
    )
    back_color = parse_color(back_color_input)
    
    logo_path_raw = get_user_input(
        "Đường dẫn logo (Enter để bỏ qua): ",
        default=None
    )
    logo_path = normalize_path(logo_path_raw) if logo_path_raw else None
    
    if logo_path and not os.path.exists(logo_path):
        print(Colors.warning("⚠️  Logo không tồn tại, bỏ qua logo"))
        logo_path = None
    
    logo_size_ratio = 0.3
    if logo_path:
        ratio_input = get_user_input(
            "Tỷ lệ logo so với QR (0.1-0.4, mặc định 0.3): ",
            default="0.3"
        )
        try:
            logo_size_ratio = float(ratio_input)
            logo_size_ratio = max(0.1, min(0.4, logo_size_ratio))
        except ValueError:
            logo_size_ratio = 0.3
    
    print("\n===== XÁC NHẬN =====")
    print(f"📝 Nội dung: {data[:50]}{'...' if len(data) > 50 else ''}")
    print(f"💾 File lưu: {output_path}")
    print(f"📏 Kích thước box: {box_size}")
    print(f"🔲 Border: {border}")
    print(f"🛡️  Sửa lỗi: {error_correction}")
    print(f"🎨 Màu mã: {fill_color}")
    print(f"🎨 Màu nền: {back_color}")
    if logo_path:
        print(f"🖼️  Logo: {logo_path}")
    
    if not confirm_action("Tạo QR code?"):
        print("❌ Đã hủy!")
        return
    
    print(f"\n🔨 Đang tạo QR code...")
    
    success, message = create_qr_code(
        data=data,
        output_path=output_path,
        size=box_size,
        border=border,
        error_correction=error_correction,
        fill_color=fill_color,
        back_color=back_color,
        add_logo=logo_path,
        logo_size_ratio=logo_size_ratio
    )
    
    if success:
        print(Colors.success(f"✅ {message}"))
        log_info(f"Tạo QR code thành công: {output_path}")
        
        if os.name == 'nt':
            print(f"\n💡 File đã được tạo: {output_path}")
            if confirm_action("Mở file ngay bây giờ?"):
                if os.path.exists(output_path):
                    os.startfile(output_path)
                else:
                    print(Colors.warning(f"⚠️  File không tồn tại: {output_path}"))
        elif sys.platform == 'darwin':
            if os.path.exists(output_path):
                os.system(f'open "{output_path}"')
            else:
                print(Colors.warning(f"⚠️  File không tồn tại: {output_path}"))
        elif sys.platform.startswith('linux'):
            if os.path.exists(output_path):
                os.system(f'xdg-open "{output_path}"')
            else:
                print(Colors.warning(f"⚠️  File không tồn tại: {output_path}"))
    else:
        print(Colors.error(f"❌ {message}"))
        log_error(f"Lỗi tạo QR code: {message}")


def mode_decode():
    """Chế độ giải mã QR code"""
    print_header("GIẢI MÃ QR CODE", width=70)
    print(Colors.primary("  📷 GIẢI MÃ MÃ VẠCH VÀ QR CODE TỪ ẢNH"))
    print()
    
    if not QRCODE_DECODE_AVAILABLE:
        install_library(
            package_name="opencv-python pyzbar pillow numpy",
            install_command="pip install opencv-python pyzbar pillow numpy",
            library_display_name="opencv-python, pyzbar, pillow, numpy"
        )
        return
    
    while True:
        directory = get_user_input("Nhập đường dẫn thư mục chứa ảnh: ")
        if directory:
            break
        print(Colors.error("❌ Vui lòng nhập đường dẫn thư mục!"))
    directory = normalize_path(directory)
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(Colors.error(f"❌ Thư mục không tồn tại: {directory}"))
        return
    
    if not directory_path.is_dir():
        print(Colors.error(f"❌ Đường dẫn không phải thư mục: {directory}"))
        return
    
    print("\n⚙️  Tùy chọn:")
    print("  (Nhập Y để di chuyển, N để giữ nguyên)")
    move_success = confirm_action("Di chuyển ảnh thành công vào thư mục 'ok'?")
    
    print(f"\n📁 Thư mục: {directory}")
    if not confirm_action("Bắt đầu quét?"):
        print("❌ Đã hủy!")
        return
    
    print(f"\n🔍 Đang quét...")
    print(Colors.muted("=" * 70))
    
    process_directory(directory_path, move_success)
    
    print()
    print(Colors.success("✅ Hoàn tất! Xem kết quả trong result.txt và results.txt"))


def mode_decode_with_export():
    """Chế độ giải mã QR code với export JSON/CSV"""
    print_header("GIẢI MÃ QR CODE VỚI EXPORT", width=70)
    print(Colors.primary("  📷 GIẢI MÃ VÀ XUẤT KẾT QUẢ RA JSON/CSV"))
    print()
    
    if not QRCODE_DECODE_AVAILABLE:
        install_library(
            package_name="opencv-python pyzbar pillow numpy",
            install_command="pip install opencv-python pyzbar pillow numpy",
            library_display_name="opencv-python, pyzbar, pillow, numpy"
        )
        return
    
    while True:
        directory = get_user_input("Nhập đường dẫn thư mục chứa ảnh: ")
        if directory:
            break
        print(Colors.error("❌ Vui lòng nhập đường dẫn thư mục!"))
    directory = normalize_path(directory)
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(Colors.error(f"❌ Thư mục không tồn tại: {directory}"))
        return
    
    if not directory_path.is_dir():
        print(Colors.error(f"❌ Đường dẫn không phải thư mục: {directory}"))
        return
    
    print("\n⚙️  Tùy chọn:")
    print("  (Nhập Y để di chuyển, N để giữ nguyên)")
    move_success = confirm_action("Di chuyển ảnh thành công vào thư mục 'ok'?")
    
    print("\n📤 Định dạng export:")
    print("  1. JSON")
    print("  2. CSV")
    print("  3. Cả hai (JSON + CSV)")
    
    while True:
        format_choice = get_user_input("Chọn định dạng (1/2/3): ", default="3")
        if format_choice in ['1', '2', '3']:
            break
        print(Colors.error("❌ Vui lòng nhập 1, 2 hoặc 3!"))
    
    if format_choice == '1':
        output_format = 'json'
    elif format_choice == '2':
        output_format = 'csv'
    else:
        output_format = 'both'
    
    print(f"\n📁 Thư mục: {directory}")
    if not confirm_action("Bắt đầu quét?"):
        print("❌ Đã hủy!")
        return
    
    print(f"\n🔍 Đang quét...")
    print(Colors.muted("=" * 70))
    
    if output_format == 'both':
        process_directory_with_export(directory_path, 'json', move_success)
        process_directory_with_export(directory_path, 'csv', move_success=False)  # Không move lần 2
    else:
        process_directory_with_export(directory_path, output_format, move_success)
    
    print()
    print(Colors.success("✅ Hoàn tất!"))


def mode_generate_special():
    """Chế độ tạo QR code đặc biệt (WiFi, Email, SMS, etc.)"""
    print_header("TẠO QR CODE ĐẶC BIỆT", width=70)
    print(Colors.primary("  🔲 TẠO QR CODE CHO WIFI, EMAIL, SMS, VCARD, etc."))
    print()
    
    if not QRCODE_GEN_AVAILABLE:
        install_library(
            package_name="qrcode[pil]",
            install_command="pip install qrcode[pil]",
            library_display_name="qrcode"
        )
        return
    
    print("Chọn loại QR code:")
    print("  1. 🌐 WiFi")
    print("  2. 📧 Email")
    print("  3. 📱 SMS")
    print("  4. ☎️  Phone")
    print("  5. 👤 vCard (Danh thiếp)")
    print("  6. 📍 Location (GPS)")
    print("  7. 🔗 URL")
    
    while True:
        qr_type = get_user_input("Chọn loại (1-7): ", default="1")
        if qr_type in ['1', '2', '3', '4', '5', '6', '7']:
            break
        print(Colors.error("❌ Vui lòng nhập 1-7!"))
    
    data = ""
    
    if qr_type == '1':  # WiFi
        ssid = get_user_input("Tên mạng WiFi (SSID): ")
        password = get_user_input("Mật khẩu: ")
        security = get_user_input("Bảo mật (WPA/WPA2/WEP/nopass, mặc định WPA): ", default="WPA")
        print("  (Nhập Y nếu mạng ẩn, N nếu mạng công khai)")
        hidden = confirm_action("Mạng ẩn?")
        data = create_wifi_qr(ssid, password, security, hidden)
        
    elif qr_type == '2':  # Email
        email = get_user_input("Địa chỉ email: ")
        subject = get_user_input("Tiêu đề (Enter để bỏ qua): ", default="")
        body = get_user_input("Nội dung (Enter để bỏ qua): ", default="")
        data = create_email_qr(email, subject, body)
        
    elif qr_type == '3':  # SMS
        phone = get_user_input("Số điện thoại: ")
        message = get_user_input("Tin nhắn (Enter để bỏ qua): ", default="")
        data = create_sms_qr(phone, message)
        
    elif qr_type == '4':  # Phone
        phone = get_user_input("Số điện thoại: ")
        data = create_phone_qr(phone)
        
    elif qr_type == '5':  # vCard
        name = get_user_input("Tên: ")
        phone = get_user_input("Số điện thoại (Enter để bỏ qua): ", default="")
        email = get_user_input("Email (Enter để bỏ qua): ", default="")
        org = get_user_input("Tổ chức (Enter để bỏ qua): ", default="")
        url = get_user_input("Website (Enter để bỏ qua): ", default="")
        address = get_user_input("Địa chỉ (Enter để bỏ qua): ", default="")
        data = create_vcard_qr(name, phone, email, org, url, address)
        
    elif qr_type == '6':  # Location
        try:
            lat = float(get_user_input("Vĩ độ (Latitude): "))
            lon = float(get_user_input("Kinh độ (Longitude): "))
            alt = get_user_input("Độ cao (Enter = 0): ", default="0")
            altitude = float(alt) if alt else 0.0
            data = create_location_qr(lat, lon, altitude)
        except ValueError:
            print(Colors.error("❌ Tọa độ không hợp lệ!"))
            return
        
    elif qr_type == '7':  # URL
        url = get_user_input("URL: ")
        data = create_url_qr(url)
    
    # Tùy chỉnh và tạo
    output_path_raw = get_user_input(
        "Đường dẫn file lưu (mặc định: qr_special.png): ",
        default="qr_special.png"
    )
    output_path = normalize_path(output_path_raw)
    
    # Đảm bảo có extension
    if not os.path.splitext(output_path)[1]:
        output_path = output_path + '.png'
    
    size_input = get_user_input("Kích thước box (mặc định 10): ", default="10")
    try:
        box_size = int(size_input)
    except ValueError:
        box_size = 10
    
    print(f"\n🔨 Đang tạo QR code...")
    success, message = create_qr_code(
        data=data,
        output_path=output_path,
        size=box_size
    )
    
    if success:
        print(Colors.success(f"✅ {message}"))
        if os.name == 'nt':
            if confirm_action("Mở file?"):
                if os.path.exists(output_path):
                    os.startfile(output_path)
                else:
                    print(Colors.warning(f"⚠️  File không tồn tại: {output_path}"))
    else:
        print(Colors.error(f"❌ {message}"))


def mode_batch_generate():
    """Chế độ tạo QR code hàng loạt"""
    print_header("TẠO QR CODE HÀNG LOẠT", width=70)
    print(Colors.primary("  🔲 TẠO NHIỀU QR CODE TỪ CSV HOẶC TEXT"))
    print()
    
    if not QRCODE_GEN_AVAILABLE:
        install_library(
            package_name="qrcode[pil]",
            install_command="pip install qrcode[pil]",
            library_display_name="qrcode"
        )
        return
    
    print("Chọn nguồn dữ liệu:")
    print("  1. File CSV")
    print("  2. File Text (mỗi dòng = 1 QR code)")
    
    while True:
        source_type = get_user_input("Chọn (1/2): ", default="1")
        if source_type in ['1', '2']:
            break
        print(Colors.error("❌ Vui lòng nhập 1 hoặc 2!"))
    
    if source_type == '1':
        csv_path = get_user_input("Đường dẫn file CSV: ")
        output_dir = get_user_input("Thư mục lưu QR code: ", default="./qr_batch_output")
        batch_generate_from_csv(csv_path, output_dir)
    else:
        text_path = get_user_input("Đường dẫn file text: ")
        output_dir = get_user_input("Thư mục lưu QR code: ", default="./qr_batch_output")
        batch_generate_from_text(text_path, output_dir)


def mode_generate_from_clipboard():
    """Tạo QR code từ clipboard"""
    if not CLIPBOARD_AVAILABLE:
        print(Colors.warning("⚠️  Cần cài đặt: pip install pyperclip"))
        print("  (Nhập Y để cài đặt, N để hủy)")
        if confirm_action("Cài đặt ngay?"):
            install_library(
                package_name="pyperclip",
                install_command="pip install pyperclip",
                library_display_name="pyperclip"
            )
        else:
            return
    
    print_header("TẠO QR CODE TỪ CLIPBOARD", width=70)
    print(Colors.primary("  📋 TẠO QR CODE TỪ NỘI DUNG CLIPBOARD"))
    print()
    
    if not CLIPBOARD_AVAILABLE or pyperclip is None:
        print(Colors.error("❌ Lỗi: pyperclip không khả dụng!"))
        return
    
    try:
        data = pyperclip.paste()
        if not data:
            print(Colors.warning("⚠️  Clipboard trống!"))
            return
        
        print(f"📋 Nội dung clipboard: {data[:100]}{'...' if len(data) > 100 else ''}")
        output_path = normalize_path(get_user_input(
            "Đường dẫn file lưu (mặc định: qr_clipboard.png): ",
            default="qr_clipboard.png"
        ))
        
        print(f"\n🔨 Đang tạo QR code...")
        success, message = create_qr_code(data=data, output_path=output_path)
        
        if success:
            print(Colors.success(f"✅ {message}"))
            if os.name == 'nt':
                if confirm_action("Mở file?"):
                    if os.path.exists(output_path):
                        os.startfile(output_path)
                    else:
                        print(Colors.warning(f"⚠️  File không tồn tại: {output_path}"))
        else:
            print(Colors.error(f"❌ {message}"))
            
    except Exception as e:
        print(Colors.error(f"❌ Lỗi: {e}"))


# ==================== MAIN ====================

def main_interactive():
    """Chế độ interactive - menu chọn chức năng"""
    print_header("TOOL QR CODE", width=70)
    print(Colors.primary("  🔲 CÔNG CỤ TẠO VÀ GIẢI MÃ QR CODE - ĐA DỤNG"))
    print()
    
    print("Chọn chức năng:")
    print("  1. 📱 Tạo QR Code (cơ bản)")
    print("  2. 🔲 Tạo QR Code đặc biệt (WiFi, Email, SMS, vCard, etc.)")
    print("  3. 🔄 Tạo QR Code hàng loạt (từ CSV/Text)")
    print("  4. 📋 Tạo QR Code từ Clipboard")
    print("  5. 📷 Giải mã QR Code từ ảnh")
    print("  6. 📤 Giải mã QR Code với Export (JSON/CSV)")
    print("  7. 📹 Đọc QR Code từ Webcam")
    print()
    
    while True:
        choice = get_user_input("Nhập lựa chọn (1-7): ", default="1")
        if choice in ['1', '2', '3', '4', '5', '6', '7']:
            break
        print(Colors.error("❌ Vui lòng nhập 1-7!"))
    
    print()
    
    if choice == '1':
        mode_generate()
    elif choice == '2':
        mode_generate_special()
    elif choice == '3':
        mode_batch_generate()
    elif choice == '4':
        mode_generate_from_clipboard()
    elif choice == '5':
        mode_decode()
    elif choice == '6':
        mode_decode_with_export()
    elif choice == '7':
        decode_from_webcam()


def main_cli(args):
    """Chế độ CLI"""
    if args.mode == 'generate':
        if not args.data:
            print(Colors.error("❌ Cần cung cấp dữ liệu để tạo QR code (--data)!"))
            return 1
        
        if not args.output:
            args.output = "qr_code.png"
        
        success, message = create_qr_code(
            data=args.data,
            output_path=args.output,
            size=args.size,
            border=args.border,
            error_correction=args.error_correction,
            fill_color=args.fill_color,
            back_color=args.back_color,
            add_logo=args.logo,
            logo_size_ratio=args.logo_size
        )
        
        if success:
            print(Colors.success(f"✅ {message}"))
            return 0
        else:
            print(Colors.error(f"❌ {message}"))
            return 1
    
    elif args.mode == 'decode':
        if not args.directory:
            print(Colors.error("❌ Cần cung cấp thư mục chứa ảnh (--directory)!"))
            return 1
        
        directory_path = Path(normalize_path(args.directory))
        if not directory_path.exists() or not directory_path.is_dir():
            print(Colors.error(f"❌ Thư mục không tồn tại: {args.directory}"))
            return 1
        
        if hasattr(args, 'export') and args.export:
            process_directory_with_export(directory_path, args.export, move_success=args.move_success)
        else:
            process_directory(directory_path, move_success=args.move_success)
        return 0
    
    elif args.mode == 'batch':
        if not args.input:
            print(Colors.error("❌ Cần cung cấp file CSV hoặc Text (--input)!"))
            return 1
        
        if not args.output:
            args.output = "./qr_batch_output"
        
        input_path = normalize_path(args.input)
        if not os.path.exists(input_path):
            print(Colors.error(f"❌ File không tồn tại: {args.input}"))
            return 1
        
        if input_path.endswith('.csv'):
            batch_generate_from_csv(input_path, args.output, 
                                   size=getattr(args, 'size', 10),
                                   border=getattr(args, 'border', 4))
        else:
            batch_generate_from_text(input_path, args.output,
                                    size=getattr(args, 'size', 10),
                                    border=getattr(args, 'border', 4))
        return 0
    
    elif args.mode == 'webcam':
        decode_from_webcam()
        return 0
    
    elif args.mode == 'clipboard':
        if not CLIPBOARD_AVAILABLE or pyperclip is None:
            print(Colors.error("❌ Cần cài đặt: pip install pyperclip"))
            return 1
        try:
            data = pyperclip.paste()
            if not data:
                print(Colors.warning("⚠️  Clipboard trống!"))
                return 1
            
            output_path = normalize_path(getattr(args, 'output', 'qr_clipboard.png'))
            success, message = create_qr_code(data=data, output_path=output_path)
            
            if success:
                print(Colors.success(f"✅ {message}"))
                return 0
            else:
                print(Colors.error(f"❌ {message}"))
                return 1
        except Exception as e:
            print(Colors.error(f"❌ Lỗi: {e}"))
            return 1
    
    else:
        print(Colors.error("❌ Chế độ không hợp lệ. Dùng 'generate', 'decode', 'batch', 'webcam', hoặc 'clipboard'"))
        return 1


def main():
    """Hàm main"""
    parser = argparse.ArgumentParser(
        description='Tool tạo và giải mã QR Code - Đa dụng',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  # Chế độ interactive
  python qr-code.py
  
  # Tạo QR code
  python qr-code.py generate -d "https://example.com" -o qr.png
  
  # Tạo QR code hàng loạt từ CSV
  python qr-code.py batch -i data.csv -o ./output
  
  # Giải mã QR code từ thư mục
  python qr-code.py decode --directory ./images
  
  # Giải mã với export JSON
  python qr-code.py decode --directory ./images --export json
  
  # Đọc từ webcam
  python qr-code.py webcam
  
  # Tạo từ clipboard
  python qr-code.py clipboard
        """
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Chế độ hoạt động')
    
    # Parser cho generate
    gen_parser = subparsers.add_parser('generate', help='Tạo QR code')
    gen_parser.add_argument('-d', '--data', required=True, help='Nội dung cần tạo QR code')
    gen_parser.add_argument('-o', '--output', help='Đường dẫn file lưu (mặc định: qr_code.png)')
    gen_parser.add_argument('-s', '--size', type=int, default=10, help='Kích thước box (mặc định: 10)')
    gen_parser.add_argument('-b', '--border', type=int, default=4, help='Độ dày border (mặc định: 4)')
    gen_parser.add_argument('-e', '--error-correction', choices=['L', 'M', 'Q', 'H'], default='M',
                          help='Mức sửa lỗi: L (~7%%), M (~15%%), Q (~25%%), H (~30%%)')
    gen_parser.add_argument('--fill-color', default='black', help='Màu mã QR (mặc định: black)')
    gen_parser.add_argument('--back-color', default='white', help='Màu nền (mặc định: white)')
    gen_parser.add_argument('--logo', help='Đường dẫn logo (tùy chọn)')
    gen_parser.add_argument('--logo-size', type=float, default=0.3,
                          help='Tỷ lệ logo (0.1-0.4, mặc định: 0.3)')
    
    # Parser cho decode
    dec_parser = subparsers.add_parser('decode', help='Giải mã QR code từ ảnh')
    dec_parser.add_argument('--directory', '-d', required=True, help='Thư mục chứa ảnh')
    dec_parser.add_argument('--no-move', dest='move_success', action='store_false',
                          help='Không di chuyển ảnh thành công vào thư mục ok')
    dec_parser.add_argument('--export', choices=['json', 'csv', 'both'], 
                          help='Xuất kết quả ra JSON/CSV')
    dec_parser.set_defaults(move_success=True)
    
    # Parser cho batch
    batch_parser = subparsers.add_parser('batch', help='Tạo QR code hàng loạt từ CSV/Text')
    batch_parser.add_argument('-i', '--input', required=True, help='File CSV hoặc Text')
    batch_parser.add_argument('-o', '--output', default='./qr_batch_output', help='Thư mục output')
    batch_parser.add_argument('-s', '--size', type=int, default=10, help='Kích thước box')
    batch_parser.add_argument('-b', '--border', type=int, default=4, help='Độ dày border')
    
    # Parser cho webcam
    webcam_parser = subparsers.add_parser('webcam', help='Đọc QR code từ webcam')
    
    # Parser cho clipboard
    clipboard_parser = subparsers.add_parser('clipboard', help='Tạo QR code từ clipboard')
    clipboard_parser.add_argument('-o', '--output', default='qr_clipboard.png', help='File output')
    
    args = parser.parse_args()
    
    if args.mode:
        sys.exit(main_cli(args))
    else:
        try:
            main_interactive()
        except KeyboardInterrupt:
            print(Colors.warning("\n⚠️  Đã hủy bởi người dùng!"))
            sys.exit(130)
        except Exception as e:
            log_error(f"❌ Lỗi không mong muốn: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()

