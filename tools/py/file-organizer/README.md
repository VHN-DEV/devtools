# File Organizer - Sắp xếp file tự động

## Mô tả

Tool sắp xếp file tự động theo loại, extension, hoặc ngày tháng. Hỗ trợ chế độ copy (giữ file gốc) hoặc move (di chuyển), xử lý trùng tên tự động, và thống kê chi tiết.

## Tính năng

✅ Sắp xếp theo loại (Images, Videos, Documents, Code...)
✅ Sắp xếp theo extension (.jpg, .mp4, .pdf...)
✅ Sắp xếp theo ngày tháng (modification date)
✅ Chế độ copy (giữ file gốc) hoặc move (di chuyển)
✅ Xử lý trùng tên tự động
✅ Thống kê chi tiết

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "file-organizer"
```

### Chạy trực tiếp

```bash
python tools/py/file-organizer/file-organizer.py
```

## Hướng dẫn chi tiết

### 1. Nhập đường dẫn

Nhập đường dẫn thư mục cần sắp xếp (vd: `D:\Downloads`)

### 2. Chọn chế độ sắp xếp

- **1**: Theo loại file (Images, Videos, Documents, ...)
- **2**: Theo đuôi file (.jpg, .mp4, .pdf, ...)
- **3**: Theo ngày tháng (modification date)

### 3. Cấu hình

#### Sắp xếp theo loại (Chế độ 1)

File được sắp xếp vào các thư mục:
- **Images**: .jpg, .png, .gif, .webp, .bmp...
- **Videos**: .mp4, .avi, .mkv, .mov, .webm...
- **Documents**: .pdf, .doc, .docx, .xls, .xlsx...
- **Audio**: .mp3, .wav, .flac, .aac, .ogg...
- **Archives**: .zip, .rar, .7z, .tar, .gz...
- **Code**: .py, .js, .html, .css, .json...
- **Executables**: .exe, .msi, .deb, .rpm...
- **Others**: Các file khác

#### Sắp xếp theo extension (Chế độ 2)

File được sắp xếp vào thư mục theo extension:
- `.jpg`, `.png` → `Images/`
- `.mp4`, `.avi` → `Videos/`
- `.pdf`, `.doc` → `Documents/`
- Và nhiều extension khác...

#### Sắp xếp theo ngày (Chế độ 3)

File được sắp xếp vào thư mục theo ngày:
- **Năm-Tháng** (YYYY-MM): `2024-01/`, `2024-02/`...
- **Năm-Tháng-Ngày** (YYYY-MM-DD): `2024-01-15/`, `2024-01-16/`...
- **Chỉ năm** (YYYY): `2024/`, `2023/`...

### 4. Chọn thư mục đích

Nhập thư mục đích (Enter để tạo thư mục 'Organized' trong thư mục nguồn)

### 5. Chọn hành động

- **1**: Copy (giữ nguyên file gốc)
- **2**: Move (di chuyển file)

### 6. Xác nhận và chờ xử lý

Tool sẽ sắp xếp file và hiển thị thống kê.

## Ví dụ

### Sắp xếp theo loại

```
Nhập đường dẫn thư mục cần sắp xếp: D:\Downloads

===== CHẾ ĐỘ SẮP XẾP =====
1. Theo loại file (Images, Videos, Documents, ...)
2. Theo đuôi file (.jpg, .mp4, .pdf, ...)
3. Theo ngày tháng (modification date)

Chọn chế độ (1-3): 1

Thư mục đích (Enter để tạo thư mục 'Organized'): [Enter]

===== HÀNH ĐỘNG =====
1. Copy (giữ nguyên file gốc)
2. Move (di chuyển file)

Chọn (1-2): 1

🚀 Bắt đầu sắp xếp...

✓ Copy: report.pdf → Documents/
✓ Copy: photo1.jpg → Images/
✓ Copy: video.mp4 → Videos/
✓ Copy: song.mp3 → Audio/
✓ Copy: setup.exe → Executables/
✓ Copy: script.py → Code/
✓ Copy: archive.zip → Archives/
... (và 43 file khác)

============================================================
✅ Hoàn thành! Đã xử lý 50 file
============================================================

📊 Thống kê theo loại:
   Images: 20 file
   Documents: 15 file
   Videos: 8 file
   Audio: 5 file
   Archives: 2 file
   Code: 2 file
   Executables: 1 file
   Others: 0 file
```

### Sắp xếp theo ngày

```
Chọn chế độ (1-3): 3

===== ĐỊNH DẠNG NGÀY =====
1. Năm-Tháng (2024-01)
2. Năm-Tháng-Ngày (2024-01-15)
3. Chỉ năm (2024)

Chọn (1-3): 1

🚀 Bắt đầu sắp xếp theo ngày...

✓ Copy: file1.txt → 2024-10/
✓ Copy: photo.jpg → 2024-10/
✓ Copy: old_doc.pdf → 2024-09/
✓ Copy: backup.zip → 2024-08/
...

============================================================
✅ Hoàn thành! Đã xử lý 50 file
============================================================

📊 Thống kê theo thời gian:
   2024-10: 25 file
   2024-09: 15 file
   2024-08: 10 file
```

## Tips

### Chế độ Copy vs Move:
- **Copy**: An toàn hơn, giữ file gốc (khuyến nghị)
- **Move**: Di chuyển file, tiết kiệm dung lượng

### Sắp xếp theo loại:
- **Phù hợp**: Khi muốn tổ chức file theo chức năng
- **Dễ tìm**: Dễ tìm file theo loại

### Sắp xếp theo extension:
- **Phù hợp**: Khi muốn tổ chức file theo định dạng
- **Chi tiết**: Phân loại chi tiết hơn

### Sắp xếp theo ngày:
- **Phù hợp**: Khi muốn tổ chức file theo thời gian
- **Archive**: Phù hợp cho archive, backup

## Use case phổ biến

- Dọn dẹp thư mục Downloads lộn xộn
- Tổ chức ảnh/video theo năm tháng
- Sắp xếp file project theo loại
- Chuẩn bị file để archive
- Tổ chức file theo thời gian tạo/sửa

## Lưu ý

- **Copy mode**: An toàn hơn, giữ file gốc
- **Move mode**: Di chuyển file, không thể hoàn tác
- **Trùng tên**: Tool tự động xử lý file trùng tên
- **Thời gian**: Xử lý nhiều file có thể mất thời gian
- **Dung lượng**: Đảm bảo có đủ dung lượng khi dùng copy mode

## Ví dụ thực tế

### Dọn dẹp Downloads

```
Thư mục: D:\Downloads (500 files lộn xộn)
Chế độ: Theo loại
Hành động: Copy
→ Sắp xếp thành công
→ Dễ tìm file hơn
```

### Tổ chức ảnh theo năm

```
Thư mục: D:\Photos (1000 ảnh)
Chế độ: Theo ngày (Năm-Tháng)
Hành động: Move
→ Sắp xếp theo 2024-01, 2024-02...
→ Dễ quản lý theo thời gian
```
