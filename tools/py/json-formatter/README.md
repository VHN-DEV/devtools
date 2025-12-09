# JSON Formatter - Định dạng và xử lý JSON

## Mô tả

Tool đa năng để định dạng (format), kiểm tra (validate), nén (minify), và sửa lỗi JSON. Hỗ trợ xử lý một file hoặc hàng loạt file JSON.

## Tính năng

✅ Format JSON (làm đẹp, indent)
✅ Validate JSON (kiểm tra lỗi)
✅ Minify JSON (giảm kích thước)
✅ Sửa lỗi JSON thường gặp
✅ Format hàng loạt nhiều file
✅ Sắp xếp keys theo alphabet
✅ Escape/unescape Unicode

## Yêu cầu

Không cần cài đặt thư viện bên ngoài (sử dụng thư viện chuẩn của Python).

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "json-formatter"
```

### Chạy trực tiếp

```bash
python tools/py/json-formatter/json-formatter.py
```

## Hướng dẫn chi tiết

### 1. Format JSON (Làm đẹp)

1. Chọn chức năng: Format JSON
2. Nhập đường dẫn file JSON
3. Chọn số spaces cho mỗi level (2 hoặc 4)
4. Chọn có sắp xếp keys theo alphabet không (y/N)
5. Chọn có escape Unicode không (mặc định: giữ nguyên)
6. Chọn vị trí lưu file output (hoặc ghi đè file gốc)

**Ví dụ:**

**Input:**
```json
{"a":1,"b":2,"c":3}
```

**Output (indent 2, sort keys):**
```json
{
  "a": 1,
  "b": 2,
  "c": 3
}
```

### 2. Validate JSON (Kiểm tra lỗi)

1. Chọn chức năng: Validate JSON
2. Nhập đường dẫn file JSON
3. Tool kiểm tra tính hợp lệ của JSON
4. Hiển thị thông tin:
   - Loại dữ liệu (Object, Array, String, Number...)
   - Số keys/phần tử
   - Lỗi cụ thể nếu có (nếu có lỗi)

**Ví dụ:**
```
Input: config.json
Status: ✅ Hợp lệ
Type: Object
Keys: 15
Size: 2.5 KB
```

### 3. Minify JSON (Giảm kích thước)

1. Chọn chức năng: Minify JSON
2. Nhập đường dẫn file JSON
3. Tool xóa tất cả spaces, xuống dòng không cần thiết
4. Chọn vị trí lưu file output

**Ví dụ:**

**Input:**
```json
{
  "name": "John",
  "age": 30,
  "city": "New York"
}
```

**Output:**
```json
{"name":"John","age":30,"city":"New York"}
```

**Lưu ý**: Minify phù hợp cho production (giảm bandwidth) nhưng khó đọc.

### 4. Sửa lỗi JSON thường gặp

1. Chọn chức năng: Sửa lỗi JSON
2. Nhập đường dẫn file JSON có lỗi
3. Tool tự động sửa một số lỗi:
   - **Trailing commas**: Dấu phẩy cuối `{ "a": 1, }` → `{ "a": 1 }`
   - **Missing quotes**: `{ a: 1 }` → `{ "a": 1 }`
   - **Invalid escape**: Tự động escape ký tự đặc biệt
4. Chọn vị trí lưu file đã sửa

**Ví dụ:**

**Input (có lỗi):**
```json
{
  "name": "John",
  "age": 30,
  "city": "New York",
}
```

**Output (đã sửa):**
```json
{
  "name": "John",
  "age": 30,
  "city": "New York"
}
```

### 5. Format hàng loạt (Batch)

1. Chọn chức năng: Format nhiều file JSON
2. Nhập thư mục chứa file JSON
3. Tool tự động tìm tất cả file `.json`
4. Format tất cả cùng lúc
5. Hiển thị báo cáo số file thành công/lỗi

**Ví dụ:**
```
Thư mục: ./configs
Tìm thấy: 25 file JSON
Format thành công: 24/25
Lỗi: 1 file (invalid.json)
```

## Lỗi JSON thường gặp

### 1. Trailing Comma
**Lỗi:**
```json
{
  "a": 1,
  "b": 2,  // ← Dấu phẩy cuối không hợp lệ
}
```

**Sửa:**
```json
{
  "a": 1,
  "b": 2
}
```

### 2. Missing Quotes
**Lỗi:**
```json
{
  name: "John",  // ← Thiếu dấu ngoặc kép
  age: 30
}
```

**Sửa:**
```json
{
  "name": "John",
  "age": 30
}
```

### 3. Invalid Escape
**Lỗi:**
```json
{
  "path": "C:\path\to\file"  // ← Escape không hợp lệ
}
```

**Sửa:**
```json
{
  "path": "C:\\path\\to\\file"
}
```

### 4. Single Quotes
**Lỗi:**
```json
{
  'name': 'John'  // ← JSON không hỗ trợ single quotes
}
```

**Sửa:**
```json
{
  "name": "John"
}
```

### 5. Comments
**Lỗi:**
```json
{
  // Comment không hợp lệ
  "name": "John"
}
```

**Lưu ý**: JSON không hỗ trợ comments. Cần xóa comments trước khi validate.

## Tips

### Format JSON:
- **Indent 2 spaces**: Phù hợp cho hầu hết trường hợp
- **Indent 4 spaces**: Phù hợp cho file lớn, phức tạp
- **Sort keys**: Giúp dễ so sánh giữa các file, dễ đọc
- **Escape Unicode**: Giữ nguyên để dễ đọc, escape khi cần

### Minify JSON:
- Giảm kích thước file đáng kể (30-50%)
- Phù hợp cho production (giảm bandwidth)
- Không phù hợp cho development (khó đọc, khó debug)

### Validate JSON:
- Luôn validate trước khi commit code
- Validate trước khi parse JSON trong code
- Kiểm tra file config JSON trước khi sử dụng

### Sửa lỗi:
- Tool tự động sửa một số lỗi cơ bản
- Không sửa được tất cả lỗi (cần kiểm tra thủ công)
- Luôn backup file gốc trước khi sửa

## Use case phổ biến

- Format file config JSON cho dễ đọc
- Validate JSON trước khi commit code
- Minify JSON cho production (giảm bandwidth)
- Sửa lỗi JSON từ API response
- Format hàng loạt file JSON trong dự án
- Chuẩn hóa format JSON trong team

## Ví dụ thực tế

### Format file config

```
Input: config.json (minified, khó đọc)
→ Format với indent 2, sort keys
→ Output: config.json (dễ đọc, có cấu trúc)
```

### Validate API response

```
Input: api_response.json
→ Validate
→ Status: ✅ Hợp lệ
→ Type: Object
→ Keys: 8
```

### Minify cho production

```
Input: data.json (10 KB, formatted)
→ Minify
→ Output: data.min.json (6 KB)
→ Giảm 40% kích thước
```

## Lưu ý

- **Backup**: Luôn backup file gốc trước khi format/sửa
- **Comments**: JSON không hỗ trợ comments (cần xóa trước)
- **Encoding**: Đảm bảo file JSON là UTF-8
- **Large files**: File quá lớn có thể mất nhiều thời gian
- **Validation**: Không validate được syntax phức tạp (cần tool chuyên dụng)

