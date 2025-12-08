# 🔌 SSH Manager Tool v2.0

## 📖 Giới Thiệu

Tool quản lý và kết nối nhanh đến các SSH server. 

**✨ Tính năng mới v2.0:**
- 💾 Lưu cấu hình vào file JSON
- ➕ Thêm server mới
- ❌ Xóa server
- ✏️ Sửa thông tin server
- 🔍 Xem file config
- 🔐 Bảo mật với SSH key

## 🚀 Cách Sử Dụng

### **Phương thức 1: Chạy từ Menu chính (Khuyến nghị)**

```bash
python __main__.py
# Hoặc
python -m menu
```

Sau đó chọn số **13** để chạy SSH Manager.

### **Phương thức 2: Chạy trực tiếp**

```bash
python tools/ssh-manager.py
```

## ⚙️ Quản Lý Server (v2.0)

### **📁 Cấu hình được lưu trong file:** `ssh_config.json`

**Vị trí:** `tools/ssh-manager/ssh_config.json` (trong cùng thư mục với tool)

Tool tự động tạo file này khi chạy lần đầu. Bạn có thể quản lý server bằng menu hoặc chỉnh sửa file JSON trực tiếp.

**Lợi ích của vị trí mới:**
- ✅ Config được tổ chức cùng tool
- ✅ Dễ backup/restore cả tool và config
- ✅ Không lộn xộn ở project root
- ✅ Vẫn tương thích với file config cũ (nếu tồn tại ở root)

### **1️⃣ Thêm Server Mới**

Trong menu SSH Manager, nhập **a** (add):

```
Chọn số để SSH hoặc lệnh: a

===== THEM SERVER MOI =====

Tên server (vd: My VPS): Production VPS
Username SSH: root
Host/IP: vps.mycompany.com
Port SSH (mặc định 22): 22
Mô tả (tùy chọn): Server production - quan trọng
Sử dụng SSH key? (y/N): y
💡 Key mặc định: C:\Users\Asus\.ssh\id_rsa
Đường dẫn SSH key (Enter = mặc định): [Enter]

✅ Đã thêm và lưu server mới!
```

**💡 Lưu ý:** Tool tự động phát hiện SSH key mặc định tại `C:\Users\Asus\.ssh\id_rsa`. Chỉ cần nhấn Enter để sử dụng!

### **2️⃣ Xóa Server**

Trong menu SSH Manager, nhập **d** (delete):

```
Chọn số để SSH hoặc lệnh: d

===== XOA SERVER =====

1. [🔑 Key] Production VPS - Server production
   root@vps.mycompany.com:22
2. [🔐 Pass] Dev Server
   dev@192.168.1.50:2222

0. Hủy bỏ

Chọn server cần xóa (số): 2

⚠️  BẠN SẮP XÓA SERVER: Dev Server
Xác nhận xóa? (YES để xác nhận): YES

✅ Đã xóa server: Dev Server
```

### **3️⃣ Sửa Server**

Trong menu SSH Manager, nhập **e** (edit):

```
Chọn số để SSH hoặc lệnh: e

===== CHINH SUA SERVER =====

1. [🔑 Key] Production VPS
   root@vps.mycompany.com:22

Chọn server cần sửa (số): 1

📝 Đang sửa: Production VPS
(Nhấn Enter để giữ nguyên giá trị cũ)

Tên [Production VPS]: Production VPS v2
User [root]: admin
Host [vps.mycompany.com]: [Enter]
Port [22]: [Enter]
Mô tả [Server production]: Updated server
SSH Key hiện tại: C:\Users\Me\.ssh\id_rsa
Thay đổi SSH key? (y/N): n

✅ Đã lưu thay đổi!
```

### **4️⃣ Xem File Config**

Trong menu SSH Manager, nhập **v** (view):

```
Chọn số để SSH hoặc lệnh: v

===== FILE CONFIG =====

Đường dẫn: D:\DevTools\tool\ssh-manager\ssh_config.json

Nội dung:
------------------------------------------------------------
{
  "version": "1.0",
  "servers": [
    {
      "name": "Production VPS",
      "user": "root",
      "host": "vps.mycompany.com",
      "port": 22,
      "password": null,
      "ssh_key": "C:\\Users\\Me\\.ssh\\id_rsa",
      "description": "Server production"
    }
  ]
}
------------------------------------------------------------
```

