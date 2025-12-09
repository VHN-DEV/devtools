#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File doc.py - Hướng dẫn sử dụng tool QR Code
"""


def get_help():
    """
    Trả về hướng dẫn sử dụng cơ bản của tool
    
    Returns:
        str: Hướng dẫn sử dụng tool
    """
    return """
📋 HƯỚNG DẪN SỬ DỤNG - TOOL QR CODE ĐA DỤNG:

⚠️  YÊU CẦU: 
   - Tạo QR code: pip install qrcode[pil]
   - Giải mã QR code: pip install opencv-python pyzbar pillow numpy
   - Clipboard (tùy chọn): pip install pyperclip

🔲 CHỨC NĂNG:

1️⃣  TẠO QR CODE (Chức năng 1 - Cơ bản):
   
   a) Nhập nội dung:
      - URL: https://example.com
      - Text: Hello World
      - Bất kỳ văn bản nào
   
   b) Đường dẫn lưu và định dạng:
      - Enter: Lưu mặc định là qr_code.png
      - Nhập đường dẫn: Chỉ định file và thư mục
      - Hỗ trợ định dạng: PNG, JPG, JPEG, SVG, BMP, TIFF
      - Tự động phát hiện định dạng từ phần mở rộng file
      - Ví dụ: qr_code.png, qr_code.jpg, qr_code.svg
   
   c) Tùy chỉnh:
      - Kích thước box: Số lớn = QR code lớn hơn (mặc định: 10)
      - Border: Độ dày viền (mặc định: 4)
      - Mức sửa lỗi: L/M/Q/H (mặc định: M)
      - Màu mã QR và nền: black, #000000, hoặc tên màu khác
      - Logo (tùy chọn): Chọn file ảnh logo, tỷ lệ 0.1-0.4

2️⃣  TẠO QR CODE ĐẶC BIỆT (Chức năng 2):
   
   Hỗ trợ các loại QR code chuẩn:
   - 🌐 WiFi: Tự động tạo QR cho mạng WiFi (SSID, mật khẩu, bảo mật)
   - 📧 Email: QR code với mailto, tiêu đề và nội dung
   - 📱 SMS: QR code để gửi SMS với số và tin nhắn
   - ☎️  Phone: QR code để gọi điện
   - 👤 vCard: QR code danh thiếp điện tử (tên, phone, email, địa chỉ, etc.)
   - 📍 Location: QR code vị trí GPS (latitude, longitude)
   - 🔗 URL: QR code URL tự động thêm https:// nếu thiếu

3️⃣  TẠO QR CODE HÀNG LOẠT (Chức năng 3):
   
   Tạo nhiều QR code từ:
   - File CSV: Cột 'data' hoặc 'content' (tùy chỉnh từng QR trong CSV)
   - File Text: Mỗi dòng = 1 QR code
   
   Tự động đặt tên file hoặc dùng cột 'filename' trong CSV

4️⃣  TẠO QR CODE TỪ CLIPBOARD (Chức năng 4):
   
   Tự động lấy nội dung từ clipboard và tạo QR code ngay

5️⃣  GIẢI MÃ QR CODE (Chức năng 5):
   
   a) Nhập đường dẫn thư mục chứa ảnh
   
   b) Tùy chọn:
      - Di chuyển ảnh thành công vào thư mục 'ok'?
   
   c) Kết quả:
      - File result.txt: Log chi tiết
      - File results.txt: Tổng kết
      - Tỷ lệ thành công/thất bại

6️⃣  GIẢI MÃ VỚI EXPORT (Chức năng 6):
   
   Giải mã và xuất kết quả ra:
   - JSON: Dữ liệu có cấu trúc, dễ xử lý
   - CSV: Dễ import vào Excel/Google Sheets
   - Cả hai định dạng
   
   Kết quả bao gồm: filename, path, status, data, method, timestamp

7️⃣  ĐỌC QR CODE TỪ WEBCAM (Chức năng 7):
   
   Quét QR code trực tiếp từ camera/webcam
   - Hiển thị real-time
   - Tự động lưu kết quả khi tìm thấy
   - Nhấn 'q' để thoát

💡 TIP TẠO QR CODE:
   - Mức sửa lỗi H (30%) tốt nhất khi có logo
   - Màu tối trên nền sáng dễ quét nhất
   - Kích thước box 10-15 phù hợp cho hầu hết trường hợp
   - Logo nên là hình vuông hoặc gần vuông
   - QR code có thể quét từ xa hơn nếu lớn hơn

💡 TIP GIẢI MÃ QR CODE:
   - Tool tự động xử lý nhiều kỹ thuật: enhance, crop, xoay
   - Hỗ trợ nhiều định dạng: jpg, png, bmp, tiff
   - Tự động thử nhiều phương pháp nếu lần đầu thất bại
   - Quét hàng loạt từ thư mục

💡 TIP SỬ DỤNG:
   
   TẠO QR CODE:
   - Mức sửa lỗi H (30%) tốt nhất khi có logo
   - Màu tối trên nền sáng dễ quét nhất
   - Kích thước box 10-15 phù hợp cho hầu hết trường hợp
   - Logo nên là hình vuông hoặc gần vuông
   
   GIẢI MÃ QR CODE:
   - Tool tự động xử lý nhiều kỹ thuật: enhance, crop, xoay
   - Hỗ trợ nhiều định dạng: jpg, png, bmp, tiff
   - Tự động thử nhiều phương pháp nếu lần đầu thất bại
   - Export JSON/CSV giúp xử lý dữ liệu dễ dàng hơn

📝 VÍ DỤ CLI:

   # Chế độ interactive (menu đầy đủ)
   python qr-code.py
   
   # Tạo QR code đơn giản
   python qr-code.py generate -d "https://example.com" -o qr.png
   
   # Tạo với tùy chỉnh
   python qr-code.py generate -d "Hello" -o output.png -s 15 -e H
   
   # Tạo QR code dạng JPG
   python qr-code.py generate -d "https://example.com" -o qr.jpg
   
   # Tạo QR code dạng SVG (vector)
   python qr-code.py generate -d "https://example.com" -o qr.svg
   
   # Tạo có logo
   python qr-code.py generate -d "URL" -o qr.png --logo logo.png
   
   # Tạo QR code hàng loạt từ CSV
   python qr-code.py batch -i data.csv -o ./output
   
   # Tạo QR code hàng loạt từ file text
   python qr-code.py batch -i urls.txt -o ./qr_codes
   
   # Tạo QR code từ clipboard
   python qr-code.py clipboard -o qr.png
   
   # Giải mã từ thư mục
   python qr-code.py decode --directory ./images
   
   # Giải mã với export JSON
   python qr-code.py decode --directory ./images --export json
   
   # Giải mã với export CSV
   python qr-code.py decode --directory ./images --export csv
   
   # Giải mã không di chuyển file
   python qr-code.py decode -d ./images --no-move
   
   # Đọc QR code từ webcam
   python qr-code.py webcam

📄 ĐỊNH DẠNG CSV CHO BATCH GENERATE:
   
   File CSV nên có các cột:
   - data hoặc content: (bắt buộc) Nội dung QR code
   - filename: (tùy chọn) Tên file output
   - size: (tùy chọn) Kích thước box
   - border: (tùy chọn) Độ dày border
   - error_correction: (tùy chọn) L/M/Q/H
   - fill_color: (tùy chọn) Màu mã QR
   - back_color: (tùy chọn) Màu nền
   
   Ví dụ CSV:
   data,filename,size,error_correction
   https://example.com,qr1.png,15,H
   Hello World,qr2.png,10,M
    """

