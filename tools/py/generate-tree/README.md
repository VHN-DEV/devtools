# Generate Tree - Tạo sơ đồ cây thư mục

## Mô tả

Tool tạo sơ đồ cây thư mục dự án với icon đẹp mắt. Hỗ trợ loại trừ folder không cần, giới hạn độ sâu, hiển thị/ẩn file ẩn, và xuất ra file text.

## Tính năng

✅ Hiển thị cây thư mục với icon đẹp mắt
✅ Loại trừ folder không cần (node_modules, .git, ...)
✅ Giới hạn độ sâu
✅ Hiển thị/ẩn file ẩn (bắt đầu bằng .)
✅ Xuất ra file text
✅ Thống kê số file và folder

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "generate-tree"
```

### Chạy trực tiếp

```bash
python tools/py/generate-tree/generate-tree.py
```

## Hướng dẫn chi tiết

### 1. Nhập đường dẫn

Nhập đường dẫn thư mục (Enter để dùng thư mục hiện tại)

### 2. Cấu hình

1. **Các thư mục/file cần bỏ qua**: Nhập pattern (cách nhau bởi dấu phẩy)
   - Mặc định: `node_modules,.git,__pycache__,venv,env,.vscode,.idea`
   - Ví dụ: `node_modules,.git,dist,build`

2. **Độ sâu tối đa**: Nhập số cấp (Enter để không giới hạn)
   - Ví dụ: `3` để chỉ hiển thị 3 cấp

3. **Hiển thị file/folder ẩn**: (y/N)
   - `y`: Hiển thị file/folder bắt đầu bằng `.`
   - `N`: Ẩn file/folder ẩn (mặc định)

### 3. Kết quả

Tool sẽ:
1. Tạo cây thư mục với icon
2. Hiển thị thống kê (số file, số folder)
3. Hỏi có muốn lưu ra file không (Y/n)

## Ví dụ

### Tạo cây thư mục đơn giản

```
Nhập đường dẫn thư mục (Enter để dùng thư mục hiện tại): D:\my-project
Các thư mục/file cần bỏ qua (cách nhau bởi dấu phẩy, Enter để mặc định): [Enter]
Độ sâu tối đa (Enter để không giới hạn): 3
Hiển thị file/folder ẩn (bắt đầu bằng .)? (y/N): N
```

**Kết quả:**
```
🌳 Đang tạo cây thư mục...

============================================================
📂 my-project/
============================================================
├── 📁 src/
│   ├── 📁 components/
│   │   ├── 🌐 Header.jsx
│   │   ├── 🌐 Footer.jsx
│   │   └── 🌐 Sidebar.jsx
│   ├── 📁 pages/
│   │   ├── 🌐 Home.jsx
│   │   ├── 🌐 About.jsx
│   │   └── 🌐 Contact.jsx
│   ├── 📁 utils/
│   │   ├── 🐍 helpers.py
│   │   └── 🐍 validators.py
│   └── 📜 index.js
├── 📁 public/
│   ├── 🌐 index.html
│   ├── 🖼️ logo.png
│   └── 🎨 styles.css
├── 📋 package.json
├── 📝 README.md
└── 📄 .gitignore

============================================================
📊 Tổng kết:
   - Thư mục: 5
   - File: 14
   - Tổng cộng: 19 mục
============================================================

Lưu kết quả ra file? (Y/n): Y

✅ Đã lưu vào: tree_my-project.txt
```

### Loại trừ thư mục cụ thể

```
Các thư mục/file cần bỏ qua: node_modules,.git,dist,build,coverage
→ Loại trừ các thư mục này khỏi cây thư mục
```

## Icon và ký hiệu

Tool sử dụng các icon để phân biệt loại file:
- 📂 Thư mục
- 📄 File text
- 🌐 File web (HTML, JS, JSX)
- 🐍 File Python
- 🖼️ File ảnh
- 🎨 File CSS
- 📋 File config (JSON, YAML)
- 📝 File markdown
- Và nhiều icon khác...

## Tips

### Độ sâu:
- **Không giới hạn**: Hiển thị toàn bộ cây (có thể rất dài)
- **Giới hạn 2-3 cấp**: Phù hợp cho documentation
- **Giới hạn 1 cấp**: Chỉ hiển thị cấp đầu tiên

### Loại trừ:
- **node_modules**: Thường rất lớn, nên loại trừ
- **.git**: Thư mục Git, không cần hiển thị
- **dist, build**: Thư mục build, không cần hiển thị
- **venv, env**: Virtual environment, không cần hiển thị

### File ẩn:
- **Ẩn file ẩn** (mặc định): Dễ đọc hơn, tập trung vào file quan trọng
- **Hiển thị file ẩn**: Xem đầy đủ cấu trúc (bao gồm .gitignore, .env...)

## Use case phổ biến

- Tạo documentation cho dự án
- Chia sẻ cấu trúc dự án với team
- Include trong README.md
- Review cấu trúc trước khi refactor
- Tạo sơ đồ tổ chức dự án

## Ví dụ thực tế

### Tạo sơ đồ cho README

```
Thư mục: ./src
Độ sâu: 2
Loại trừ: node_modules,.git,dist
→ Tạo sơ đồ ngắn gọn cho README.md
```

### Review cấu trúc dự án

```
Thư mục: ./project
Độ sâu: 3
Loại trừ: node_modules,.git,__pycache__
→ Xem cấu trúc tổng quan của dự án
```

## Lưu ý

- **File lớn**: Dự án lớn có thể tạo file text rất dài
- **Encoding**: File output là UTF-8 để hiển thị icon đúng
- **Icon**: Icon có thể không hiển thị đúng trên một số terminal
- **Performance**: Dự án lớn có thể mất một chút thời gian
