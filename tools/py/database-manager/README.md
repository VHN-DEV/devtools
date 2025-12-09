# Database Manager - Quản lý Database MySQL (Bản beta)

Mô tả ngắn gọn: Tool Quản lý Database MySQL (Bản beta) với các tính năng backup/restore, chạy SQL queries, export/import, và quản lý kết nối database. Hỗ trợ XAMPP MySQL.

## Cách sử dụng

```bash
python tools/py/database-manager/database-manager.py
```

## Tính năng

### 1. Quản lý kết nối database
- Thêm/sửa/xóa kết nối database
- Test kết nối
- Đặt kết nối mặc định
- Hỗ trợ nhiều kết nối

### 2. Quản lý databases
- Liệt kê danh sách databases
- Xem danh sách tables trong database
- Xem cấu trúc table
- Export table ra file SQL

### 3. Backup database
- Backup toàn bộ database
- Backup từng table
- Tự động tạo timestamp trong tên file
- Lưu vào thư mục backup

### 4. Restore database
- Restore từ file SQL
- Tạo database mới nếu chưa có
- Cảnh báo trước khi ghi đè
- Hỗ trợ file backup lớn

### 5. Chạy SQL queries
- Chạy SQL queries trực tiếp
- Hiển thị kết quả
- Hỗ trợ queries nhiều dòng
- Xử lý lỗi SQL

## Cấu hình

Tool tự động tạo file `database_config.json` với các cài đặt mặc định:

```json
{
  "version": "1.0",
  "default_xampp_path": "C:\\xampp",
  "connections": [
    {
      "name": "XAMPP Local",
      "host": "localhost",
      "port": 3306,
      "user": "root",
      "password": "",
      "default_db": "",
      "xampp_path": "C:\\xampp"
    }
  ],
  "backup_folder": "database_backups",
  "default_connection": 0
}
```

## Yêu cầu

- MySQL đã cài đặt (XAMPP hoặc standalone)
- MySQL command line tools (mysql, mysqldump)
- Quyền truy cập database

## Ví dụ sử dụng

### Ví dụ 1: Thêm kết nối mới

```
1. Menu chính → 2 (Quản lý kết nối)
2. Chọn 'a' (Thêm kết nối)
3. Nhập thông tin:
   - Tên kết nối: Production Server
   - Host: 192.168.1.100
   - Port: 3306
   - Username: admin
   - Password: ****
4. Test kết nối để kiểm tra
```

### Ví dụ 2: Backup database

```
1. Menu chính → 1 (Quản lý databases)
2. Chọn database cần backup (ví dụ: 1)
3. Chọn 'b 1' (backup database số 1)
4. File backup: ~/database_backups/mydb_20250108_102300.sql
```

### Ví dụ 3: Restore database

```
1. Menu chính → 1 (Quản lý databases)
2. Chọn 'r' (Restore)
3. Chọn file SQL từ danh sách
4. Nhập tên database: mydb_restored
5. Xác nhận: YES
```

### Ví dụ 4: Chạy SQL query

```
1. Menu chính → 1 (Quản lý databases)
2. Chọn 'q' (Query)
3. Nhập tên database: mydb
4. Nhập SQL query:
   SELECT * FROM users LIMIT 10;
5. Xem kết quả
```

## Lưu ý quan trọng

⚠️ **Backup trước khi restore**: Restore sẽ ghi đè database hiện tại. Luôn backup trước khi restore.

⚠️ **Quyền truy cập**: Cần có quyền truy cập database để backup/restore/chạy queries.

⚠️ **File backup**: File backup được lưu trong thư mục `~/database_backups/` (có thể cấu hình).

⚠️ **XAMPP MySQL**: Tool sử dụng MySQL command line tools từ XAMPP. Đảm bảo XAMPP đã cài đặt.

## Cấu trúc thư mục backup

```
~/database_backups/
├── mydb_20250108_102300.sql
├── mydb_20250108_103000.sql
└── exports/
    ├── mydb_users_20250108_104500.sql
    └── mydb_products_20250108_105000.sql
```

## Use case phổ biến

- Backup database trước khi deploy
- Restore database từ backup
- Migrate database giữa các môi trường
- Chạy SQL queries nhanh
- Export table để backup
- Quản lý nhiều database connections

## Troubleshooting

### Lỗi: Không tìm thấy MySQL
- Kiểm tra đường dẫn XAMPP trong config
- Đảm bảo MySQL đã được cài đặt
- Kiểm tra file mysql.exe và mysqldump.exe

### Lỗi: Kết nối thất bại
- Kiểm tra MySQL service đang chạy
- Kiểm tra host, port, username, password
- Kiểm tra firewall và network

### Lỗi: Permission denied
- Kiểm tra quyền truy cập database
- Kiểm tra user có quyền SELECT, INSERT, UPDATE, DELETE
- Kiểm tra quyền tạo database (cho restore)

## Tài liệu tham khảo

- MySQL Documentation: https://dev.mysql.com/doc/
- mysqldump: https://dev.mysql.com/doc/refman/8.0/en/mysqldump.html
- XAMPP: https://www.apachefriends.org/

