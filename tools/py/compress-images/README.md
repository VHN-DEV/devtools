# Compress Images - Nén và chỉnh sửa ảnh

## Mô tả

Tool nén và chỉnh sửa ảnh hàng loạt (resize, đổi format, nén dung lượng). Hỗ trợ nhiều định dạng ảnh phổ biến với khả năng tùy chỉnh chất lượng và kích thước.

## Tính năng

✅ Nén ảnh giảm dung lượng với quality tùy chỉnh (1-100)
✅ Resize ảnh (theo width/height/percent) giữ nguyên tỉ lệ
✅ Chuyển đổi format (JPG, PNG, WEBP, GIF)
✅ Xử lý hàng loạt nhiều ảnh
✅ Giữ nguyên ảnh gốc hoặc ghi đè
✅ Giới hạn dung lượng tối đa tự động
✅ Tự động tối ưu hóa
✅ Tạo thư mục output với timestamp

## Định dạng hỗ trợ

JPG, JPEG, PNG, WEBP, GIF, BMP

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "compress-images"
```

### Chạy trực tiếp

```bash
python tools/py/compress-images/compress-images.py
```

## Hướng dẫn chi tiết

1. **Chọn thư mục chứa ảnh** hoặc file ảnh cụ thể
2. **Chọn thư mục output** (Enter để tạo thư mục mặc định với timestamp)
3. **Nhập quality** (1-100, mặc định: 70)
4. **Chọn có optimize không** (Y/n)
5. **Chọn định dạng đích** (jpg, png, webp, hoặc giữ nguyên)
6. **Nhập dung lượng tối đa** (KB, Enter để bỏ qua)
7. **Nhập chiều rộng** (px, Enter để bỏ qua)
8. **Nhập chiều cao** (px, Enter để bỏ qua)

## Ví dụ thực tế

```
Nhập đường dẫn thư mục chứa ảnh: D:\Photos
Nhập đường dẫn thư mục đầu ra (Enter để mặc định): [Enter]
Nhập quality (mặc định 70): 80
Có bật optimize không? (Y/n): Y
Muốn đổi sang định dạng nào? (jpg, png, webp): webp
Nhập dung lượng tối đa mỗi ảnh (KB, Enter để bỏ qua): 500
Nhập chiều rộng (px, Enter để bỏ qua): 1920
Nhập chiều cao (px, Enter để bỏ qua): [Enter]
```

**Kết quả:**
```
✅ photo1.jpg | 2500.0KB → 450.2KB (q=80)
✅ photo2.png | 1800.5KB → 480.8KB (q=80)
✅ photo3.jpg | 3200.0KB → 495.5KB (q=75)

🎉 Hoàn thành nén ảnh! Ảnh đã được lưu tại: D:\Photos\compressed_20241029_143022
```

## Use case phổ biến

- **Tối ưu ảnh cho website**: Giảm thời gian load, tiết kiệm bandwidth
- **Resize ảnh để upload**: Giảm kích thước trước khi upload lên mạng xã hội
- **Chuyển PNG sang WEBP**: Giảm 30-50% dung lượng với chất lượng tương đương
- **Giảm dung lượng album ảnh**: Nén toàn bộ album để tiết kiệm dung lượng ổ cứng

## Lưu ý

- **Format WEBP**: Cho kết quả tốt nhất (nhỏ gọn, chất lượng cao) nhưng không phải trình duyệt nào cũng hỗ trợ
- **Quality 70-85%**: Lý tưởng cho web, cân bằng giữa chất lượng và dung lượng
- **Resize**: Mặc định giữ nguyên aspect ratio
- **Optimize**: Giúp giảm thêm 5-10% dung lượng nhưng có thể làm chậm quá trình xử lý
- **Dung lượng tối đa**: Tool sẽ tự động giảm quality nếu ảnh vượt quá giới hạn

## Tips

- Sử dụng quality 70-80 cho ảnh web
- Sử dụng quality 85-95 cho ảnh in ấn
- Format WEBP tiết kiệm dung lượng nhất nhưng cần kiểm tra trình duyệt hỗ trợ
- Resize trước khi nén sẽ giảm đáng kể dung lượng
- Luôn giữ bản gốc khi làm việc với ảnh quan trọng
