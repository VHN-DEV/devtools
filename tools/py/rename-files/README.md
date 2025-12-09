# Rename Files - Đổi tên file hàng loạt

## Mô tả

Tool đổi tên file hàng loạt với nhiều tùy chọn: thêm prefix/suffix, thay thế text trong tên, đánh số thứ tự, đổi phần mở rộng, chuyển sang chữ thường, và xử lý khoảng trắng.

## Tính năng

✅ Thêm prefix (tiền tố)
✅ Thêm suffix (hậu tố)
✅ Thay thế text trong tên
✅ Đổi tên theo số thứ tự (001, 002, 003...)
✅ Đổi phần mở rộng file
✅ Chuyển sang chữ thường/hoa
✅ Xóa/thay thế khoảng trắng
✅ Filter theo extension

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "rename-files"
```

### Chạy trực tiếp

```bash
python tools/py/rename-files/rename-files.py
```

## Hướng dẫn chi tiết

### 1. Nhập đường dẫn

Nhập đường dẫn thư mục chứa file cần đổi tên (vd: `D:\Wedding_Photos`)

### 2. Chọn chức năng

- **1**: Thêm prefix (tiền tố)
- **2**: Thêm suffix (hậu tố)
- **3**: Thay thế text trong tên
- **4**: Đổi tên file theo số thứ tự
- **5**: Đổi phần mở rộng file
- **6**: Chuyển sang chữ thường
- **7**: Xóa/thay thế khoảng trắng

### 3. Cấu hình

Tùy thuộc vào chức năng đã chọn:

#### Thêm prefix
- Nhập prefix (vd: `[Backup]_`)

#### Thêm suffix
- Nhập suffix (vd: `_backup`)

#### Thay thế text
- Nhập text cần tìm (vd: `old_name`)
- Nhập text thay thế (vd: `new_name`)

#### Đổi tên theo số thứ tự
- Chỉ xử lý file có đuôi (vd: `.jpg .png`)
- Nhập tên cơ sở (vd: `wedding`)
- Bắt đầu từ số (vd: `1`)

#### Đổi phần mở rộng
- Nhập extension cũ (vd: `.jpeg`)
- Nhập extension mới (vd: `.jpg`)

#### Chuyển sang chữ thường
- Tự động chuyển tất cả chữ hoa sang chữ thường

#### Xóa/thay thế khoảng trắng
- Xóa khoảng trắng hoặc thay bằng `_` hoặc `-`

### 4. Xem kết quả và xác nhận

Tool sẽ hiển thị preview và yêu cầu xác nhận trước khi đổi tên.

## Ví dụ

### Đổi tên theo số thứ tự

```
Nhập đường dẫn thư mục: D:\Wedding_Photos
Chọn chức năng (1-7): 4

Chỉ xử lý file có đuôi (.jpg .png - Enter để tất cả): .jpg
Nhập tên cơ sở (vd: image): wedding
Bắt đầu từ số (vd: 1): 1

📋 Preview:
   DSC_5423.jpg → wedding_001.jpg
   DSC_5424.jpg → wedding_002.jpg
   DSC_5425.jpg → wedding_003.jpg
   IMG_9871.jpg → wedding_004.jpg
   IMG_9872.jpg → wedding_005.jpg

Xác nhận đổi tên? (YES để xác nhận): YES

🔄 Đang đổi tên...
✓ DSC_5423.jpg → wedding_001.jpg
✓ DSC_5424.jpg → wedding_002.jpg
✓ DSC_5425.jpg → wedding_003.jpg
✓ IMG_9871.jpg → wedding_004.jpg
✓ IMG_9872.jpg → wedding_005.jpg

✅ Hoàn thành! Đã đổi tên 5 file.
```

### Thêm prefix

```
Chọn chức năng (1-7): 1
Nhập prefix (tiền tố): [Backup]_

📋 Preview:
   document.pdf → [Backup]_document.pdf
   report.xlsx → [Backup]_report.xlsx

✅ Hoàn thành! Đã đổi tên 2 file.
```

### Thay thế text

```
Chọn chức năng (1-7): 3
Nhập text cần tìm: old_name
Nhập text thay thế: new_name

📋 Preview:
   file_old_name.txt → file_new_name.txt
   photo_old_name.jpg → photo_new_name.jpg

✅ Hoàn thành! Đã đổi tên 2 file.
```

### Xóa khoảng trắng

```
Chọn chức năng (1-7): 7
Thay thế khoảng trắng bằng (_/-/xóa): _

📋 Preview:
   My Document.pdf → My_Document.pdf
   Photo 2024.jpg → Photo_2024.jpg

✅ Hoàn thành! Đã đổi tên 2 file.
```

### Đổi extension

```
Chọn chức năng (1-7): 5
Nhập extension cũ: .jpeg
Nhập extension mới: .jpg

📋 Preview:
   photo1.jpeg → photo1.jpg
   photo2.jpeg → photo2.jpg

✅ Hoàn thành! Đã đổi tên 2 file.
```

## Tips

### Đổi tên an toàn:
- **Preview**: Luôn xem preview trước khi xác nhận
- **Backup**: Backup file quan trọng trước khi đổi tên
- **Test**: Test với một vài file trước khi đổi tên hàng loạt

### Số thứ tự:
- **Bắt đầu từ 1**: Dùng cho hầu hết trường hợp
- **Padding**: Tool tự động thêm số 0 phía trước (001, 002...)
- **Extension**: Chỉ xử lý file có extension cụ thể

### Khoảng trắng:
- **Xóa**: Xóa khoảng trắng (không khuyến nghị cho web)
- **Thay bằng _**: Dùng cho file (phổ biến)
- **Thay bằng -**: Dùng cho URL, web

## Use case phổ biến

- Đổi tên ảnh chụp từ máy ảnh (DSC_xxx → tên có nghĩa)
- Thêm prefix cho file backup
- Xóa khoảng trắng trong tên file (tốt cho web server)
- Đổi extension hàng loạt (.jpeg → .jpg)
- Đánh số thứ tự cho ảnh/video
- Chuẩn hóa tên file

## Lưu ý

- **Preview**: Luôn xem preview trước khi xác nhận
- **Backup**: Backup file quan trọng trước khi đổi tên
- **Trùng tên**: Tool sẽ tự động xử lý file trùng tên
- **Extension**: Không đổi tên file ẩn hoặc file hệ thống
- **Xác nhận**: Xác nhận bằng `YES` (chữ hoa) để tránh đổi nhầm

## Ví dụ thực tế

### Đổi tên ảnh chụp

```
Thư mục: D:\Photos (500 ảnh)
Chức năng: Đổi tên theo số thứ tự
Tên cơ sở: vacation
→ Đổi tên: vacation_001.jpg, vacation_002.jpg...
→ Dễ quản lý hơn
```

### Chuẩn hóa tên file

```
Thư mục: D:\Documents
Chức năng: Xóa khoảng trắng, thay bằng _
→ My Document.pdf → My_Document.pdf
→ Tốt cho web server
```
