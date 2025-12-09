# PDF Tools - Xử lý PDF

## Mô tả

Tool xử lý PDF đa năng: gộp (merge), tách (split), nén (compress), chuyển sang ảnh, và trích xuất text từ PDF.

## Tính năng

✅ Merge nhiều PDF thành 1 file
✅ Split PDF thành nhiều file nhỏ
✅ Compress PDF giảm dung lượng
✅ Convert PDF sang image (JPG, PNG)
✅ Extract text từ PDF
✅ Rotate pages
✅ Xử lý hàng loạt nhiều PDF

## Yêu cầu

```bash
pip install PyPDF2 pdf2image Pillow
```

**Quan trọng**: Cần cài đặt poppler-utils cho chức năng convert PDF sang ảnh

### Cài đặt poppler-utils

**Windows:**
1. Download từ https://github.com/oschwartz10612/poppler-windows/releases
2. Giải nén và thêm vào PATH

**Linux:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "pdf-tools"
```

### Chạy trực tiếp

```bash
python tools/py/pdf-tools/pdf-tools.py
```

## Hướng dẫn chi tiết

### 1. Chọn chức năng

- **1**: Merge PDF (gộp nhiều PDF thành 1)
- **2**: Split PDF (tách PDF thành nhiều file)
- **3**: Compress PDF (nén giảm dung lượng)
- **4**: Convert PDF sang ảnh (PDF → JPG/PNG)
- **5**: Extract text từ PDF
- **6**: Rotate pages

### 2. Merge PDF

1. Chọn nhiều file PDF (theo thứ tự cần gộp)
2. Chọn file output
3. Xử lý và chờ hoàn thành

**Ví dụ:**
```
File: doc1.pdf, doc2.pdf, doc3.pdf
Output: merged.pdf
→ Gộp thành công: merged.pdf (5.2 MB)
```

### 3. Split PDF

1. Chọn file PDF cần tách
2. Nhập trang cần tách:
   - Theo range: `1-5, 10-15, 20-25`
   - Theo số trang mỗi file: `5` (mỗi file 5 trang)
3. Chọn thư mục output
4. Xử lý và chờ hoàn thành

**Ví dụ:**
```
Input: document.pdf (20 trang)
Split: 1-5, 10-15
Output: 
  - document_pages_1-5.pdf
  - document_pages_10-15.pdf
```

### 4. Compress PDF

1. Chọn file PDF hoặc thư mục chứa PDF
2. Chọn mức nén (Low/Medium/High)
3. Chọn thư mục output
4. Xử lý và chờ hoàn thành

**Lưu ý**: Nén có thể làm giảm chất lượng hình ảnh trong PDF

### 5. Convert PDF sang ảnh

1. Chọn file PDF hoặc thư mục chứa PDF
2. Chọn format ảnh (jpg, png)
3. Chọn DPI (mặc định: 200)
   - 150 DPI: Chất lượng thấp, file nhỏ
   - 200 DPI: Chất lượng tốt (mặc định)
   - 300 DPI: Chất lượng cao, file lớn
4. Chọn thư mục output
5. Xử lý và chờ hoàn thành

**Ví dụ:**
```
Input: document.pdf (10 trang)
Format: jpg
DPI: 200
Output:
  - document_page_1.jpg
  - document_page_2.jpg
  - ...
  - document_page_10.jpg
```

### 6. Extract Text

1. Chọn file PDF
2. Chọn file output (text file)
3. Xử lý và chờ hoàn thành

**Lưu ý**: Kết quả phụ thuộc vào loại PDF (text-based hay scanned)

### 7. Rotate Pages

1. Chọn file PDF
2. Chọn góc xoay (90, 180, 270 độ)
3. Chọn trang cần xoay (all hoặc range)
4. Chọn file output
5. Xử lý và chờ hoàn thành

## Tips

### Merge PDF:
- Sắp xếp file theo thứ tự cần gộp trước khi merge
- File lớn có thể mất nhiều thời gian

### Split PDF:
- Tách theo range linh hoạt hơn
- Tách theo số trang mỗi file tiện cho việc chia nhỏ

### Compress PDF:
- Cân bằng giữa dung lượng và chất lượng
- Nén cao có thể làm mờ hình ảnh
- Test với một file trước khi nén hàng loạt

### Convert PDF:
- DPI cao hơn = chất lượng tốt hơn nhưng file lớn hơn
- 200 DPI phù hợp cho hầu hết trường hợp
- PNG cho chất lượng tốt hơn nhưng file lớn hơn JPG

## Use case phổ biến

- Gộp nhiều PDF thành 1 file để gửi email
- Tách PDF theo trang để upload từng phần
- Nén PDF để upload nhanh hơn
- Chuyển PDF sang ảnh để preview trên web
- Extract text từ PDF để chỉnh sửa
- Xoay trang PDF bị ngược

## Lưu ý

- **poppler-utils**: Cần cài đặt cho chức năng convert PDF sang ảnh
- **Chất lượng**: Nén và convert có thể làm giảm chất lượng
- **PDF scanned**: Extract text từ PDF scanned (ảnh) cần OCR tool khác
- **File lớn**: PDF lớn có thể mất nhiều thời gian xử lý
- **Backup**: Luôn giữ bản gốc trước khi xử lý

## Ví dụ thực tế

### Gộp nhiều PDF

```
File: 
  - chapter1.pdf (2 MB)
  - chapter2.pdf (3 MB)
  - chapter3.pdf (2.5 MB)
Output: book.pdf (7.5 MB)
→ Gộp thành công!
```

### Tách PDF

```
Input: report.pdf (50 trang)
Split: Mỗi file 10 trang
Output:
  - report_pages_1-10.pdf
  - report_pages_11-20.pdf
  - report_pages_21-30.pdf
  - report_pages_31-40.pdf
  - report_pages_41-50.pdf
```

### Nén PDF

```
Input: document.pdf (10 MB)
Compress: Medium
Output: document_compressed.pdf (3 MB)
→ Giảm 70% dung lượng
```

