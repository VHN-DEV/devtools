# Duplicate Finder - Tìm file trùng lặp

## Mô tả

Tool tìm và xóa file trùng lặp trong thư mục. Hỗ trợ tìm bằng hash (MD5/SHA256) hoặc theo kích thước, hiển thị dung lượng lãng phí, và xóa trùng tự động (giữ 1 file gốc).

## Tính năng

✅ Tìm file trùng lặp bằng hash (MD5/SHA256)
✅ Tìm file trùng lặp theo kích thước
✅ Hiển thị dung lượng lãng phí
✅ Xóa trùng tự động (giữ file đầu tiên)
✅ Xóa trùng thủ công (chọn file giữ lại)
✅ Lưu báo cáo chi tiết
✅ Preview trước khi xóa

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "duplicate-finder"
```

### Chạy trực tiếp

```bash
python tools/py/duplicate-finder/duplicate-finder.py
```

## Hướng dẫn chi tiết

### 1. Chọn thư mục

Nhập đường dẫn thư mục cần tìm file trùng (vd: `D:\Photos`)

### 2. Cấu hình tìm kiếm

1. **Tìm trong tất cả thư mục con?** (Y/n): Tìm đệ quy hay không
2. **Kích thước tối thiểu (KB)**: Chỉ tìm file >= kích thước này (Enter để tìm tất cả)
   - Ví dụ: `1024` để chỉ tìm file >= 1MB
3. **Phương pháp tìm kiếm**:
   - **1**: MD5 hash (nhanh, chính xác)
   - **2**: SHA256 hash (chậm hơn, an toàn hơn)
   - **3**: Theo kích thước (nhanh nhất, nhưng có thể sai sót)

### 3. Xem kết quả

Tool sẽ:
1. Quét thư mục và tính hash/kích thước
2. Tìm file trùng lặp
3. Hiển thị danh sách nhóm file trùng
4. Hiển thị tổng dung lượng lãng phí

### 4. Xóa file trùng

- **Tự động**: Giữ file đầu tiên, xóa các file còn lại
- **Thủ công**: Chọn file giữ lại cho từng nhóm

### 5. Lưu báo cáo (tùy chọn)

Tool có thể lưu báo cáo chi tiết ra file text.

## Ví dụ

### Tìm file trùng lặp

```
Nhập đường dẫn thư mục: D:\Photos
Tìm trong tất cả thư mục con? (Y/n): Y
Kích thước tối thiểu (KB, Enter để tìm tất cả): 1024
Phương pháp tìm kiếm (1: MD5, 2: SHA256, 3: Size): 1

🔍 Đang quét thư mục...
📊 Đang tính hash...

✅ Tìm thấy 3 nhóm file trùng lặp:

📁 Nhóm 1 (3 file, 15.2 MB):
   1. D:\Photos\2024\photo1.jpg (15.2 MB)
   2. D:\Photos\Backup\photo1.jpg (15.2 MB)
   3. D:\Photos\Old\photo1.jpg (15.2 MB)

📁 Nhóm 2 (2 file, 8.5 MB):
   1. D:\Photos\2024\photo2.jpg (8.5 MB)
   2. D:\Photos\Backup\photo2.jpg (8.5 MB)

📁 Nhóm 3 (2 file, 12.3 MB):
   1. D:\Photos\2024\photo3.jpg (12.3 MB)
   2. D:\Photos\Old\photo3.jpg (12.3 MB)

============================================================
📊 Tổng kết:
   - Số nhóm trùng: 3
   - Số file trùng: 7
   - Dung lượng lãng phí: 52.0 MB
============================================================
```

### Xóa file trùng tự động

```
Xóa file trùng? (Y/n): Y

===== CHẾ ĐỘ XÓA =====
1. Tự động (giữ file đầu tiên)
2. Thủ công (chọn file giữ lại)

Chọn (1-2): 1

⚠️  CẢNH BÁO: Bạn sắp xóa 4 file!
Xác nhận xóa? (YES để xác nhận): YES

🗑️  Đang xóa...
✓ Xóa: D:\Photos\Backup\photo1.jpg (15.2 MB)
✓ Xóa: D:\Photos\Old\photo1.jpg (15.2 MB)
✓ Xóa: D:\Photos\Backup\photo2.jpg (8.5 MB)
✓ Xóa: D:\Photos\Old\photo3.jpg (12.3 MB)

✅ Hoàn thành! Đã giải phóng 52.0 MB
```

## Phương pháp tìm kiếm

### MD5 Hash
- **Ưu điểm**: Nhanh, chính xác
- **Nhược điểm**: Không an toàn bằng SHA256
- **Khuyến nghị**: Dùng cho hầu hết trường hợp

### SHA256 Hash
- **Ưu điểm**: An toàn hơn MD5
- **Nhược điểm**: Chậm hơn MD5
- **Khuyến nghị**: Dùng khi cần độ an toàn cao

### Theo kích thước
- **Ưu điểm**: Nhanh nhất
- **Nhược điểm**: Có thể sai sót (2 file khác nhau nhưng cùng kích thước)
- **Khuyến nghị**: Chỉ dùng để tìm nhanh, sau đó kiểm tra lại

## Tips

### An toàn:
- **Preview trước**: Luôn xem danh sách file trước khi xóa
- **Backup**: Backup file quan trọng trước khi xóa
- **Thủ công**: Dùng chế độ thủ công để chọn file giữ lại cẩn thận

### Tối ưu:
- **Kích thước tối thiểu**: Chỉ tìm file >= 1MB để tiết kiệm thời gian
- **MD5**: Dùng MD5 cho hầu hết trường hợp (nhanh hơn)
- **Thư mục nhỏ**: Xử lý từng thư mục nhỏ thay vì toàn bộ ổ đĩa

### Hiệu quả:
- **Dọn dẹp định kỳ**: Chạy định kỳ để giải phóng dung lượng
- **Sau khi copy**: Kiểm tra file trùng sau khi copy nhiều file
- **Merge thư mục**: Tìm file trùng trước khi merge thư mục

## Use case phổ biến

- Dọn dẹp thư mục ảnh/video trùng lặp
- Tìm file backup trùng
- Giải phóng dung lượng ổ đĩa
- Merge thư mục có file chung
- Dọn dẹp sau khi download nhiều lần

## Lưu ý quan trọng

- **⚠️ CẢNH BÁO**: Xóa vĩnh viễn, không thể hoàn tác!
- **Xác nhận**: Luôn xác nhận bằng `YES` (chữ hoa) để tránh xóa nhầm
- **Backup**: Backup file quan trọng trước khi xóa
- **Kiểm tra**: Kiểm tra kỹ danh sách file trước khi xóa
- **Thời gian**: Quét thư mục lớn có thể mất nhiều thời gian

## Ví dụ thực tế

### Dọn dẹp ảnh trùng lặp

```
Thư mục: D:\Photos (1000 ảnh)
Kích thước tối thiểu: 512 KB
Phương pháp: MD5
→ Tìm thấy 50 file trùng (250 MB)
→ Xóa tự động
→ Giải phóng 250 MB
```

### Merge thư mục

```
Thư mục 1: D:\Photos\2024
Thư mục 2: D:\Photos\Backup
→ Tìm file trùng
→ Giữ file trong thư mục 2024
→ Xóa file trùng trong Backup
```
