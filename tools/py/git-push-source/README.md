# Git Push Source Tool

Tool đa dụng để quản lý Git, tự động hóa quá trình commit và push source code lên repository.

## Tính năng

### Quản lý Repository
- ✅ Quản lý nhiều repository (lưu danh sách yêu thích)
- ✅ Clone repository từ remote
- ✅ Khởi tạo Git repository mới
- ✅ Thiết lập remote repository
- ✅ Xem trạng thái Git (files, branch, remotes)
- ✅ Lưu lịch sử thao tác

### Thao tác Code
- ✅ Add files và commit
- ✅ Push code lên remote
- ✅ Pull code từ remote
- ✅ Fetch từ remote
- ✅ Thực hiện đầy đủ (add + commit + push) trong một lần

### Quản lý Branch
- ✅ Tạo branch mới
- ✅ Chuyển branch (switch)
- ✅ Xem danh sách branches
- ✅ Xóa branch

### Tính năng Nâng cao
- ✅ Merge branch
- ✅ Rebase branch
- ✅ Stash changes
- ✅ Pop stash
- ✅ Xem danh sách remotes

## Yêu cầu

- Git đã được cài đặt và có trong PATH
- Quyền truy cập repository (Personal Access Token hoặc SSH key)

## Sử dụng

### Interactive Mode

```bash
python git-push-source.py
```

Menu tương tác với 21 chức năng, được tổ chức theo nhóm:
- Quản lý Repository (1-5)
- Thao tác Code (6-10)
- Quản lý Branch (11-14)
- Tính năng Nâng cao (15-19)
- Khác (20-21)

### CLI Mode

```bash
# Clone repository
python git-push-source.py --clone --repo https://github.com/user/repo --path ./project

# Add, commit và push
python git-push-source.py --add . --commit "Update code" --push --branch main

# Xem trạng thái
python git-push-source.py --status
```

## Quản lý Repository

Tool tự động lưu danh sách repository đã sử dụng vào file `git_repos_config.json`:
- Lưu repository yêu thích để dùng lại nhanh
- Xem lịch sử 100 thao tác gần nhất
- Chuyển đổi giữa các repository dễ dàng

## Repository mặc định

Tool được cấu hình sẵn với repository:
- `https://github.com/VHN-DEV/laravel-botble-cms`

## Lưu ý

- Cần có quyền write vào repository
- Kiểm tra kỹ files trước khi commit
- Không commit files nhạy cảm (.env, keys, passwords)
- Không nên force push lên main/master branch
- Cẩn thận khi merge/rebase để tránh conflict
- Backup code quan trọng trước khi thực hiện các thao tác nguy hiểm

