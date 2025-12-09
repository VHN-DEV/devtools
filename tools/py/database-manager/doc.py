#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File doc.py - Hướng dẫn sử dụng tool Database Manager
"""


def get_help():
    """
    Trả về hướng dẫn sử dụng cơ bản của tool
    
    Returns:
        str: Hướng dẫn sử dụng tool
    """
    return """
📋 HƯỚNG DẪN SỬ DỤNG:

1️⃣  Cấu hình kết nối database:
   - Vào menu "Quản lý kết nối" (2)
   - Thêm kết nối mới với thông tin MySQL
   - Test kết nối để đảm bảo hoạt động
   - Đặt kết nối mặc định nếu cần

2️⃣  Quản lý databases:
   - Chọn "Quản lý databases" (1)
   - Xem danh sách databases
   - Chọn database để xem tables
   - Backup/Restore database
   - Chạy SQL queries

3️⃣  Backup database:
   - Chọn database cần backup
   - Chọn "b [số]" để backup
   - File backup sẽ được lưu trong thư mục backup

4️⃣  Restore database:
   - Chọn "r" trong menu databases
   - Chọn file SQL cần restore
   - Nhập tên database (sẽ tạo mới nếu chưa có)

5️⃣  Chạy SQL queries:
   - Chọn "q" trong menu databases
   - Nhập tên database
   - Nhập SQL query
   - Xem kết quả

🔧 CÁC TÍNH NĂNG:

✅ Quản lý kết nối database
✅ Liệt kê databases và tables
✅ Backup database (toàn bộ hoặc từng table)
✅ Restore database từ file SQL
✅ Chạy SQL queries
✅ Export table ra file SQL
✅ Xem cấu trúc table
✅ Hỗ trợ XAMPP MySQL

💡 LƯU Ý QUAN TRỌNG:

⚠️  Cần có MySQL đã cài đặt (XAMPP)
⚠️  Cần quyền truy cập database
⚠️  Backup trước khi restore (sẽ ghi đè database)
⚠️  File backup được lưu trong thư mục: ~/database_backups/

📝 VÍ DỤ:

1. Thêm kết nối mới:
   - Menu chính → 2 (Quản lý kết nối)
   - Chọn 'a' (Thêm kết nối)
   - Nhập thông tin: Host, Port, User, Password
   - Test kết nối để kiểm tra

2. Backup database:
   - Menu chính → 1 (Quản lý databases)
   - Chọn database cần backup
   - Chọn 'b 1' (backup database số 1)
   - File backup sẽ được tạo tự động

3. Restore database:
   - Menu chính → 1 (Quản lý databases)
   - Chọn 'r' (Restore)
   - Chọn file SQL từ danh sách
   - Nhập tên database
   - Xác nhận restore

4. Chạy SQL query:
   - Menu chính → 1 (Quản lý databases)
   - Chọn 'q' (Query)
   - Nhập tên database
   - Nhập SQL query
   - Xem kết quả
    """

