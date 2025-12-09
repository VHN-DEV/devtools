# 🚀 Hướng dẫn di chuyển dự án sang máy khác

## 📋 Checklist khi di chuyển dự án

### 1. ✅ Yêu cầu hệ thống

- **Python 3.7+** đã được cài đặt
- **pip** đã được cài đặt
- **Git** (tùy chọn, chỉ cần cho một số tool như `copy-changed-files`)
- Hệ điều hành: **Windows, Linux, macOS** đều hỗ trợ

### 2. ✅ Các bước cài đặt

#### Bước 1: Copy dự án sang máy mới

```bash
# Cách 1: Clone từ Git (khuyến nghị)
git clone https://github.com/VHN-DEV/DevTools.git
cd DevTools

# Cách 2: Copy thư mục dự án
# Copy toàn bộ thư mục devtools sang máy mới
```

#### Bước 2: Cài đặt dependencies

```bash
# Vào thư mục dự án
cd devtools

# Cài đặt tất cả thư viện Python cần thiết
pip install -r requirements.txt

# Hoặc cài đặt như một package (khuyến nghị)
pip install -e .
```

#### Bước 3: Kiểm tra cài đặt

```bash
# Kiểm tra Python
python --version

# Kiểm tra thư viện đã cài
python -c "import PIL, chardet; print('✅ Cài đặt thành công!')"

# Chạy thử menu
python .
# Hoặc nếu đã cài bằng pip install -e .
devtools
```

---

## 🔧 Cấu hình lại các đường dẫn

### 1. File `scripts/devtools.bat` (nếu dùng Windows)

**File này đã được cập nhật để tự động phát hiện đường dẫn**, không cần hardcode nữa!

Script sẽ tự động tìm project theo thứ tự ưu tiên:

1. **Biến môi trường `DEVTOOLS_DIR`** (nếu có)
2. **File .bat nằm trong project** (`scripts/devtools.bat`)
3. **Tìm từ thư mục hiện tại lên trên** (tự động phát hiện)
4. **Thử tìm trong thư mục scripts** (nếu file .bat được copy vào PATH)

**Cách sử dụng:**

**Cách 1: Chạy từ thư mục project (khuyến nghị)**
```batch
cd C:\duong\dan\toi\devtools
scripts\devtools.bat
```

**Cách 2: Set biến môi trường (nếu copy vào PATH)**
```batch
# Set biến môi trường một lần
setx DEVTOOLS_DIR "C:\duong\dan\toi\devtools"

# Sau đó mở cmd mới và chạy từ bất kỳ đâu
devtools
```

**Cách 3: Chạy trực tiếp bằng Python (đơn giản nhất)**
```batch
cd C:\duong\dan\toi\devtools
python .
```

**Lưu ý:** 
- ✅ **Không cần sửa code** - script tự động phát hiện
- ✅ Nếu cài bằng `pip install -e .` thì không cần dùng file này
- ✅ Script tự động tìm project root bằng cách tìm file `__main__.py`

### 2. Cấu hình các tool có file config

Một số tool sẽ tự tạo file config khi chạy lần đầu. Bạn có thể cấu hình lại sau:

#### a) SSH Manager (`tools/py/ssh-manager/ssh_config.json`)

```json
{
  "servers": [
    {
      "name": "My Server",
      "host": "192.168.1.100",
      "port": 22,
      "user": "your_username",
      "key_path": "C:\\Users\\YourName\\.ssh\\id_rsa",
      "password": ""
    }
  ]
}
```

**Cần sửa:**
- `key_path`: Đường dẫn SSH key trên máy mới
- `host`, `user`: Thông tin server của bạn

#### b) Database Manager (`tools/py/database-manager/database_config.json`)

```json
{
  "default_xampp_path": "C:\\xampp",
  "connections": [
    {
      "name": "XAMPP Local",
      "host": "localhost",
      "port": 3306,
      "user": "root",
      "password": "",
      "xampp_path": "C:\\xampp"
    }
  ]
}
```

