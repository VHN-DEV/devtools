# Thư mục Tools

## Cấu trúc

Mỗi tool nằm trong một thư mục riêng để dễ quản lý và mở rộng:

```
tools/
├── py/
│   ├── backup-folder/
│   │   ├── __init__.py
│   │   ├── backup-folder.py          # File chính của tool
│   │   ├── tool_info.json            # (Optional) Metadata của tool
│   │   ├── doc.py                    # (Optional) Hướng dẫn sử dụng
│   │   └── README.md                  # (Optional) Hướng dẫn chi tiết
│   └── ...
└── sh/
    ├── setup-project-linux/
    │   ├── __init__.py
    │   ├── setup-project-linux.py    # File chính của tool
    │   ├── tool_info.json            # (Optional) Metadata của tool
    │   ├── doc.py                    # (Optional) Hướng dẫn sử dụng
    │   └── app.sh                    # Script shell (nếu cần)
    └── ...
```

## Cách thêm tool mới

### ⚡ Cách nhanh nhất: Dùng script tự động

Sử dụng script `create-tool.py` để tạo tool mới với template sẵn có:

**Windows:**
```cmd
scripts\create-tool.bat
```

**Linux/Mac hoặc chạy Python trực tiếp:**
```bash
python scripts/create-tool.py
```

Script sẽ tự động:
- ✅ Tạo thư mục tool
- ✅ Tạo file chính với template đầy đủ
- ✅ Tạo `__init__.py`
- ✅ Tạo `tool_info.json`
- ✅ (Optional) Tạo `doc.py`

Sau đó chỉ cần mở file `.py` và thêm logic của tool!

---

### Cách thủ công: Tạo tool từ đầu

### Bước 1: Tạo thư mục tool

Tạo thư mục mới trong `tools/py/` (cho tool Python) hoặc `tools/sh/` (cho tool shell script):

```
tools/py/ten-tool-moi/
```

### Bước 2: Tạo file chính

Tạo file chính có tên giống tên thư mục:

```
tools/py/ten-tool-moi/ten-tool-moi.py
```

### Bước 3: Tạo __init__.py

Tạo file `__init__.py`:

```python
"""
Tool: ten-tool-moi
"""
```

### Bước 4: (Optional) Tạo tool_info.json

Tạo file `tool_info.json` để cung cấp metadata cho tool:

```json
{
  "name": "Tên hiển thị tiếng Việt của tool",
  "tags": [
    "tag1",
    "tag2",
    "tag3"
  ]
}
```

**Lưu ý:**
- ✅ **TỰ ĐỘNG HOÀN TOÀN**: Nếu không có `tool_info.json`, hệ thống sẽ tự động:
  - Generate tên hiển thị từ tên file (vd: `backup-folder.py` → "Sao lưu thư mục")
  - Generate tags từ các từ trong tên file
  - Phân loại category tự động (dựa trên keywords: image, video, file, archive, etc.)
- Tên file theo format `kebab-case` (ví dụ: `backup-folder.py`) sẽ được tự động chuyển đổi
- Tool sẽ tự động xuất hiện trong menu với category và icon phù hợp

### Bước 5: (Optional) Tạo doc.py

Tạo file `doc.py` để cung cấp hướng dẫn sử dụng:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File doc.py - Hướng dẫn sử dụng tool
"""

def get_help():
    """
    Trả về hướng dẫn sử dụng cơ bản của tool
    
    Returns:
        str: Hướng dẫn sử dụng tool
    """
    return """
📋 HƯỚNG DẪN SỬ DỤNG:

1️⃣  Bước 1: ...
2️⃣  Bước 2: ...

