# Backup Folder - Sao lưu và nén thư mục

## Mô tả

Tool sao lưu và nén thư mục với timestamp tự động. Hỗ trợ nhiều định dạng nén và có thể loại trừ các file/thư mục không cần thiết.

## Tính năng

✅ Sao lưu thư mục thành file nén
✅ Tự động thêm timestamp vào tên file
✅ Hỗ trợ nhiều định dạng: ZIP, TAR, TAR.GZ, TAR.BZ2
✅ Backup có loại trừ (exclude pattern)
✅ Hiển thị tỷ lệ nén và dung lượng trước/sau
✅ Có thể chọn vị trí lưu file backup

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "backup-folder"
```

### Chạy trực tiếp

```bash
python tools/py/backup-folder/backup-folder.py
```

## Hướng dẫn chi tiết

### 1. Chọn thư mục cần backup

Nhập đường dẫn thư mục cần backup (vd: `D:\my-project`)

### 2. Chọn vị trí lưu backup

Nhập vị trí lưu backup (Enter để lưu tại thư mục hiện tại)

### 3. Chọn chế độ backup

- **1**: Backup toàn bộ (backup tất cả file và thư mục)
- **2**: Backup có loại trừ (exclude pattern)

### 4. Backup có loại trừ

Nếu chọn chế độ 2, nhập các pattern cần loại trừ (cách nhau bởi dấu phẩy):
- `node_modules,.git,__pycache__`
- `*.log,*.tmp,.vscode`

### 5. Kết quả

File backup được tạo với format: `[tên-thư-mục]_backup_YYYYMMDD_HHMMSS.zip`

## Ví dụ

### Backup toàn bộ

```
Nhập đường dẫn thư mục cần backup: D:\my-project
Nhập vị trí lưu backup (Enter để lưu tại thư mục hiện tại): D:\Backups

===== CHẾ ĐỘ BACKUP =====
1. Backup toàn bộ
2. Backup có loại trừ (exclude)

Chọn chế độ (1-2): 1

🚀 Bắt đầu backup...
📦 Đang copy file...
📦 Đang nén...

✅ Backup thành công!
   💾 File backup: D:\Backups\my-project_backup_20241029_153045.zip
   📊 Kích thước: 45.20 MB
```

### Backup có loại trừ

```
Nhập đường dẫn thư mục cần backup: D:\my-project
Nhập vị trí lưu backup: D:\Backups

Chọn chế độ (1-2): 2

Nhập các pattern cần loại trừ (cách nhau bởi dấu phẩy): node_modules,.git,__pycache__

🚫 Loại trừ: node_modules, .git, __pycache__

🚀 Bắt đầu backup...
📦 Đang copy file...
📦 Đang nén...

✅ Backup thành công!
   💾 File backup: D:\Backups\my-project_backup_20241029_153045.zip
   📊 Kích thước: 15.50 MB (giảm 65% so với backup toàn bộ)
```

## Định dạng nén

### ZIP
- **Ưu điểm**: Phổ biến nhất, hỗ trợ tốt trên mọi hệ điều hành
- **Nhược điểm**: Nén không tốt bằng TAR.GZ
- **Khuyến nghị**: Dùng cho Windows, chia sẻ file

### TAR.GZ
- **Ưu điểm**: Nén tốt hơn ZIP, phổ biến trên Linux
- **Nhược điểm**: Cần tool giải nén trên Windows
- **Khuyến nghị**: Dùng cho Linux, server

### TAR.BZ2
- **Ưu điểm**: Nén tốt nhất
- **Nhược điểm**: Chậm hơn, cần tool giải nén
- **Khuyến nghị**: Dùng khi cần giảm tối đa dung lượng

## Pattern loại trừ

Các pattern phổ biến để loại trừ:

- `node_modules` - Thư mục node_modules
- `.git` - Thư mục Git
- `__pycache__` - Cache Python
- `*.log` - File log
- `*.tmp` - File tạm
- `.vscode`, `.idea` - Thư mục IDE
- `venv`, `env` - Virtual environment
- `dist`, `build` - Thư mục build

**Ví dụ:**
```
node_modules,.git,__pycache__,.vscode,*.log,*.tmp
```

## Tips

### Khi nào dùng backup toàn bộ:
- Backup dự án nhỏ
- Cần backup tất cả mọi thứ
- Backup để archive

### Khi nào dùng backup có loại trừ:
- Backup dự án lớn (có node_modules, .git...)
- Giảm dung lượng backup
- Backup chỉ code, không backup dependencies

### Tối ưu:
- Loại trừ `node_modules`, `.git` để giảm 80-90% dung lượng
- Loại trừ file log, cache để giảm thêm dung lượng
- Dùng TAR.GZ hoặc TAR.BZ2 cho Linux

## Use case phổ biến

- Backup dự án trước khi refactor
- Tạo snapshot định kỳ
- Backup trước khi xóa file cũ
- Nén folder để gửi email/upload
- Backup trước khi deploy
- Archive dự án cũ

## Lưu ý

- **Dung lượng**: Đảm bảo có đủ dung lượng ổ đĩa
- **Thời gian**: Backup thư mục lớn có thể mất nhiều thời gian
- **Pattern**: Pattern loại trừ phân biệt chữ hoa/thường
- **Backup**: File backup sẽ ghi đè nếu tên file trùng (theo timestamp)
- **Đường dẫn**: Đường dẫn có thể chứa khoảng trắng
