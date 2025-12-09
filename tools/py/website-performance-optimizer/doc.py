#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File doc.py - Hướng dẫn sử dụng tool Website Performance Optimizer
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

2️⃣  Chọn dự án để tối ưu hóa:
   - Nhập số thứ tự: Chọn dự án từ danh sách (ví dụ: 1, 2, 3...)
   - Nhập đường dẫn: Nếu dự án không có trong danh sách, nhập đường dẫn đầy đủ
     (ví dụ: C:\\xampp\\htdocs\\samsung-sft)
   - Nhập tên dự án: Có thể nhập tên dự án trực tiếp nếu có trong danh sách

3️⃣  Xác nhận tối ưu hóa:
   - Tool sẽ hỏi xác nhận trước khi thực hiện
   - File gốc sẽ được backup tự động (nếu bật backup)
   - Sau khi tối ưu, file gốc có thể được khôi phục từ thư mục backup

4️⃣  Cài đặt (tùy chọn):
   - Nhập 's' để vào menu cài đặt
   - Có thể thay đổi đường dẫn htdocs mặc định
   - Có thể bật/tắt các tùy chọn tối ưu hóa
   - Có thể bật/tắt backup file gốc

🔧 CÁC TỐI ƯU HÓA ĐƯỢC THỰC HIỆN:

✅ Minify CSS - Giảm kích thước file CSS lên đến 50-70%
✅ Minify JavaScript - Giảm kích thước file JS lên đến 50-70%
✅ Tối ưu hóa HTML - Loại bỏ comments và khoảng trắng thừa
✅ Tạo .htaccess - Thêm cache headers và Gzip compression
✅ Backup file gốc - Tự động backup trước khi tối ưu

💡 LƯU Ý QUAN TRỌNG:

⚠️  Tool sẽ thay đổi file gốc (nếu không bật backup)
⚠️  Nên backup dự án trước khi sử dụng tool
⚠️  File .min.js sẽ được bỏ qua (đã minify)
⚠️  File trong node_modules, .git, vendor sẽ được bỏ qua

📝 VÍ DỤ:

1. Tối ưu dự án từ danh sách:
   - Vào tool, danh sách dự án hiển thị ngay
   - Nhập số thứ tự: 1 (chọn dự án đầu tiên)
   - Xác nhận: y
   - Tool sẽ tự động tối ưu và hiển thị kết quả

2. Tối ưu dự án từ đường dẫn khác:
   - Vào tool
   - Nhập đường dẫn: C:\\xampp\\htdocs\\samsung-sft
   - Xác nhận: y
   - Tool sẽ tự động tối ưu

3. Kết quả:
   - File CSS/JS/HTML đã được minify
   - File .htaccess đã được tạo/cập nhật
   - File gốc đã được backup (nếu bật)
   - Hiển thị tổng tiết kiệm dung lượng
    """

