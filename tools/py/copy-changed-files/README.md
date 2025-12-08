# Copy Changed Files - Sao chép file thay đổi theo Git

## Mô tả

Tool sao chép file thay đổi từ Git repository theo commit range. Giữ nguyên cấu trúc thư mục, bỏ qua file đã xóa, tạo danh sách file đã copy, và verify commit ID trước khi thực hiện.

## Tính năng

✅ Copy file theo commit range
✅ Giữ nguyên cấu trúc thư mục
✅ Bỏ qua file đã xóa
✅ Tạo danh sách file đã copy
✅ Verify commit ID trước khi thực hiện
✅ Tự động tạo thư mục output
✅ Cấu hình vị trí thư mục output (lưu trong config)
✅ Hiển thị tiến trình chi tiết
✅ Liệt kê dự án trong htdocs và cho phép chọn
✅ Cho phép nhập đường dẫn dự án tùy chỉnh

## Yêu cầu

- **Git repository**: Thư mục phải là Git repository
- **Git installed**: Cần cài đặt Git trên hệ thống

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "copy-changed-files"
```

### Chạy trực tiếp

```bash
python tools/py/copy-changed-files/copy-changed-files.py
```

## Hướng dẫn chi tiết

### 1. Chọn dự án hoặc nhập đường dẫn

Tool sẽ tự động tìm và liệt kê các dự án trong thư mục htdocs (`C:\xampp\htdocs`). Bạn có thể:

**Cách 1: Chọn dự án từ danh sách**
- Nhập số thứ tự của dự án (ví dụ: `1`, `2`, `3`)
- Tool sẽ tự động lấy đường dẫn đầy đủ

**Cách 2: Nhập đường dẫn tùy chỉnh**
- Nhập đường dẫn đầy đủ đến dự án (ví dụ: `C:\xampp\htdocs\my-ecommerce`)
- Hoặc đường dẫn bất kỳ đến Git repository

**Lưu ý:**
- Tool sẽ hiển thị icon `✓` cho dự án là Git repository
- Tool sẽ hiển thị icon `⚠️` cho dự án không phải Git repository
- Nếu không tìm thấy htdocs hoặc không có dự án, tool sẽ yêu cầu nhập đường dẫn thủ công

### 2. Nhập commit ID

1. **Commit ID bắt đầu**: Nhập commit hash (vd: `9d172f6` hoặc `9d172f6a1b2c3d4e5f6...`)
2. **Commit ID kết thúc**: Nhập commit hash hoặc Enter để dùng `HEAD` (commit mới nhất)

### 3. Verify commit ID

Tool sẽ kiểm tra commit ID có hợp lệ không trước khi thực hiện.

### 4. Lấy danh sách file thay đổi

Tool sẽ:
1. Lấy danh sách file thay đổi từ Git
2. Hiển thị số lượng file tìm thấy
3. Hiển thị danh sách file (preview)

### 5. Cấu hình thư mục output

Tool sẽ hỏi bạn về vị trí thư mục output:
- **Lần đầu chạy**: Tool sẽ hỏi bạn nhập đường dẫn thư mục output
- **Các lần sau**: Tool sẽ sử dụng đường dẫn đã lưu trong config, nhưng bạn có thể thay đổi
- **Lưu config**: Bạn có thể chọn lưu đường dẫn làm mặc định cho các lần sau

**Ví dụ đường dẫn:**
- `changed-files-export` - Thư mục trong thư mục hiện tại (mặc định)
- `C:\exports\changed-files` - Đường dẫn tuyệt đối
- `./exports` - Thư mục exports trong thư mục hiện tại

**File config:** `copy-changed-files_config.json` (tự động tạo trong thư mục tool)

### 6. Copy file

Tool sẽ:
1. Tạo thư mục output theo cấu hình
2. Copy file và giữ nguyên cấu trúc thư mục
3. Tạo file danh sách: `danh-sach-file-thay-doi.txt`
4. Hiển thị tiến trình và kết quả

## Ví dụ

### Copy file từ commit cụ thể đến HEAD

```
============================================================
  DANH SACH DU AN TRONG HTDOCS
============================================================
📁 Đường dẫn: C:\xampp\htdocs

  1. ✓ my-ecommerce
  2. ✓ my-blog
  3. ⚠️ test-project

------------------------------------------------------------
HƯỚNG DẪN:
  [số]      - Chọn dự án theo số thứ tự
  [đường dẫn] - Nhập đường dẫn dự án tùy chỉnh
============================================================

Chọn dự án hoặc nhập đường dẫn: 1
✓ Đã chọn dự án: my-ecommerce
✓ Dự án hợp lệ: C:\xampp\htdocs\my-ecommerce

Nhập commit ID bắt đầu (vd: 9d172f6): 9d172f6
Nhập commit ID kết thúc (Enter = HEAD): [Enter]