**Cần sửa:**
- `default_xampp_path`: Đường dẫn XAMPP trên máy mới (nếu có)
- Thông tin database connection

#### c) XAMPP Project Manager (`tools/py/xampp-project-manager/xampp_config.json`)

```json
{
  "xampp_path": "C:\\xampp",
  "htdocs_path": "C:\\xampp\\htdocs",
  "hosts_file": "C:\\Windows\\System32\\drivers\\etc\\hosts"
}
```

**Cần sửa:**
- `xampp_path`: Đường dẫn XAMPP trên máy mới
- `htdocs_path`: Đường dẫn htdocs

#### d) Website Performance Tools

- `tools/py/website-performance-checker/performance_config.json`
- `tools/py/website-performance-optimizer/optimizer_config.json`

**Cần sửa:**
- `default_htdocs_path`: Đường dẫn htdocs trên máy mới

---

## 🎯 Cài đặt các công cụ bổ sung (tùy chọn)

Một số tool cần cài đặt thêm phần mềm bên ngoài:

### 1. FFmpeg (cho video-converter)

**Windows:**
```bash
# Tải từ: https://ffmpeg.org/download.html
# Giải nén vào: C:\ffmpeg
# Thêm C:\ffmpeg\bin vào PATH
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 2. Poppler (cho pdf-tools)

**Windows:**
```bash
# Tải từ: https://github.com/oschwartz10612/poppler-windows/releases
# Giải nén vào: C:\poppler
# Thêm C:\poppler\Library\bin vào PATH
```

**Linux:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

### 3. Git Bash (cho các tool shell script trên Windows)

- Cài đặt Git for Windows: https://git-scm.com/download/win
- Các tool trong `tools/sh/` sẽ tự động tìm Git Bash

---

## 📝 File cấu hình không cần di chuyển

Các file sau sẽ được tạo tự động khi chạy tool lần đầu, **không cần copy**:

- ✅ `tools/py/ssh-manager/ssh_config.json` (tạo tự động)
- ✅ `tools/py/database-manager/database_config.json` (tạo tự động)
- ✅ `tools/py/xampp-project-manager/xampp_config.json` (tạo tự động)
- ✅ `tools/py/website-performance-*/performance_config.json` (tạo tự động)
- ✅ `menus/tool_config.json` (tạo tự động, lưu favorites/recent)

**Lưu ý:** Nếu bạn muốn giữ lại cấu hình cũ, có thể copy các file này và sửa đường dẫn bên trong.

---

## 🔄 Quy trình di chuyển nhanh (tóm tắt)

```bash
# 1. Copy/clone dự án
git clone https://github.com/VHN-DEV/DevTools.git
cd DevTools

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Cài đặt package (tùy chọn, để chạy từ bất kỳ đâu)
pip install -e .

# 4. Kiểm tra
devtools  # hoặc python .

