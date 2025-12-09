# 📦 Hướng dẫn cài đặt DevTools

## 🎯 Mục tiêu: Chạy `devtools` từ bất kỳ đâu

---

## ⚡ Cài đặt nhanh (2 bước)

```bash
# Bước 1: Vào thư mục dự án
cd D:\DevTools

# Bước 2: Cài đặt
pip install -e .
```

**Xong!** Bây giờ bạn có thể chạy `devtools` từ bất kỳ đâu 🎉

```bash
# Test từ bất kỳ thư mục nào
cd C:\
devtools
```

---

## 📖 Giải thích chi tiết

### Lệnh `pip install -e .` làm gì?

1. **Cài DevTools như một Python package**
2. **Tạo lệnh toàn cục `devtools`**
3. **Thêm vào PATH tự động**
4. **Cho phép sửa code có hiệu lực ngay** (nhờ cờ `-e`)

### Sau khi cài đặt

```bash
# Từ bất kỳ thư mục nào
cd D:\Documents
cd C:\Projects
cd ~

# Chỉ cần gõ
devtools

# Menu sẽ xuất hiện! ✨
```

---

## 🔧 Phương pháp thay thế (Windows)

Nếu không muốn dùng pip, có thể dùng batch file:

### Bước 1: Chạy từ thư mục project

```batch
cd D:\DevTools
scripts\devtools.bat
```

**Lưu ý:** File `devtools.bat` đã được cập nhật để **tự động phát hiện đường dẫn**, không cần hardcode nữa!

### Bước 2: (Tùy chọn) Copy vào thư mục trong PATH

Nếu muốn chạy từ bất kỳ đâu, set biến môi trường:

```batch
setx DEVTOOLS_DIR "D:\DevTools"
```

Sau đó copy file vào PATH:

**Cách nhanh** (cần quyền Admin):
```bash
copy devtools.bat C:\Windows\System32\
```

**Cách an toàn:**
1. Tạo thư mục: `C:\Users\<TenBan>\bin\`
2. Copy `devtools.bat` vào đó
3. Thêm thư mục vào PATH:
   - Win+R → `sysdm.cpl` → Enter
   - Tab "Advanced" → "Environment Variables"
   - Chọn "Path" → "Edit" → "New"
   - Thêm: `C:\Users\<TenBan>\bin`
   - OK

### Bước 3: Thử nghiệm

```bash
# Mở CMD mới
devtools
```

---

## 🆘 Xử lý lỗi

### ❌ Lỗi: "devtools không được nhận dạng"

**Nguyên nhân:** Thư mục Scripts chưa trong PATH

**Giải pháp:**

```bash
# 1. Tìm thư mục Scripts
python -m site --user-base

# 2. Thêm Scripts vào PATH
# Kết quả (ví dụ): C:\Users\YourName\AppData\Roaming\Python\Python310
# → Thư mục Scripts: ...\Python\Python310\Scripts

# 3. Thêm vào PATH theo hướng dẫn trên
# 4. Mở CMD mới và thử lại
```

---

### ❌ Lỗi: "ModuleNotFoundError"

**Giải pháp:**

```bash
cd D:\DevTools
pip install -r requirements.txt
```

---

### ❌ Lỗi: "Permission denied"

**Giải pháp:**

```bash
# Cài cho user hiện tại
pip install --user -e .

# Hoặc chạy CMD với quyền Administrator
```

---

## 🗑️ Gỡ cài đặt

### Nếu cài bằng pip:

```bash
pip uninstall DevTools
```

### Nếu dùng batch file:

Xóa file `devtools.bat` đã copy:
```bash
del C:\Windows\System32\devtools.bat
```

---

## 💡 Lưu ý

- **Mở terminal/cmd mới** sau khi cài đặt để lệnh có hiệu lực
- **Cài ở chế độ editable** (`-e`) → sửa code không cần cài lại
- **Cập nhật code:** `git pull` → không cần cài lại

---

## 📚 Xem thêm

- **Tài liệu đầy đủ:** [README.md](../README.md)
- **Lịch sử thay đổi:** [CHANGELOG.md](CHANGELOG.md)

---

**Chúc bạn sử dụng hiệu quả!** 🎉
