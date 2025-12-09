# Find and Replace - Tìm và thay thế text

## Mô tả

Tool tìm kiếm và thay thế text trong nhiều file cùng lúc. Hỗ trợ Regular Expression, case sensitive/insensitive, tìm đệ quy trong thư mục con, và preview trước khi thay đổi.

## Tính năng

✅ Tìm kiếm text trong nhiều file
✅ Thay thế text (simple hoặc regex)
✅ Hỗ trợ Regular Expression
✅ Case sensitive/insensitive
✅ Tìm đệ quy trong thư mục con
✅ Preview trước khi thay thế (chế độ tìm kiếm)
✅ Hiển thị số dòng tìm thấy
✅ Filter theo extension file
✅ Xác nhận an toàn trước khi thay thế

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "find-and-replace"
```

### Chạy trực tiếp

```bash
python tools/py/find-and-replace/find-and-replace.py
```

## Hướng dẫn chi tiết

### 1. Chọn thư mục

Nhập đường dẫn thư mục cần tìm kiếm (vd: `D:\my-react-project`)

### 2. Cấu hình tìm kiếm

1. **Tìm trong tất cả thư mục con?** (Y/n): Có tìm đệ quy hay không
2. **Chỉ xử lý file có đuôi**: Nhập extension (vd: `.js .jsx .py`), Enter để xử lý tất cả
3. **Nhập text cần tìm**: Text hoặc pattern cần tìm
4. **Phân biệt chữ hoa/thường?** (y/N): Case sensitive hay không
5. **Sử dụng Regular Expression?** (y/N): Dùng regex hay không

### 3. Chọn chế độ

- **1**: Chỉ tìm kiếm (không thay đổi file)
- **2**: Tìm và thay thế

### 4. Tìm và thay thế

Nếu chọn chế độ 2:
1. Nhập text thay thế
2. Xem preview kết quả
3. Xác nhận bằng `YES` để thực hiện

## Ví dụ

### 1. Tìm kiếm (không thay đổi)

```
Nhập đường dẫn thư mục: D:\my-react-project
Tìm kiếm trong tất cả thư mục con? (Y/n): Y
Chỉ xử lý file có đuôi (.txt .py .js - Enter để xử lý tất cả): .js .jsx
Nhập text cần tìm: useState
Phân biệt chữ hoa/thường? (y/N): N
Sử dụng Regular Expression? (y/N): N

===== CHẾ ĐỘ =====
1. Chỉ tìm kiếm (không thay đổi file)
2. Tìm và thay thế

Chọn chế độ (1-2): 1
```

**Kết quả:**
```
🔍 Đang tìm kiếm...

📄 src/components/Counter.jsx
   Line 5: import { useState, useEffect } from 'react';
   Line 12: const [count, setCount] = useState(0);

📄 src/components/Form.jsx
   Line 8: const [name, setName] = useState('');
   Line 9: const [email, setEmail] = useState('');

📄 src/pages/Dashboard.jsx
   Line 15: const [data, setData] = useState([]);

============================================================
✅ Tìm thấy 5 kết quả trong 3 file
============================================================
```

### 2. Thay thế đơn giản

```
Nhập text cần tìm: var 
Nhập text thay thế: let 
Chọn chế độ (1-2): 2

⚠️  CẢNH BÁO: Bạn sắp thay thế trong nhiều file!
   Tìm: 'var '
   Thay bằng: 'let '

Xác nhận thực hiện? (YES để xác nhận): YES
```

**Kết quả:**
```
🔄 Đang thay thế...

✓ src/old-script.js - Thay thế 5 lần
✓ src/legacy.js - Thay thế 3 lần
✓ src/utils.js - Thay thế 2 lần

============================================================
✅ Đã thay thế 10 lần trong 3 file
============================================================
```

### 3. Thay thế với Regular Expression

```
Nhập text cần tìm: function\s+(\w+)\s*\(
Nhập text thay thế: const $1 = (
Sử dụng Regular Expression? (y/N): y
Chọn chế độ (1-2): 2
```

**Kết quả:**
```
Tìm: function myFunction(
Thay bằng: const myFunction = (
```

## Regular Expression Examples

### Thay thế function declaration

**Tìm:**
```regex
function\s+(\w+)\s*\(
```

**Thay bằng:**
```
const $1 = (
```

**Kết quả:**
- `function myFunction(` → `const myFunction = (`

### Format số điện thoại

**Tìm:**
```regex
(\d{3})-(\d{3})-(\d{4})
```

**Thay bằng:**
```
($1) $2-$3
```

**Kết quả:**
- `123-456-7890` → `(123) 456-7890`

### Thay thế URL

**Tìm:**
```regex
http://old-domain\.com
```

**Thay bằng:**
```
https://new-domain.com
```

**Kết quả:**
- `http://old-domain.com` → `https://new-domain.com`

## Tips

### Tìm kiếm:
- **Preview trước**: Luôn dùng chế độ 1 (tìm kiếm) trước khi thay thế
- **Filter file**: Chỉ xử lý file cần thiết để tránh thay đổi nhầm
- **Case sensitive**: Dùng khi cần phân biệt chữ hoa/thường

### Thay thế:
- **Backup**: Luôn backup file trước khi thay thế
- **Test nhỏ**: Test với một vài file trước khi thay thế hàng loạt
- **Regex**: Học regex cơ bản để thay thế phức tạp hơn

### An toàn:
- **Xác nhận**: Luôn xác nhận bằng `YES` trước khi thay thế
- **Preview**: Xem kết quả trước khi xác nhận
- **Backup**: Backup file quan trọng trước khi thay thế

## Use case phổ biến

- **Refactor code**: Đổi tên biến, function
- **Cập nhật URL/domain**: Thay đổi domain trong nhiều file
- **Fix typo**: Sửa lỗi chính tả trong documentation
- **Thay đổi config**: Cập nhật đường dẫn config hàng loạt
- **Format code**: Chuẩn hóa format code
- **Migration**: Chuyển đổi code từ version cũ sang mới

## Lưu ý

- **Backup**: Luôn backup file trước khi thay thế
- **Preview**: Dùng chế độ tìm kiếm để preview trước
- **Regex**: Kiểm tra kỹ regex trước khi dùng
- **Case sensitive**: Cẩn thận với case sensitive/insensitive
- **File lớn**: File quá lớn có thể mất nhiều thời gian
- **Encoding**: Đảm bảo file là UTF-8 để tránh lỗi encoding

## Ví dụ thực tế

### Refactor: Đổi tên function

```
Tìm: function oldFunctionName
Thay bằng: function newFunctionName
Files: *.js
→ Thay thế trong tất cả file JavaScript
```

### Cập nhật domain

```
Tìm: http://old-domain.com
Thay bằng: https://new-domain.com
Files: *.html, *.php, *.js
→ Cập nhật domain trong toàn bộ website
```

### Fix typo

```
Tìm: recieve
Thay bằng: receive
Files: *.md, *.txt
→ Sửa lỗi chính tả trong documentation
```
