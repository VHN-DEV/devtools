#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copy Changed Files Tool - Sao chép file thay đổi theo Git
- Copy file thay đổi giữa 2 commit cụ thể
- Copy file hiện tại đang thay đổi (git status)

LƯU Ý: Script này sử dụng tiếng Việt có dấu.
Trên Windows, để hiển thị đúng:
1. Mở Command Prompt (cmd.exe)
2. Chạy: chcp 65001
3. Sau đó chạy: python tools/py/copy-changed-files/copy-changed-files.py

Hoặc sử dụng PowerShell với UTF-8:
- $env:PYTHONIOENCODING = "utf-8"
- python tools/py/copy-changed-files/copy-changed-files.py
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime

# Đảm bảo UTF-8 encoding cho Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def get_config_path():
    """Lấy đường dẫn đến file config"""
    script_dir = Path(__file__).parent
    return script_dir / "copy-changed-files_config.json"


def load_config():
    """Load cấu hình từ file config"""
    config_path = get_config_path()

    if not config_path.exists():
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def get_output_folder():
    """Lấy đường dẫn thư mục output từ config hoặc hỏi người dùng"""
    config = load_config()

    if config and 'output_folder' in config and config['output_folder']:
        output_folder = config['output_folder']
        print(f"[DIR] Thư mục output: {output_folder}")
        print("[TIP] Nhấn 'c' để cấu hình hoặc Enter để tiếp tục")
        change = input("Nhấn Enter để tiếp tục, hoặc 'c' để cấu hình: ").strip().lower()
        if change == 'c':
            print("\n" + "=" * 60)
            print("  CẤU HÌNH THƯ MỤC OUTPUT")
            print("=" * 60)
            new_output = input(f"Nhập đường dẫn thư mục output (Enter để giữ nguyên '{output_folder}'): ").strip().strip('"')
            if new_output:
                output_folder = new_output
                save_config(output_folder)
                print(f"[OK] Đã cập nhật: {output_folder}")
            else:
                print(f"[OK] Giữ nguyên: {output_folder}")
            print()
    else:
        print("\n" + "=" * 60)
        print("  CẤU HÌNH THƯ MỤC OUTPUT")
        print("=" * 60)
        output_folder = input("Nhập đường dẫn thư mục output (Enter để dùng mặc định 'changed-files-export'): ").strip().strip('"')
        if not output_folder:
            output_folder = "changed-files-export"

        save_config(output_folder)
        print(f"[OK] Đã lưu cấu hình: {output_folder}")
        print()

    return output_folder


def save_config(output_folder):
    """Lưu cấu hình vào file"""
    config_path = get_config_path()
    config = {'output_folder': output_folder}

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"[OK] Đã lưu cấu hình vào: {config_path}")
    except IOError as e:
        print(f"[!] Không thể lưu config: {e}")


def print_header():
    """In tiêu đề của script"""
    print("=" * 60)
    print("  SCRIPT COPY FILE THAY DOI THEO GIT")
    print("=" * 60)
    print("Chức năng:")
    print("  1. Copy file thay đổi giữa 2 commit cụ thể")
    print("  2. Copy file đã staged (git add)")
    print("  3. Copy file hiện tại đang thay đổi (unstaged)")
    print("  4. Copy tất cả file có thay đổi (staged + unstaged)")
    print("=" * 60)
    print()


def get_default_htdocs_path():
    """Lấy đường dẫn htdocs mặc định"""
    return r"C:\xampp\htdocs"


def list_projects(htdocs_path):
    """Liệt kê các dự án trong thư mục htdocs"""
    projects = []

    if not os.path.exists(htdocs_path):
        return projects

    try:
        for item in os.listdir(htdocs_path):
            item_path = os.path.join(htdocs_path, item)
            if os.path.isdir(item_path):
                if item.lower() not in ['cgi-bin', 'webalizer', 'usage']:
                    projects.append(item)
    except Exception as e:
        print(f"[!] Lỗi đọc thư mục htdocs: {e}")

    return sorted(projects)


def validate_git_repository(project_path):
    """Kiểm tra đường dẫn có phải là Git repository không"""
    if not project_path.exists():
        print(f"[ERROR] Đường dẫn '{project_path}' không tồn tại!")
        return False

    if not project_path.is_dir():
        print(f"[ERROR] '{project_path}' không phải là thư mục!")
        return False

    git_dir = project_path / ".git"
    if not git_dir.exists():
        print(f"[ERROR] '{project_path}' không phải là Git repository!")
        print("[TIP] Đảm bảo thư mục đã được khởi tạo Git: git init")
        return False

    return True


