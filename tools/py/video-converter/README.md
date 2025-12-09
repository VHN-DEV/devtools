# Video Converter - Xử lý video

## Mô tả

Tool xử lý video đa năng: chuyển đổi định dạng, nén dung lượng, cắt đoạn (trim), và trích xuất audio từ video.

## Tính năng

✅ Convert định dạng (MP4, AVI, MOV, MKV, WEBM)
✅ Compress video giảm dung lượng
✅ Trim video (cắt đoạn)
✅ Extract audio từ video (MP3, WAV, AAC)
✅ Resize video (giảm resolution)
✅ Thay đổi bitrate, FPS
✅ Xử lý hàng loạt nhiều video

## Yêu cầu

```bash
pip install moviepy
```

**Quan trọng**: Cần cài đặt FFmpeg

### Cài đặt FFmpeg

**Windows:**
1. Download từ https://ffmpeg.org/download.html
2. Giải nén và thêm vào PATH

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "video-converter"
```

### Chạy trực tiếp

```bash
python tools/py/video-converter/video-converter.py
```

## Hướng dẫn chi tiết

### 1. Nhập đường dẫn

- File video cụ thể
- Hoặc thư mục chứa nhiều video

### 2. Chọn chức năng

- **1**: Convert format (.mp4, .avi, .mov, .mkv, .webm)
- **2**: Nén video (giảm dung lượng)
- **3**: Trim video (cắt đoạn)
- **4**: Extract audio (trích xuất âm thanh)

### 3. Convert Format

1. Chọn format đích (mp4, avi, mov, mkv, webm)
2. Chọn thư mục output
3. Xử lý và chờ hoàn thành

### 4. Compress Video

1. Nhập bitrate (vd: 2000k, 1500k)
   - Bitrate càng thấp, dung lượng càng nhỏ nhưng chất lượng giảm
   - Khuyến nghị: 1500k-2500k cho video HD
2. Chọn thư mục output
3. Xử lý và chờ hoàn thành

### 5. Trim Video

1. Nhập thời gian bắt đầu (vd: 00:00:10 hoặc 10)
2. Nhập thời gian kết thúc (vd: 00:01:30 hoặc 90)
3. Chọn thư mục output
4. Xử lý và chờ hoàn thành

### 6. Extract Audio

1. Chọn format audio (mp3, wav, aac)
2. Chọn chất lượng (cho MP3: 128k, 192k, 320k)
3. Chọn thư mục output
4. Xử lý và chờ hoàn thành

## Ví dụ

### Convert Format

```
Input: video.avi (500 MB)
Format đích: mp4
Output: video.mp4 (480 MB)
```

### Compress Video

```
Input: video.mp4 (100 MB)
Bitrate: 2000k
Output: video_compressed.mp4 (25 MB)
→ Giảm 75% dung lượng
```

### Trim Video

```
Input: video.mp4 (10 phút)
Thời gian: 00:00:10 - 00:01:30
Output: video_trimmed.mp4 (1 phút 20 giây)
```

### Extract Audio

```
Input: video.mp4
Format: mp3
Quality: 192k
Output: video.mp3
```

## Tips

- **Xem thông tin video**: Xem duration, resolution, size trước khi xử lý
- **Nén video**: Có thể mất chất lượng, test với một video trước
- **Bitrate**: 
  - 1000k-1500k: Chất lượng thấp, dung lượng nhỏ
  - 2000k-2500k: Chất lượng tốt, dung lượng vừa phải
  - 3000k+: Chất lượng cao, dung lượng lớn
- **FFmpeg**: Đảm bảo FFmpeg được cài đặt và cấu hình đúng
- **Format MP4**: Phổ biến nhất, hỗ trợ tốt trên nhiều thiết bị

## Use case phổ biến

- Chuyển đổi video để upload lên website
- Nén video để tiết kiệm dung lượng
- Cắt clip ngắn từ video dài
- Extract nhạc từ video YouTube
- Tối ưu video cho mobile
- Chuẩn hóa format video trong thư viện

## Lưu ý

- **FFmpeg bắt buộc**: Tool không hoạt động nếu chưa cài FFmpeg
- **Xử lý lâu**: Video lớn có thể mất nhiều thời gian
- **Chất lượng**: Nén video luôn làm giảm chất lượng ít nhiều
- **Backup**: Luôn giữ bản gốc trước khi xử lý
- **Format**: Một số format có thể không hỗ trợ trên tất cả thiết bị

