# QR Code - Tạo và giải mã QR Code

## Mô tả

Tool đa năng để tạo và giải mã QR code với nhiều tính năng: tạo QR code từ text/URL/WiFi/Email/vCard, tạo hàng loạt từ CSV, giải mã từ ảnh, và quét trực tiếp từ webcam.

## Tính năng

✅ Tạo QR code cơ bản (text, URL)
✅ Tạo QR code đặc biệt (WiFi, Email, SMS, Phone, vCard, Location)
✅ Tạo QR code hàng loạt từ CSV/Text file
✅ Tạo QR code từ clipboard
✅ Giải mã QR code từ ảnh
✅ Export kết quả giải mã ra JSON/CSV
✅ Quét QR code trực tiếp từ webcam
✅ Tùy chỉnh màu sắc, kích thước, logo
✅ Hỗ trợ nhiều định dạng ảnh (PNG, JPG, SVG, BMP, TIFF)

## Yêu cầu

```bash
# Tạo QR code
pip install qrcode[pil]

# Giải mã QR code
pip install opencv-python pyzbar pillow numpy

# Clipboard (tùy chọn)
pip install pyperclip
```

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "qr-code"
```

### Chạy trực tiếp

```bash
python tools/py/qr-code/qr-code.py
```

### Chế độ CLI

```bash
# Tạo QR code đơn giản
python qr-code.py generate -d "https://example.com" -o qr.png

# Tạo với tùy chỉnh
python qr-code.py generate -d "Hello" -o output.png -s 15 -e H

# Tạo QR code dạng SVG (vector)
python qr-code.py generate -d "https://example.com" -o qr.svg

# Tạo có logo
python qr-code.py generate -d "URL" -o qr.png --logo logo.png

# Tạo QR code hàng loạt từ CSV
python qr-code.py batch -i data.csv -o ./output

# Giải mã từ thư mục
python qr-code.py decode --directory ./images

# Giải mã với export JSON
python qr-code.py decode --directory ./images --export json

# Đọc QR code từ webcam
python qr-code.py webcam
```

## Hướng dẫn chi tiết

### 1. Tạo QR Code cơ bản

1. Chọn chức năng 1: Tạo QR Code
2. Nhập nội dung (URL, text, bất kỳ văn bản nào)
3. Chọn đường dẫn lưu (Enter để dùng mặc định: `qr_code.png`)
4. Tùy chỉnh (tùy chọn):
   - Kích thước box (mặc định: 10)
   - Border (mặc định: 4)
   - Mức sửa lỗi: L/M/Q/H (mặc định: M)
   - Màu mã QR và nền
   - Logo (tùy chọn)

### 2. Tạo QR Code đặc biệt

Hỗ trợ các loại QR code chuẩn:
- **WiFi**: Tạo QR cho mạng WiFi (SSID, mật khẩu, bảo mật)
- **Email**: QR code với mailto, tiêu đề và nội dung
- **SMS**: QR code để gửi SMS với số và tin nhắn
- **Phone**: QR code để gọi điện
- **vCard**: QR code danh thiếp điện tử
- **Location**: QR code vị trí GPS
- **URL**: QR code URL (tự động thêm https:// nếu thiếu)

### 3. Tạo QR Code hàng loạt

- **Từ CSV**: Cột 'data' hoặc 'content' (bắt buộc), các cột khác tùy chọn
- **Từ Text file**: Mỗi dòng = 1 QR code
- Tự động đặt tên file hoặc dùng cột 'filename' trong CSV

### 4. Giải mã QR Code

1. Chọn chức năng 5 hoặc 6
2. Nhập đường dẫn thư mục chứa ảnh
3. Chọn có di chuyển ảnh thành công vào thư mục 'ok' không
4. Xem kết quả trong file `result.txt` và `results.txt`

### 5. Giải mã với Export

- Export ra JSON: Dữ liệu có cấu trúc, dễ xử lý
- Export ra CSV: Dễ import vào Excel/Google Sheets
- Kết quả bao gồm: filename, path, status, data, method, timestamp

### 6. Đọc từ Webcam

Quét QR code trực tiếp từ camera/webcam:
- Hiển thị real-time
- Tự động lưu kết quả khi tìm thấy
- Nhấn 'q' để thoát

## Định dạng CSV cho Batch Generate

File CSV nên có các cột:

```csv
data,filename,size,error_correction,fill_color,back_color
https://example.com,qr1.png,15,H,black,white
Hello World,qr2.png,10,M,#000000,#FFFFFF
```

**Các cột:**
- `data` hoặc `content`: (bắt buộc) Nội dung QR code
- `filename`: (tùy chọn) Tên file output
- `size`: (tùy chọn) Kích thước box
- `border`: (tùy chọn) Độ dày border
- `error_correction`: (tùy chọn) L/M/Q/H
- `fill_color`: (tùy chọn) Màu mã QR
- `back_color`: (tùy chọn) Màu nền

## Mức sửa lỗi (Error Correction)

- **L (Low)**: ~7% - Phù hợp cho QR code đơn giản
- **M (Medium)**: ~15% - Mặc định, phù hợp cho hầu hết trường hợp
- **Q (Quartile)**: ~25% - Tốt hơn, có thể chịu được một số hư hỏng
- **H (High)**: ~30% - Tốt nhất khi có logo, chịu được nhiều hư hỏng

## Tips

### Tạo QR Code:
- Mức sửa lỗi H (30%) tốt nhất khi có logo
- Màu tối trên nền sáng dễ quét nhất
- Kích thước box 10-15 phù hợp cho hầu hết trường hợp
- Logo nên là hình vuông hoặc gần vuông
- QR code có thể quét từ xa hơn nếu lớn hơn

### Giải mã QR Code:
- Tool tự động xử lý nhiều kỹ thuật: enhance, crop, xoay
- Hỗ trợ nhiều định dạng: jpg, png, bmp, tiff
- Tự động thử nhiều phương pháp nếu lần đầu thất bại
- Quét hàng loạt từ thư mục
- Export JSON/CSV giúp xử lý dữ liệu dễ dàng hơn

## Ví dụ

### Tạo QR Code WiFi

```
Chức năng: 2 (QR Code đặc biệt)
Loại: WiFi
SSID: MyNetwork
Password: mypassword123
Security: WPA2
→ Tạo QR code, quét bằng điện thoại để kết nối WiFi
```

### Tạo QR Code vCard

```
Chức năng: 2 (QR Code đặc biệt)
Loại: vCard
Tên: John Doe
Phone: +1234567890
Email: john@example.com
→ Tạo QR code danh thiếp điện tử
```

### Giải mã hàng loạt

```
Thư mục: D:\QR_Images
→ Quét 50 ảnh
→ Thành công: 48/50
→ Export: results.json, results.csv
```

## Use case phổ biến

- Tạo QR code cho website/sản phẩm
- Chia sẻ WiFi password dễ dàng
- Tạo danh thiếp điện tử
- Giải mã QR code từ nhiều ảnh
- Quét QR code nhanh từ webcam
- Tạo QR code hàng loạt cho marketing

