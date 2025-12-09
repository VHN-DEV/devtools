# Font Generator - Xử lý Font

## Mô tả

Tool xử lý font chuyên nghiệp: chuyển đổi định dạng font (TTF/OTF → WOFF/WOFF2), xem thông tin font, và tạo font subset (font chỉ chứa các ký tự cần thiết) để giảm kích thước file.

## Tính năng

✅ Chuyển đổi định dạng font (TTF ↔ OTF ↔ WOFF ↔ WOFF2)
✅ Xem thông tin chi tiết của font
✅ Tạo font subset (chỉ chứa ký tự cần thiết)
✅ Giảm kích thước file font đáng kể (90%+)
✅ Hỗ trợ Unicode ranges
✅ Tự động hiển thị thông tin font

## Yêu cầu

```bash
pip install fonttools brotli
```

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "font-generator"
```

### Chạy trực tiếp

```bash
python tools/py/font-generator/font-generator.py
```

## Hướng dẫn chi tiết

### 1. Chuyển đổi định dạng Font

1. Chọn chức năng: Chuyển đổi định dạng
2. Nhập đường dẫn file font gốc (TTF hoặc OTF)
3. Chọn định dạng output:
   - **WOFF**: Web Open Font Format (cho web)
   - **WOFF2**: Phiên bản nén tốt hơn WOFF (khuyến nghị cho web)
   - **TTF**: TrueType Font (cho desktop)
   - **OTF**: OpenType Font (cho desktop)
4. Chọn vị trí lưu file output
5. Tool tự động hiển thị thông tin font trước khi convert

**Ví dụ:**
```
Input: Arial.ttf (500 KB)
Format: WOFF2
Output: Arial.woff2 (200 KB)
→ Giảm 60% kích thước!
```

### 2. Xem thông tin Font

1. Chọn chức năng: Xem thông tin
2. Nhập đường dẫn file font
3. Xem thông tin:
   - **Family name**: Tên font
   - **Style**: Regular, Bold, Italic, Bold Italic...
   - **Version**: Phiên bản font
   - **Số lượng glyphs**: Số ký tự trong font
   - **Copyright**: Thông tin bản quyền
   - **Kích thước file**: Dung lượng file

**Ví dụ:**
```
Font: Arial.ttf
Family: Arial
Style: Regular
Version: 5.06
Glyphs: 1,365
Size: 500 KB
```

### 3. Tạo Font Subset

1. Chọn chức năng: Tạo font subset
2. Nhập đường dẫn file font gốc
3. Chọn phương thức:
   - **Nhập danh sách ký tự**: `Hello World 123`, `abcABC`
   - **Nhập Unicode ranges**: `U+0020-007F,U+0100-017F`
4. Chọn vị trí lưu file output
5. Tool tạo font mới chỉ chứa các ký tự được chọn

**Ví dụ:**
```
Input: CustomFont.ttf (2 MB)
Ký tự: 'Hello World 123'
Output: CustomFont_subset.ttf (50 KB)
→ Giảm 97.5% kích thước!
```

## Định dạng Font

### WOFF / WOFF2
- **Ưu điểm**: Nén tốt, tải nhanh, hỗ trợ tốt trên web
- **Nhược điểm**: Chỉ dùng được trên web (không dùng được trên desktop)
- **Khuyến nghị**: Dùng cho website, web app

### TTF / OTF
- **Ưu điểm**: Chất lượng cao, hỗ trợ tốt trên desktop
- **Nhược điểm**: File lớn hơn WOFF/WOFF2
- **Khuyến nghị**: Dùng cho ứng dụng desktop, design

## Unicode Ranges phổ biến

| Range | Mô tả | Ký tự |
|-------|-------|-------|
| `U+0020-007F` | ASCII cơ bản | A-Z, a-z, 0-9, ký tự đặc biệt |
| `U+0100-017F` | Latin Extended-A | Ā, ă, ą, ć... |
| `U+0180-024F` | Latin Extended-B | ƀ, Ɓ, Ƃ, ƃ... |
| `U+0300-036F` | Combining Diacritical Marks | Dấu phụ (á, é, í...) |
| `U+1E00-1EFF` | Latin Extended Additional | Ạ, ạ, Ả, ả... |
| `U+2000-206F` | General Punctuation | Dấu câu đặc biệt |
| `U+20A0-20CF` | Currency Symbols | €, £, ¥, $... |
| `U+2100-214F` | Letterlike Symbols | ™, ©, ®... |

### Tiếng Việt

Để hỗ trợ đầy đủ tiếng Việt, cần các ranges:
```
U+0020-007F,U+0100-017F,U+1E00-1EFF
```

## Tips

### Chọn định dạng:
- **Web**: Dùng WOFF2 (nén tốt nhất, hỗ trợ tốt)
- **Desktop**: Dùng TTF hoặc OTF (chất lượng cao)

### Font Subset:
- Giảm đáng kể kích thước file (90%+)
- Phù hợp khi chỉ cần một số ký tự cụ thể
- Unicode ranges hữu ích cho các ngôn ngữ cụ thể

### Tối ưu cho web:
1. Tạo subset chỉ với ký tự cần thiết
2. Convert sang WOFF2
3. Giảm kích thước file đáng kể, tăng tốc độ tải trang

## Ví dụ thực tế

### Tạo font cho website

```
1. Font gốc: CustomFont.ttf (2 MB)
2. Tạo subset với ký tự: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 !@#$%^&*()'
3. → CustomFont_subset.ttf (80 KB)
4. Convert sang WOFF2
5. → CustomFont_subset.woff2 (40 KB)
→ Giảm 98% kích thước!
```

### Hỗ trợ tiếng Việt

```
Input: VietnameseFont.ttf
Unicode ranges: U+0020-007F,U+0100-017F,U+1E00-1EFF
Output: VietnameseFont_subset.ttf
→ Chứa đầy đủ ký tự tiếng Việt có dấu
```

## Use case phổ biến

- Tối ưu font cho website (giảm dung lượng, tăng tốc độ tải)
- Tạo font chỉ chứa ký tự cần thiết (logo, icon font)
- Convert font giữa các định dạng
- Xem thông tin font trước khi sử dụng
- Giảm dung lượng font trong ứng dụng mobile

## Lưu ý

- **Font subset**: Không thể thêm ký tự mới vào font subset sau khi tạo
- **Backup**: Luôn giữ bản gốc font trước khi tạo subset
- **Bản quyền**: Đảm bảo có quyền sử dụng font trước khi convert
- **Testing**: Test font trên các trình duyệt/thiết bị khác nhau
- **Fallback**: Luôn có font fallback trong CSS cho web