# 5. Cấu hình lại các tool (nếu cần)
# - SSH Manager: sửa ssh_config.json
# - Database Manager: sửa database_config.json
# - XAMPP Manager: sửa xampp_config.json
```

---

## ❓ Câu hỏi thường gặp

### Q: Có cần cài lại Python không?

**A:** Có, máy mới cần cài Python 3.7+. Nhưng không cần cài lại các thư viện, vì đã có `requirements.txt`.

### Q: File config có thể copy từ máy cũ không?

**A:** Có, nhưng cần **sửa lại các đường dẫn** bên trong (vd: `C:\xampp` → đường dẫn mới). 

Tốt nhất là để tool tự tạo config mới và cấu hình lại.

### Q: Tool nào không cần cấu hình?

**A:** Hầu hết các tool không cần cấu hình, chỉ cần:
- ✅ Cài đặt Python dependencies (`pip install -r requirements.txt`)
- ✅ Chạy tool và nhập thông tin khi cần

### Q: Có thể chạy trên Linux/macOS không?

**A:** Có! Dự án hỗ trợ đa nền tảng. Xem phần [Hướng dẫn cho Linux/macOS](#-hướng-dẫn-cho-linuxmacos) bên dưới.

### Q: Tool nào cần cài thêm phần mềm bên ngoài?

**A:**
- **video-converter**: Cần FFmpeg
- **pdf-tools**: Cần Poppler (để convert PDF sang image)
- **tools/sh/***: Cần Git Bash (trên Windows) hoặc bash (Linux/macOS)

Các tool khác chỉ cần Python dependencies.

---

## 🐧 Hướng dẫn cho Linux/macOS

Dự án đã được thiết kế để hỗ trợ đa nền tảng. Hầu hết các tool đều hoạt động tốt trên Linux/macOS.

### 📋 Yêu cầu hệ thống

- **Python 3.7+** đã được cài đặt
- **pip3** đã được cài đặt
- **bash** (thường có sẵn trên Linux/macOS)
- Hệ điều hành: **Ubuntu, Debian, CentOS, macOS, và các distro Linux khác**

### 🚀 Cài đặt trên Linux/macOS

#### Bước 1: Clone hoặc copy dự án

```bash
# Clone từ Git
git clone https://github.com/VHN-DEV/DevTools.git
cd DevTools

# Hoặc copy thư mục dự án
```

#### Bước 2: Cài đặt dependencies

```bash
# Cài đặt Python dependencies
pip3 install -r requirements.txt

# Hoặc cài đặt như một package (khuyến nghị)
pip3 install -e .
```

#### Bước 3: Chạy menu

```bash
# Cách 1: Chạy trực tiếp
python3 .
# hoặc
python3 __main__.py

# Cách 2: Dùng shell script wrapper
chmod +x scripts/devtools.sh
./scripts/devtools.sh

# Cách 3: Nếu đã cài bằng pip install -e .
devtools
```

### 🔧 Cấu hình trên Linux/macOS

#### 1. Shell Script Wrapper (`scripts/devtools.sh`)

**Script này đã được tạo để tự động phát hiện đường dẫn**, tương tự như `devtools.bat` trên Windows.

**Cách sử dụng:**

**Cách 1: Chạy từ thư mục project**
```bash
cd /path/to/devtools
chmod +x scripts/devtools.sh
./scripts/devtools.sh
```

**Cách 2: Tạo symlink để chạy từ bất kỳ đâu**
```bash
# Tạo symlink
sudo ln -s /path/to/devtools/scripts/devtools.sh /usr/local/bin/devtools

# Sau đó chạy từ bất kỳ đâu
devtools
```

**Cách 3: Thêm vào PATH**
```bash
# Thêm vào ~/.bashrc hoặc ~/.zshrc
export PATH="$PATH:/path/to/devtools/scripts"

# Reload shell
source ~/.bashrc  # hoặc source ~/.zshrc

# Sau đó chạy
devtools.sh
```

**Cách 4: Set biến môi trường**
```bash
# Thêm vào ~/.bashrc hoặc ~/.zshrc
export DEVTOOLS_DIR="/path/to/devtools"

# Reload shell
source ~/.bashrc

# Sau đó script sẽ tự động tìm project
```

#### 2. Cấu hình các tool (tương tự Windows)

Các tool sẽ tự tạo file config khi chạy lần đầu. Bạn chỉ cần cấu hình lại đường dẫn cho phù hợp với Linux/macOS.

**SSH Manager:**
```json
{
  "servers": [
    {
      "name": "My Server",
      "host": "192.168.1.100",
      "port": 22,
      "user": "your_username",
      "key_path": "/home/username/.ssh/id_rsa",
      "password": ""
    }
  ]
}
```

**Database Manager:**
```json
{
  "connections": [
    {
      "name": "Local MySQL",
      "host": "localhost",
      "port": 3306,
      "user": "root",
      "password": "your_password",
      "default_db": ""
    }
  ]
}
```

### 🎯 Cài đặt các công cụ bổ sung

#### 1. FFmpeg (cho video-converter)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

#### 2. Poppler (cho pdf-tools)

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**CentOS/RHEL:**
```bash
sudo yum install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