💡 TIP: ...
    """
```

### Bước 6: Hoàn thành! ✅

**Tool sẽ tự động xuất hiện trong menu chính mà không cần sửa code nào khác!**

#### 🎯 Tính năng tự động:

1. ✅ **Tự động phát hiện**: Tool được scan tự động khi khởi động
2. ✅ **Tự động tên hiển thị**: Tạo từ tên file hoặc lấy từ `tool_info.json`
3. ✅ **Tự động tags**: Generate từ tên file hoặc lấy từ `tool_info.json`
4. ✅ **Tự động phân loại category**: Dựa trên keywords (image, video, file, etc.)
   - 🖼️ Hình ảnh: tools có từ "image", "anh", "photo", "watermark"
   - 🎬 Video: tools có từ "video", "phim", "movie"
   - 📁 File & Thư mục: tools có từ "file", "folder", "backup", "organizer"
   - 📦 Nén & Giải nén: tools có từ "archive", "extract", "compress", "zip"
   - 📝 Text & Encoding: tools có từ "text", "encoding", "find", "replace", "json"
   - 📄 PDF: tools có từ "pdf"
   - 🔀 Git: tools có từ "git", "commit", "changed"
   - ⚙️ Hệ thống: tools có từ "clean", "temp", "setup", "project", "tree"
   - 🌐 Network & Server: tools có từ "ssh", "server", "connect", "remote"
   - 🔧 Khác: các tools không khớp với categories trên
5. ✅ **Tự động hiển thị**: Xuất hiện trong menu với icon category phù hợp
6. ✅ **Tự động hướng dẫn**: Đọc từ `doc.py` khi nhập `[số]h`

## Ví dụ: Thêm tool mới

### Tool: `my-new-tool`

1. Tạo thư mục: `tools/py/my-new-tool/`
2. Tạo file: `tools/py/my-new-tool/my-new-tool.py`
3. Tạo file: `tools/py/my-new-tool/__init__.py`
4. (Optional) Tạo file: `tools/py/my-new-tool/tool_info.json`:
```json
{
  "name": "Tool mới của tôi - Mô tả ngắn",
  "tags": ["my", "new", "tool", "custom"]
}
```

**Kết quả:**
- ✅ Tool `my-new-tool.py` sẽ tự động xuất hiện trong menu
- ✅ Nếu không có `tool_info.json`, tên hiển thị sẽ là: "My New Tool"
- ✅ Tags sẽ tự động là: `["my", "new", "tool", "my-new-tool"]`
- ✅ Category sẽ tự động là "Khác" (vì không match keywords nào)
- ✅ Để vào category cụ thể, thêm keyword phù hợp vào tên file (vd: `my-image-tool.py` → category "Hình ảnh")

## File Config của Tool

Mỗi tool có thể có file config riêng trong thư mục của nó:

- **ssh-manager**: `ssh_config.json` - Danh sách SSH servers
- **image-watermark**: `watermark_templates.json` - Templates watermark đã lưu
- **backup-folder**: `backup_metadata.json` - Lịch sử backup (lưu trong thư mục backup)

**Lợi ích:**
- Config được tổ chức cùng tool sử dụng nó
- Dễ backup/restore từng tool với config riêng
- Không lộn xộn ở project root

## ✨ Tóm tắt: Thêm tool mới CHỈ CẦN 3 BƯỚC

```bash
# 1. Tạo thư mục
mkdir tools/py/my-tool

# 2. Tạo file chính
cat > tools/py/my-tool/my-tool.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def main():
    print("Hello from my tool!")
if __name__ == "__main__":
    main()
EOF

# 3. Tạo __init__.py
echo '"""Tool: my-tool"""' > tools/py/my-tool/__init__.py
```

**Xong!** Tool sẽ tự động xuất hiện trong menu khi chạy `python .` hoặc `devtools`.

## Lưu ý

- ✅ Tool phải có file `.py` chính có tên giống tên thư mục
- ✅ File chính phải có thể chạy độc lập bằng `python ten-tool.py`
- ✅ Nếu tool cần dependencies, thêm vào `requirements.txt` ở project root
- ✅ Tool nên có xử lý lỗi và thông báo rõ ràng cho người dùng
- ✅ **Không cần config gì thêm** - mọi thứ đều tự động!
