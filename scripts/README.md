# Scripts - Các script tiện ích

Thư mục này chứa các script hỗ trợ cho project.

## Files

### `devtools.bat`
Batch script để chạy DevTools trên Windows (không cần cài đặt pip).

**Cách sử dụng:**
```cmd
scripts\devtools.bat
```

**Hoặc** thêm thư mục `scripts/` vào PATH để chạy từ mọi nơi:
```cmd
devtools
```

### `create-tool.py` / `create-tool.bat`
Script tạo tool mới nhanh chóng với template sẵn có.

**Cách sử dụng:**

**Windows:**
```cmd
scripts\create-tool.bat
```

**Hoặc chạy trực tiếp Python:**
```bash
python scripts/create-tool.py
# hoặc
python -m scripts.create-tool
```

**Script sẽ hỏi:**
1. Tên tool (vd: `my-awesome-tool` hoặc `My Awesome Tool`)
2. Tên hiển thị (mặc định: tự động từ tên tool)
3. Mô tả ngắn gọn
4. Loại tool (Python hoặc Shell)

**Kết quả:**
- ✅ Tự động tạo thư mục tool trong `tools/py/` hoặc `tools/sh/`
- ✅ Tạo file chính với template đầy đủ
- ✅ Tạo `__init__.py`
- ✅ Tạo `tool_info.json` với metadata
- ✅ (Optional) Tạo `doc.py` cho hướng dẫn sử dụng

**Sau khi tạo:**
1. Mở file `{tool-name}.py` và thêm logic của tool
2. (Optional) Cập nhật `tool_info.json` với tags phù hợp
3. (Optional) Hoàn thiện `doc.py` với hướng dẫn chi tiết
4. Chạy lại chương trình → Tool tự động xuất hiện trong menu!

## Lưu ý

Nếu đã cài đặt bằng `pip install -e .`, không cần sử dụng script này.
Chỉ dùng khi muốn chạy trực tiếp mà không cài đặt.

