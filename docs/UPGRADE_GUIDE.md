# 🚀 Hướng dẫn nâng cấp - Tính năng mới

## Tổng quan

DevTools đã được nâng cấp với 3 tính năng chính:
1. **Tool Marketplace** - Tải và cài đặt tools từ cộng đồng
2. **Performance Improvements** - Cải thiện hiệu suất với smart cache và lazy loading
3. **UI/UX Enhancements** - Giao diện đẹp hơn với Rich library và themes

---

## 📦 Cài đặt Dependencies mới

Cài đặt các thư viện mới:

```bash
pip install -r requirements.txt
```

Hoặc cài riêng:
```bash
pip install rich>=13.0.0 requests>=2.31.0
```

---

## 🛒 Tool Marketplace

### Tính năng
- ✅ Tìm kiếm tools từ cộng đồng
- ✅ Tải và cài đặt tools tự động
- ✅ Cập nhật tools lên phiên bản mới
- ✅ Quản lý tools đã cài

### Cách sử dụng

Từ menu chính:
```
marketplace
# hoặc
mp
```

**Xem chi tiết:** [MARKETPLACE.md](MARKETPLACE.md)

---

## ⚡ Performance Improvements

### Smart Cache System
- Cache thông minh với TTL (Time To Live)
- Tự động invalidate khi hết hạn
- Memory cache + File cache
- Giảm thời gian load tools

### Lazy Loading
- Chỉ load metadata khi cần
- Giảm thời gian khởi động
- Tối ưu memory usage

### Cách sử dụng

Tự động hoạt động, không cần cấu hình. Cache được lưu trong:
- `plugins/cache/` - File cache
- Memory cache (tự động cleanup)

---

## 🎨 UI/UX Enhancements

### Rich Library Integration
- Tables đẹp với Rich
- Panels và borders
- Progress bars nâng cao
- Syntax highlighting

### Theme System
- Dark mode
- Light mode
- Custom themes
- Tự động fallback nếu không có Rich

### Cách sử dụng

Rich tự động được sử dụng nếu đã cài đặt. Nếu không, sẽ fallback về UI cũ.

**Thay đổi theme:**
```python
from utils.theme import ThemeManager

theme_manager = ThemeManager()
theme_manager.set_theme('dark')  # hoặc 'light', 'blue', 'green'
```

---

## 📊 So sánh trước/sau

### Trước
- ❌ Không có marketplace
- ❌ Cache đơn giản, không có TTL
- ❌ Load tất cả metadata khi khởi động
- ❌ UI cơ bản với colorama

### Sau
- ✅ Tool Marketplace đầy đủ
- ✅ Smart cache với TTL và invalidation
- ✅ Lazy loading metadata
- ✅ Rich UI với tables, panels, themes

---

## 🔧 Cấu hình

### Marketplace Config
File: `plugins/cache/marketplace/marketplace_config.json`

```json
{
  "registry_url": "https://raw.githubusercontent.com/VHN-DEV/DevTools-Marketplace/main/registry.json",
  "installed_tools": {},
  "last_update": null
}
```

### Theme Config
File: `menus/theme_config.json`

```json
{
  "theme": "default"
}
```

---

## 🐛 Troubleshooting

### Rich không hoạt động
- Cài đặt: `pip install rich`
- Kiểm tra: `python -c "import rich; print('OK')"`
- Nếu lỗi, UI sẽ tự động fallback

### Marketplace không tải được
- Kiểm tra kết nối internet
- Kiểm tra URL registry
- Xem cache: `plugins/cache/marketplace/`

### Cache không hoạt động
- Kiểm tra quyền ghi trong `plugins/cache/`
- Xóa cache cũ: `plugins/cache/`
- Restart chương trình

---

## 📝 Migration Notes

### Từ version cũ
- Config files tự động migrate
- Cache cũ sẽ được dọn dẹp tự động
- Không cần thay đổi code tools hiện có

### Breaking Changes
- Không có breaking changes
- Tất cả tính năng cũ vẫn hoạt động bình thường

---

## 🎯 Next Steps

1. **Cài đặt dependencies mới**
2. **Thử marketplace**: `marketplace` trong menu
3. **Khám phá Rich UI**: Tự động hiển thị khi có Rich
4. **Tùy chỉnh theme**: Sửa `theme_config.json`

---

## 📚 Tài liệu tham khảo

- [MARKETPLACE.md](MARKETPLACE.md) - Hướng dẫn chi tiết về Marketplace
- [README.md](../README.md) - Tài liệu chính
- [CHANGELOG.md](CHANGELOG.md) - Lịch sử thay đổi

---

**Chúc bạn sử dụng vui vẻ! 🎉**