#### 3. Unrar (cho extract-archive)

**Ubuntu/Debian:**
```bash
sudo apt-get install unrar
```

**macOS:**
```bash
brew install unrar
```

### ⚠️ Tool Windows-only

Một số tool chỉ hoạt động trên Windows:

- ✅ **xampp-project-manager**: Chỉ dành cho Windows (quản lý XAMPP)
  - **Giải pháp trên Linux/macOS**: Dùng tool `setup-project-linux` thay thế
  - Tool này sẽ tự động bị ẩn hoặc disable trên Linux/macOS

Các tool khác đều hoạt động tốt trên Linux/macOS!

### 🔄 Quy trình di chuyển từ Windows sang Linux/macOS

```bash
# 1. Copy/clone dự án
git clone https://github.com/VHN-DEV/DevTools.git
cd DevTools

# 2. Cài đặt dependencies
pip3 install -r requirements.txt

# 3. (Tùy chọn) Cài đặt như package
pip3 install -e .

# 4. Kiểm tra
python3 .  # hoặc devtools nếu đã cài bằng pip

# 5. Cấu hình lại các tool (nếu cần)
# - SSH Manager: sửa ssh_config.json (đường dẫn SSH key)
# - Database Manager: sửa database_config.json (connection info)
```

### 📝 Lưu ý đặc biệt cho Linux/macOS

1. **Python command**: Trên Linux/macOS, dùng `python3` thay vì `python`
2. **File permissions**: Có thể cần `chmod +x scripts/devtools.sh`
3. **Path separator**: Linux/macOS dùng `/` thay vì `\`
4. **Home directory**: Linux/macOS dùng `~` hoặc `$HOME`
5. **Package manager**: 
   - Ubuntu/Debian: `apt-get`
   - CentOS/RHEL: `yum` hoặc `dnf`
   - macOS: `brew`

### ❓ FAQ cho Linux/macOS

**Q: Lỗi "python: command not found"?**

**A:** Trên Linux/macOS, dùng `python3` thay vì `python`:
```bash
python3 .
```

**Q: Lỗi "Permission denied" khi chạy script?**

**A:** Cấp quyền execute:
```bash
chmod +x scripts/devtools.sh
```

**Q: Tool xampp-project-manager có chạy được không?**

**A:** Không, tool này chỉ dành cho Windows. Trên Linux/macOS, dùng tool `setup-project-linux` thay thế.

**Q: Có cần cài Git Bash không?**

**A:** Không, Linux/macOS đã có bash sẵn. Chỉ cần bash là đủ.

**Q: Cách cài đặt trên macOS?**

**A:** Giống Linux, nhưng dùng Homebrew để cài các công cụ bổ sung:
```bash
brew install python3 ffmpeg poppler
```

---

## 🎉 Kết luận

**Dự án hoàn toàn portable!** Chỉ cần:

1. ✅ Copy/clone dự án
2. ✅ `pip install -r requirements.txt`
3. ✅ (Tùy chọn) `pip install -e .` để chạy từ bất kỳ đâu
4. ✅ Cấu hình lại một số tool nếu cần (SSH, Database, XAMPP)

**Không cần:**
- ❌ Sửa code
- ❌ Cài đặt phức tạp
- ❌ Copy file config (tool tự tạo)

---

## 📞 Hỗ trợ

Nếu gặp vấn đề khi di chuyển, hãy:

1. Kiểm tra Python version: `python --version`
2. Kiểm tra dependencies: `pip list`
3. Xem log lỗi trong `logs/` (nếu có)
4. Tạo Issue trên GitHub: https://github.com/VHN-DEV/DevTools/issues

---

**Chúc bạn di chuyển thành công!** 🚀

