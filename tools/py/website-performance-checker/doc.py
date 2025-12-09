#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File doc.py - Hướng dẫn sử dụng tool Website Performance Checker
"""


def get_help():
    """
    Trả về hướng dẫn sử dụng cơ bản của tool
    
    Returns:
        str: Hướng dẫn sử dụng tool
    """
    return """
📋 HƯỚNG DẪN SỬ DỤNG:

1️⃣  Khi vào tool:
   - Tool sẽ tự động hiển thị danh sách các dự án trong đường dẫn đã cấu hình
   - Đường dẫn mặc định: C:\\xampp\\htdocs

2️⃣  Chọn dự án để kiểm tra:
   - Nhập số thứ tự: Chọn dự án từ danh sách (ví dụ: 1, 2, 3...)
   - Nhập đường dẫn: Nếu dự án không có trong danh sách, nhập đường dẫn đầy đủ
     (ví dụ: C:\\xampp\\htdocs\\samsung-sft)
   - Nhập tên dự án: Có thể nhập tên dự án trực tiếp nếu có trong danh sách

3️⃣  Cài đặt (tùy chọn):
   - Nhập 's' để vào menu cài đặt
   - Có thể thay đổi đường dẫn htdocs mặc định
   - Có thể cấu hình các thông số kiểm tra

4️⃣  Xem báo cáo:
   - File báo cáo được lưu trong thư mục dự án
   - Tên file: performance_report_[tên_dự_án]_[timestamp].txt
   - Chứa các gợi ý tối ưu hóa chi tiết

📊 CÁC VẤN ĐỀ ĐƯỢC KIỂM TRA:

✅ File quá lớn (CSS, JS, HTML)
✅ Hình ảnh chưa được tối ưu
✅ File chưa được minify
✅ File PHP quá lớn
✅ Thiếu cấu hình cache headers

💡 GỢI Ý TỐI ƯU HÓA:

🔹 Minify CSS và JavaScript
🔹 Tối ưu hóa hình ảnh (WebP, compression)
🔹 Thiết lập Cache Headers
🔹 Tách nhỏ file PHP lớn
🔹 Code Splitting
🔹 Sử dụng CDN
🔹 Gzip Compression

📝 VÍ DỤ:

1. Kiểm tra dự án từ danh sách:
   - Vào tool, danh sách dự án hiển thị ngay
   - Nhập số thứ tự: 1 (chọn dự án đầu tiên)
   - Tool sẽ tự động kiểm tra và tạo báo cáo

2. Kiểm tra dự án từ đường dẫn khác:
   - Vào tool
   - Nhập đường dẫn: C:\\xampp\\htdocs\\samsung-sft
   - Tool sẽ tự động kiểm tra và tạo báo cáo

3. Kiểm tra bằng tên dự án:
   - Vào tool
   - Nhập tên dự án: samsung-sft
   - Tool sẽ tự động tìm và kiểm tra

4. Kết quả:
   - File báo cáo: performance_report_samsung-sft_20250108_094500.txt
   - Chứa danh sách vấn đề và gợi ý chi tiết
    """

