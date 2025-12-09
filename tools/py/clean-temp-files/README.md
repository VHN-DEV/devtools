# Clean Temp Files - Dọn dẹp file tạm và cache

## Mô tả

Tool dọn dẹp file tạm, cache và file rác để giải phóng dung lượng ổ đĩa. Hỗ trợ tìm file lớn, thư mục rỗng, và xác nhận an toàn trước khi xóa.

## Tính năng

✅ Xóa file tạm (.tmp, .log, .bak, .cache...)
✅ Xóa thư mục cache (__pycache__, node_modules, .pytest_cache...)
✅ Tìm file lớn (>10MB tùy chỉnh)
✅ Tìm thư mục rỗng
✅ Hiển thị dung lượng giải phóng
✅ Xác nhận an toàn trước khi xóa
✅ Preview danh sách file trước khi xóa

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "clean-temp-files"
```

### Chạy trực tiếp

```bash
python tools/py/clean-temp-files/clean-temp-files.py
```

## Hướng dẫn chi tiết

### 1. Nhập đường dẫn

Nhập đường dẫn thư mục cần dọn dẹp (Enter để dùng thư mục hiện tại)

### 2. Chọn loại cần dọn dẹp

- **1**: File tạm (.tmp, .log, .bak, .cache...)
- **2**: Thư mục cache (__pycache__, node_modules, .pytest_cache...)
- **3**: File lớn (>10MB tùy chỉnh)
- **4**: Thư mục rỗng
- **5**: Tất cả các loại trên

### 3. Cấu hình (nếu cần)

- **File lớn**: Nhập kích thước tối thiểu (MB, mặc định: 10)
- **Recursive**: Tìm trong tất cả thư mục con (Y/n)

### 4. Xem kết quả

Tool sẽ hiển thị:
- Số lượng file/thư mục tìm thấy
- Tổng dung lượng có thể giải phóng
- Danh sách 10 file/thư mục đầu (preview)

### 5. Xác nhận xóa

- Xác nhận bằng `YES` để xóa
- Tool sẽ xóa và hiển thị tiến trình
- Hiển thị tổng dung lượng đã giải phóng

## Ví dụ

### Dọn dẹp file tạm

```
Nhập đường dẫn thư mục cần dọn dẹp: D:\Projects
Chọn loại cần dọn dẹp (1-5): 1

🔍 Đang quét...

📄 Tìm thấy 45 file tạm (15.2 MB)

📋 Danh sách (10 file đầu):
   - D:\Projects\project1\temp.log (2.5 MB)
   - D:\Projects\project2\cache.tmp (1.8 MB)
   ...

⚠️  CẢNH BÁO: Bạn sắp xóa 45 file!
Xác nhận xóa? (YES để xác nhận): YES

🗑️  Đang xóa...
✓ Xóa: temp.log (2.5 MB)
✓ Xóa: cache.tmp (1.8 MB)
...

============================================================
✅ Hoàn thành!
   - Đã xóa: 45/45 file
   - Giải phóng: 15.2 MB
============================================================
```

### Dọn dẹp thư mục cache

```
Chọn loại cần dọn dẹp (1-5): 2

🔍 Đang quét...

📁 Tìm thấy 8 thư mục cache (850.5 MB)

📋 Danh sách:
   - D:\Projects\project1\node_modules (450.5 MB)
   - D:\Projects\project2\__pycache__ (15.2 MB)
   ...

⚠️  CẢNH BÁO: Bạn sắp xóa 8 thư mục!
Xác nhận xóa? (YES để xác nhận): YES

✅ Hoàn thành! Giải phóng: 850.5 MB
```

### Tìm file lớn

```
Chọn loại cần dọn dẹp (1-5): 3
Kích thước tối thiểu (MB, mặc định 10): 50

🔍 Đang quét...

💾 Tìm thấy 3 file lớn (>50MB) (425.8 MB)

