# 🎨 Hướng dẫn đổi Theme

## Cách đổi Theme

### Từ Menu Settings

1. Chạy DevTools: `devtools`
2. Nhập: `set` (hoặc `settings`)
3. Chọn: `3` (theme)
4. Chọn theme muốn dùng (1-5)
5. Theme sẽ được lưu vào config

### Themes có sẵn

1. **default** - Theme mặc định
   - Sáng, dễ nhìn
   - Màu sắc chuẩn

2. **dark** - Dark mode
   - Tối, dễ nhìn ban đêm
   - Màu sắc nhẹ nhàng

3. **light** - Light mode
   - Sáng, tương phản cao
   - Dễ đọc

4. **blue** - Blue theme
   - Tông màu xanh dương
   - Chuyên nghiệp

5. **green** - Green theme
   - Tông màu xanh lá
   - Tươi mát

---

## Lưu ý

### Theme hiện tại

Theme system hiện tại:
- ✅ Lưu theme vào config
- ✅ Hiển thị theme đã chọn
- ⚠️ Chưa áp dụng màu sắc vào UI (cần Rich library)

### Để áp dụng theme đầy đủ

1. **Cài Rich library:**
   ```bash
   pip install rich
   ```

2. **Theme sẽ tự động áp dụng** khi có Rich

3. **Nếu không có Rich:**
   - Theme chỉ lưu config
   - UI vẫn dùng màu mặc định (colorama/ANSI)

---

## File Config

Theme được lưu trong: `menus/theme_config.json`

```json
{
  "theme": "dark"
}
```

---

## Tạo Theme tùy chỉnh

### Cách 1: Sửa code

Mở `utils/theme.py` và thêm theme mới:

```python
'my-theme': ThemeColors(
    primary="#your-color",
    success="#your-color",
    warning="#your-color",
    error="#your-color",
    # ...
)
```

### Cách 2: Dùng API

```python
from utils.theme import ThemeManager

theme_manager = ThemeManager()
theme_manager.create_custom_theme('my-theme', {
    'primary': '#3498db',
    'success': '#2ecc71',
    # ...
})
```

---

## Preview Themes

### Default
- Primary: Blue (#3498db)
- Success: Green (#2ecc71)
- Warning: Orange (#f39c12)
- Error: Red (#e74c3c)

### Dark
- Primary: Light Blue (#5dade2)
- Success: Light Green (#52b788)
- Background: Dark (#1a1a1a)
- Foreground: Light (#e0e0e0)

### Light
- Primary: Dark Blue (#2980b9)
- Success: Dark Green (#27ae60)
- Background: White (#ffffff)
- Foreground: Dark (#2c3e50)

---

## Troubleshooting

### Theme không đổi
- Kiểm tra file `menus/theme_config.json` có được tạo không
- Khởi động lại chương trình
- Kiểm tra quyền ghi file

### Màu sắc không thay đổi
- Theme hiện tại chỉ lưu config
- Cần Rich library để áp dụng màu sắc
- Cài: `pip install rich`

---

**Theme được lưu tự động khi chọn! 🎨**

