#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File doc.py - Hướng dẫn sử dụng tool Copy Changed Files
"""


def get_help():
    """
    Trả về hướng dẫn sử dụng cơ bản của tool
    
    Returns:
        str: Hướng dẫn sử dụng tool
    """
    return """
📋 HƯỚNG DẪN SỬ DỤNG:

⚠️  YÊU CẦU: Dự án phải là Git repository

🔄 CHỌN CHẾ ĐỘ:

1️⃣  Copy file thay đổi theo commit range:
   - Nhập đường dẫn dự án (Git repository)
   - Nhập commit ID bắt đầu (ví dụ: 9d172f6)
   - Nhập commit ID kết thúc (Enter để chọn HEAD)
   - Xem danh sách commit: git log --oneline -20

2️⃣  Copy file đã staged (git add):
   - Nhập đường dẫn dự án (Git repository)
   - Tool sẽ lấy các file đã được git add
   - Chỉ copy file đã staged, bỏ qua file unstaged

3️⃣  Copy file hiện tại đang thay đổi (unstaged):
   - Nhập đường dẫn dự án (Git repository)
   - Tool sẽ lấy file có thay đổi nhưng chưa git add
   - Bỏ qua file đã staged

4️⃣  Copy tất cả file có thay đổi (mặc định):
   - Nhập đường dẫn dự án (Git repository)
   - Tool sẽ lấy tất cả file có thay đổi (staged + unstaged)
   - Nhấn Enter để chọn chế độ này

📁 TOOL SẼ:
   - Lấy danh sách file đã thay đổi
   - Copy các file vào thư mục export với timestamp (tùy chỉnh được)
   - Giữ nguyên cấu trúc thư mục gốc
   - Tạo file danh-sach-file-thay-doi.txt

💡 TIP:
   - Chế độ 1: Phù hợp để deploy code đã commit
   - Chế độ 2: Phù hợp để backup file đang làm việc
   - Chỉ copy file có nội dung, không copy file đã xóa
   - Giữ nguyên cấu trúc thư mục để dễ upload lên server

📝 VÍ DỤ:

[Chế độ 1] Commit range:
   Dự án: D:\\my-project
   Commit bắt đầu: 9d172f6
   Commit kết thúc: HEAD
   → Tìm thấy 25 file đã thay đổi
   → Copy vào: changed-files-export/

[Chế độ 2] File hiện tại:
   Dự án: D:\\my-project
   → Tìm thấy 5 file đang thay đổi (modified/added)
   → Copy vào: changed-files-export/

🚀 KẾT QUẢ: Có thể upload toàn bộ thư mục lên server bằng FileZilla
    """