📋 Danh sách:
   - D:\Projects\project1\build\temp.log (125.8 MB)
   - D:\Projects\old\backup.bak (200.0 MB)
   ...

✅ Hoàn thành! Giải phóng: 425.8 MB
```

### Dọn dẹp tất cả

```
Chọn loại cần dọn dẹp (1-5): 5

🔍 Đang quét...

📄 Tìm thấy 45 file tạm (15.2 MB)
📁 Tìm thấy 8 thư mục cache (850.5 MB)
💾 Tìm thấy 3 file lớn (>50MB) (425.8 MB)
📂 Tìm thấy 12 thư mục rỗng

============================================================
📊 Tổng kết:
   - Số lượng: 68 mục
   - Dung lượng: 1.27 GB
============================================================

⚠️  CẢNH BÁO: Bạn sắp xóa 68 mục!
Xác nhận xóa? (YES để xác nhận): YES

✅ Hoàn thành! Giải phóng: 1.27 GB
```

## Loại file/thư mục được tìm thấy

### File tạm
- `.tmp`, `.temp`, `.cache`
- `.log`, `.bak`, `.backup`
- `.old`, `.swp`, `.swo`
- `~`, `*.~`, `Thumbs.db`

### Thư mục cache
- `__pycache__` - Python cache
- `node_modules` - Node.js dependencies
- `.pytest_cache` - pytest cache
- `.mypy_cache` - mypy cache
- `.vscode`, `.idea` - IDE settings
- `venv`, `env` - Virtual environment
- `dist`, `build` - Build output

### File lớn
- File có kích thước >10MB (mặc định, có thể tùy chỉnh)
- Thường là file log, backup, cache lớn

### Thư mục rỗng
- Thư mục không chứa file nào
- Có thể chứa thư mục con rỗng

## Tips

### An toàn:
- **Luôn xem danh sách trước khi xóa**: Kiểm tra kỹ danh sách file/thư mục
- **Backup quan trọng trước**: Backup dữ liệu quan trọng trước khi dọn dẹp
- **Chỉ xóa file tạm**: Không xóa file quan trọng

### Tối ưu:
- **Dọn dẹp định kỳ**: Dọn dẹp hàng tuần/tháng để giải phóng dung lượng
- **Tập trung vào cache**: Thư mục cache thường chiếm nhiều dung lượng nhất
- **File lớn**: Tìm và xóa file lớn không cần thiết

### Lưu ý:
- **node_modules**: Có thể xóa và cài lại bằng `npm install`
- **__pycache__**: Tự động tạo lại khi chạy Python
- **File log**: Xóa file log cũ nếu không cần

## Use case phổ biến

- Giải phóng dung lượng ổ cứng
- Dọn dẹp thư mục Downloads
- Xóa file build/temp trong dự án
- Tìm và xóa file log cũ
- Dọn dẹp sau khi xóa dự án
- Chuẩn bị ổ đĩa trước khi cài đặt phần mềm lớn

## Lưu ý quan trọng

- **⚠️ CẢNH BÁO**: Xóa vĩnh viễn, không thể hoàn tác!
- **Xác nhận**: Luôn xác nhận bằng `YES` (chữ hoa) để tránh xóa nhầm
- **Backup**: Backup dữ liệu quan trọng trước khi dọn dẹp
- **Kiểm tra**: Kiểm tra kỹ danh sách file trước khi xóa
- **node_modules**: Có thể xóa và cài lại, nhưng mất thời gian
- **File log**: Đảm bảo không cần file log trước khi xóa

## Khôi phục

- **Không thể khôi phục**: File đã xóa không thể khôi phục bằng tool này
- **Backup**: Luôn backup trước khi dọn dẹp
- **Recycle Bin**: Một số file có thể được khôi phục từ Recycle Bin (Windows)
- **Git**: Nếu file trong Git repository, có thể khôi phục từ Git
