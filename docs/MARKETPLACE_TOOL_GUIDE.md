# 📦 Hướng dẫn: Tool trong Marketplace là gì và lấy từ đâu?

## ❓ Câu hỏi

**"Tool trong registry là gì và lấy từ đâu?"**

## 💡 Giải thích

### Tool trong Registry là gì?

Tool trong registry là **thông tin metadata** về một tool có thể tải và cài đặt. Mỗi tool entry bao gồm:
- **ID**: Tên duy nhất của tool
- **Name**: Tên hiển thị
- **Description**: Mô tả chức năng
- **Download URL**: Link để tải file ZIP của tool
- **Version**: Phiên bản tool

### Tool lấy từ đâu?

Có 3 nguồn chính:

#### 1. **Tools có sẵn trong DevTools** (Export)

Bạn có thể export bất kỳ tool nào từ DevTools:

```
Menu → manage → 1 (Export tool)
```

Ví dụ: Export tool `backup-folder`:
- Tool sẽ được nén thành file ZIP
- File lưu trong `exports/backup-folder_YYYYMMDD_HHMMSS.zip`
- Upload file này lên GitHub Releases hoặc server
- Thêm vào registry với `download_url` trỏ đến file đó

#### 2. **Tools từ cộng đồng**

Người khác tạo tool và chia sẻ:
- Họ export tool của họ
- Upload lên GitHub/server
- Thêm vào registry công khai
- Bạn có thể tải và cài đặt

#### 3. **Tạo tool mới**

Bạn tự tạo tool mới:
- Dùng script `create-tool.py` hoặc tạo thủ công
- Export tool
- Upload và thêm vào registry

---

## 🔧 Cách tạo Tool Package thực tế

### Bước 1: Export Tool từ DevTools

1. Chạy DevTools: `devtools`
2. Nhập: `manage`
3. Chọn: `1` (Export tool)
4. Chọn tool cần export (vd: `backup-folder`)
5. File ZIP sẽ được tạo trong `exports/`

### Bước 2: Upload Tool Package

**Cách 1: GitHub Releases (Khuyến nghị)**

1. Tạo repository mới trên GitHub
2. Tạo Release mới
3. Upload file ZIP vào Release
4. Copy link download (vd: `https://github.com/user/repo/releases/download/v1.0.0/backup-folder.zip`)

**Cách 2: Server/Cloud Storage**

1. Upload file ZIP lên server
2. Lấy public URL (vd: `https://example.com/tools/backup-folder.zip`)

### Bước 3: Thêm vào Registry

Mở file: `plugins/cache/marketplace/registry.json`

Thêm tool mới:

```json
{
  "id": "backup-folder",
  "name": "Sao lưu và nén thư mục",
  "description": "Tool sao lưu và nén thư mục với timestamp tự động",
  "version": "1.0.0",
  "author": "V.H.Nam",
  "category": "file-management",
  "tags": ["backup", "zip", "folder"],
  "download_url": "https://github.com/user/repo/releases/download/v1.0.0/backup-folder.zip",
  "type": "py",
  "homepage": "https://github.com/user/repo"
}
```

---

## 📋 Ví dụ: Tạo Tool Package từ Tool có sẵn

### Ví dụ: Export `backup-folder`

1. **Export tool:**
   ```
   devtools → manage → 1 → chọn backup-folder
   ```
   → File: `exports/backup-folder_20241219_120000.zip`

2. **Upload lên GitHub:**
   - Tạo repo: `my-devtools-tools`
   - Tạo Release v1.0.0
   - Upload file ZIP
   - Link: `https://github.com/user/my-devtools-tools/releases/download/v1.0.0/backup-folder.zip`

3. **Thêm vào registry:**
   ```json
   {
     "id": "backup-folder",
     "name": "Sao lưu và nén thư mục",
     "description": "Tool sao lưu và nén thư mục với timestamp",
     "version": "1.0.0",
     "author": "Your Name",
     "category": "file-management",
     "tags": ["backup", "zip"],
     "download_url": "https://github.com/user/my-devtools-tools/releases/download/v1.0.0/backup-folder.zip",
     "type": "py"
   }
   ```

4. **Test:**
   ```
   devtools → marketplace → 2 (Xem danh sách)
   ```
   → Tool `backup-folder` sẽ xuất hiện

---

## 🎯 Tool mẫu hiện tại

Tool `example-tool` trong registry mẫu:
- ⚠️ **Chỉ là ví dụ** - không phải tool thực tế
- Download URL trỏ đến repo chính (toàn bộ DevTools)
- **Không thể cài đặt được** vì không đúng cấu trúc

**Để có tool thực tế:**
1. Export một tool có sẵn (vd: `backup-folder`)
2. Upload lên server/GitHub
3. Cập nhật registry với download_url đúng

---

## 📝 Checklist tạo Tool Package

- [ ] Tool đã được export thành ZIP
- [ ] File ZIP có cấu trúc đúng: `py/tool-name/` hoặc `sh/tool-name/`
- [ ] File ZIP đã upload lên server/GitHub
- [ ] Có public URL để download
- [ ] Đã thêm vào registry với đầy đủ thông tin
- [ ] Test cài đặt thành công

---

## 🔍 Kiểm tra Tool Package

### Cấu trúc ZIP đúng:

```
tool-name.zip
└── py/                    # hoặc sh/
    └── tool-name/
        ├── tool-name.py   # File chính
        ├── tool_info.json # Metadata (optional)
        ├── doc.py         # Help (optional)
        └── README.md      # Documentation (optional)
```

### Kiểm tra:

1. Giải nén ZIP
2. Kiểm tra cấu trúc thư mục
3. Đảm bảo có file `.py` chính
4. Test import: `python tool-name.py`

---

## 💡 Tips

1. **Đặt tên tool rõ ràng**: Dùng kebab-case (vd: `backup-folder`)
2. **Version**: Dùng semantic versioning (vd: `1.0.0`)
3. **Description**: Mô tả ngắn gọn, rõ ràng
4. **Tags**: Thêm nhiều tags để dễ tìm kiếm
5. **Category**: Chọn category phù hợp

---

**Tóm lại:** Tool trong registry là metadata + download link. Bạn cần export tool thực tế, upload lên server, rồi thêm vào registry với link đó.

