# XAMPP Project Manager - Quản lý dự án XAMPP

## Mô tả

Tool quản lý và cài đặt dự án trên XAMPP Windows. Quản lý dự án trong thư mục htdocs, quản lý hosts file, chuyển đổi phiên bản PHP, restart XAMPP và mở dự án trong VSCode/Cursor.

## Tính năng

✅ Quản lý dự án trong thư mục htdocs
✅ Quản lý hosts file (thêm/xóa/sửa)
✅ Chuyển đổi phiên bản PHP
✅ Restart XAMPP và Apache
✅ Mở dự án trong VSCode hoặc Cursor
✅ Clone dự án từ Git repository
✅ Đổi tên dự án
✅ Xóa dự án

## Yêu cầu

- **Windows OS**: Tool chỉ hoạt động trên Windows
- **XAMPP**: Đã cài đặt XAMPP
- **Git**: (Tùy chọn) Để clone dự án
- **VSCode hoặc Cursor**: (Tùy chọn) Để mở dự án

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "xampp-project-manager"
```

### Chạy trực tiếp

```bash
python tools/py/xampp-project-manager/xampp-project-manager.py
```

## Cấu hình ban đầu

### 1. Vào Settings

Chạy tool lần đầu và chọn **`s`** để vào Settings.

### 2. Cấu hình các đường dẫn

- **XAMPP path**: Đường dẫn thư mục cài XAMPP (vd: `C:\xampp`)
- **htdocs path**: Đường dẫn thư mục htdocs (vd: `C:\xampp\htdocs`)
- **Hosts file**: Đường dẫn file hosts (mặc định: `C:\Windows\System32\drivers\etc\hosts`)
- **Apache path**: Đường dẫn Apache httpd.exe (vd: `C:\xampp\apache\bin\httpd.exe`)
- **Default editor**: Chọn editor mặc định (`code` hoặc `cursor`)

### 3. Lưu cấu hình

Cấu hình được lưu trong file `xampp_config.json` trong thư mục tool.

## Các lệnh quản lý dự án

### Mở dự án

- **`[số]`**: Mở dự án theo số thứ tự bằng editor mặc định
  - Ví dụ: `1` để mở dự án đầu tiên

- **`o [số]`**: Mở dự án và chọn editor
  - Ví dụ: `o 1` để mở dự án đầu tiên và chọn editor

### Clone dự án mới

- **`c`**: Clone dự án từ Git repository
  - Nhập Git URL (vd: `https://github.com/user/repo.git`)
  - Nhập tên dự án
  - Tool tự động clone vào thư mục htdocs

### Xóa dự án

- **`d [số]`**: Xóa dự án (cần xác nhận YES)
  - Ví dụ: `d 1` để xóa dự án đầu tiên
  - **Cảnh báo**: Xóa vĩnh viễn, không thể hoàn tác!

### Đổi tên dự án

- **`r [số]`**: Đổi tên dự án
  - Ví dụ: `r 1` để đổi tên dự án đầu tiên
  - Nhập tên mới

## Quản lý hosts

### Xem danh sách hosts

- **`h`**: Liệt kê tất cả host entries trong file hosts

### Thêm host mới

- **`ha`**: Thêm entry mới vào hosts file
  - Nhập domain (vd: `mysite.local`)
  - Nhập IP (mặc định: `127.0.0.1`)
  - **Lưu ý**: Cần chạy với quyền Administrator

### Xóa host

- **`hd [domain]`**: Xóa host entry
  - Ví dụ: `hd mysite.local`
  - **Lưu ý**: Cần chạy với quyền Administrator

### Sửa host

- **`he [domain]`**: Sửa host entry
  - Ví dụ: `he mysite.local`
  - Có thể thay đổi domain hoặc IP
  - **Lưu ý**: Cần chạy với quyền Administrator

## Quản lý PHP

### Chuyển đổi phiên bản PHP

- **`php`**: Xem và chuyển đổi phiên bản PHP
  - Hiển thị danh sách PHP version có sẵn trong XAMPP
  - Chọn version để chuyển đổi
  - **Lưu ý**: Cần chỉnh sửa `httpd.conf` thủ công theo hướng dẫn