def get_project_path():
    """Hỏi người dùng chọn dự án từ htdocs hoặc nhập đường dẫn tùy chỉnh"""
    htdocs_path = get_default_htdocs_path()
    projects = list_projects(htdocs_path)

    if projects and os.path.exists(htdocs_path):
        print("\n" + "=" * 60)
        print("  DANH SÁCH DỰ ÁN TRONG HTDOCS")
        print("=" * 60)
        print(f"[DIR] Đường dẫn: {htdocs_path}\n")

        for idx, project in enumerate(projects, start=1):
            project_path = os.path.join(htdocs_path, project)
            git_check = Path(project_path) / ".git"
            git_icon = "[OK]" if git_check.exists() else "[!]"
            print(f"  {idx}. {git_icon} {project}")

        print("\n" + "-" * 60)
        print("HƯỚNG DẪN:")
        print("  [số]      - Chọn dự án theo số thứ tự")
        print("  [đường dẫn] - Nhập đường dẫn dự án tùy chỉnh")
        print("=" * 60)
        print()

        choice = input("Chọn dự án hoặc nhập đường dẫn: ").strip().strip('"')

        if not choice:
            print("[ERROR] Bạn phải chọn dự án hoặc nhập đường dẫn!")
            sys.exit(1)

        try:
            project_idx = int(choice)
            if 1 <= project_idx <= len(projects):
                selected_project = projects[project_idx - 1]
                project_path_input = os.path.join(htdocs_path, selected_project)
                print(f"[OK] Đã chọn dự án: {selected_project}")
            else:
                print(f"[ERROR] Số thứ tự không hợp lệ! Vui lòng chọn từ 1 đến {len(projects)}")
                sys.exit(1)
        except ValueError:
            project_path_input = choice
    else:
        if not os.path.exists(htdocs_path):
            print(f"[INFO] Không tìm thấy thư mục htdocs tại: {htdocs_path}")
        else:
            print(f"[INFO] Không tìm thấy dự án nào trong: {htdocs_path}")
        print()
        project_path_input = input("Nhập đường dẫn dự án (ví dụ: C:\\xampp\\htdocs\\my-project): ").strip().strip('"')

        if not project_path_input:
            print("[ERROR] Bạn phải nhập đường dẫn dự án!")
            sys.exit(1)

    project_path = Path(project_path_input).resolve()

    if not validate_git_repository(project_path):
        sys.exit(1)

    print(f"[OK] Dự án hợp lệ: {project_path}")
    print()
    return project_path


def get_user_input():
    """Bước 1: Hỏi người dùng chọn chế độ và nhập commit ID nếu cần"""
    print("\n" + "=" * 60)
    print("  CHỌN CHẾ ĐỘ COPY FILE")
    print("=" * 60)
    print("1. [LIST] Copy file thay đổi theo commit range")
    print("2. [STAGED] Copy file đã staged (git add)")
    print("3. [CURRENT] Copy file hiện tại đang thay đổi (unstaged)")
    print("4. [ALL] Copy tất cả file có thay đổi (staged + unstaged)")
    print("=" * 60)
    print("[TIP] Enter để chọn chế độ 4 (tất cả)")

    choice = input("Chọn chế độ (1-4 hoặc Enter): ").strip()

    # Nếu không chọn gì, mặc định chọn chế độ 4 (tất cả)
    if not choice:
        choice = "4"

    if choice == "1":
        print("\n[LIST] CHẾ ĐỘ: Copy file thay đổi theo commit range")
        print("-" * 50)

        commit_start = input("Nhập commit ID bắt đầu (ví dụ: 9d172f6): ").strip()
        if not commit_start:
            print("[ERROR] Lỗi: Bạn phải nhập commit ID bắt đầu!")
            return get_user_input()  # Đệ quy để chọn lại

        commit_end_input = input("Nhập commit ID kết thúc (Enter để chọn HEAD - commit mới nhất): ").strip()
        if not commit_end_input:
            commit_end = "HEAD"
            print("[OK] Sử dụng commit kết thúc: HEAD (commit mới nhất)")
        else:
            commit_end = commit_end_input

        print()
        return "commit", commit_start, commit_end

    elif choice == "2":
        print("\n[STAGED] CHẾ ĐỘ: Copy file đã staged")
        print("[OK] Sẽ copy các file đã được git add")
        print()
        return "staged", None, None

    elif choice == "3":
        print("\n[CURRENT] CHẾ ĐỘ: Copy file hiện tại đang thay đổi (unstaged)")
        print("[OK] Sẽ copy các file có thay đổi nhưng chưa git add")
        print()
        return "current", None, None

    elif choice == "4":
        print("\n[ALL] CHẾ ĐỘ: Copy tất cả file có thay đổi")
        print("[OK] Sẽ copy tất cả file đã thay đổi (staged + unstaged)")
        print()
        return "all", None, None

    else:
        print("[ERROR] Lỗi: Vui lòng chọn từ 1 đến 4 hoặc Enter!")
        return get_user_input()  # Đệ quy để chọn lại