🔍 Kiểm tra commit ID...
✓ Commit ID hợp lệ!

📂 Đang lấy danh sách file thay đổi từ commit 9d172f6 đến HEAD...
✓ Tìm thấy 15 file đã thay đổi

📋 Danh sách file (preview):
   - src/components/Header.jsx
   - src/styles/main.css
   - public/index.html
   - api/products.php
   ... (11 file khác)

🚀 Bắt đầu copy file...

📋 Đang copy file...
✓ [OK] src/components/Header.jsx
✓ [OK] src/styles/main.css
✓ [OK] public/index.html
✓ [OK] api/products.php
✓ [OK] config/database.php
✓ [OK] assets/images/logo.png
... (9 file khác)

===================================================
✓ Hoàn tất!
- Đã copy: 15 file
- Bỏ qua: 0 file
- Thư mục xuất: changed-files-export
- Danh sách file: changed-files-export/danh-sach-file-thay-doi.txt

🚀 Bạn có thể upload toàn bộ thư mục 'changed-files-export' lên server bằng FileZilla!
===================================================
```

### Copy file giữa 2 commit

```
Nhập commit ID bắt đầu: abc1234
Nhập commit ID kết thúc: def5678

🔍 Kiểm tra commit ID...
✓ Commit ID hợp lệ!

📂 Đang lấy danh sách file thay đổi từ commit abc1234 đến def5678...
✓ Tìm thấy 8 file đã thay đổi

✅ Hoàn thành! Đã copy 8 file.
```

## Cấu trúc output

Sau khi copy, thư mục `changed-files-export` sẽ có cấu trúc:

```
changed-files-export/
├── src/
│   ├── components/
│   │   └── Header.jsx
│   └── styles/
│       └── main.css
├── public/
│   └── index.html
├── api/
│   └── products.php
├── config/
│   └── database.php
└── danh-sach-file-thay-doi.txt
```

File `danh-sach-file-thay-doi.txt` chứa danh sách đầy đủ các file đã copy.

## Tips

### Commit ID:
- **Short hash**: Có thể dùng hash ngắn (7 ký tự đầu)
- **Full hash**: Có thể dùng hash đầy đủ
- **HEAD**: Dùng để chỉ commit mới nhất

### Verify:
- **Kiểm tra trước**: Tool tự động kiểm tra commit ID trước khi thực hiện
- **Lỗi**: Nếu commit ID không hợp lệ, tool sẽ báo lỗi và dừng

### Upload:
- **FileZilla**: Upload toàn bộ thư mục `changed-files-export` lên server
- **FTP**: Sử dụng FTP client để upload
- **SCP**: Sử dụng SCP để upload (Linux)

## Use case phổ biến

- Upload file thay đổi lên shared hosting (không có Git)
- Tạo package update cho khách hàng
- Kiểm tra file đã sửa trước khi deploy
- Backup file quan trọng đã thay đổi
- Deploy từng phần (chỉ deploy file thay đổi)

## Cấu hình

### File config

Tool tự động tạo file `copy-changed-files_config.json` trong thư mục tool để lưu cấu hình.

**Cấu trúc file config:**
```json
{
  "output_folder": "changed-files-export"
}
```

**Cách cấu hình:**

1. **Tự động**: Khi chạy tool lần đầu, tool sẽ hỏi và cho phép lưu đường dẫn
2. **Thủ công**: Tạo file `copy-changed-files_config.json` dựa trên `copy-changed-files_config.example.json`

**Ví dụ cấu hình:**
```json
{
  "output_folder": "C:\\exports\\changed-files"
}
```

**Lưu ý:**
- Đường dẫn có thể là tuyệt đối hoặc tương đối
- Nếu không có config, tool sẽ hỏi bạn mỗi lần chạy
- Bạn có thể thay đổi đường dẫn mỗi lần chạy mà không cần sửa file config

## Lưu ý

- **Git repository**: Thư mục phải là Git repository
- **Commit ID**: Commit ID phải hợp lệ và tồn tại
- **File đã xóa**: File đã xóa sẽ bị bỏ qua
- **Cấu trúc**: Cấu trúc thư mục được giữ nguyên
- **Overwrite**: File đã tồn tại sẽ bị ghi đè
- **Config**: File config được tạo tự động, bạn có thể chỉnh sửa thủ công

## Ví dụ thực tế

### Deploy lên shared hosting

```
Project: my-ecommerce (Git repo)
Commit từ: abc1234
Commit đến: HEAD
→ Copy 15 file thay đổi
→ Upload lên server bằng FileZilla
→ Deploy thành công!
```

### Tạo package update

```
Project: my-app (Git repo)
Commit từ: version-1.0
Commit đến: version-1.1
→ Copy 25 file thay đổi
→ Tạo package update
→ Gửi cho khách hàng
```
