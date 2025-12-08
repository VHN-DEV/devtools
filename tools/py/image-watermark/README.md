# Image Watermark - Thêm watermark vào ảnh

## Mô tả

Tool thêm watermark (text hoặc logo) vào ảnh hàng loạt với nhiều tùy chọn: vị trí, độ trong suốt, kích thước, và hỗ trợ lưu template để tái sử dụng.

## Tính năng

✅ Thêm text watermark với font, size, color tùy chỉnh
✅ Thêm image watermark (logo) với transparency
✅ 9 vị trí đặt watermark (góc, cạnh, center)
✅ Tùy chỉnh opacity (độ trong suốt)
✅ Xử lý hàng loạt nhiều ảnh
✅ Lưu template để tái sử dụng
✅ Hỗ trợ nhiều định dạng: JPG, PNG, WEBP, BMP

## Yêu cầu

```bash
pip install Pillow
```

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "image-watermark"
```

### Chạy trực tiếp

```bash
python tools/py/image-watermark/image-watermark.py
```

## Hướng dẫn chi tiết

### 1. Chọn chế độ watermark

- **1**: Text Watermark (chữ)
- **2**: Image Watermark (logo)
- **3**: Dùng Template đã lưu

### 2. Text Watermark

1. Nhập text watermark (vd: © 2024 Your Name)
2. Kích thước chữ (pixels, mặc định: 36)
3. Màu chữ (white/black, mặc định: white)

### 3. Image Watermark

1. Nhập đường dẫn logo/watermark (PNG trong suốt khuyến nghị)
2. Kích thước logo (% chiều rộng ảnh, mặc định: 10%)

### 4. Cấu hình chung

1. Vị trí watermark:
   - `top-left`, `top-center`, `top-right`
   - `center-left`, `center`, `center-right`
   - `bottom-left`, `bottom-center`, `bottom-right`
2. Độ trong suốt (0-255):
   - 0 = trong suốt hoàn toàn
   - 128 = mặc định (50% trong suốt)
   - 255 = đặc hoàn toàn

### 5. Thư mục ảnh

1. Thư mục chứa ảnh gốc
2. Thư mục output (Enter để tạo 'watermarked' với timestamp)

### 6. Lưu template (tùy chọn)

Lưu config thành template để tái sử dụng sau (y/N)

## Ví dụ

### Text Watermark

```
Chế độ: Text Watermark
Text: © 2024 My Company
Kích thước: 36 pixels
Màu: white
Vị trí: bottom-right
Opacity: 128
Thư mục: D:\Photos
→ Xử lý 50 ảnh
→ Thành công: 50/50
→ Lưu vào: D:\Photos\watermarked_20241029_153045\
```

### Image Watermark

```
Chế độ: Image Watermark
Logo: D:\logo.png
Kích thước: 15% chiều rộng
Vị trí: bottom-right
Opacity: 150
Thư mục: D:\Photos
→ Xử lý 30 ảnh
→ Thành công: 30/30
```

## Tips

- **Logo**: Nên là PNG trong suốt để có kết quả đẹp nhất
- **Opacity**: Càng cao watermark càng rõ, nhưng có thể che mất nội dung ảnh
- **Vị trí**: `bottom-right` hoặc `bottom-left` phổ biến nhất
- **Template**: Lưu template để dùng lại cho các batch ảnh khác
- **Định dạng**: Hỗ trợ JPG, PNG, WEBP, BMP

## Use case phổ biến

- Bảo vệ bản quyền ảnh trước khi đăng online
- Thêm logo công ty vào ảnh sản phẩm
- Watermark hàng loạt cho stock photos
- Thêm copyright cho portfolio
- Tạo ảnh demo với watermark

## Lưu ý

- Luôn giữ bản gốc ảnh trước khi thêm watermark
- Test với một vài ảnh trước khi xử lý hàng loạt
- Logo PNG trong suốt cho kết quả tốt nhất
- Opacity 100-150 thường phù hợp cho hầu hết trường hợp
- Template giúp tiết kiệm thời gian khi xử lý nhiều batch

