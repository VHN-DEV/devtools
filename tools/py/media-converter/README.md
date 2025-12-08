# Media Converter - Chuyển đổi Media

## Mô tả

Tool chuyển đổi media đa năng: chuyển đổi audio (MP3, WAV, AAC, FLAC, OGG), video (MP4, AVI, MKV, WEBM, MOV), tạo video từ audio, và trích xuất audio từ video.

## Tính năng

✅ Chuyển đổi audio (MP3, WAV, AAC, FLAC, OGG)
✅ Chuyển đổi video (MP4, AVI, MKV, WEBM, MOV)
✅ Audio → Video (tạo video từ audio + hình ảnh)
✅ Video → Audio (trích xuất audio từ video)
✅ Tùy chỉnh bitrate, preset
✅ Xử lý hàng loạt nhiều file

## Yêu cầu

```bash
pip install pydub moviepy
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
# Chọn tool "media-converter"
```

### Chạy trực tiếp

```bash
python tools/py/media-converter/media-converter.py
```

## Hướng dẫn chi tiết

### 1. Chuyển đổi Audio

1. Chọn chức năng: Chuyển đổi Audio
2. Nhập đường dẫn file audio
3. Chọn định dạng output:
   - **MP3**: Phổ biến nhất, nén tốt
   - **WAV**: Chất lượng cao, không nén (file lớn)
   - **AAC**: Chất lượng tốt, file nhỏ
   - **FLAC**: Chất lượng cao, nén không mất dữ liệu
   - **OGG**: Mã nguồn mở, nén tốt
4. Chọn bitrate (128k, 192k, 320k)
5. Chọn vị trí lưu file output

**Ví dụ:**
```
Input: music.wav (50 MB)
Format: MP3
Bitrate: 192k
Output: music.mp3 (5 MB)
→ Giảm 90% dung lượng!
```

### 2. Chuyển đổi Video

1. Chọn chức năng: Chuyển đổi Video
2. Nhập đường dẫn file video
3. Chọn định dạng output:
   - **MP4**: Phổ biến nhất, hỗ trợ tốt
   - **AVI**: Chất lượng cao, file lớn
   - **MKV**: Container linh hoạt
   - **WEBM**: Tối ưu cho web
   - **MOV**: Apple QuickTime
4. Chọn preset:
   - **ultrafast**: Nhanh nhất, chất lượng thấp
   - **fast**: Nhanh, chất lượng tốt
   - **medium**: Cân bằng (mặc định)
   - **slow**: Chậm, chất lượng cao nhất
5. Chọn vị trí lưu file output

**Ví dụ:**
```
Input: clip.avi (200 MB)
Format: MP4
Preset: medium
Output: clip.mp4 (180 MB)
```

### 3. Audio → Video

1. Chọn chức năng: Audio → Video
2. Nhập đường dẫn file audio
3. Chọn hình ảnh background:
   - Nhập đường dẫn file ảnh (JPG, PNG)
   - Hoặc Enter để dùng màu đen
4. Chọn định dạng video (MP4, AVI, WEBM)
5. Chọn bitrate audio
6. Tool tạo video từ audio + hình ảnh

**Ví dụ:**
```
Input: song.mp3
Image: cover.jpg
Format: MP4
Output: song.mp4 (video tĩnh với audio)
→ Phù hợp cho YouTube, Spotify
```

### 4. Video → Audio

1. Chọn chức năng: Video → Audio
2. Nhập đường dẫn file video
3. Chọn định dạng audio output:
   - **MP3**: Phổ biến nhất
   - **WAV**: Chất lượng cao
   - **AAC**: Chất lượng tốt, file nhỏ
4. Chọn bitrate (128k, 192k, 320k)
5. Chọn vị trí lưu file output

**Ví dụ:**
```
Input: video.mp4
Format: MP3
Bitrate: 192k
Output: video.mp3
→ Trích xuất audio track từ video
```

## Định dạng Audio

### MP3
- **Ưu điểm**: Phổ biến nhất, nén tốt, hỗ trợ rộng rãi
- **Nhược điểm**: Nén có mất dữ liệu
- **Bitrate khuyến nghị**: 192k (cân bằng), 320k (chất lượng cao)

### WAV
- **Ưu điểm**: Chất lượng cao nhất, không nén
- **Nhược điểm**: File rất lớn
- **Khuyến nghị**: Dùng cho master, archive

### AAC
- **Ưu điểm**: Chất lượng tốt hơn MP3 ở cùng bitrate, file nhỏ
- **Nhược điểm**: Hỗ trợ ít hơn MP3
- **Bitrate khuyến nghị**: 128k-192k

