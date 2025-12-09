# 🛠️ Hướng dẫn Setup Marketplace Registry

## Vấn đề: Registry không tồn tại

Nếu bạn gặp lỗi 404 khi tải registry, có 2 cách giải quyết:

---

## Cách 1: Sử dụng Registry Local (Khuyến nghị)

### Tạo registry local

1. Tạo file: `plugins/cache/marketplace/registry.json`

2. Copy nội dung mẫu:

```json
{
  "version": "1.0.0",
  "last_updated": "2024-12-19T00:00:00Z",
  "description": "DevTools Marketplace Registry",
  "tools": [
    {
      "id": "my-tool",
      "name": "My Custom Tool",
      "description": "Mô tả tool của bạn",
      "version": "1.0.0",
      "author": "Tên bạn",
      "category": "utilities",
      "tags": ["tag1", "tag2"],
      "download_url": "https://example.com/my-tool.zip",
      "type": "py",
      "homepage": "https://github.com/your-repo"
    }
  ]
}
```

3. Marketplace sẽ tự động sử dụng registry local này

---

## Cách 2: Tạo Registry trên GitHub

### Bước 1: Tạo repository mới

1. Tạo repository mới trên GitHub (vd: `DevTools-Marketplace`)
2. Tạo file `registry.json` với nội dung như trên

### Bước 2: Cập nhật URL trong config

1. Mở file: `plugins/cache/marketplace/marketplace_config.json`
2. Sửa `registry_url`:

```json
{
  "registry_url": "https://raw.githubusercontent.com/YOUR_USERNAME/DevTools-Marketplace/main/registry.json"
}
```

---

## Cấu trúc Registry

### Format JSON

```json
{
  "version": "1.0.0",
  "last_updated": "2024-12-19T00:00:00Z",
  "description": "Mô tả registry",
  "tools": [
    {
      "id": "tool-id",              // Bắt buộc: ID duy nhất
      "name": "Tên Tool",            // Bắt buộc: Tên hiển thị
      "description": "Mô tả",        // Bắt buộc: Mô tả tool
      "version": "1.0.0",            // Bắt buộc: Version
      "author": "Tác giả",           // Tùy chọn
      "category": "utilities",       // Tùy chọn: Category
      "tags": ["tag1", "tag2"],      // Tùy chọn: Tags
      "download_url": "https://...", // Bắt buộc: URL download
      "type": "py",                  // Bắt buộc: "py" hoặc "sh"
      "homepage": "https://..."      // Tùy chọn: Homepage
    }
  ]
}
```

### Categories có sẵn

- `file-management` - Quản lý file
- `image-processing` - Xử lý ảnh
- `video-processing` - Xử lý video
- `text-processing` - Xử lý text
- `devops` - DevOps tools
- `utilities` - Tiện ích
- `security` - Bảo mật
- `other` - Khác

---

## Tạo Tool Package

### Tool lấy từ đâu?

**Xem chi tiết:** [MARKETPLACE_TOOL_GUIDE.md](MARKETPLACE_TOOL_GUIDE.md)

**Tóm tắt:**
1. **Export từ DevTools**: `manage → 1` (Export tool)
2. **Upload lên GitHub/server**: Tạo public URL
3. **Thêm vào registry**: Cập nhật `download_url`

### Cấu trúc Tool

Tool cần được đóng gói thành file ZIP với cấu trúc:

```
tool-name.zip
└── py/                    # hoặc sh/
    └── tool-name/
        ├── tool-name.py
        ├── tool_info.json
        ├── doc.py
        └── README.md
```

### Export Tool

Sử dụng lệnh trong menu:
```
manage
# Chọn 1 - Export tool
```

Hoặc tạo thủ công:
1. Zip thư mục tool
2. Upload lên GitHub Releases hoặc server
3. Thêm vào registry với `download_url`

---

## Test Registry

### Test local registry

1. Tạo file `plugins/cache/marketplace/registry.json`
2. Chạy marketplace: `marketplace`
3. Chọn option 2 để xem danh sách

### Test remote registry

1. Upload registry.json lên GitHub
2. Lấy raw URL (vd: `https://raw.githubusercontent.com/...`)
3. Cập nhật config với URL mới
4. Test lại

---

## Troubleshooting

### Lỗi 404
- Kiểm tra URL có đúng không
- Kiểm tra file có tồn tại trên GitHub không
- Thử dùng registry local

### Lỗi JSON
- Validate JSON tại: https://jsonlint.com/
- Kiểm tra cú pháp JSON
- Đảm bảo encoding UTF-8

### Tool không cài được
- Kiểm tra download_url có hợp lệ không
- Kiểm tra file ZIP có đúng cấu trúc không
- Xem log trong `logs/`

---

## Ví dụ Registry đầy đủ

Xem file mẫu: `plugins/cache/marketplace/registry.json`

---

**Lưu ý:** Registry local sẽ được ưu tiên sử dụng nếu tồn tại.

