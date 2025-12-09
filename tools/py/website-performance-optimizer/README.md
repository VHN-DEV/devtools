# Website Performance Optimizer - Tối ưu hóa hiệu năng website (Bản beta)

Mô tả ngắn gọn: Tool tự động Tối ưu hóa hiệu năng website (Bản beta) bằng cách minify CSS, JavaScript, HTML, tạo cache headers và Gzip compression. Hỗ trợ backup file gốc trước khi tối ưu.

## Cách sử dụng

```bash
python tools/py/website-performance-optimizer/website-performance-optimizer.py
```

## Tính năng

### 1. Minify CSS
- Loại bỏ comments và khoảng trắng thừa
- Giảm kích thước file lên đến 50-70%
- Giữ nguyên chức năng của CSS

### 2. Minify JavaScript
- Loại bỏ comments và khoảng trắng thừa
- Giảm kích thước file lên đến 50-70%
- Bỏ qua file .min.js (đã minify)
- Giữ nguyên chức năng của JavaScript

### 3. Tối ưu hóa HTML
- Loại bỏ HTML comments
- Loại bỏ khoảng trắng thừa
- Giảm kích thước file

### 4. Tạo/Cập nhật .htaccess
- Thêm cache headers cho images, CSS, JS
- Kích hoạt Gzip compression
- Cấu hình browser caching
- Không ghi đè nếu đã có cấu hình

### 5. Backup file gốc
- Tự động backup file trước khi tối ưu
- Lưu vào thư mục `backup_original` (có thể cấu hình)
- Giữ nguyên cấu trúc thư mục

## Cấu hình

Tool tự động tạo file `optimizer_config.json` với các cài đặt mặc định:

```json
{
  "default_htdocs_path": "C:\\xampp\\htdocs",
  "optimize_css": true,
  "optimize_js": true,
  "optimize_html": true,
  "create_htaccess": true,
  "backup_files": true,
  "backup_folder": "backup_original",
  "minify_css": true,
  "minify_js": true,
  "remove_html_comments": true,
  "remove_whitespace": true
}
```

Có thể thay đổi cài đặt qua menu "Cài đặt" trong tool.

## Ví dụ sử dụng

### Ví dụ 1: Tối ưu dự án từ danh sách

```
1. Vào tool, danh sách dự án sẽ hiển thị ngay
2. Nhập số thứ tự dự án (ví dụ: 1)
3. Xác nhận: y
4. Tool sẽ tự động tối ưu và hiển thị kết quả
```

### Ví dụ 2: Tối ưu dự án từ đường dẫn cụ thể

```
1. Vào tool, danh sách dự án sẽ hiển thị
2. Nhập đường dẫn: C:\xampp\htdocs\samsung-sft
3. Xác nhận: y
4. Tool sẽ tự động tối ưu
```

### Ví dụ 3: Thay đổi cài đặt

```
1. Vào tool
2. Nhập 's' để vào menu cài đặt
3. Chọn mục cần thay đổi:
   - 1: Đường dẫn htdocs mặc định
   - 2: Bật/tắt tối ưu CSS
   - 3: Bật/tắt tối ưu JavaScript
   - 4: Bật/tắt tối ưu HTML
   - 5: Bật/tắt tạo .htaccess
   - 6: Bật/tắt backup file gốc
   - 7: Thay đổi tên thư mục backup
```

## Kết quả

Sau khi tối ưu, tool sẽ hiển thị:
- Số lượng file đã xử lý
- Tổng dung lượng tiết kiệm (KB/MB)
- Đường dẫn thư mục backup (nếu bật)
- Danh sách file đã tối ưu

## Lưu ý quan trọng

⚠️ **Backup trước khi sử dụng**: Mặc dù tool có tính năng backup, nhưng nên backup toàn bộ dự án trước khi sử dụng.

⚠️ **File sẽ bị thay đổi**: Tool sẽ thay đổi file gốc (trừ khi bật backup). File gốc sẽ được lưu trong thư mục backup.

⚠️ **Bỏ qua file đã minify**: File `.min.js` sẽ được bỏ qua vì đã được minify.

⚠️ **Bỏ qua thư mục đặc biệt**: Tool sẽ bỏ qua `node_modules`, `.git`, `vendor`, `.idea`.

## Khôi phục file gốc

Nếu cần khôi phục file gốc:
1. Vào thư mục `backup_original` trong dự án
2. Copy file từ thư mục backup về vị trí gốc
3. Hoặc xóa file đã tối ưu và copy từ backup

## So sánh với Website Performance Checker

| Tính năng | Checker | Optimizer |
|-----------|---------|-----------|
| Phân tích hiệu năng | ✅ | ❌ |
| Đưa ra gợi ý | ✅ | ❌ |
| Minify CSS/JS | ❌ | ✅ |
| Tối ưu HTML | ❌ | ✅ |
| Tạo .htaccess | ❌ | ✅ |
| Backup file | ❌ | ✅ |
| Thực thi tối ưu | ❌ | ✅ |

**Khuyến nghị**: Sử dụng Checker trước để phân tích, sau đó dùng Optimizer để tối ưu hóa.

## Use case phổ biến

- Tối ưu hóa dự án trước khi deploy
- Giảm kích thước file để tăng tốc độ tải trang
- Tự động hóa quy trình tối ưu hóa
- Chuẩn bị dự án cho production

## Tài liệu tham khảo

- Minify CSS: https://cssnano.co/
- Minify JS: https://terser.org/
- Apache .htaccess: https://httpd.apache.org/docs/current/howto/htaccess.html
- Gzip Compression: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Encoding