def run_git_command(command, cwd=None):
    """Chạy lệnh git và trả về kết quả"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            cwd=cwd
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def verify_commit(commit_id, project_path):
    """Bước 2: Kiểm tra commit ID có tồn tại không"""
    success, _ = run_git_command(['git', 'rev-parse', '--verify', commit_id], cwd=project_path)
    return success


def normalize_commit_id(commit_id, project_path):
    """Chuan hoa commit ID ve full hash de so sanh"""
    success, output = run_git_command(['git', 'rev-parse', commit_id], cwd=project_path)
    if success:
        return output.strip()
    return None


def get_changed_files(commit_start, commit_end, project_path):
    """Buoc 3: Lay danh sach cac file da thay doi giua 2 commit"""
    success, output = run_git_command([
        'git', 'diff', '--name-only', '--diff-filter=d',
        f'{commit_start}..{commit_end}'
    ], cwd=project_path)

    if not success:
        print(f"[ERROR] Lỗi khi lấy danh sách file: {output}")
        sys.exit(1)

    if not output:
        return []

    return output.split('\n')


def get_staged_changed_files(project_path):
    """Lấy danh sách các file đã staged (git add)"""
    success, output = run_git_command(['git', 'status', '--porcelain'], cwd=project_path)

    if not success:
        print(f"[ERROR] Lỗi khi lấy danh sách file staged: {output}")
        sys.exit(1)

    if not output:
        return []

    staged_files = []
    for line in output.split('\n'):
        if not line.strip():
            continue

        status = line[:2]
        file_path = line[3:].strip()

        staged_status = status[0]

        # Chỉ lấy file đã được staged (không phải ' ' hoặc '?')
        # Và không phải deleted
        if staged_status not in [' ', '?', 'D']:
            staged_files.append(file_path)

    return staged_files


def get_current_changed_files(project_path):
    """Lấy danh sách các file hiện tại đang thay đổi (git status - chỉ unstaged)"""
    success, output = run_git_command(['git', 'status', '--porcelain'], cwd=project_path)

    if not success:
        print(f"[ERROR] Lỗi khi lấy danh sách file thay đổi hiện tại: {output}")
        sys.exit(1)

    if not output:
        return []

    changed_files = []
    for line in output.split('\n'):
        if not line.strip():
            continue

        status = line[:2]
        file_path = line[3:].strip()

        staged_status = status[0]
        unstaged_status = status[1]

        # Chỉ lấy file có thay đổi unstaged và không phải deleted
        if staged_status in [' ', '?'] and unstaged_status not in [' ', '?', 'D']:
            changed_files.append(file_path)

    return changed_files


def get_all_changed_files(project_path):
    """Lấy danh sách tất cả file có thay đổi (staged + unstaged)"""
    success, output = run_git_command(['git', 'status', '--porcelain'], cwd=project_path)

    if not success:
        print(f"[ERROR] Lỗi khi lấy danh sách tất cả file thay đổi: {output}")
        sys.exit(1)

    if not output:
        return []

    all_changed_files = []
    for line in output.split('\n'):
        if not line.strip():
            continue

        status = line[:2]
        file_path = line[3:].strip()

        staged_status = status[0]
        unstaged_status = status[1]

        # Lấy tất cả file có thay đổi (không phải unmodified) và không phải deleted
        if staged_status != 'D' and unstaged_status != 'D' and (staged_status != ' ' or unstaged_status != ' '):
            all_changed_files.append(file_path)

    return all_changed_files


def create_export_folder(folder_name, project_name):
    """Buoc 4: Tao thu muc export voi ten du an va timestamp"""
    base_path = Path(folder_name).resolve()

    # Tạo timestamp với format YYYY-MM-DD-HH-MM-SS
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # Tạo tên thư mục với format: project_name-YYYY-MM-DD-HH-MM-SS
    folder_with_timestamp = f"{project_name}-{timestamp}"
    export_path = base_path / folder_with_timestamp

    base_path.mkdir(parents=True, exist_ok=True)

    # Vì có timestamp, thư mục sẽ luôn là mới, không cần kiểm tra tồn tại
    export_path.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Tạo thư mục: {export_path}")

    print()
    return export_path


def copy_files(changed_files, output_folder, project_path):
    """Buoc 5: Copy tung file vao thu muc dich voi cau truc giong goc"""
    copied_count = 0
    skipped_count = 0
    copied_file_paths = []

    for file_path in changed_files:
        source_path = project_path / file_path
        destination_path = Path(output_folder) / file_path

        if source_path.exists():
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, destination_path)
            print(f"[OK] [OK] {file_path}")
            copied_file_paths.append(str(destination_path.resolve()))
            copied_count += 1
        else:
            print(f"[!] [SKIP] {file_path} (file không tồn tại)")
            skipped_count += 1

    return copied_count, skipped_count, copied_file_paths


def save_file_list(changed_files, output_folder):
    """Buoc 6: Xuat danh sach file da copy ra file text"""
    list_file = Path(output_folder) / "danh-sach-file-thay-doi.txt"
    with open(list_file, 'w', encoding='utf-8') as f:
        for file_path in changed_files:
            f.write(f"{file_path}\n")

    return str(list_file)


def print_summary(copied_count, skipped_count, output_folder, list_file, copied_file_paths):
    """Buoc 7: In thong tin tong ket"""
    print("\n" + "=" * 50)
    print("[OK] Hoàn tất!")
    print(f"- Đã copy: {copied_count} file")
    print(f"- Bỏ qua: {skipped_count} file")
    print(f"- Thư mục xuất: {output_folder}")
    print(f"- Danh sách file: {list_file}")
    print(f"\n[DEPLOY] Bạn có thể upload toàn bộ thư mục '{output_folder}' lên server bằng FileZilla!")
    print("\n" + "=" * 50)
    print("[DIR] ĐƯỜNG DẪN CÁC FILE ĐÃ SAO CHÉP:")
    print("=" * 50)
    if copied_file_paths:
        for i, file_path in enumerate(copied_file_paths, 1):
            print(f"{i}. {file_path}")
    else:
        print("Không có file nào được sao chép.")
    print("=" * 50)
    print()


def main():
    """Ham chinh cua script"""
    print_header()
    project_path = get_project_path()

    mode, commit_start, commit_end = get_user_input()

    if mode == "commit":
        print("[LIST] Kiểm tra commit ID...")
        if not verify_commit(commit_start, project_path):
            print(f"[ERROR] Lỗi: Commit ID bắt đầu '{commit_start}' không tồn tại!")
            print("[TIP] Bạn có thể xem danh sách commit bằng lệnh: git log --oneline -20")
            sys.exit(1)

        if commit_end != "HEAD":
            if not verify_commit(commit_end, project_path):
                print(f"[ERROR] Lỗi: Commit ID kết thúc '{commit_end}' không tồn tại!")
                print("[TIP] Bạn có thể xem danh sách commit bằng lệnh: git log --oneline -20")
                sys.exit(1)

        print("[OK] Commit ID hợp lệ!\n")

        normalized_start = normalize_commit_id(commit_start, project_path)
        normalized_end = normalize_commit_id(commit_end, project_path)

        if normalized_start and normalized_end and normalized_start == normalized_end:
            print(f"[INFO] Phát hiện commit bắt đầu và kết thúc giống nhau ({commit_start})")
            print(f"[TIP] Tự động so sánh với commit trước đó ({commit_start}^) để lấy file thay đổi trong commit này...")
            print()
            commit_start = f"{commit_start}^"

        print(f"[DIR] Đang lấy danh sách file thay đổi từ commit {commit_start} đến {commit_end}...")
        changed_files = get_changed_files(commit_start, commit_end, project_path)

    elif mode == "staged":
        print("[DIR] Đang lấy danh sách file đã staged...")
        changed_files = get_staged_changed_files(project_path)

    elif mode == "current":
        print("[DIR] Đang lấy danh sách file hiện tại đang thay đổi (unstaged)...")
        changed_files = get_current_changed_files(project_path)

    elif mode == "all":
        print("[DIR] Đang lấy danh sách tất cả file có thay đổi...")
        changed_files = get_all_changed_files(project_path)

    if not changed_files:
        mode_messages = {
            "commit": "không có file nào thay đổi giữa các commit đã chọn",
            "staged": "không có file nào đã được staged",
            "current": "không có file nào đang thay đổi (unstaged)",
            "all": "không có file nào có thay đổi"
        }
        print(f"[ERROR] {mode_messages.get(mode, 'Không có file nào thay đổi')}!")
        sys.exit(0)

    print(f"[OK] Tìm thấy {len(changed_files)} file đã thay đổi\n")

    base_output_folder = get_output_folder()
    project_name = project_path.name
    export_folder = create_export_folder(base_output_folder, project_name)
    export_folder_str = str(export_folder)

    print("[LIST] Đang copy file...\n")
    copied_count, skipped_count, copied_file_paths = copy_files(changed_files, export_folder_str, project_path)

    list_file = save_file_list(changed_files, export_folder_str)

    print_summary(copied_count, skipped_count, export_folder_str, list_file, copied_file_paths)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[ERROR] Script đã bị hủy bỏ bởi người dùng!")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Lỗi: {e}")
        sys.exit(1)