## Quản lý XAMPP

### Restart XAMPP

- **`rx`**: Restart XAMPP
  - Mở XAMPP Control Panel
  - Tự động restart Apache và MySQL từ Control Panel

### Restart Apache

- **`ra`**: Restart Apache
  - Tự động restart Apache service
  - Sử dụng `apache_start.bat` và `apache_stop.bat`

## Cài đặt

### Vào menu Settings

- **`s`**: Vào menu Settings
  - Cấu hình các đường dẫn XAMPP, htdocs, hosts, Apache
  - Chọn editor mặc định (VSCode hoặc Cursor)

## Ví dụ sử dụng

### 1. Mở dự án

```
> 1              # Mở dự án đầu tiên bằng editor mặc định
> o 1            # Mở dự án đầu tiên và chọn editor
```

### 2. Clone dự án mới

```
> c
> Git URL: https://github.com/user/repo.git
> Tên dự án: mynewproject
→ Clone thành công vào C:\xampp\htdocs\mynewproject
```

### 3. Thêm host cho dự án

```
> ha
> Domain: myproject.local
> IP: 127.0.0.1
→ Thêm thành công vào hosts file
```

### 4. Đổi tên dự án

```
> r 1
> Tên mới: newprojectname
→ Đổi tên thành công
```

### 5. Xóa dự án

```
> d 1
> Xác nhận: YES
→ Xóa thành công
```

## Lưu ý quan trọng

### Quyền Administrator

- **Cần Admin để chỉnh sửa hosts file**: Chạy tool với quyền Administrator
- **Không cần Admin để quản lý dự án**: Quản lý dự án trong htdocs không cần Admin

### Đường dẫn

- Đảm bảo các đường dẫn cấu hình đúng và tồn tại
- Tool sẽ tự động tạo config file nếu chưa có
- Kiểm tra đường dẫn trước khi lưu settings

### Backup

- **Luôn backup hosts file** trước khi chỉnh sửa
- **Backup dự án** trước khi xóa
- Tool tự động backup hosts file trước khi chỉnh sửa

### Git

- Cần cài Git nếu muốn clone dự án
- Git phải có trong PATH
- Kiểm tra Git: `git --version`

### Editor

- VSCode/Cursor phải có trong PATH
- Hoặc cài đặt từ Microsoft Store/Website chính thức
- Kiểm tra editor: `code --version` hoặc `cursor --version`

## Tips

- **Sử dụng tab**: Sử dụng tab để autocomplete khi nhập đường dẫn
- **Kiểm tra đường dẫn**: Luôn kiểm tra đường dẫn trước khi lưu settings
- **Xem hosts**: Sử dụng `h` để xem hosts trước khi thêm/sửa/xóa
- **Backup hosts**: Backup hosts file thường xuyên
- **Editor mặc định**: Đặt editor mặc định để mở nhanh hơn

## Use case phổ biến

- Quản lý nhiều dự án trong XAMPP
- Thêm/xóa hosts cho các dự án local
- Clone dự án mới từ Git
- Mở nhanh dự án trong editor
- Chuyển đổi phiên bản PHP
- Restart XAMPP nhanh chóng

## Troubleshooting

### Lỗi: "Permission denied" khi chỉnh sửa hosts

**Giải pháp**: Chạy tool với quyền Administrator (Right-click → Run as administrator)

### Lỗi: "Editor not found"

**Giải pháp**: 
- Kiểm tra editor có trong PATH: `code --version`
- Hoặc cài đặt editor và thêm vào PATH

### Lỗi: "XAMPP path not found"

**Giải pháp**: 
- Vào Settings (`s`) và cấu hình lại đường dẫn XAMPP
- Đảm bảo đường dẫn đúng và tồn tại

### Lỗi: "Git not found"

**Giải pháp**: 
- Cài đặt Git từ https://git-scm.com/
- Đảm bảo Git có trong PATH

