#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: Copy các file đã thay đổi từ commit cụ thể đến commit mới nhất
Mục đích: Tạo thư mục chứa các file thay đổi theo đúng cấu trúc để upload lên server
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path


def get_config_path():
    """
    Lấy đường dẫn đến file config
    
    Returns:
        Path: Đường dẫn đến file config
    """
    script_dir = Path(__file__).parent
    return script_dir / "copy-changed-files_config.json"


def load_config():
    """
    Load cấu hình từ file config
    
    Returns:
        dict: Dictionary chứa cấu hình, hoặc None nếu không tìm thấy
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️  Lỗi đọc file config: {e}")
        return None


def get_output_folder():
    """
    Lấy đường dẫn thư mục output từ config hoặc hỏi người dùng
    
    Returns:
        str: Đường dẫn thư mục output
    """
    config = load_config()
    
    # Nếu có config và có output_folder trong config
    if config and 'output_folder' in config and config['output_folder']:
        output_folder = config['output_folder']
        print(f"📁 Thư mục output: {output_folder}")
        print("💡 Để thay đổi, chỉnh sửa file config hoặc nhấn 'c' để cấu hình")
        change = input("Nhấn Enter để tiếp tục, hoặc 'c' để cấu hình: ").strip().lower()
        if change == 'c':
            # Hiển thị menu cấu hình nhanh
            print("\n" + "=" * 60)
            print("  CẤU HÌNH THƯ MỤC OUTPUT")
            print("=" * 60)
            print("Nhập đường dẫn thư mục để lưu file export.")
            print("Có thể là đường dẫn tuyệt đối hoặc tương đối.")
            print("Ví dụ:")
            print("  - changed-files-export (thư mục trong thư mục hiện tại)")
            print("  - C:\\exports\\changed-files (đường dẫn tuyệt đối)")
            print("  - ./exports (thư mục exports trong thư mục hiện tại)")
            print("=" * 60)
            new_output = input(f"\nNhập đường dẫn thư mục output (Enter để giữ nguyên '{output_folder}'): ").strip().strip('"')
            if new_output:
                output_folder = new_output
                save_config(output_folder)
                print(f"✓ Đã cập nhật: {output_folder}")
            else:
                print(f"✓ Giữ nguyên: {output_folder}")
            print()
    else:
        # Không có config hoặc không có output_folder trong config
        print("\n" + "=" * 60)
        print("  CẤU HÌNH THƯ MỤC OUTPUT")
        print("=" * 60)
        print("Nhập đường dẫn thư mục để lưu file export.")
        print("Có thể là đường dẫn tuyệt đối hoặc tương đối.")
        print("Ví dụ:")
        print("  - changed-files-export (thư mục trong thư mục hiện tại)")
        print("  - C:\\exports\\changed-files (đường dẫn tuyệt đối)")
        print("  - ./exports (thư mục exports trong thư mục hiện tại)")
        print("=" * 60)
        output_folder = input("Nhập đường dẫn thư mục output (Enter để dùng mặc định 'changed-files-export'): ").strip().strip('"')
        if not output_folder:
            output_folder = "changed-files-export"
        
        # Tự động lưu config
        save_config(output_folder)
        print(f"✓ Đã lưu cấu hình: {output_folder}")
        print()
    
    return output_folder


def save_config(output_folder):
    """
    Lưu cấu hình vào file config
    
    Args:
        output_folder (str): Đường dẫn thư mục output
    """
    config_path = get_config_path()
    config = {
        'output_folder': output_folder
    }
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✓ Đã lưu cấu hình vào: {config_path}")
    except IOError as e:
        print(f"⚠️  Không thể lưu config: {e}")


def print_header():
    """In header của script"""
    print("=" * 50)
    print("  SCRIPT COPY FILE THAY ĐỔI THEO COMMIT")
    print("=" * 50)
    print()


def get_default_htdocs_path():
    """
    Lấy đường dẫn htdocs mặc định
    
    Returns:
        str: Đường dẫn htdocs mặc định (C:\\xampp\\htdocs)
    """
    return r"C:\xampp\htdocs"


def list_projects(htdocs_path):
    """
    Liệt kê các dự án trong thư mục htdocs
    
    Args:
        htdocs_path (str): Đường dẫn thư mục htdocs
        
    Returns:
        list: Danh sách tên dự án
    """
    projects = []
    
    if not os.path.exists(htdocs_path):
        return projects
    
    try:
        for item in os.listdir(htdocs_path):
            item_path = os.path.join(htdocs_path, item)
            if os.path.isdir(item_path):
                # Bỏ qua các thư mục đặc biệt
                if item.lower() not in ['cgi-bin', 'webalizer', 'usage']:
                    projects.append(item)
    except Exception as e:
        print(f"⚠️  Lỗi đọc thư mục htdocs: {e}")
    
    return sorted(projects)


def validate_git_repository(project_path):
    """
    Kiểm tra đường dẫn có phải là Git repository không
    
    Args:
        project_path (Path): Đường dẫn đến dự án
        
    Returns:
        bool: True nếu là Git repository hợp lệ, False nếu không
    """
    # Kiểm tra đường dẫn có tồn tại không
    if not project_path.exists():
        print(f"❌ Lỗi: Đường dẫn '{project_path}' không tồn tại!")
        return False

    # Kiểm tra có phải là thư mục không
    if not project_path.is_dir():
        print(f"❌ Lỗi: '{project_path}' không phải là thư mục!")
        return False

    # Kiểm tra có phải là Git repository không
    git_dir = project_path / ".git"
    if not git_dir.exists():
        print(f"❌ Lỗi: '{project_path}' không phải là Git repository!")
        print("💡 Đảm bảo thư mục đã được khởi tạo Git: git init")
        return False

    return True


def get_project_path():
    """
    Hỏi người dùng chọn dự án từ htdocs hoặc nhập đường dẫn tùy chỉnh

    Returns:
        Path: Đường dẫn đến thư mục dự án

    Giải thích:
    - Thử tìm và liệt kê các dự án trong htdocs
    - Cho phép người dùng chọn dự án theo số thứ tự
    - Hoặc cho phép nhập đường dẫn tùy chỉnh
    - Kiểm tra đường dẫn có tồn tại không
    - Kiểm tra có phải là Git repository không
    - Trả về Path object nếu hợp lệ
    """
    # Thử lấy danh sách dự án từ htdocs
    htdocs_path = get_default_htdocs_path()
    projects = list_projects(htdocs_path)
    
    # Hiển thị danh sách dự án nếu có
    if projects and os.path.exists(htdocs_path):
        print("\n" + "=" * 60)
        print("  DANH SACH DU AN TRONG HTDOCS")
        print("=" * 60)
        print(f"📁 Đường dẫn: {htdocs_path}\n")
        
        for idx, project in enumerate(projects, start=1):
            project_path = os.path.join(htdocs_path, project)
            # Kiểm tra xem có phải Git repo không để hiển thị icon
            git_check = Path(project_path) / ".git"
            git_icon = "✓" if git_check.exists() else "⚠️"
            print(f"  {idx}. {git_icon} {project}")
        
        print("\n" + "-" * 60)
        print("HƯỚNG DẪN:")
        print("  [số]      - Chọn dự án theo số thứ tự")
        print("  [đường dẫn] - Nhập đường dẫn dự án tùy chỉnh")
        print("=" * 60)
        print()
        
        choice = input("Chọn dự án hoặc nhập đường dẫn: ").strip().strip('"')
        
        if not choice:
            print("❌ Lỗi: Bạn phải chọn dự án hoặc nhập đường dẫn!")
            sys.exit(1)
        
        # Kiểm tra xem có phải là số không
        try:
            project_idx = int(choice)
            if 1 <= project_idx <= len(projects):
                # Chọn dự án từ danh sách
                selected_project = projects[project_idx - 1]
                project_path_input = os.path.join(htdocs_path, selected_project)
                print(f"✓ Đã chọn dự án: {selected_project}")
            else:
                print(f"❌ Lỗi: Số thứ tự không hợp lệ! Vui lòng chọn từ 1 đến {len(projects)}")
                sys.exit(1)
        except ValueError:
            # Không phải số, coi như đường dẫn tùy chỉnh
            project_path_input = choice
    else:
        # Không có dự án trong htdocs hoặc htdocs không tồn tại
        if not os.path.exists(htdocs_path):
            print(f"ℹ️  Không tìm thấy thư mục htdocs tại: {htdocs_path}")
        else:
            print(f"ℹ️  Không tìm thấy dự án nào trong: {htdocs_path}")
        print()
        project_path_input = input("Nhập đường dẫn dự án (ví dụ: C:\\xampp\\htdocs\\mitsuheavy-ecommerce): ").strip().strip('"')
        
        if not project_path_input:
            print("❌ Lỗi: Bạn phải nhập đường dẫn dự án!")
            sys.exit(1)

    # Chuyển đổi sang Path object
    project_path = Path(project_path_input).resolve()

    # Kiểm tra và validate Git repository
    if not validate_git_repository(project_path):
        sys.exit(1)

    print(f"✓ Dự án hợp lệ: {project_path}")
    print()
    return project_path


def get_user_input():
    """
    Bước 1: Hỏi người dùng nhập commit ID

    Returns:
        tuple: (commit_start, commit_end)

    Giải thích:
    - Nhận input từ người dùng về commit bắt đầu (bắt buộc)
    - Nhận input commit kết thúc (mặc định là HEAD)
    """
    # Nhập commit bắt đầu
    commit_start = input("Nhập commit ID bắt đầu (ví dụ: 9d172f6): ").strip()
    if not commit_start:
        print("❌ Lỗi: Bạn phải nhập commit ID bắt đầu!")
        sys.exit(1)

    # Nhập commit kết thúc
    commit_end_input = input("Nhập commit ID kết thúc (Enter để chọn HEAD - commit mới nhất): ").strip()
    if not commit_end_input:
        commit_end = "HEAD"
        print("✓ Sử dụng commit kết thúc: HEAD (commit mới nhất)")
    else:
        commit_end = commit_end_input

    print()
    return commit_start, commit_end


def run_git_command(command, cwd=None):
    """
    Chạy lệnh git và trả về kết quả

    Args:
        command (list): Danh sách lệnh git
        cwd (Path): Thư mục làm việc (working directory)

    Returns:
        tuple: (success, output)

    Giải thích:
    - Chạy lệnh git bằng subprocess trong thư mục cwd
    - Bắt lỗi nếu lệnh thất bại
    - Trả về True/False và output
    """
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
    """
    Bước 2: Kiểm tra commit ID có tồn tại không

    Args:
        commit_id (str): Commit ID cần kiểm tra
        project_path (Path): Đường dẫn đến dự án

    Returns:
        bool: True nếu commit hợp lệ, False nếu không

    Giải thích:
    - Sử dụng git rev-parse để verify commit
    - Chạy lệnh trong thư mục project_path
    - Nếu commit không tồn tại, git sẽ trả về lỗi
    """
    success, _ = run_git_command(['git', 'rev-parse', '--verify', commit_id], cwd=project_path)
    return success


def normalize_commit_id(commit_id, project_path):
    """
    Chuẩn hóa commit ID về full hash để so sánh

    Args:
        commit_id (str): Commit ID (có thể là short hash, HEAD, etc.)
        project_path (Path): Đường dẫn đến dự án

    Returns:
        str: Full commit hash, hoặc None nếu không hợp lệ
    """
    success, output = run_git_command(['git', 'rev-parse', commit_id], cwd=project_path)
    if success:
        return output.strip()
    return None


def get_changed_files(commit_start, commit_end, project_path):
    """
    Bước 3: Lấy danh sách các file đã thay đổi

    Args:
        commit_start (str): Commit bắt đầu
        commit_end (str): Commit kết thúc
        project_path (Path): Đường dẫn đến dự án

    Returns:
        list: Danh sách file đã thay đổi

    Giải thích:
    - Sử dụng git diff --name-only để lấy tên file
    - --diff-filter=d để loại bỏ file đã xóa
    - Chạy lệnh trong thư mục project_path
    - Trả về danh sách file dạng list
    """
    success, output = run_git_command([
        'git', 'diff', '--name-only', '--diff-filter=d',
        f'{commit_start}..{commit_end}'
    ], cwd=project_path)

    if not success:
        print(f"❌ Lỗi khi lấy danh sách file: {output}")
        sys.exit(1)

    if not output:
        return []

    return output.split('\n')


def create_export_folder(folder_name, project_name):
    """
    Bước 4: Tạo thư mục export với tên dự án

    Args:
        folder_name (str): Tên thư mục output gốc
        project_name (str): Tên dự án (để tạo thư mục con)

    Returns:
        Path: Đường dẫn đến thư mục export cuối cùng (folder_name/project_name)

    Giải thích:
    - Tạo thư mục output gốc nếu chưa có
    - Tạo thư mục con với tên dự án bên trong
    - Nếu là thư mục export cũ (có file danh-sach-file-thay-doi.txt), xóa nội dung cũ
    - Nếu không phải thư mục export cũ, chỉ tạo thư mục (không xóa gì)
    """
    # Tạo đường dẫn: folder_name/project_name
    base_path = Path(folder_name).resolve()
    export_path = base_path / project_name

    # Tạo thư mục gốc nếu chưa có
    base_path.mkdir(parents=True, exist_ok=True)

    # Kiểm tra thư mục export (có tên dự án) có tồn tại không
    if export_path.exists() and export_path.is_dir():
        # Kiểm tra xem có phải là thư mục export cũ không (có file danh-sach-file-thay-doi.txt)
        old_list_file = export_path / "danh-sach-file-thay-doi.txt"
        
        if old_list_file.exists():
            # Đây là thư mục export cũ, xóa nội dung bên trong (an toàn hơn)
            print(f"🗑️  Đang xóa nội dung export cũ...")
            try:
                # Xóa từng item bên trong thư mục, không xóa thư mục gốc
                for item in export_path.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    except Exception as e:
                        print(f"⚠️  Không thể xóa {item.name}: {e}")
                print(f"✓ Đã xóa nội dung export cũ")
            except Exception as e:
                print(f"⚠️  Lỗi khi xóa nội dung cũ: {e}")
                print(f"💡 Tiếp tục với thư mục hiện tại...")
        else:
            # Không phải thư mục export cũ, chỉ tạo thư mục (không xóa gì)
            print(f"ℹ️  Thư mục đã tồn tại, sẽ thêm file export vào đây")
    else:
        # Tạo thư mục mới
        export_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Tạo thư mục: {export_path}")
    
    print()
    return export_path


def copy_files(changed_files, output_folder, project_path):
    """
    Bước 5: Copy từng file vào thư mục đích với cấu trúc giống gốc

    Args:
        changed_files (list): Danh sách file cần copy
        output_folder (str): Thư mục đích
        project_path (Path): Đường dẫn đến dự án

    Returns:
        tuple: (copied_count, skipped_count, copied_file_paths)

    Giải thích:
    - Duyệt qua từng file trong danh sách
    - File gốc nằm trong project_path
    - Tạo thư mục cha nếu chưa có
    - Copy file giữ nguyên cấu trúc thư mục
    - Đếm số file đã copy và bỏ qua
    - Thu thập danh sách đường dẫn file đã copy (đường dẫn tuyệt đối)
    """
    copied_count = 0
    skipped_count = 0
    copied_file_paths = []

    for file_path in changed_files:
        # Đường dẫn file gốc (trong thư mục dự án)
        source_path = project_path / file_path

        # Đường dẫn file đích (giữ nguyên cấu trúc)
        destination_path = Path(output_folder) / file_path

        # Kiểm tra file có tồn tại không
        if source_path.exists():
            # Tạo thư mục cha nếu chưa có
            destination_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source_path, destination_path)
            print(f"✓ [OK] {file_path}")
            
            # Lưu đường dẫn tuyệt đối của file đã copy
            copied_file_paths.append(str(destination_path.resolve()))
            copied_count += 1
        else:
            print(f"⚠️  [SKIP] {file_path} (file không tồn tại)")
            skipped_count += 1

    return copied_count, skipped_count, copied_file_paths


def save_file_list(changed_files, output_folder):
    """
    Bước 6: Xuất danh sách file đã copy ra file text

    Args:
        changed_files (list): Danh sách file đã thay đổi
        output_folder (str): Thư mục đích

    Giải thích:
    - Tạo file text chứa danh sách tất cả file đã copy
    - Giúp người dùng kiểm tra và đối chiếu
    """
    list_file = Path(output_folder) / "danh-sach-file-thay-doi.txt"
    with open(list_file, 'w', encoding='utf-8') as f:
        for file_path in changed_files:
            f.write(f"{file_path}\n")

    return str(list_file)


def print_summary(copied_count, skipped_count, output_folder, list_file, copied_file_paths):
    """
    Bước 7: In thông tin tổng kết

    Args:
        copied_count (int): Số file đã copy
        skipped_count (int): Số file đã bỏ qua
        output_folder (str): Thư mục export
        list_file (str): Đường dẫn file danh sách
        copied_file_paths (list): Danh sách đường dẫn file đã copy

    Giải thích:
    - Hiển thị thông tin tổng kết cho người dùng
    - Hướng dẫn cách upload lên server
    - Hiển thị danh sách đường dẫn file đã copy
    """
    print("\n" + "=" * 50)
    print("✓ Hoàn tất!")
    print(f"- Đã copy: {copied_count} file")
    print(f"- Bỏ qua: {skipped_count} file")
    print(f"- Thư mục xuất: {output_folder}")
    print(f"- Danh sách file: {list_file}")
    print("\n🚀 Bạn có thể upload toàn bộ thư mục '{}' lên server bằng FileZilla!".format(output_folder))
    print("\n" + "=" * 50)
    print("📁 ĐƯỜNG DẪN CÁC FILE ĐÃ SAO CHÉP:")
    print("=" * 50)
    if copied_file_paths:
        for i, file_path in enumerate(copied_file_paths, 1):
            print(f"{i}. {file_path}")
    else:
        print("Không có file nào được sao chép.")
    print("=" * 50)
    print()


def main():
    """
    Hàm chính của script

    Giải thích:
    - Điều phối tất cả các bước của script
    - Hỏi đường dẫn dự án, commit ID
    - Xử lý lỗi và thoát khi cần thiết
    - Tạo thư mục export ở vị trí chạy script (không phải trong dự án)
    """
    # Bước 1: In header và lấy đường dẫn dự án
    print_header()
    project_path = get_project_path()

    # Bước 2: Lấy commit ID từ người dùng
    commit_start, commit_end = get_user_input()

    # Bước 3: Kiểm tra commit ID hợp lệ
    print("🔍 Kiểm tra commit ID...")
    if not verify_commit(commit_start, project_path):
        print(f"❌ Lỗi: Commit ID bắt đầu '{commit_start}' không tồn tại!")
        print("💡 Bạn có thể xem danh sách commit bằng lệnh: git log --oneline -20")
        sys.exit(1)

    if commit_end != "HEAD":
        if not verify_commit(commit_end, project_path):
            print(f"❌ Lỗi: Commit ID kết thúc '{commit_end}' không tồn tại!")
            print("💡 Bạn có thể xem danh sách commit bằng lệnh: git log --oneline -20")
            sys.exit(1)

    print("✓ Commit ID hợp lệ!\n")

    # Chuẩn hóa commit ID để so sánh
    normalized_start = normalize_commit_id(commit_start, project_path)
    normalized_end = normalize_commit_id(commit_end, project_path)
    
    # Nếu commit bắt đầu và kết thúc giống nhau, tự động so sánh với commit trước đó
    if normalized_start and normalized_end and normalized_start == normalized_end:
        print(f"ℹ️  Phát hiện commit bắt đầu và kết thúc giống nhau ({commit_start})")
        print(f"💡 Tự động so sánh với commit trước đó ({commit_start}^) để lấy file thay đổi trong commit này...")
        print()
        commit_start = f"{commit_start}^"
    
    # Bước 4: Lấy danh sách file thay đổi
    print(f"📂 Đang lấy danh sách file thay đổi từ commit {commit_start} đến {commit_end}...")
    changed_files = get_changed_files(commit_start, commit_end, project_path)

    if not changed_files:
        print("❌ Không có file nào thay đổi!")
        if normalized_start == normalized_end:
            print("💡 Commit này không có file nào thay đổi so với commit trước đó.")
        sys.exit(0)

    print(f"✓ Tìm thấy {len(changed_files)} file đã thay đổi\n")

    # Bước 5: Lấy đường dẫn thư mục output từ config hoặc hỏi người dùng
    base_output_folder = get_output_folder()
    
    # Lấy tên dự án từ đường dẫn
    project_name = project_path.name
    
    # Tạo thư mục export với tên dự án (base_output_folder/project_name)
    export_folder = create_export_folder(base_output_folder, project_name)
    export_folder_str = str(export_folder)

    # Bước 6: Copy files
    print("📋 Đang copy file...\n")
    copied_count, skipped_count, copied_file_paths = copy_files(changed_files, export_folder_str, project_path)

    # Bước 7: Lưu danh sách file
    list_file = save_file_list(changed_files, export_folder_str)

    # Bước 8: In tổng kết
    print_summary(copied_count, skipped_count, export_folder_str, list_file, copied_file_paths)


# Chạy script
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Script đã bị hủy bởi người dùng!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        sys.exit(1)

