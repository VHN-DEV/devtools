# Extract Archive - Giải nén file

## Mô tả

Tool giải nén file archive đa năng. Hỗ trợ nhiều định dạng (ZIP, RAR, 7Z, TAR, TAR.GZ), giải nén một file hoặc hàng loạt, và tự động tạo thư mục đích.

## Tính năng

✅ Hỗ trợ nhiều định dạng (ZIP, TAR, TAR.GZ, 7Z, RAR)
✅ Giải nén 1 file hoặc hàng loạt
✅ Tự động tạo thư mục đích
✅ Hiển thị dung lượng trước/sau
✅ Xử lý nhiều file cùng lúc
✅ Báo cáo chi tiết kết quả

## Yêu cầu

### Định dạng cơ bản (không cần cài thêm)
- ZIP, TAR, TAR.GZ, TAR.BZ2, TAR.XZ

### Định dạng cần cài thêm

**7Z:**
```bash
pip install py7zr
```

**RAR:**
```bash
pip install rarfile
```
**Lưu ý**: Cần cài WinRAR (Windows) hoặc unrar (Linux/macOS)

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "extract-archive"
```

### Chạy trực tiếp

```bash
python tools/py/extract-archive/extract-archive.py
```

## Hướng dẫn chi tiết

### 1. Chọn chế độ

- **1**: Giải nén 1 file
- **2**: Giải nén tất cả file trong thư mục

### 2. Giải nén 1 file

1. Nhập đường dẫn file cần giải nén
2. Nhập thư mục đích (Enter để dùng thư mục hiện tại)
3. Tool tự động giải nén và hiển thị kết quả

### 3. Giải nén hàng loạt

1. Nhập đường dẫn thư mục chứa file nén
2. Nhập thư mục đích (Enter để dùng thư mục hiện tại)
3. Tool liệt kê tất cả file nén tìm thấy
4. Xác nhận để giải nén tất cả

## Ví dụ

### Giải nén 1 file

```
Chế độ: 1 (Giải nén 1 file)
File: D:\Downloads\archive.zip
Thư mục đích: D:\Extracted

🚀 Bắt đầu giải nén...
📦 archive.zip... ✅ (145.5 MB)
✅ Hoàn thành!
```

### Giải nén hàng loạt

```
Chế độ: 2 (Giải nén tất cả file trong thư mục)
Thư mục chứa file nén: D:\Downloads\archives
Thư mục đích: D:\Extracted

📦 Tìm thấy 5 file nén:
   1. project1.zip (50.2 MB)
   2. photos.tar.gz (125.8 MB)
   3. documents.7z (35.5 MB)
   4. backup.rar (80.3 MB)
   5. code.zip (15.7 MB)

Giải nén 5 file? (Y/n): Y

🚀 Bắt đầu giải nén...

📦 project1.zip... ✅ (145.5 MB)
📦 photos.tar.gz... ✅ (380.2 MB)
📦 documents.7z... ✅ (92.8 MB)
📦 backup.rar... ✅ (215.6 MB)
📦 code.zip... ✅ (45.3 MB)

============================================================
✅ Hoàn thành!
   - Thành công: 5/5 file
   - Tổng kích thước: 879.4 MB
============================================================
```

## Định dạng hỗ trợ

### ZIP
- **Hỗ trợ**: Có sẵn (không cần cài thêm)
- **Phổ biến**: Rất phổ biến trên Windows
- **Khuyến nghị**: Dùng cho hầu hết trường hợp

### TAR, TAR.GZ, TAR.BZ2, TAR.XZ
- **Hỗ trợ**: Có sẵn (không cần cài thêm)
- **Phổ biến**: Phổ biến trên Linux/Unix
- **Khuyến nghị**: Dùng cho Linux, server

### 7Z
- **Hỗ trợ**: Cần cài `py7zr`
- **Phổ biến**: Phổ biến trên Windows
- **Khuyến nghị**: Nén tốt nhất, file nhỏ nhất

### RAR
- **Hỗ trợ**: Cần cài `rarfile` và WinRAR/unrar
- **Phổ biến**: Phổ biến trên Windows
- **Khuyến nghị**: Dùng khi nhận file .rar

## Cài đặt thư viện

### Cài py7zr (cho 7Z)

```bash
pip install py7zr
```

### Cài rarfile (cho RAR)

**Windows:**
1. Cài WinRAR từ https://www.winrar.com/
2. Cài rarfile: `pip install rarfile`

**Linux:**
```bash
sudo apt-get install unrar
pip install rarfile
```

**macOS:**
```bash
brew install unrar
pip install rarfile
```

## Tips

### Giải nén hàng loạt:
- **Kiểm tra trước**: Xem danh sách file trước khi giải nén
- **Thư mục đích**: Chọn thư mục riêng để dễ quản lý
- **Dung lượng**: Đảm bảo có đủ dung lượng ổ đĩa

### Định dạng:
- **ZIP**: Dùng cho hầu hết trường hợp
- **7Z**: Nén tốt nhất, nhưng cần cài thêm
- **RAR**: Chỉ dùng khi nhận file .rar

### Xử lý lỗi:
- **File hỏng**: Tool sẽ báo lỗi và tiếp tục với file khác
- **Thiếu thư viện**: Tool sẽ hướng dẫn cài đặt
- **Dung lượng**: Kiểm tra dung lượng trước khi giải nén

## Use case phổ biến

- Giải nén nhiều file download cùng lúc
- Extract backup files
- Giải nén attachments hàng loạt
- Unpack project files
- Giải nén file từ email

## Lưu ý

- **Dung lượng**: Đảm bảo có đủ dung lượng ổ đĩa
- **Thời gian**: File lớn có thể mất nhiều thời gian
- **Thư viện**: Một số định dạng cần cài thư viện bên ngoài
- **File hỏng**: File hỏng sẽ bị bỏ qua và báo lỗi
- **Encoding**: Tên file có thể bị lỗi encoding nếu file nén dùng encoding cũ

## Ví dụ thực tế

### Giải nén file download

```
Thư mục: D:\Downloads
→ Tìm thấy 10 file ZIP
→ Giải nén tất cả vào D:\Extracted
→ Hoàn thành trong 2 phút
```

### Giải nén backup

```
File: backup_20250101.rar
Thư mục đích: D:\Restore
→ Giải nén thành công
→ Khôi phục dữ liệu
```
