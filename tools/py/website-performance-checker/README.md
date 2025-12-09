# Website Performance Checker - Kiểm tra hiệu năng dự án website

Mô tả ngắn gọn: Tool kiểm tra và phân tích hiệu năng website, phát hiện các vấn đề và đưa ra gợi ý tối ưu hóa. Hỗ trợ kiểm tra CSS, JavaScript, hình ảnh, HTML, PHP và cấu hình cache.

## Cách sử dụng

```bash
python tools/py/website-performance-checker/website-performance-checker.py
```

## Tính năng

### 1. Phân tích file CSS
- Kiểm tra kích thước file
- Phát hiện file chưa được minify
- Gợi ý tối ưu hóa

### 2. Phân tích file JavaScript
- Kiểm tra kích thước file
- Phát hiện file chưa được minify
- Gợi ý tối ưu hóa

### 3. Phân tích hình ảnh
- Kiểm tra kích thước ảnh
- Phát hiện ảnh quá lớn
- Gợi ý nén ảnh và chuyển sang WebP

### 4. Phân tích HTML/PHP
- Kiểm tra kích thước file
- Phát hiện file quá lớn
- Gợi ý tối ưu code

### 5. Kiểm tra Cache Headers
- Kiểm tra file .htaccess
- Phát hiện thiếu cấu hình cache
- Gợi ý thêm cache headers

## Cấu hình

Tool tự động tạo file `performance_config.json` với các cài đặt mặc định:

```json
{
  "default_htdocs_path": "C:\\xampp\\htdocs",
  "max_file_size_mb": 1.0,
  "max_image_size_kb": 500,
  "check_minified": true,
  "check_css": true,
  "check_js": true,
  "check_images": true,
  "check_html": true,
  "check_php": true
}
```

Có thể thay đổi cài đặt qua menu "Cài đặt" trong tool.

## Ví dụ sử dụng

### Ví dụ 1: Kiểm tra dự án từ danh sách

```
1. Vào tool, danh sách dự án sẽ hiển thị ngay
2. Nhập số thứ tự dự án (ví dụ: 1)
3. Tool sẽ phân tích và tạo báo cáo
```

### Ví dụ 2: Kiểm tra dự án từ đường dẫn cụ thể

```
1. Vào tool, danh sách dự án sẽ hiển thị
2. Nhập đường dẫn: C:\xampp\htdocs\samsung-sft
3. Tool sẽ phân tích và tạo báo cáo
```

### Ví dụ 3: Nhập tên dự án

```
1. Vào tool, danh sách dự án sẽ hiển thị
2. Nhập tên dự án: samsung-sft
3. Tool sẽ tự động tìm và kiểm tra
```

### Ví dụ 4: Thay đổi cài đặt

```
1. Vào tool
2. Nhập 's' để vào menu cài đặt
3. Chọn mục cần thay đổi:
   - 1: Đường dẫn htdocs mặc định
   - 2: Kích thước file tối đa (MB)
   - 3: Kích thước ảnh tối đa (KB)
   - 4: Bật/tắt kiểm tra file minified
   - ...
```

## Kết quả

Báo cáo được lưu trong thư mục dự án với tên:
```
performance_report_[tên_dự_án]_[timestamp].txt
```

Báo cáo bao gồm:
- Tổng quan về dự án
- Danh sách các vấn đề phát hiện
- Gợi ý tối ưu hóa chi tiết
- Tài liệu tham khảo

## Use case phổ biến

- Kiểm tra hiệu năng dự án trước khi deploy
- Tìm các file cần tối ưu hóa
- Phát hiện ảnh chưa được nén
- Kiểm tra cấu hình cache
- Đánh giá hiệu năng tổng thể website

## Gợi ý tối ưu hóa

1. **Minify CSS và JavaScript**: Giảm kích thước file lên đến 50-70%
2. **Tối ưu hóa hình ảnh**: Nén ảnh và chuyển sang WebP, giảm kích thước lên đến 80%
3. **Thiết lập Cache Headers**: Tăng tốc độ tải trang
4. **Tách nhỏ file PHP**: Dễ bảo trì và tối ưu hiệu năng
5. **Code Splitting**: Chỉ load code khi cần thiết
6. **Sử dụng CDN**: Giảm tải server và tăng tốc độ
7. **Gzip Compression**: Nén response, giảm bandwidth lên đến 70%

## Tài liệu tham khảo

- Google PageSpeed Insights: https://pagespeed.web.dev/
- GTmetrix: https://gtmetrix.com/
- WebPageTest: https://www.webpagetest.org/
- Minify CSS: https://cssnano.co/
- Minify JS: https://terser.org/
- Optimize Images: https://tinypng.com/
- WebP Converter: https://developers.google.com/speed/webp