### **5️⃣ Chỉnh Sửa File JSON Trực Tiếp**

Bạn có thể mở file `tools/ssh-manager/ssh_config.json` và chỉnh sửa:

**Mẫu file:** Xem `ssh_config.example.json` trong cùng thư mục

```json
{
  "version": "1.0",
  "servers": [
    {
      "name": "Production VPS",
      "user": "root",
      "host": "vps.mycompany.com",
      "port": 22,
      "password": null,
      "ssh_key": "C:\\Users\\You\\.ssh\\id_rsa",
      "description": "Server production - quan trọng"
    },
    {
      "name": "Dev Server",
      "user": "developer",
      "host": "192.168.1.50",
      "port": 2222,
      "password": null,
      "ssh_key": null,
      "description": "Server development"
    }
  ]
}
```

## 🎯 Tính Năng

### **Quản lý cấu hình:**
- ✅ Lưu cấu hình vào file JSON (`ssh_config.json`)
- ✅ Thêm server mới (lưu vĩnh viễn)
- ✅ Xóa server với xác nhận
- ✅ Sửa thông tin server
- ✅ Xem và kiểm tra file config

### **Kết nối SSH:**
- ✅ Kết nối nhanh bằng SSH key
- ✅ Kết nối với password (nhập thủ công)
- ✅ Hiển thị phương thức xác thực rõ ràng
- ✅ Validate SSH key trước khi kết nối
- ✅ Hỗ trợ custom port

### **Trải nghiệm:**
- ✅ Menu thân thiện tiếng Việt
- ✅ Hướng dẫn chi tiết trong tool
- ✅ Tìm kiếm: `s ssh` trong menu chính
- ✅ Icon phân biệt Key/Password

## 🔐 Bảo Mật

### ⚠️ **QUAN TRỌNG:**

1. **Không lưu password trong code**
2. **Sử dụng SSH key thay vì password**
3. **Bảo vệ SSH key:**
   ```bash
   # Linux/Mac
   chmod 600 ~/.ssh/id_rsa
   ```
4. **Thêm vào .gitignore nếu chứa thông tin nhạy cảm:**
   ```bash
   tools/ssh-manager.py
   ```

## 🛠️ Yêu Cầu

- **Windows:** OpenSSH Client (Windows 10/11 có sẵn) hoặc Git Bash
- **Linux/Mac:** SSH có sẵn

Kiểm tra:
```bash
ssh -V
```

## 💡 Menu Commands

Khi chạy tool, bạn có thể:

- Nhập **số** (1-n) - Kết nối đến server
- Nhập **a** - Thêm server mới (tạm thời)
- Nhập **h** - Xem hướng dẫn chi tiết
- Nhập **0** - Quay lại menu chính

## 🔍 Tìm Kiếm Tool

Trong menu chính, bạn có thể tìm SSH tool bằng:

```
s ssh          # Tìm theo keyword "ssh"
s server       # Tìm theo keyword "server"
s ket noi      # Tìm theo keyword "ket noi"
s remote       # Tìm theo keyword "remote"
```

## 📝 Lưu Ý

- ✅ **v2.2:** File config giờ lưu trong `tools/ssh-manager/ssh_config.json`
- ✅ **v2.0:** Tất cả thay đổi được lưu vĩnh viễn vào file config
- ⚠️ Nên thêm `tools/ssh-manager/ssh_config.json` vào `.gitignore` nếu chứa thông tin nhạy cảm
- 💡 Backup file config trước khi chỉnh sửa trực tiếp
- 🔐 Không lưu password trong config (để null)
- 🔄 Tool vẫn tìm file config cũ ở root nếu tồn tại (backward compatible)

## 🚀 Use Cases

1. **DevOps:** Quản lý nhiều server (dev/staging/prod)
2. **Web Developer:** Kết nối VPS/hosting nhanh
3. **Sysadmin:** Quản lý danh sách server tập trung
4. **Team work:** Share config (không share password!)

---

**Happy SSHing! 🔌**

_DevTools v2.1 - SSH Manager Tool_

