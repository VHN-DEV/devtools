# 🛒 Tool Marketplace

## Giới thiệu

Tool Marketplace cho phép bạn tải và cài đặt tools từ cộng đồng DevTools. Bạn có thể:
- 🔍 Tìm kiếm tools có sẵn
- 📥 Tải và cài đặt tools mới
- 🔄 Cập nhật tools lên phiên bản mới nhất
- 🗑️ Gỡ cài đặt tools

## Cách sử dụng

### Truy cập Marketplace

Từ menu chính, nhập lệnh:
```
marketplace
# hoặc
mp
# hoặc
store
```

### Các tính năng

#### 1. Tìm kiếm Tools
- Chọn `1` - Tìm kiếm tools
- Nhập từ khóa (tên, mô tả, tags)
- Xem kết quả và chọn tool để cài đặt

#### 2. Xem danh sách Tools
- Chọn `2` - Xem danh sách tools có sẵn
- Xem tất cả tools trong marketplace
- Lọc theo category (nếu có)

#### 3. Cài đặt Tool
- Chọn `3` - Cài đặt tool từ marketplace
- Nhập ID của tool
- Tool sẽ được tải và cài đặt tự động

#### 4. Xem Tools đã cài
- Chọn `4` - Xem tools đã cài từ marketplace
- Xem danh sách tools đã cài, version, thời gian cài đặt

#### 5. Cập nhật Tools
- Chọn `5` - Cập nhật tools
- Tự động kiểm tra và cập nhật tất cả tools đã cài

#### 6. Gỡ cài đặt Tool
- Chọn `6` - Gỡ cài đặt tool
- Chọn tool cần gỡ từ danh sách

## Cấu trúc Registry

Marketplace sử dụng registry JSON để quản lý tools:

```json
{
  "version": "1.0.0",
  "last_updated": "2024-01-01T00:00:00Z",
  "tools": [
    {
      "id": "tool-id",
      "name": "Tên Tool",
      "description": "Mô tả tool",
      "version": "1.0.0",
      "author": "Tác giả",
      "category": "file-management",
      "tags": ["tag1", "tag2"],
      "download_url": "https://example.com/tool.zip",
      "type": "py"
    }
  ]
}
```

## Cache

Marketplace tự động cache registry để tăng tốc độ:
- Registry cache: 1 giờ
- Tool metadata cache: 1 giờ
- Cache được lưu trong `plugins/cache/marketplace/`

## Troubleshooting

### Không tải được registry
- Kiểm tra kết nối internet
- Thử refresh: chọn lại option và chọn "force refresh"
- Kiểm tra URL registry trong config

### Tool cài đặt lỗi
- Kiểm tra file zip có hợp lệ không
- Kiểm tra cấu trúc thư mục tool
- Xem log files trong `logs/`

### Tool không xuất hiện sau khi cài
- Refresh menu: nhập `l` hoặc `list`
- Khởi động lại chương trình
- Kiểm tra tool có trong `tools/py/` hoặc `tools/sh/` không

## Đóng góp Tools

Bạn muốn chia sẻ tool của mình lên marketplace? 

1. Tạo tool theo cấu trúc chuẩn
2. Export tool thành file zip
3. Upload lên GitHub hoặc server
4. Thêm vào registry (liên hệ maintainer)

## Registry URL

Mặc định: `https://raw.githubusercontent.com/VHN-DEV/DevTools-Marketplace/main/registry.json`

Có thể thay đổi trong config: `plugins/cache/marketplace/marketplace_config.json`

