# Text Encoding Converter - Chuyển đổi encoding

## Mô tả

Tool chuyển đổi encoding file text tự động. Tự động phát hiện encoding, chuyển đổi sang UTF-8/Windows-1252/ISO-8859-1..., backup file gốc, và xử lý hàng loạt.

## Tính năng

✅ Tự động phát hiện encoding
✅ Chuyển đổi sang nhiều encoding (UTF-8, Windows-1252, ISO-8859-1...)
✅ Backup file gốc (.bak)
✅ Xử lý hàng loạt nhiều file
✅ Thống kê confidence của phát hiện
✅ Filter theo extension
✅ Xử lý đệ quy trong thư mục con

## Yêu cầu

```bash
pip install chardet
```

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "text-encoding-converter"
```

### Chạy trực tiếp

```bash
python tools/py/text-encoding-converter/text-encoding-converter.py
```

## Hướng dẫn chi tiết

### 1. Chọn chế độ

- **1**: Phát hiện encoding (chỉ xem, không thay đổi)
- **2**: Chuyển đổi encoding

### 2. Nhập đường dẫn

Nhập đường dẫn thư mục hoặc file (vd: `D:\old-php-project`)

### 3. Cấu hình

1. **Chỉ xử lý file có đuôi**: Nhập extension (vd: `.php .txt .html`), Enter để xử lý tất cả
2. **Tìm trong tất cả thư mục con?** (Y/n): Xử lý đệ quy hay không

### 4. Phát hiện encoding (Chế độ 1)

Tool sẽ:
1. Quét tất cả file
2. Phát hiện encoding của từng file
3. Hiển thị kết quả với confidence

### 5. Chuyển đổi encoding (Chế độ 2)

1. **Encoding nguồn**: 
   - `auto`: Tự động phát hiện (khuyến nghị)
   - Hoặc chọn encoding cụ thể: `windows-1252`, `iso-8859-1`...
2. **Encoding đích**: 
   - `utf-8`: Khuyến nghị cho hầu hết trường hợp
   - Hoặc chọn encoding khác: `windows-1252`, `iso-8859-1`...
3. **Backup file gốc**: (Y/n) Tạo file .bak
4. **Xác nhận**: Xác nhận bằng `YES` để thực hiện

## Ví dụ

### Phát hiện encoding

```
Nhập đường dẫn: D:\old-php-project
Chỉ xử lý file có đuôi (.php .txt .html - Enter để tất cả): .php .txt
Tìm trong tất cả thư mục con? (Y/n): Y
Chế độ (1: Phát hiện, 2: Chuyển đổi): 1

🔍 Đang quét file...

📄 index.php
   Encoding: windows-1252 (confidence: 0.95)

📄 config.php
   Encoding: iso-8859-1 (confidence: 0.92)

📄 data.txt
   Encoding: utf-8 (confidence: 0.99)

...

============================================================
✅ Hoàn thành! Đã kiểm tra 25 file
============================================================

📊 Thống kê:
   UTF-8: 10 file
   Windows-1252: 8 file
   ISO-8859-1: 5 file
   Khác: 2 file
```

### Chuyển đổi encoding

```
Chế độ (1: Phát hiện, 2: Chuyển đổi): 2

Encoding nguồn (auto/windows-1252/iso-8859-1...): auto
Encoding đích (utf-8/windows-1252/iso-8859-1...): utf-8
Backup file gốc (.bak)? (Y/n): Y

⚠️  CẢNH BÁO: Bạn sắp chuyển đổi encoding 25 file!
Xác nhận thực hiện? (YES để xác nhận): YES

🔄 Đang chuyển đổi...

✓ index.php (windows-1252 → utf-8) [Backup: index.php.bak]
✓ config.php (iso-8859-1 → utf-8) [Backup: config.php.bak]
✓ data.txt (utf-8 → utf-8) [Giữ nguyên]

...

============================================================
✅ Hoàn thành! Đã chuyển đổi 23 file
============================================================

📊 Thống kê:
   Đã chuyển đổi: 23 file
   Giữ nguyên: 2 file (đã là UTF-8)
   Backup: 23 file (.bak)
```

## Encoding phổ biến

### UTF-8
- **Mô tả**: Encoding hiện đại, hỗ trợ đầy đủ Unicode
- **Khuyến nghị**: Dùng cho hầu hết trường hợp
- **Hỗ trợ**: Tất cả ngôn ngữ, emoji

### Windows-1252
- **Mô tả**: Encoding Windows cũ
- **Phổ biến**: File Windows cũ, PHP cũ
- **Vấn đề**: Không hỗ trợ đầy đủ ký tự đặc biệt

### ISO-8859-1 (Latin-1)
- **Mô tả**: Encoding Latin cơ bản
- **Phổ biến**: File cũ, email
- **Vấn đề**: Không hỗ trợ nhiều ký tự

### Shift_JIS
- **Mô tả**: Encoding tiếng Nhật
- **Phổ biến**: File tiếng Nhật

### GB2312, GBK
- **Mô tả**: Encoding tiếng Trung
- **Phổ biến**: File tiếng Trung

## Tips

### Phát hiện encoding:
- **Auto**: Dùng `auto` để tự động phát hiện
- **Confidence**: Xem confidence để đánh giá độ chính xác
- **Kiểm tra**: Kiểm tra một vài file trước khi chuyển đổi hàng loạt

### Chuyển đổi:
- **UTF-8**: Luôn chuyển sang UTF-8 nếu có thể
- **Backup**: Luôn backup file gốc trước khi chuyển đổi
- **Test**: Test với một vài file trước khi chuyển đổi hàng loạt

### An toàn:
- **Backup**: Luôn backup file gốc
- **Xác nhận**: Luôn xác nhận bằng `YES` trước khi chuyển đổi
- **Kiểm tra**: Kiểm tra kết quả sau khi chuyển đổi

## Use case phổ biến

- Fix lỗi hiển thị tiếng Việt
- Chuyển project cũ sang UTF-8
- Chuẩn hóa encoding toàn bộ project
- Fix file PHP/HTML cũ bị lỗi font
- Chuyển đổi file từ encoding cũ sang UTF-8

## Lưu ý

- **Backup**: Luôn backup file gốc trước khi chuyển đổi
- **Confidence**: Confidence thấp (<0.8) có thể không chính xác
- **File lớn**: File quá lớn có thể mất nhiều thời gian
- **Binary file**: Không xử lý file binary (ảnh, video...)
- **Test**: Test với một vài file trước khi chuyển đổi hàng loạt

## Ví dụ thực tế

### Fix lỗi tiếng Việt

```
Project: D:\old-php-project
Encoding nguồn: auto
Encoding đích: utf-8
→ Chuyển đổi 50 file PHP
→ Fix lỗi hiển thị tiếng Việt
→ Hoàn thành!
```

### Chuẩn hóa encoding

```
Project: D:\website
Encoding nguồn: auto
Encoding đích: utf-8
→ Chuyển đổi toàn bộ file
→ Chuẩn hóa encoding
→ Dễ maintain hơn
```