### FLAC
- **Ưu điểm**: Chất lượng cao, nén không mất dữ liệu
- **Nhược điểm**: File lớn hơn MP3, hỗ trợ ít hơn
- **Khuyến nghị**: Dùng cho archive, audiophile

### OGG
- **Ưu điểm**: Mã nguồn mở, nén tốt
- **Nhược điểm**: Hỗ trợ ít hơn MP3
- **Khuyến nghị**: Dùng cho web, open source projects

## Định dạng Video

### MP4
- **Ưu điểm**: Phổ biến nhất, hỗ trợ tốt, nén tốt
- **Nhược điểm**: Một số codec có thể không hỗ trợ
- **Khuyến nghị**: Dùng cho hầu hết trường hợp

### AVI
- **Ưu điểm**: Chất lượng cao, hỗ trợ nhiều codec
- **Nhược điểm**: File lớn, ít tối ưu cho web
- **Khuyến nghị**: Dùng cho archive, editing

### MKV
- **Ưu điểm**: Container linh hoạt, hỗ trợ nhiều codec
- **Nhược điểm**: Hỗ trợ ít hơn MP4
- **Khuyến nghị**: Dùng cho phim, video chất lượng cao

### WEBM
- **Ưu điểm**: Tối ưu cho web, mã nguồn mở
- **Nhược điểm**: Hỗ trợ ít hơn MP4
- **Khuyến nghị**: Dùng cho web, HTML5 video

### MOV
- **Ưu điểm**: Chất lượng cao, hỗ trợ tốt trên macOS
- **Nhược điểm**: Hỗ trợ ít hơn MP4 trên Windows
- **Khuyến nghị**: Dùng cho macOS, Apple devices

## Bitrate khuyến nghị

### Audio

| Bitrate | Chất lượng | Dung lượng | Khuyến nghị |
|---------|------------|------------|-------------|
| 128k | Thấp | Nhỏ | Podcast, voice |
| 192k | Tốt | Vừa | **Khuyến nghị** (cân bằng) |
| 320k | Cao | Lớn | Music chất lượng cao |

### Video

| Preset | Tốc độ | Chất lượng | Khuyến nghị |
|--------|--------|------------|-------------|
| ultrafast | Rất nhanh | Thấp | Test, preview |
| fast | Nhanh | Tốt | **Khuyến nghị** (cân bằng) |
| medium | Vừa | Tốt | Production |
| slow | Chậm | Cao | Final output |

## Tips

### Chọn định dạng:
- **Audio web**: MP3 192k (cân bằng tốt nhất)
- **Audio archive**: FLAC hoặc WAV (chất lượng cao)
- **Video web**: MP4 (hỗ trợ tốt nhất)
- **Video archive**: AVI hoặc MKV (chất lượng cao)

### Tối ưu:
- **Bitrate cao hơn** = Chất lượng tốt hơn nhưng file lớn hơn
- **Preset chậm hơn** = Chất lượng tốt hơn nhưng mất nhiều thời gian
- **Cân bằng**: MP3 192k, MP4 với preset medium

### Audio → Video:
- Phù hợp cho YouTube, Spotify, podcast
- Sử dụng hình ảnh cover đẹp
- Đảm bảo kích thước ảnh phù hợp (1920x1080 cho video)

## Use case phổ biến

- Chuyển đổi audio giữa các định dạng
- Chuyển đổi video để upload lên website
- Tạo video từ audio cho YouTube/Spotify
- Trích xuất audio từ video
- Tối ưu media cho web (giảm dung lượng)
- Chuẩn hóa format media trong thư viện

## Ví dụ thực tế

### Chuyển đổi audio

```
Input: music.wav (50 MB)
Format: MP3
Bitrate: 192k
Output: music.mp3 (5 MB)
→ Giảm 90% dung lượng, chất lượng vẫn tốt
```

### Tạo video từ audio

```
Input: podcast.mp3
Image: podcast_cover.jpg (1920x1080)
Format: MP4
Output: podcast.mp4
→ Video tĩnh với audio, phù hợp cho YouTube
```

### Trích xuất audio

```
Input: movie.mp4 (1 GB)
Format: MP3
Bitrate: 192k
Output: soundtrack.mp3 (5 MB)
→ Trích xuất soundtrack từ phim
```

## Lưu ý

- **FFmpeg bắt buộc**: Tool không hoạt động nếu chưa cài FFmpeg
- **Xử lý lâu**: File lớn có thể mất nhiều thời gian
- **Chất lượng**: Convert có thể làm giảm chất lượng ít nhiều
- **Backup**: Luôn giữ bản gốc trước khi convert
- **Format**: Một số format có thể không hỗ trợ trên tất cả thiết bị
- **Codec**: Một số codec có thể cần cài đặt thêm

