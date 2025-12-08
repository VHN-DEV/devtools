# GitLab Commits Export - Xuất commits ra Excel

## Mô tả

Tool xuất danh sách commits từ Git repository ra file Excel với định dạng đẹp. Hỗ trợ lọc theo thời gian, tác giả, branch, và phân loại commit tăng ca (ngoài giờ làm việc).

## Tính năng

✅ Xuất commits ra file Excel với định dạng đẹp
✅ Lọc theo thời gian (since/until)
✅ Lọc theo tác giả
✅ Lọc theo branch
✅ Lọc theo keyword trong commit message
✅ Phân loại commit tăng ca (ngoài 8:00-17:30)
✅ Hiển thị thống kê chi tiết
✅ Hỗ trợ merge commits và child commits

## Yêu cầu

```bash
pip install openpyxl
```

**Quan trọng**: Phải chạy tool trong thư mục Git repository.

## Cách sử dụng

### Chạy từ menu chính

```bash
devtools
# Chọn tool "gitlab-commits-export"
```

### Chạy trực tiếp

```bash
cd /path/to/git/repository
python tools/py/gitlab-commits-export/gitlab-commits-export.py
```

## Hướng dẫn chi tiết

### 1. Chuẩn bị

1. Mở terminal/command prompt
2. Di chuyển đến thư mục Git repository cần export
3. Chạy tool

### 2. Cấu hình Export

Tool sẽ yêu cầu các thông tin:

1. **Khoảng thời gian (since/until)**:
   - Từ ngày: `2025-01-01` hoặc `2025-01-01 00:00:00`
   - Đến ngày: `2025-01-31` hoặc `2025-01-31 23:59:59`
   - Enter để dùng mặc định (tất cả commits)

2. **Tác giả (optional)**:
   - Nhập tên tác giả hoặc email
   - Enter để bỏ qua (lấy tất cả tác giả)

3. **Branch (optional)**:
   - Nhập tên branch (vd: `develop`, `main`, `master`)
   - Enter để bỏ qua (lấy tất cả branches)

4. **Keyword trong commit message (optional)**:
   - Nhập từ khóa cần tìm trong commit message
   - Enter để bỏ qua

5. **Bao gồm commit trong giờ làm việc**:
   - `y`: Có (mặc định)
   - `n`: Không (chỉ lấy commit tăng ca)

### 3. Kết quả

Tool sẽ:
1. Lấy danh sách commits từ Git
2. Phân loại commit tăng ca (ngoài 8:00-17:30)
3. Export ra file Excel với định dạng đẹp
4. Hiển thị thống kê trên console

**File Excel chứa:**
- **Tác giả**: Tên và email người commit
- **Ngày**: Ngày commit
- **Thời gian**: Giờ commit (để xác định tăng ca)
- **Mã commit**: Hash của commit (short)
- **Event**: Loại commit (merge/commit)
- **Type**: Phân loại (Trong giờ/Tăng ca)
- **Branch**: Branch chứa commit
- **Nội dung commit**: Commit message
- **OP Link**: Link tới issue (nếu có {OP#1234} trong message)
- **Child commits**: Danh sách commits con (nếu là merge commit)

## Giờ làm việc mặc định

- **Bắt đầu**: 8:00
- **Kết thúc**: 17:30
- **Commit ngoài giờ này** được tính là **tăng ca**

## Ví dụ

### Export tất cả commits

```
Thư mục: ./my-project (Git repo)
Từ ngày: [Enter] (tất cả)
Đến ngày: [Enter] (tất cả)
Tác giả: [Enter] (tất cả)
Branch: [Enter] (tất cả)
Keyword: [Enter] (tất cả)
Bao gồm commit trong giờ: y

→ Xuất file: commits_20250131.xlsx
→ Tổng số: 165 commits
→ Trong giờ: 120 commits
→ Tăng ca: 45 commits
```

### Export theo thời gian

```
Thư mục: ./my-project
Từ ngày: 2025-01-01
Đến ngày: 2025-01-31
Tác giả: [Enter]
Branch: develop
Keyword: [Enter]
Bao gồm commit trong giờ: y

→ Xuất file: commits_20250131.xlsx
→ Tổng số: 85 commits
→ Trong giờ: 60 commits
→ Tăng ca: 25 commits
```

### Export chỉ tăng ca

```
Thư mục: ./my-project
Từ ngày: 2025-01-01
Đến ngày: 2025-01-31
Tác giả: [Enter]
Branch: [Enter]
Keyword: [Enter]
Bao gồm commit trong giờ: n

→ Xuất file: commits_20250131.xlsx
→ Chỉ tăng ca: 45 commits
```

### Export theo tác giả

```
Thư mục: ./my-project
Từ ngày: 2025-01-01
Đến ngày: 2025-01-31
Tác giả: john.doe@example.com
Branch: [Enter]
Keyword: [Enter]
Bao gồm commit trong giờ: y

→ Xuất file: commits_20250131.xlsx
→ Tổng số: 35 commits (chỉ của john.doe@example.com)
```

### Export theo keyword

```
Thư mục: ./my-project
Từ ngày: 2025-01-01
Đến ngày: 2025-01-31
Tác giả: [Enter]
Branch: [Enter]
Keyword: bugfix
Bao gồm commit trong giờ: y

→ Xuất file: commits_20250131.xlsx
→ Tổng số: 20 commits (chỉ commits có từ "bugfix")
```

## Định dạng file Excel

File Excel được tạo với:
- **Định dạng đẹp**: Màu sắc, border, alignment
- **Phân loại rõ ràng**: Màu khác nhau cho commit trong giờ/tăng ca
- **Dễ đọc**: Cột rõ ràng, dễ filter, sort
- **Thông tin đầy đủ**: Tất cả thông tin cần thiết về commit

## Use case phổ biến

- **Báo cáo công việc**: Xuất commits để báo cáo công việc đã làm
- **Theo dõi tăng ca**: Xem số lượng commit tăng ca trong tháng
- **Phân tích dự án**: Phân tích commits theo tác giả, thời gian
- **Audit**: Kiểm tra lịch sử commits của dự án
- **Reporting**: Tạo báo cáo commits cho manager/client

## Tips

### Lọc commits:
- **Theo thời gian**: Dùng để báo cáo theo tháng/quý
- **Theo tác giả**: Dùng để báo cáo cá nhân
- **Theo branch**: Dùng để phân tích từng branch
- **Theo keyword**: Dùng để tìm commits liên quan đến tính năng cụ thể

### Tăng ca:
- Commit ngoài 8:00-17:30 được tính là tăng ca
- Có thể tắt commit trong giờ để chỉ xem tăng ca
- Hữu ích cho việc tracking overtime

### File Excel:
- Dễ filter, sort trong Excel
- Có thể pivot table để phân tích
- Có thể export sang PDF để báo cáo

## Lưu ý

- **Git repository**: Phải chạy trong thư mục Git repository
- **Thời gian**: Định dạng thời gian: `YYYY-MM-DD` hoặc `YYYY-MM-DD HH:MM:SS`
- **Branch**: Phải là branch tồn tại trong repository
- **Tác giả**: Có thể dùng tên hoặc email
- **Keyword**: Tìm kiếm không phân biệt chữ hoa/thường
- **File Excel**: File được lưu trong thư mục hiện tại với tên `commits_YYYYMMDD.xlsx`

