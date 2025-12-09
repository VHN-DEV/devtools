#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File doc.py - Hướng dẫn sử dụng tool Git Push Source
"""


def get_help():
    """
    Trả về hướng dẫn sử dụng cơ bản của tool
    
    Returns:
        str: Hướng dẫn sử dụng tool
    """
    return """
📋 HƯỚNG DẪN SỬ DỤNG:

1️⃣  CHUẨN BỊ:
   - Đảm bảo Git đã được cài đặt
   - Có quyền truy cập repository (Personal Access Token hoặc SSH key)

2️⃣  QUẢN LÝ REPOSITORY:
   - Tool tự động lưu danh sách repository đã sử dụng
   - Có thể thêm/xóa repository khỏi danh sách
   - Chọn repository từ danh sách hoặc nhập mới
   - Lưu lịch sử thao tác để theo dõi

3️⃣  CÁC CHỨC NĂNG CHÍNH:

   📦 QUẢN LÝ REPOSITORY:
   1. Clone repository - Clone từ remote về local
   2. Khởi tạo repository - Tạo Git repo mới
   3. Thiết lập remote - Thêm/cập nhật remote
   4. Xem trạng thái - Hiển thị thay đổi, branch, remotes
   5. Quản lý repository - Thêm/xóa repository vào danh sách

   📝 THAO TÁC CODE:
   6. Add files và commit - Thêm files và commit
   7. Push code - Push lên remote
   8. Pull code - Pull từ remote
   9. Fetch - Fetch từ remote
   10. Thực hiện đầy đủ - Add → Commit → Push tự động

   🌿 QUẢN LÝ BRANCH:
   11. Tạo branch mới - Tạo và chuyển sang branch mới
   12. Chuyển branch - Switch sang branch khác
   13. Xem danh sách branches - Liệt kê tất cả branches
   14. Xóa branch - Xóa branch (cẩn thận!)

   🔀 TÍNH NĂNG NÂNG CAO:
   15. Merge branch - Merge branch vào branch hiện tại
   16. Rebase branch - Rebase branch hiện tại lên branch khác
   17. Stash changes - Lưu tạm thay đổi
   18. Pop stash - Khôi phục thay đổi từ stash
   19. Xem danh sách remotes - Liệt kê tất cả remotes

   📊 KHÁC:
   20. Xem lịch sử thao tác - Xem 20 thao tác gần nhất
   21. Chọn repository khác - Chuyển sang repository khác

4️⃣  QUY TRÌNH ĐẦY ĐỦ:

   Bước 1: Chọn repository từ danh sách hoặc nhập mới
   Bước 2: Clone hoặc khởi tạo repository (nếu cần)
   Bước 3: Chỉnh sửa code
   Bước 4: Chọn chức năng 10 (Thực hiện đầy đủ)
   Bước 5: Nhập commit message
   Bước 6: Xác nhận push

💡 TIP:
   - Lưu repository vào danh sách để dùng lại nhanh
   - Sử dụng chức năng 10 để thao tác nhanh nhất
   - Kiểm tra trạng thái (4) trước khi commit
   - Commit message nên rõ ràng, mô tả thay đổi
   - Không nên force push lên main/master branch
   - Sử dụng branch riêng cho các tính năng mới
   - Dùng stash (17) để tạm lưu thay đổi khi cần switch branch
   - Xem lịch sử (20) để theo dõi các thao tác đã thực hiện

📝 VÍ DỤ:
   Repository: https://github.com/VHN-DEV/laravel-botble-cms
   Local path: D:\\projects\\laravel-botble-cms
   Chức năng: 10 (Thực hiện đầy đủ)
   Commit message: "Update authentication feature"
   Branch: main
   → Add files → Commit → Push thành công!

⚠️  LƯU Ý:
   - Cần có quyền write vào repository
   - Kiểm tra kỹ files trước khi commit
   - Backup code quan trọng trước khi push
   - Không commit files nhạy cảm (.env, keys, passwords)
   - Cẩn thận khi force push hoặc force delete branch
   - Merge và rebase có thể gây conflict, cần xử lý cẩn thận
    """

