#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menu chính - Giao diện quản lý và chạy các tools

Mục đích: Entry point cho menu system
Lý do: Dễ dàng truy cập và quản lý tools
"""

import os
import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding - Improved
if sys.platform == 'win32':
    try:
        # Thiết lập UTF-8 cho console output
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        
        # Thiết lập UTF-8 cho console input (quan trọng cho EOFError)
        sys.stdin.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        # Fallback: sử dụng wrapper
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

# Import ToolManager từ module riêng
from .tool_manager import ToolManager
from utils.colors import Colors
from utils.format import print_separator
from utils.helpers import print_welcome_tip, print_command_suggestions, suggest_command, strip_ansi
from utils.logger import clear_logs, get_log_files


def get_current_version():
    """
    Lấy version hiện tại của package
    
    Returns:
        str: Version hiện tại hoặc "Unknown" nếu không tìm thấy
    
    Giải thích:
    - Thử lấy từ package đã cài đặt trước (chính xác hơn)
    - Nếu không có, đọc từ pyproject.toml
    """
    # Thử lấy từ package đã cài đặt
    try:
        import importlib.metadata
        version = importlib.metadata.version("DevTools")
        return version
    except Exception:
        pass
    
    # Thử lấy từ pkg_resources (setuptools cũ)
    try:
        import pkg_resources
        version = pkg_resources.get_distribution("DevTools").version
        return version
    except Exception:
        pass
    
    # Fallback: Đọc từ pyproject.toml
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"
    
    if pyproject_path.exists():
        # Thử dùng tomllib (Python 3.11+)
        try:
            import tomllib
            with open(pyproject_path, 'rb') as f:
                data = tomllib.load(f)
                version = data.get('project', {}).get('version', 'Unknown')
                if version != 'Unknown':
                    return version
        except ImportError:
            # Python < 3.11, không có tomllib, dùng regex
            pass
        except Exception:
            pass
        
        # Nếu không có tomllib hoặc lỗi, dùng regex
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Tìm pattern: version = "1.0.0"
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
    
    return "Unknown"


def show_version():
    """Hiển thị danh sách các version và cho phép chuyển version"""
    version = get_current_version()
    
    print()
    print_separator("═", 70, Colors.INFO)
    print(Colors.bold(f"📦 DANH SÁCH PHIÊN BẢN"))
    print_separator("═", 70, Colors.INFO)
    print()
    
    project_root = Path(__file__).parent.parent
    git_dir = project_root / ".git"
    
    # Kiểm tra xem có phải git repository không
    if not git_dir.exists():
        print(f"   {Colors.info('DevTools')}: {Colors.bold(Colors.success(version))}")
        print()
        print_separator("═", 70, Colors.INFO)
        print()
        input(Colors.muted("Nhấn Enter để quay lại..."))
        return
    
    try:
        # Lấy branch hiện tại
        current_branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=10
        )
        current_branch = current_branch_result.stdout.strip() if current_branch_result.returncode == 0 else "Unknown"
        
        # Lấy danh sách các branch version (tool-v*)
        branch_list_result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Danh sách các version branch (chỉ lấy tool-v*)
        available_versions = []
        
        if branch_list_result.returncode == 0:
            for line in branch_list_result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Xử lý branch name
                branch_name = None
                
                # Remote branch: remotes/origin/tool-v1.0.0
                if line.startswith('remotes/'):
                    # Lấy phần sau remotes/origin/ hoặc remotes/origin/develop/
                    parts = line.split('/')
                    if len(parts) >= 3:
                        # Bỏ qua 'remotes', 'origin' và các phần khác, lấy phần cuối
                        branch_name = parts[-1]
                else:
                    # Local branch: * tool-v1.0.0 hoặc   tool-v1.0.0
                    branch_name = line.lstrip('*').strip()
                
                if not branch_name:
                    continue
                
                # Chỉ thêm các branch version (tool-v*)
                if branch_name.startswith('tool-v'):
                    if branch_name not in available_versions:
                        available_versions.append(branch_name)
        
        # Sắp xếp các version từ mới đến cũ
        available_versions.sort(reverse=True)
        
        # Version mới nhất là version đầu tiên (cao nhất) trong danh sách
        # Nếu đang ở branch không phải tool-v*, coi như đang ở version mới nhất
        is_current_a_version = current_branch.startswith('tool-v')
        sorted_branches = available_versions
        
        # Hiển thị danh sách version
        if sorted_branches:
            print(Colors.bold("   Các phiên bản có sẵn:"))
            print()
            
            for idx, branch in enumerate(sorted_branches, start=1):
                # Kiểm tra xem có phải branch hiện tại không
                is_active = branch == current_branch
                
                # Nếu đang ở branch không phải tool-v*, coi như đang ở version mới nhất (version đầu tiên)
                if not is_current_a_version and idx == 1:
                    is_active = True
                
                # Định dạng tên branch để hiển thị
                display_name = branch.replace('tool-v', 'v')
                
                # Version đầu tiên (mới nhất) hiển thị thêm "Mới nhất"
                if idx == 1:
                    display_name = f"{display_name} (Mới nhất)"
                
                # Hiển thị với dấu hiệu active
                if is_active:
                    marker = Colors.success("✓")
                    branch_color = Colors.success
                    if is_current_a_version:
                        status_text = Colors.success(f"(Đang active - {current_branch})")
                    else:
                        status_text = Colors.success(f"(Đang active - {current_branch} = Mới nhất)")
                else:
                    marker = " "
                    branch_color = Colors.info
                    status_text = ""
                
                print(f"   {marker} {Colors.warning(f'{idx}')}. {branch_color(display_name)} {status_text}")
            
            print()
            print_separator("═", 70, Colors.INFO)
            print()
            print(f"   {Colors.muted('0')}. Quay lại menu chính")
            print()
            
            # Cho phép chọn version để chuyển
            while True:
                choice = input(f"{Colors.info('Chọn version để chuyển')} [{Colors.muted('0')}]: ").strip()
                
                if not choice or choice == '0':
                    break
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(sorted_branches):
                        selected_branch = sorted_branches[choice_num - 1]
                        
                        # Nếu chọn version mới nhất (version đầu tiên) và đang ở branch không phải tool-v*
                        if choice_num == 1 and not is_current_a_version:
                            print()
                            print(Colors.info(f"ℹ️  Bạn đang ở version mới nhất ({selected_branch.replace('tool-v', 'v')}) - branch: {current_branch}"))
                            print()
                            input(Colors.muted("Nhấn Enter để tiếp tục..."))
                            break
                        
                        # Nếu đã là branch hiện tại, không cần chuyển
                        if selected_branch == current_branch:
                            print()
                            version_display = selected_branch.replace('tool-v', 'v')
                            if choice_num == 1:
                                version_display += " (Mới nhất)"
                            print(Colors.info(f"ℹ️  Bạn đang ở version: {version_display}"))
                            print()
                            input(Colors.muted("Nhấn Enter để tiếp tục..."))
                            break
                        
                        # Nếu chọn version mới nhất (version đầu tiên) nhưng đang ở tool-v* khác
                        if choice_num == 1:
                            # Cần chuyển về develop hoặc main để có version mới nhất
                            print()
                            print(Colors.warning("⚠️  Để chuyển về version mới nhất, bạn cần checkout về branch develop hoặc main"))
                            print()
                            print(f"   {Colors.info('1')}. Chuyển về develop")
                            print(f"   {Colors.info('2')}. Chuyển về main")
                            print(f"   {Colors.muted('0')}. Hủy")
                            print()
                            
                            branch_choice = input(f"{Colors.info('Chọn branch')} [{Colors.muted('0')}]: ").strip()
                            
                            if branch_choice == '1':
                                switch_to_old_version('develop')
                                break
                            elif branch_choice == '2':
                                switch_to_old_version('main')
                                break
                            else:
                                break
                        else:
                            # Chuyển về version đã chọn (tool-v*)
                            switch_to_old_version(selected_branch)
                            break
                    else:
                        print(Colors.error(f"❌ Lựa chọn phải từ 1 đến {len(sorted_branches)}"))
                except ValueError:
                    print(Colors.error("❌ Vui lòng nhập số!"))
        else:
            print(Colors.warning("⚠️  Không tìm thấy branch version nào"))
            print()
            print(f"   {Colors.info('Branch hiện tại')}: {Colors.bold(current_branch)}")
            print(f"   {Colors.info('Version')}: {Colors.bold(Colors.success(version))}")
            print()
            print_separator("═", 70, Colors.INFO)
            print()
            input(Colors.muted("Nhấn Enter để quay lại..."))
            
    except FileNotFoundError:
        print(Colors.error("❌ Không tìm thấy Git. Vui lòng cài đặt Git trước."))
        print()
        input(Colors.muted("Nhấn Enter để quay lại..."))
    except Exception as e:
        print(Colors.error(f"❌ Lỗi: {e}"))
        print()
        input(Colors.muted("Nhấn Enter để quay lại..."))


def switch_to_old_version(branch_name: str):
    """
    Chuyển về phiên bản cũ bằng cách checkout về branch cụ thể
    
    Args:
        branch_name: Tên branch cần checkout (ví dụ: 'tool-v1.0.0', 'tool-v1.0.1')
    """
    print()
    print_separator("═", 70, Colors.INFO)
    print(Colors.bold(f"🔄 ĐANG CHUYỂN VỀ PHIÊN BẢN: {branch_name}"))
    print_separator("═", 70, Colors.INFO)
    print()
    
    project_root = Path(__file__).parent.parent
    
    try:
        # Kiểm tra xem branch có tồn tại không (local hoặc remote)
        check_branch_result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if check_branch_result.returncode != 0:
            print(Colors.error("❌ Không thể kiểm tra danh sách branch"))
            print(Colors.error(f"   {check_branch_result.stderr.strip()}"))
            print()
            input(Colors.muted("Nhấn Enter để quay lại..."))
            return
        
        # Kiểm tra xem branch có tồn tại không (kiểm tra chính xác)
        branch_exists_local = False
        branch_exists_remote = False
        
        for line in check_branch_result.stdout.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Kiểm tra branch local (format: "* branch_name" hoặc "  branch_name")
            if not line.startswith('remotes/'):
                # Loại bỏ dấu * nếu có
                branch_part = line.lstrip('*').strip()
                if branch_part == branch_name:
                    branch_exists_local = True
            # Kiểm tra branch remote
            else:
                if f"remotes/origin/{branch_name}" in line or f"remotes/origin/develop/{branch_name}" in line:
                    branch_exists_remote = True
        
        if not branch_exists_local and not branch_exists_remote:
            print(Colors.error(f"❌ Không tìm thấy branch: {branch_name}"))
            print()
            print(Colors.info("💡 Các branch có sẵn:"))
            print(Colors.secondary(check_branch_result.stdout))
            print()
            input(Colors.muted("Nhấn Enter để quay lại..."))
            return
        
        # Nếu branch chỉ có trên remote, fetch trước
        if not branch_exists_local and branch_exists_remote:
            print(Colors.info(f"📥 Branch {branch_name} chỉ có trên remote, đang fetch..."))
            fetch_result = subprocess.run(
                ["git", "fetch", "origin", branch_name],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if fetch_result.returncode != 0:
                print(Colors.error("❌ Không thể fetch branch từ remote"))
                print(Colors.error(f"   {fetch_result.stderr.strip()}"))
                print()
                input(Colors.muted("Nhấn Enter để quay lại..."))
                return
        
        # Checkout về branch
        print(Colors.info(f"🔄 Đang checkout về branch: {branch_name}..."))
        checkout_result = subprocess.run(
            ["git", "checkout", branch_name],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if checkout_result.returncode == 0:
            print()
            print(Colors.success(f"✅ Đã chuyển về branch: {branch_name}"))
            print()
            print(Colors.warning("⚠️  QUAN TRỌNG:"))
            print(Colors.warning("   Bạn cần khởi động lại chương trình để áp dụng thay đổi!"))
            print()
            print_separator("═", 70, Colors.INFO)
            print()
            input(Colors.muted("Nhấn Enter để quay lại..."))
        else:
            print(Colors.error("❌ Lỗi khi checkout branch"))
            print(Colors.error(f"   {checkout_result.stderr.strip()}"))
            print()
            input(Colors.muted("Nhấn Enter để quay lại..."))
            
    except FileNotFoundError:
        print(Colors.error("❌ Không tìm thấy Git. Vui lòng cài đặt Git trước."))
        print()
        input(Colors.muted("Nhấn Enter để quay lại..."))
    except subprocess.TimeoutExpired:
        print(Colors.error("❌ Quá trình checkout quá lâu, đã hủy"))
        print()
        input(Colors.muted("Nhấn Enter để quay lại..."))
    except Exception as e:
        print(Colors.error(f"❌ Lỗi: {e}"))
        print()
        input(Colors.muted("Nhấn Enter để quay lại..."))


def _check_and_sync_missing_files(project_root: Path) -> bool:
    """
    Kiểm tra và đồng bộ file thiếu từ GitHub
    
    Args:
        project_root: Đường dẫn root của project
        
    Returns:
        bool: True nếu có file được đồng bộ, False nếu không có file thiếu
    """
    try:
        # Lấy branch hiện tại trước
        current_branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if current_branch_result.returncode != 0:
            return False
        
        current_branch = current_branch_result.stdout.strip()
        remote_branch = f"origin/{current_branch}"
        
        # Fetch thông tin mới nhất từ remote
        fetch_result = subprocess.run(
            ["git", "fetch", "origin"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if fetch_result.returncode != 0:
            return False
        
        # Kiểm tra xem remote branch có tồn tại không
        check_remote_result = subprocess.run(
            ["git", "ls-remote", "--heads", "origin", current_branch],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Nếu không có remote branch tương ứng, thử dùng origin/HEAD hoặc origin/main/master
        if check_remote_result.returncode != 0 or not check_remote_result.stdout.strip():
            # Thử các branch phổ biến
            for default_branch in ["main", "master", "develop"]:
                check_default = subprocess.run(
                    ["git", "ls-remote", "--heads", "origin", default_branch],
                    cwd=str(project_root),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if check_default.returncode == 0 and check_default.stdout.strip():
                    remote_branch = f"origin/{default_branch}"
                    break
            else:
                # Nếu không tìm thấy, dùng origin/HEAD
                remote_branch = "origin/HEAD"
        
        # Lấy danh sách file được track trong git từ remote
        ls_files_result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", remote_branch],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if ls_files_result.returncode != 0:
            return False
        
        # Lấy danh sách file từ remote
        remote_files = set(ls_files_result.stdout.strip().split('\n'))
        remote_files = {f for f in remote_files if f.strip()}  # Loại bỏ empty
        
        # Kiểm tra file nào thiếu trong local
        missing_files = []
        for file_path in remote_files:
            local_file = project_root / file_path
            if not local_file.exists():
                missing_files.append(file_path)
        
        if not missing_files:
            return False
        
        # Hiển thị danh sách file thiếu
        print()
        print(Colors.warning(f"⚠️  Tìm thấy {len(missing_files)} file thiếu so với GitHub:"))
        print()
        for file_path in missing_files[:20]:  # Hiển thị tối đa 20 file đầu
            print(Colors.muted(f"   - {file_path}"))
        if len(missing_files) > 20:
            print(Colors.muted(f"   ... và {len(missing_files) - 20} file khác"))
        
        print()
        print(Colors.info("🔄 Đang đồng bộ file thiếu từ GitHub..."))
        print()
        
        # Đồng bộ tất cả file thiếu cùng lúc bằng git checkout
        checkout_result = subprocess.run(
            ["git", "checkout", remote_branch, "--"] + missing_files,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if checkout_result.returncode == 0:
            print(Colors.success(f"✅ Đã đồng bộ thành công {len(missing_files)} file"))
            return True
        else:
            # Nếu không thành công, thử từng file một
            print(Colors.warning("⚠️  Đồng bộ hàng loạt thất bại, thử từng file..."))
            print()
            
            synced_count = 0
            for file_path in missing_files:
                try:
                    checkout_single = subprocess.run(
                        ["git", "checkout", remote_branch, "--", file_path],
                        cwd=str(project_root),
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if checkout_single.returncode == 0:
                        synced_count += 1
                        print(Colors.success(f"   ✅ Đã đồng bộ: {file_path}"))
                    else:
                        print(Colors.error(f"   ❌ Không thể đồng bộ: {file_path}"))
                except Exception as e:
                    print(Colors.error(f"   ❌ Lỗi khi đồng bộ {file_path}: {e}"))
            
            if synced_count > 0:
                print()
                print(Colors.success(f"✅ Đã đồng bộ thành công {synced_count}/{len(missing_files)} file"))
                return True
            
            return False
        
    except FileNotFoundError:
        return False
    except subprocess.TimeoutExpired:
        print(Colors.error("   ❌ Quá trình kiểm tra quá lâu, đã hủy"))
        return False
    except Exception as e:
        print(Colors.error(f"   ❌ Lỗi khi kiểm tra file thiếu: {e}"))
        return False


def update_version():
    """
    Update version mới của package
    
    Giải thích:
    - Kiểm tra xem có phải git repository không
    - Nếu có, thử git pull
    - Sau đó kiểm tra và đồng bộ file thiếu từ GitHub
    - Nếu không, thử pip install --upgrade
    """
    print()
    print_separator("═", 70, Colors.INFO)
    print(Colors.bold("🔄 CẬP NHẬT PHIÊN BẢN"))
    print_separator("═", 70, Colors.INFO)
    print()
    
    current_version = get_current_version()
    print(f"   {Colors.info('Version hiện tại')}: {Colors.bold(current_version)}")
    print()
    
    project_root = Path(__file__).parent.parent
    git_dir = project_root / ".git"
    
    # Kiểm tra xem có phải git repository không
    if git_dir.exists():
        print(Colors.info("📥 Đang cập nhật từ Git repository..."))
        print()
        
        try:
            # Thực hiện git pull
            result = subprocess.run(
                ["git", "pull"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Kiểm tra xem có thay đổi không
                if "Already up to date" in result.stdout or "Đã cập nhật" in result.stdout:
                    print(Colors.success("✅ Đã ở phiên bản mới nhất!"))
                else:
                    print(Colors.success("✅ Đã cập nhật thành công!"))
                    print()
                    print(Colors.info("💡 Khởi động lại chương trình để áp dụng thay đổi"))
                    
                    # Hiển thị output của git pull
                    if result.stdout.strip():
                        print()
                        print(Colors.muted("Chi tiết:"))
                        print(Colors.secondary(result.stdout.strip()))
                
                # Kiểm tra và đồng bộ file thiếu
                print()
                print_separator("─", 70, Colors.INFO)
                print(Colors.info("🔍 Đang kiểm tra file thiếu so với GitHub..."))
                print_separator("─", 70, Colors.INFO)
                
                has_synced = _check_and_sync_missing_files(project_root)
                
                if not has_synced:
                    print()
                    print(Colors.success("✅ Không có file nào thiếu"))
            else:
                print(Colors.error("❌ Lỗi khi cập nhật từ Git"))
                if result.stderr:
                    print(Colors.error(f"   {result.stderr.strip()}"))
        except FileNotFoundError:
            print(Colors.error("❌ Không tìm thấy Git. Vui lòng cài đặt Git trước."))
        except subprocess.TimeoutExpired:
            print(Colors.error("❌ Quá trình cập nhật quá lâu, đã hủy"))
        except Exception as e:
            print(Colors.error(f"❌ Lỗi: {e}"))
    else:
        # Không phải git repository, thử pip install --upgrade
        print(Colors.info("📦 Đang cập nhật từ PyPI..."))
        print()
        
        try:
            # Thực hiện pip install --upgrade
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "DevTools"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(Colors.success("✅ Đã cập nhật thành công!"))
                print()
                print(Colors.info("💡 Khởi động lại chương trình để áp dụng thay đổi"))
                
                # Hiển thị output của pip
                if result.stdout.strip():
                    print()
                    print(Colors.muted("Chi tiết:"))
                    # Chỉ hiển thị dòng quan trọng
                    for line in result.stdout.strip().split('\n'):
                        if 'Successfully installed' in line or 'Requirement already satisfied' in line:
                            print(Colors.secondary(line))
            else:
                print(Colors.error("❌ Lỗi khi cập nhật từ PyPI"))
                if result.stderr:
                    # Chỉ hiển thị dòng lỗi quan trọng
                    error_lines = result.stderr.strip().split('\n')
                    for line in error_lines[-5:]:  # 5 dòng cuối
                        if line.strip():
                            print(Colors.error(f"   {line.strip()}"))
        except subprocess.TimeoutExpired:
            print(Colors.error("❌ Quá trình cập nhật quá lâu, đã hủy"))
        except Exception as e:
            print(Colors.error(f"❌ Lỗi: {e}"))
    
    print()
    print_separator("═", 70, Colors.INFO)
    print()
    input(Colors.muted("Nhấn Enter để quay lại..."))


def safe_print(text, fallback_text=None):
    """
    In text an toàn với fallback cho encoding errors
    
    Args:
        text: Text cần in (có thể chứa emoji/unicode)
        fallback_text: Text dự phòng nếu không in được (ASCII)
    
    Giải thích:
    - Cố gắng in text gốc với emoji
    - Nếu lỗi encoding, dùng fallback
    - Nếu không có fallback, bỏ qua emoji
    """
    try:
        print(text)
    except UnicodeEncodeError:
        if fallback_text:
            print(fallback_text)
        else:
            # Loại bỏ emoji và in lại
            import re
            ascii_text = re.sub(r'[^\x00-\x7F]+', '', text)
            print(ascii_text)


def _run_create_tool_script(manager):
    """Chạy script create-tool.py để tạo tool mới"""
    print()
    print_separator("─", 70, Colors.INFO)
    print(Colors.bold("🛠️  TẠO TOOL MỚI"))
    print_separator("─", 70, Colors.INFO)
    print()
    
    # Tìm đường dẫn script create-tool.py
    project_root = Path(__file__).parent.parent
    create_tool_script = project_root / "scripts" / "create-tool.py"
    
    if not create_tool_script.exists():
        print(Colors.error(f"❌ Không tìm thấy script: {create_tool_script}"))
        print()
        return
    
    try:
        # Chạy script create-tool.py
        print(Colors.info("📦 Đang khởi động script tạo tool..."))
        print()
        
        result = subprocess.run(
            [sys.executable, str(create_tool_script)],
            cwd=str(project_root)
        )
        
        print()
        print_separator("─", 70, Colors.INFO)
        
        if result.returncode == 0:
            print(Colors.success("✅ Hoàn tất!"))
            print()
            print(Colors.info("💡 Chạy lại chương trình để tool mới xuất hiện trong menu"))
        else:
            print(Colors.warning("⚠️  Script đã kết thúc với mã lỗi"))
        
        print_separator("─", 70, Colors.INFO)
        print()
        input(Colors.muted("Nhấn Enter để quay lại..."))
        
    except KeyboardInterrupt:
        print()
        print(Colors.warning("⚠️  Đã hủy bởi người dùng"))
        print()
    except Exception as e:
        print()
        print(Colors.error(f"❌ Lỗi khi chạy script: {e}"))
        print()
        input(Colors.muted("Nhấn Enter để quay lại..."))


def _view_log_file(log_file_path: str):
    """Hiển thị nội dung file log"""
    try:
        log_path = Path(log_file_path)
        if not log_path.exists():
            print(Colors.error(f"❌ File log không tồn tại: {log_file_path}"))
            return
        
        print()
        print_separator("─", 70, Colors.INFO)
        print(Colors.bold(f"📄 NỘI DUNG FILE LOG: {log_path.name}"))
        print_separator("─", 70, Colors.INFO)
        print()
        
        # Đọc và hiển thị nội dung file
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Hiển thị nội dung (giới hạn số dòng để tránh quá dài)
        lines = content.split('\n')
        max_lines = 100  # Giới hạn hiển thị 100 dòng đầu tiên
        
        if len(lines) > max_lines:
            print(Colors.warning(f"⚠️  File quá dài, chỉ hiển thị {max_lines} dòng đầu tiên (tổng: {len(lines)} dòng)"))
            print()
            for i, line in enumerate(lines[:max_lines], 1):
                print(line)
            print()
            print(Colors.muted(f"... (còn {len(lines) - max_lines} dòng nữa)"))
        else:
            print(content)
        
        print()
        print_separator("─", 70, Colors.INFO)
        print()
        input(Colors.muted("Nhấn Enter để quay lại..."))
        
    except Exception as e:
        print()
        print(Colors.error(f"❌ Lỗi khi đọc file log: {e}"))
        print()
        input(Colors.muted("Nhấn Enter để quay lại..."))


def _show_logs_menu(manager):
    """Hiển thị menu quản lý logs"""
    while True:
        # Lấy danh sách log files
        try:
            log_files = get_log_files()
        except Exception as e:
            # Debug: nếu có lỗi, hiển thị lỗi để debug
            print()
            print(Colors.error(f"❌ Lỗi khi lấy danh sách log files: {e}"))
            import traceback
            traceback.print_exc()
            print()
            input(Colors.muted("Nhấn Enter để quay lại..."))
            break
        
        print()
        print_separator("─", 70, Colors.INFO)
        print(Colors.bold("📋 QUẢN LÝ LOG FILES"))
        print_separator("─", 70, Colors.INFO)
        print()
        
        if not log_files:
            print(Colors.info("ℹ️  Không có file log nào"))
            print()
            print(Colors.muted("💡 Các file log sẽ được tạo tự động khi có lỗi xảy ra"))
            print()
            input(Colors.muted("Nhấn Enter để quay lại..."))
            break
        
        print(Colors.info(f"📊 Tìm thấy {len(log_files)} file log:"))
        print()
        
        for i, log_file in enumerate(log_files, 1):
            file_path = Path(log_file)
            file_name = file_path.name
            file_size = file_path.stat().st_size
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Format thời gian sửa đổi
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            time_str = mtime.strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"   {Colors.info(str(i))}. {Colors.secondary(file_name)}")
            print(f"      📅 {Colors.muted(time_str)} | 📦 {Colors.muted(size_str)}")
            print()
        
        print_separator("─", 70, Colors.INFO)
        print()
        print(Colors.bold("📝 Lệnh:"))
        print(f"   • Nhập {Colors.info('số')} để xem nội dung file log")
        print(f"   • Nhập {Colors.info('d [số]')} hoặc {Colors.info('d[số]')} để xóa file log (ví dụ: d 1, d1, d 1 2 3)")
        print(f"   • Nhập {Colors.info('clear')} để xóa tất cả file log")
        print(f"   • Nhập {Colors.info('q')} hoặc {Colors.info('0')} để quay lại")
        print()
        
        user_input = input(f"{Colors.primary('Nhập lệnh')}: ").strip()
        
        if not user_input:
            continue
        
        # Parse command
        # Hỗ trợ cả "d1" và "d 1"
        user_input_lower = user_input.lower().strip()
        
        # Quay lại
        if user_input_lower in ['q', 'quit', '0', 'exit']:
            break
        
        # Xóa file log - kiểm tra pattern "d[số]" hoặc "d [số]"
        if user_input_lower.startswith('d'):
            # Loại bỏ 'd' và lấy phần còn lại
            rest = user_input_lower[1:].strip()
            if not rest:
                print()
                print(Colors.warning("⚠️  Vui lòng nhập số thứ tự file log cần xóa (ví dụ: d 1 hoặc d1)"))
                print()
                input(Colors.muted("Nhấn Enter để tiếp tục..."))
                continue
            
            # Parse nhiều số (hỗ trợ cả space và comma)
            numbers_str = re.split(r'[,\s]+', rest)
            numbers = []
            for num_str in numbers_str:
                if num_str.strip():
                    try:
                        num = int(num_str.strip())
                        numbers.append(num)
                    except ValueError:
                        print(Colors.error(f"❌ Số không hợp lệ: {num_str}"))
            
            if not numbers:
                print()
                print(Colors.error("❌ Không có số hợp lệ nào"))
                print()
                input(Colors.muted("Nhấn Enter để tiếp tục..."))
                continue
            
            # Xóa các file log
            deleted_count = 0
            invalid_numbers = []
            deleted_files = []
            
            for idx in numbers:
                if 1 <= idx <= len(log_files):
                    log_file = log_files[idx - 1]
                    file_path = Path(log_file)
                    
                    # Đảm bảo đường dẫn là tuyệt đối
                    if not file_path.is_absolute():
                        # Nếu là đường dẫn tương đối, tìm project root
                        from utils.logger import _get_project_root
                        project_root = _get_project_root()
                        file_path = project_root / log_file
                    
                    file_name = file_path.name
                    
                    # Kiểm tra file có tồn tại không
                    if not file_path.exists():
                        print(Colors.warning(f"⚠️  File không tồn tại: {file_name} (đường dẫn: {file_path})"))
                        continue
                    
                    try:
                        # Xóa file
                        file_path.unlink()
                        # Kiểm tra lại xem file đã bị xóa chưa
                        if file_path.exists():
                            print(Colors.error(f"❌ File vẫn tồn tại sau khi xóa: {file_name}"))
                        else:
                            deleted_count += 1
                            deleted_files.append(file_name)
                    except PermissionError as e:
                        print(Colors.error(f"❌ Không có quyền xóa file {file_name}: {e}"))
                    except Exception as e:
                        print(Colors.error(f"❌ Không thể xóa file {file_name}: {e}"))
                        import traceback
                        traceback.print_exc()
                else:
                    invalid_numbers.append(idx)
            
            # Thông báo kết quả
            if deleted_count > 0:
                print()
                print(Colors.success(f"✅ Đã xóa {deleted_count} file log:"))
                for file_name in deleted_files:
                    print(f"   • {Colors.secondary(file_name)}")
                print()
                input(Colors.muted("Nhấn Enter để tiếp tục..."))
                
                # Refresh danh sách log files
                log_files = get_log_files()
                if not log_files:
                    # Không còn file log nào, quay lại menu chính
                    print()
                    print(Colors.info("ℹ️  Đã xóa hết file log, quay lại menu chính..."))
                    print()
                    break
                # Nếu còn file, tiếp tục vòng lặp để hiển thị lại menu
                continue
            
            if invalid_numbers:
                print()
                print(Colors.error(f"❌ Số không hợp lệ: {', '.join(map(str, invalid_numbers))}"))
                print(Colors.info(f"💡 Vui lòng nhập số từ 1 đến {len(log_files)}"))
                print()
                input(Colors.muted("Nhấn Enter để tiếp tục..."))
        
        # Xem file log
        elif user_input_lower.isdigit():
            try:
                idx = int(user_input_lower)
                if 1 <= idx <= len(log_files):
                    _view_log_file(log_files[idx - 1])
                else:
                    print()
                    print(Colors.error(f"❌ Số không hợp lệ (phải từ 1 đến {len(log_files)})"))
                    print()
                    input(Colors.muted("Nhấn Enter để tiếp tục..."))
            except ValueError:
                print()
                print(Colors.error("❌ Số không hợp lệ"))
                print()
                input(Colors.muted("Nhấn Enter để tiếp tục..."))
            
        
        # Xóa tất cả file log
        elif user_input_lower == 'clear':
            print()
            confirm = input(Colors.warning("⚠️  Bạn có chắc chắn muốn xóa TẤT CẢ file log? (yes/no): ")).strip().lower()
            if confirm in ['yes', 'y', 'có', 'c']:
                deleted_count = clear_logs()
                if deleted_count > 0:
                    print()
                    print(Colors.success(f"✅ Đã xóa {deleted_count} file log"))
                    print()
                    input(Colors.muted("Nhấn Enter để quay lại..."))
                    break  # Quay lại menu chính
                else:
                    print()
                    print(Colors.warning("⚠️  Không xóa được file log nào"))
                    print()
                    input(Colors.muted("Nhấn Enter để tiếp tục..."))
            else:
                print()
                print(Colors.info("ℹ️  Đã hủy xóa log"))
                print()
                input(Colors.muted("Nhấn Enter để tiếp tục..."))
        
        else:
            print()
            print(Colors.error(f"❌ Lệnh không hợp lệ: {user_input_lower}"))
            print(Colors.info("💡 Sử dụng: [số] để xem, d [số] hoặc d[số] để xóa, clear để xóa tất cả"))
            print()
            input(Colors.muted("Nhấn Enter để tiếp tục..."))


def _show_tool_management_menu(manager, tools):
    """Hiển thị menu quản lý tool (export/import/delete)"""
    while True:
        print()
        print_separator("─", 70, Colors.INFO)
        print(Colors.bold("🛠️  QUẢN LÝ TOOL"))
        print_separator("─", 70, Colors.INFO)
        print()
        
        print(Colors.bold("📝 Lệnh:"))
        print(f"   {Colors.info('1')} - Export tool (xuất tool thành file zip)")
        print(f"   {Colors.info('2')} - Import tool (nhập tool từ file zip hoặc thư mục)")
        print(f"   {Colors.info('3')} - Xóa tool")
        print(f"   {Colors.info('0')} - Quay lại")
        print()
        
        choice = input(f"{Colors.primary('Chọn lệnh')} (0-3): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            # Export tool
            print()
            print_separator("─", 70, Colors.INFO)
            print(Colors.bold("📦 EXPORT TOOL"))
            print_separator("─", 70, Colors.INFO)
            print()
            
            # Hiển thị danh sách tools
            displayed_tools = getattr(manager, 'displayed_tools_order', tools)
            if not displayed_tools:
                displayed_tools = tools
            
            manager.display_menu(displayed_tools, title="CHỌN TOOL ĐỂ EXPORT", group_by_category=False)
            
            tool_input = input(f"{Colors.primary('Nhập số thứ tự tool')} (hoặc Enter để hủy): ").strip()
            
            if not tool_input:
                continue
            
            try:
                idx = int(tool_input)
                if 1 <= idx <= len(displayed_tools):
                    tool = displayed_tools[idx - 1]
                    tool_display_name = manager.get_tool_display_name(tool)
                    
                    print()
                    print(Colors.info(f"📦 Đang export tool: {Colors.bold(tool_display_name)}..."))
                    
                    zip_path = manager.export_tool(tool)
                    if zip_path:
                        print()
                        print(Colors.success(f"✅ Export thành công!"))
                        print(f"   {Colors.secondary('File')}: {Colors.bold(zip_path)}")
                        print()
                        input(Colors.muted("Nhấn Enter để tiếp tục..."))
                    else:
                        print()
                        print(Colors.error("❌ Export thất bại"))
                        print()
                        input(Colors.muted("Nhấn Enter để tiếp tục..."))
                else:
                    print(Colors.error(f"❌ Số không hợp lệ (phải từ 1 đến {len(displayed_tools)})"))
                    print()
                    input(Colors.muted("Nhấn Enter để tiếp tục..."))
            except ValueError:
                print(Colors.error("❌ Số không hợp lệ"))
                print()
                input(Colors.muted("Nhấn Enter để tiếp tục..."))
        
        elif choice == '2':
            # Import tool
            print()
            print_separator("─", 70, Colors.INFO)
            print(Colors.bold("📥 IMPORT TOOL"))
            print_separator("─", 70, Colors.INFO)
            print()
            
            print(Colors.info("💡 Nhập đường dẫn đến file .zip hoặc thư mục tool"))
            print()
            import_path = input(f"{Colors.primary('Đường dẫn')} (hoặc Enter để hủy): ").strip()
            
            if not import_path:
                continue
            
            # Kiểm tra đường dẫn
            import_path_obj = Path(import_path)
            if not import_path_obj.exists():
                print()
                print(Colors.error(f"❌ Không tìm thấy: {import_path}"))
                print()
                input(Colors.muted("Nhấn Enter để tiếp tục..."))
                continue
            
            print()
            print(Colors.info("📥 Đang import tool..."))
            
            success = manager.import_tool(import_path)
            if success:
                print()
                print(Colors.success("✅ Import thành công!"))
                print(Colors.info("💡 Khởi động lại chương trình để tool xuất hiện trong menu"))
            else:
                print()
                print(Colors.error("❌ Import thất bại"))
            
            print()
            input(Colors.muted("Nhấn Enter để tiếp tục..."))
        
        elif choice == '3':
            # Delete tool
            print()
            print_separator("─", 70, Colors.INFO)
            print(Colors.bold("🗑️  XÓA TOOL"))
            print_separator("─", 70, Colors.INFO)
            print()
            
            # Hiển thị danh sách tools
            displayed_tools = getattr(manager, 'displayed_tools_order', tools)
            if not displayed_tools:
                displayed_tools = tools
            
            manager.display_menu(displayed_tools, title="CHỌN TOOL ĐỂ XÓA", group_by_category=False)
            
            tool_input = input(f"{Colors.primary('Nhập số thứ tự tool')} (hoặc Enter để hủy): ").strip()
            
            if not tool_input:
                continue
            
            try:
                idx = int(tool_input)
                if 1 <= idx <= len(displayed_tools):
                    tool = displayed_tools[idx - 1]
                    
                    success = manager.delete_tool(tool, confirm=True)
                    if success:
                        # Refresh tools list
                        tools = manager.get_tool_list()
                        print()
                        print(Colors.info("💡 Tool đã bị xóa khỏi danh sách"))
                        print()
                        input(Colors.muted("Nhấn Enter để tiếp tục..."))
                    else:
                        print()
                        input(Colors.muted("Nhấn Enter để tiếp tục..."))
                else:
                    print(Colors.error(f"❌ Số không hợp lệ (phải từ 1 đến {len(displayed_tools)})"))
                    print()
                    input(Colors.muted("Nhấn Enter để tiếp tục..."))
            except ValueError:
                print(Colors.error("❌ Số không hợp lệ"))
                print()
                input(Colors.muted("Nhấn Enter để tiếp tục..."))
        else:
            print()
            print(Colors.error("❌ Lựa chọn không hợp lệ"))
            print()


def _show_quick_actions_menu(manager, tools):
    """
    Hiển thị menu quick actions cho các thao tác thường dùng
    
    Mục đích: Giúp người dùng truy cập nhanh các chức năng phổ biến
    """
    while True:
        print()
        print_separator("─", 70, Colors.INFO)
        print(Colors.bold("⚡ QUICK ACTIONS"))
        print_separator("─", 70, Colors.INFO)
        print()
        
        # Lấy recent và favorites
        recent = manager.config.get('recent', [])
        favorites = manager.config.get('favorites', [])
        valid_recent = [r for r in recent if r in tools][:5]  # Tối đa 5 recent
        valid_favorites = [f for f in favorites if f in tools][:5]  # Tối đa 5 favorites
        
        print(Colors.bold("📋 Các thao tác nhanh:"))
        print()
        
        action_idx = 1
        actions = []
        
        # Recent tools
        if valid_recent:
            print(Colors.info(f"📚 Recent Tools:"))
            for idx, tool in enumerate(valid_recent, start=1):
                tool_name = manager.get_tool_display_name(tool)
                print(f"   {Colors.warning(f'{action_idx}')}. {Colors.bold(tool_name)} {Colors.muted(f'(r{idx})')}")
                actions.append(('recent', idx - 1))
                action_idx += 1
            print()
        
        # Favorites
        if valid_favorites:
            print(Colors.info(f"⭐ Favorites:"))
            for idx, tool in enumerate(valid_favorites, start=1):
                tool_name = manager.get_tool_display_name(tool)
                print(f"   {Colors.warning(f'{action_idx}')}. {Colors.bold(tool_name)} {Colors.muted(f'(favorite {idx})')}")
                actions.append(('favorite', idx - 1))
                action_idx += 1
            print()
        
        # Common actions
        print(Colors.info(f"🔧 Common Actions:"))
        common_actions = [
            ("Tìm kiếm tool", "search"),
            ("Xem favorites", "favorites"),
            ("Xem recent", "recent"),
            ("Xem help", "help"),
            ("Settings", "settings"),
        ]
        
        for desc, cmd in common_actions:
            print(f"   {Colors.warning(f'{action_idx}')}. {Colors.bold(desc)} {Colors.muted(f'({cmd})')}")
            actions.append(('common', cmd))
            action_idx += 1
        
        print()
        print_separator("─", 70, Colors.INFO)
        print()
        print(f"   {Colors.muted('0')}. Quay lại menu chính")
        print()
        
        choice = input(f"{Colors.primary('Chọn action')} (0-{action_idx - 1}): ").strip()
        
        if not choice or choice == '0':
            break
        
        try:
            idx = int(choice)
            if 1 <= idx <= len(actions):
                action_type, action_data = actions[idx - 1]
                
                if action_type == 'recent':
                    tool = valid_recent[action_data]
                    _run_tool_loop(manager, tool, tools)
                    break
                elif action_type == 'favorite':
                    tool = valid_favorites[action_data]
                    _run_tool_loop(manager, tool, tools)
                    break
                elif action_type == 'common':
                    cmd = action_data
                    if cmd == 'search':
                        query = input(f"{Colors.primary('Nhập từ khóa tìm kiếm')}: ").strip()
                        if query:
                            results = manager.search_tools(query)
                            if results:
                                manager.display_menu(results, title=f"KẾT QUẢ: {query}", group_by_category=False, search_query=query)
                            else:
                                print(Colors.error(f"❌ Không tìm thấy tool nào phù hợp với '{query}'"))
                    elif cmd == 'favorites':
                        if valid_favorites:
                            manager.display_menu(valid_favorites, title="FAVORITES")
                        else:
                            print(Colors.warning("⭐ Chưa có favorites nào"))
                    elif cmd == 'recent':
                        if valid_recent:
                            manager.display_menu(valid_recent, title="RECENT TOOLS")
                        else:
                            print(Colors.warning("📚 Chưa có recent tools"))
                    elif cmd == 'help':
                        manager.show_help()
                        from utils.helpers import print_keyboard_shortcuts
                        print_keyboard_shortcuts()
                    elif cmd == 'settings':
                        _show_settings_menu(manager)
            else:
                print(Colors.error(f"❌ Số không hợp lệ (phải từ 1 đến {len(actions)})"))
                print()
                input(Colors.muted("Nhấn Enter để tiếp tục..."))
        except ValueError:
            print(Colors.error("❌ Vui lòng nhập số!"))
            print()
            input(Colors.muted("Nhấn Enter để tiếp tục..."))


def _show_statistics(manager):
    """Hiển thị thống kê sử dụng tools"""
    print()
    print_separator("─", 70, Colors.INFO)
    print(Colors.bold("📊 THỐNG KÊ SỬ DỤNG"))
    print_separator("─", 70, Colors.INFO)
    print()
    
    stats = manager.config.get('statistics', {})
    tool_usage = stats.get('tool_usage', {})
    last_used = stats.get('last_used', {})
    
    if not tool_usage:
        print(Colors.info("ℹ️  Chưa có thống kê sử dụng"))
        print()
        input(Colors.muted("Nhấn Enter để quay lại..."))
        return
    
    # Sắp xếp tools theo số lần sử dụng
    sorted_usage = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)
    
    print(Colors.bold("📈 Top Tools được sử dụng nhiều nhất:"))
    print()
    
    for idx, (tool, count) in enumerate(sorted_usage[:10], start=1):  # Top 10
        tool_name = manager.get_tool_display_name(tool)
        last_used_time = last_used.get(tool, 0)
        
        # Format thời gian
        if last_used_time > 0:
            from datetime import datetime
            last_used_dt = datetime.fromtimestamp(last_used_time)
            time_str = last_used_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = "Chưa sử dụng"
        
        # Hiển thị với màu sắc
        if idx <= 3:
            rank_color = Colors.success
        elif idx <= 5:
            rank_color = Colors.warning
        else:
            rank_color = Colors.info
        
        print(f"   {rank_color(f'{idx}.')} {Colors.bold(tool_name)}")
        print(f"      {Colors.muted('Số lần sử dụng:')} {Colors.info(str(count))} | {Colors.muted('Lần cuối:')} {Colors.secondary(time_str)}")
        print()
    
    if len(sorted_usage) > 10:
        print(Colors.muted(f"   ... và {len(sorted_usage) - 10} tool khác"))
        print()
    
    # Tổng kết
    total_usage = sum(tool_usage.values())
    print_separator("─", 70, Colors.INFO)
    print()
    print(Colors.bold("📊 Tổng kết:"))
    print(f"   {Colors.info('Tổng số lần sử dụng:')} {Colors.bold(str(total_usage))}")
    print(f"   {Colors.info('Số tools đã sử dụng:')} {Colors.bold(str(len(tool_usage)))}")
    print()
    print_separator("─", 70, Colors.INFO)
    print()
    input(Colors.muted("Nhấn Enter để quay lại..."))


def _show_settings_menu(manager):
    """Hiển thị menu settings với các tùy chọn"""
    while True:
        print()
        print_separator("─", 70, Colors.INFO)
        print(Colors.bold("⚙️  SETTINGS"))
        print_separator("─", 70, Colors.INFO)
        print()
        
        # Hiển thị settings hiện tại
        print(Colors.bold("📋 Settings hiện tại:"))
        for key, value in manager.config['settings'].items():
            key_colored = Colors.info(key)
            value_colored = Colors.secondary(str(value))
            print(f"   {key_colored}: {value_colored}")
        
        # Hiển thị số disabled tools
        disabled_count = len(manager.config.get('disabled_tools', []))
        if disabled_count > 0:
            print(f"   {Colors.info('disabled_tools')}: {Colors.error(str(disabled_count))}")
        
        print()
        print_separator("─", 70, Colors.INFO)
        print()
        print(Colors.bold("📝 Tùy chọn:"))
        print(f"   1. {Colors.info('show_descriptions')} - Hiển thị mô tả tool")
        print(f"   2. {Colors.info('max_recent')} - Số lượng recent tools tối đa")
        print(f"   3. {Colors.info('create-tool')} - Tạo tool mới")
        print(f"   0. {Colors.muted('Quay lại')}")
        print()
        
        choice = input(f"{Colors.primary('Chọn tùy chọn')} (0-3): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            # Toggle show_descriptions
            current = manager.config['settings'].get('show_descriptions', True)
            new_value = not current
            manager.config['settings']['show_descriptions'] = new_value
            manager._save_config()
            print()
            print(Colors.success(f"✅ Đã {'bật' if new_value else 'tắt'} hiển thị mô tả"))
            print()
        elif choice == '2':
            # Thay đổi max_recent
            print()
            current = manager.config['settings'].get('max_recent', 10)
            new_value_input = input(f"Nhập số lượng recent tools tối đa (hiện tại: {current}): ").strip()
            try:
                new_value = int(new_value_input)
                if new_value < 0:
                    print(Colors.error("❌ Số phải >= 0"))
                else:
                    manager.config['settings']['max_recent'] = new_value
                    manager._save_config()
                    print()
                    print(Colors.success(f"✅ Đã cập nhật max_recent = {new_value}"))
                    print()
            except ValueError:
                print(Colors.error("❌ Giá trị không hợp lệ"))
                print()
        elif choice == '3':
            # Chạy script create-tool
            _run_create_tool_script(manager)
        else:
            print()
            print(Colors.error("❌ Lựa chọn không hợp lệ"))
            print()


def _run_tool_loop(manager, tool, tools):
    """
    Chạy tool với vòng lặp riêng - tự động quay lại đầu tool khi kết thúc
    
    Args:
        manager: ToolManager instance
        tool: Tên tool cần chạy
        tools: Danh sách tools để hiển thị menu khi thoát
    
    Giải thích:
    - Bước 1: Chạy tool lần đầu
    - Bước 2: Kiểm tra exit code từ tool
    - Bước 3: Nếu exit code là 130 (KeyboardInterrupt), quay về menu chính
    - Bước 4: Nếu exit code là 0 (thành công), tự động chạy lại tool đó
    - Bước 5: Nếu có lỗi khác, quay về menu chính
    
    Lý do:
    - Giúp người dùng tiếp tục làm việc với cùng một tool mà không cần quay về menu chính
    - Tiết kiệm thời gian và thao tác
    - Cho phép người dùng nhấn Ctrl+C để quay về menu chính
    """
    # Vòng lặp cho tool - tự động chạy lại khi kết thúc
    while True:
        try:
            # Chạy tool và lấy exit code
            exit_code = manager.run_tool(tool)
            
            # Kiểm tra exit code
            # 130 là exit code khi người dùng nhấn Ctrl+C (KeyboardInterrupt)
            if exit_code == 130:
                # Người dùng nhấn Ctrl+C trong tool - quay về menu chính
                print()
                print(Colors.info("🔄 Quay lại menu chính..."))
                print()
                manager.display_menu(tools)
                break
            
            # Exit code 0 (thành công) hoặc code khác - tự động chạy lại tool
            # Không cần hiển thị menu chính, chỉ chạy lại tool
            continue
            
        except KeyboardInterrupt:
            # Người dùng nhấn Ctrl+C trong vòng lặp tool (ngoài tool)
            # Quay về menu chính
            try:
                print()
                print(Colors.info("🔄 Quay lại menu chính..."))
                print()
                manager.display_menu(tools)
            except (KeyboardInterrupt, EOFError, Exception):
                # Nếu vẫn bị interrupt, thoát luôn
                try:
                    print()
                    print(Colors.info("👋 Tạm biệt!"))
                except:
                    pass
                sys.exit(0)
            break
        
        except Exception as e:
            # Xử lý lỗi khác và log vào file
            from utils.logger import log_error_to_file
            
            try:
                # Log lỗi vào file
                tool_name = tool if 'tool' in locals() else "Unknown"
                log_file = log_error_to_file(
                    error=e,
                    tool_name=tool_name,
                    context="Exception occurred in tool loop"
                )
                if log_file:
                    print()
                    print(Colors.warning(f"📝 Lỗi đã được ghi vào file: {log_file}"))
                
                print()
                print(Colors.error(f"❌ Lỗi khi chạy tool: {e}"))
                print(Colors.info("🔄 Quay lại menu chính..."))
                print()
                manager.display_menu(tools)
            except Exception as ex:
                print(f"\nLỗi: {str(ex)}")
                # Log cả exception này nữa nếu có thể
                try:
                    log_error_to_file(ex, "Error handler", "Failed to handle error in tool loop")
                except:
                    pass
            break


def main():
    """
    Hàm main - Menu chính
    
    Giải thích:
    - Vòng lặp chính của menu
    - Xử lý input từ người dùng
    - Dispatch đến các chức năng tương ứng
    """
    # Khởi tạo ToolManager
    # __file__ là menus/__init__.py, cần lùi 1 cấp lên project root
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    tool_dir = str(project_root / "tools")
    manager = ToolManager(tool_dir)
    
    # Lấy danh sách tools
    tools = manager.get_tool_list()
    
    if not tools:
        print(Colors.error("❌ Không tìm thấy tool nào trong thư mục tools/"))
        return
    
    # Hiển thị banner đẹp hơn với design hiện đại
    from utils.helpers import print_banner, print_welcome_message
    print_banner()
    
    # Welcome message với onboarding tips (chỉ hiển thị lần đầu hoặc khi có flag)
    # Kiểm tra xem có phải lần đầu chạy không (dựa vào recent tools)
    is_first_run = len(manager.config.get('recent', [])) == 0
    if is_first_run:
        print_welcome_message()
    else:
        # Chỉ hiển thị tip ngẫu nhiên cho người dùng cũ
        print_welcome_tip()
        print()
    
    # Tính content_width để đồng nhất với display_menu
    def get_display_width(text: str) -> int:
        """Tính độ dài hiển thị thực tế của text (bao gồm cả emoji)"""
        import unicodedata
        plain_text = strip_ansi(text)
        width = 0
        for char in plain_text:
            try:
                eaw = unicodedata.east_asian_width(char)
                if eaw in ('W', 'F'):  # Wide hoặc Fullwidth
                    width += 2
                else:
                    width += 1
            except:
                width += 1
        return width
    
    # Tính dòng dài nhất để xác định content_width (giống như trong display_menu)
    max_line_width = 0
    if len(tools) > 5:
        from utils.categories import group_tools_by_category
        grouped = group_tools_by_category(tools, manager)
        for tool in tools:
            tool_name = manager.get_tool_display_name(tool)
            is_favorite = tool in manager.config['favorites']
            star_plain = "⭐" if is_favorite else "  "
            idx_str = "99."  # Giả sử max 99 tools
            line_plain = f"{star_plain} {idx_str} {tool_name}"
            line_display_width = get_display_width(line_plain)
            if line_display_width > max_line_width:
                max_line_width = line_display_width
    
    # Xác định content_width dựa trên dòng dài nhất
    required_content_width = max_line_width + 4 if max_line_width > 0 else 68
    content_width = max(required_content_width, 68)
    prompt_width = content_width  # Prompt width = content_width để đồng nhất
    
    # Hiển thị menu lần đầu
    manager.display_menu(tools)
    
    # Command history để hỗ trợ auto-complete
    command_history = []
    history_file = Path(__file__).parent / "command_history.json"
    
    # Load command history nếu có
    if history_file.exists():
        try:
            import json
            with open(history_file, 'r', encoding='utf-8') as f:
                command_history = json.load(f)
                # Giới hạn 100 lệnh gần nhất
                command_history = command_history[-100:]
        except Exception:
            command_history = []
    
    # Vòng lặp chính
    while True:
        try:
            # Nhận input với prompt đẹp và rõ ràng hơn - đồng nhất với content_width
            prompt_title = "devtools"
            prompt_title_display_width = get_display_width(prompt_title)
            prompt_title_padding = prompt_width - prompt_title_display_width - 3
            if prompt_title_padding < 0:
                prompt_title_padding = 0
            
            prompt_prefix = Colors.primary("┌─") + " " + Colors.bold(Colors.info(prompt_title)) + Colors.primary(" " + "─" * prompt_title_padding + "┐")
            print(f"  {prompt_prefix}")
            
            prompt_text = "Chọn tool (h=help, q=quit):"
            prompt_text_display_width = get_display_width(prompt_text)
            # Tính padding cần thiết để đủ width
            prompt_text_padding = prompt_width - prompt_text_display_width - 3
            if prompt_text_padding < 0:
                prompt_text_padding = 0
            
            # In prompt text không có padding (để input() hiển thị text ngay sau)
            prompt_input = "  " + Colors.primary("└─ ") + Colors.secondary("➤") + " " + Colors.bold(prompt_text)
            user_input = input(prompt_input).strip()
            
            # Lưu vào history (trừ các lệnh rỗng)
            if user_input and user_input not in command_history[-10:]:  # Tránh duplicate gần đây
                command_history.append(user_input)
                # Giới hạn 100 lệnh
                if len(command_history) > 100:
                    command_history = command_history[-100:]
            
            # Tính độ dài input đã nhập và in padding + ký tự đóng box
            input_display_width = get_display_width(user_input) if user_input else 0
            # Tổng độ dài: prompt_text_display_width + input_display_width + padding = prompt_width - 3
            # Vậy: padding = prompt_width - 3 - prompt_text_display_width - input_display_width
            remaining_padding = prompt_width - 3 - prompt_text_display_width - input_display_width
            if remaining_padding < 0:
                remaining_padding = 0
            # print(" " * remaining_padding + Colors.primary("┘"))
            print()
            
            if not user_input:
                continue
            
            # Parse command
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            # Xử lý command
            
            # Thoát
            if command in ['q', 'quit', '0', 'exit']:
                print(Colors.info("👋 Tạm biệt!"))
                break
            
            # Help
            elif command in ['h', 'help', '?']:
                manager.show_help()
                # Hiển thị keyboard shortcuts sau help
                from utils.helpers import print_keyboard_shortcuts
                print_keyboard_shortcuts()
            
            # Version
            elif command == 'v':
                show_version()
                manager.display_menu(tools)
            
            # Update
            elif command == 'u':
                update_version()
                manager.display_menu(tools)
            
            # List
            elif command in ['l', 'list']:
                manager.display_menu(tools)
            
            # Clear screen
            elif command == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                manager.display_menu(tools)
            
            # Clear logs
            elif command in ['clear-log', 'clearlog', 'clear-logs']:
                print()
                print_separator("─", 70, Colors.INFO)
                print(Colors.bold("🗑️  XÓA LOG FILES"))
                print_separator("─", 70, Colors.INFO)
                print()
                
                # Lấy danh sách log files
                log_files = get_log_files()
                
                if not log_files:
                    print(Colors.info("ℹ️  Không có file log nào để xóa"))
                    print()
                else:
                    print(Colors.info(f"📊 Tìm thấy {len(log_files)} file log:"))
                    for i, log_file in enumerate(log_files[:10], 1):  # Hiển thị tối đa 10 file đầu tiên
                        file_name = Path(log_file).name
                        print(f"   {i}. {Colors.secondary(file_name)}")
                    if len(log_files) > 10:
                        print(f"   ... và {len(log_files) - 10} file khác")
                    print()
                    
                    # Xác nhận xóa
                    confirm = input(Colors.warning("⚠️  Bạn có chắc chắn muốn xóa tất cả file log? (yes/no): ")).strip().lower()
                    if confirm in ['yes', 'y', 'có', 'c']:
                        deleted_count = clear_logs()
                        if deleted_count > 0:
                            print()
                            print(Colors.success(f"✅ Đã xóa {deleted_count} file log"))
                        else:
                            print()
                            print(Colors.warning("⚠️  Không xóa được file log nào"))
                    else:
                        print()
                        print(Colors.info("ℹ️  Đã hủy xóa log"))
                    print()
            
            # Search
            elif command in ['s', 'search'] or command.startswith('/'):
                if command.startswith('/'):
                    query = command[1:] + (" " + args if args else "")
                else:
                    query = args
                
                if not query:
                    print(Colors.warning("⚠️  Vui lòng nhập từ khóa tìm kiếm"))
                    continue
                
                # Sử dụng fuzzy matching
                results = manager.search_tools(query, use_fuzzy=True)
                
                if results:
                    count_msg = Colors.success(f"{len(results)}")
                    query_msg = Colors.secondary(f"'{query}'")
                    print()
                    print(Colors.info(f"🔍 Tìm thấy {count_msg} tool phù hợp với {query_msg}:"))
                    manager.display_menu(results, title=f"KẾT QUẢ TÌM KIẾM: {query}", group_by_category=False, search_query=query)
                else:
                    print(Colors.error(f"❌ Không tìm thấy tool nào phù hợp với '{query}'"))
                    # Gợi ý các tools gần đúng
                    all_tools = manager.get_tool_list()
                    suggestions = suggest_command(query, [manager.get_tool_display_name(t) for t in all_tools][:10])
                    if suggestions:
                        print()
                        print(Colors.info(f"💡 Gợi ý tìm kiếm: {', '.join([Colors.secondary(s) for s in suggestions[:3]])}"))
            
            # Favorites
            elif command == 'f':
                favorites = manager.config['favorites']
                if favorites:
                    valid_favorites = [f for f in favorites if f in tools]
                    manager.display_menu(valid_favorites, title="FAVORITES")
                else:
                    print(Colors.warning("⭐ Chưa có favorites nào"))
            
            elif command.startswith('f+'):
                # Thêm vào favorites
                try:
                    idx = int(args or command[2:])
                    if 1 <= idx <= len(tools):
                        tool = tools[idx - 1]
                        manager.add_to_favorites(tool)
                    else:
                        print(Colors.error("❌ Số không hợp lệ"))
                except ValueError:
                    print(Colors.error("❌ Số không hợp lệ"))
            
            elif command.startswith('f-'):
                # Xóa khỏi favorites
                try:
                    idx = int(args or command[2:])
                    if 1 <= idx <= len(tools):
                        tool = tools[idx - 1]
                        manager.remove_from_favorites(tool)
                    else:
                        print(Colors.error("❌ Số không hợp lệ"))
                except ValueError:
                    print(Colors.error("❌ Số không hợp lệ"))
            
            # Recent
            elif command == 'r':
                recent = manager.config['recent']
                if recent:
                    # Lọc chỉ những tool còn tồn tại
                    valid_recent = [r for r in recent if r in tools]
                    manager.display_menu(valid_recent, title="RECENT TOOLS")
                else:
                    print(Colors.warning("📚 Chưa có recent tools"))
            
            elif command.startswith('r') and len(command) > 1:
                # Chạy recent tool
                try:
                    idx = int(command[1:])
                    recent = manager.config['recent']
                    # Lọc chỉ những tool còn tồn tại (giống như khi hiển thị menu)
                    valid_recent = [r for r in recent if r in tools]
                    
                    if not valid_recent:
                        print(Colors.warning("📚 Không có recent tool nào còn tồn tại"))
                        continue
                    
                    if 1 <= idx <= len(valid_recent):
                        tool = valid_recent[idx - 1]
                        # Chạy tool với vòng lặp riêng - quay lại đầu tool khi kết thúc
                        _run_tool_loop(manager, tool, tools)
                    else:
                        print(Colors.error(f"❌ Số không hợp lệ (phải từ 1 đến {len(valid_recent)})"))
                except ValueError:
                    print(Colors.error("❌ Số không hợp lệ"))
            
            # Activate/Deactivate tools
            elif command.startswith('on') or command.startswith('activate'):
                # Kích hoạt tool từ danh sách disabled (hỗ trợ nhiều tool)
                try:
                    idx_str = args or (command[2:].lstrip() if command.startswith('on') else "")
                    disabled_tools = manager.config.get('disabled_tools', [])
                    all_tools = manager.get_all_tools_including_disabled()
                    valid_disabled = [t for t in disabled_tools if t in all_tools]
                    
                    if not valid_disabled:
                        print(Colors.warning("⚠️  Không có tool nào bị disabled"))
                        continue
                    
                    if not idx_str:
                        # Nếu không có số, hiển thị danh sách disabled để user chọn
                        print(Colors.info("💡 Danh sách tools bị disabled:"))
                        manager.display_menu(valid_disabled, title="DISABLED TOOLS", group_by_category=False)
                        print(Colors.info("💡 Sử dụng 'on [số]' để kích hoạt lại tool (ví dụ: on 1 hoặc on 1 2 3)"))
                        continue
                    
                    # Parse nhiều số (hỗ trợ cả space và comma)
                    # Tách số từ string (hỗ trợ space, comma, hoặc cả hai)
                    numbers_str = re.split(r'[,\s]+', idx_str.strip())
                    numbers = []
                    for num_str in numbers_str:
                        if num_str.strip():
                            try:
                                num = int(num_str.strip())
                                numbers.append(num)
                            except ValueError:
                                print(Colors.error(f"❌ Số không hợp lệ: {num_str}"))
                    
                    if not numbers:
                        print(Colors.error("❌ Không có số hợp lệ nào"))
                        continue
                    
                    # Xử lý từng số
                    activated_count = 0
                    invalid_numbers = []
                    for idx in numbers:
                        if 1 <= idx <= len(valid_disabled):
                            tool = valid_disabled[idx - 1]
                            # Activate tool (không in thông báo ngay)
                            if tool in manager.config['disabled_tools']:
                                manager.config['disabled_tools'].remove(tool)
                                activated_count += 1
                                tool_name = manager.get_tool_display_name(tool)
                                print(Colors.success(f"✅ Đã kích hoạt: {Colors.bold(tool_name)}"))
                            else:
                                tool_name = manager.get_tool_display_name(tool)
                                print(Colors.warning(f"ℹ️  Tool đã được kích hoạt: {tool_name}"))
                        else:
                            invalid_numbers.append(idx)
                    
                    # Lưu config nếu có thay đổi
                    if activated_count > 0:
                        manager._save_config()
                        # Refresh tools list
                        tools = manager.get_tool_list()
                        print()
                        print(Colors.success(f"📊 Đã kích hoạt {activated_count} tool(s)"))
                    
                    if invalid_numbers:
                        print(Colors.error(f"❌ Số không hợp lệ: {', '.join(map(str, invalid_numbers))}"))
                        print(Colors.info(f"💡 Vui lòng nhập số từ 1 đến {len(valid_disabled)}"))
                        
                except Exception as e:
                    print(Colors.error(f"❌ Lỗi: {e}"))
                    # Tự động hiển thị danh sách disabled
                    disabled_tools = manager.config.get('disabled_tools', [])
                    all_tools = manager.get_all_tools_including_disabled()
                    valid_disabled = [t for t in disabled_tools if t in all_tools]
                    if valid_disabled:
                        print()
                        print(Colors.info("💡 Danh sách tools bị disabled:"))
                        manager.display_menu(valid_disabled, title="DISABLED TOOLS", group_by_category=False)
            
            elif command.startswith('off') or command.startswith('deactivate'):
                # Vô hiệu hóa tool từ danh sách active (menu hiện tại, hỗ trợ nhiều tool)
                try:
                    idx_str = args or (command[3:].lstrip() if command.startswith('off') else "")
                    if not idx_str:
                        # Sử dụng displayed_tools_order nếu có (khi hiển thị theo category)
                        displayed_tools = getattr(manager, 'displayed_tools_order', tools)
                        print(Colors.warning("⚠️  Vui lòng nhập số thứ tự tool cần vô hiệu hóa"))
                        print(Colors.info(f"💡 Sử dụng số từ 1 đến {len(displayed_tools)} (ví dụ: off 1 hoặc off 1 2 3)"))
                        continue
                    
                    # Parse nhiều số (hỗ trợ cả space và comma)
                    # Tách số từ string (hỗ trợ space, comma, hoặc cả hai)
                    numbers_str = re.split(r'[,\s]+', idx_str.strip())
                    numbers = []
                    for num_str in numbers_str:
                        if num_str.strip():
                            try:
                                num = int(num_str.strip())
                                numbers.append(num)
                            except ValueError:
                                print(Colors.error(f"❌ Số không hợp lệ: {num_str}"))
                    
                    if not numbers:
                        print(Colors.error("❌ Không có số hợp lệ nào"))
                        continue
                    
                    # Xử lý từng số
                    deactivated_count = 0
                    invalid_numbers = []
                    
                    # Sử dụng displayed_tools_order nếu có (khi hiển thị theo category)
                    # Nếu không có, dùng tools gốc (khi hiển thị flat list)
                    displayed_tools = getattr(manager, 'displayed_tools_order', tools)
                    
                    for idx in numbers:
                        if 1 <= idx <= len(displayed_tools):
                            tool = displayed_tools[idx - 1]
                            # Deactivate tool - sử dụng method của manager để tự động xóa khỏi favorites/recent
                            if tool not in manager.config['disabled_tools']:
                                manager.deactivate_tool(tool)
                                deactivated_count += 1
                            else:
                                tool_name = manager.get_tool_display_name(tool)
                                print(Colors.warning(f"ℹ️  Tool đã bị vô hiệu hóa: {tool_name}"))
                        else:
                            invalid_numbers.append(idx)
                    
                    # Refresh tools list sau khi disable
                    if deactivated_count > 0:
                        tools = manager.get_tool_list()
                        print()
                        print(Colors.success(f"📊 Đã vô hiệu hóa {deactivated_count} tool(s)"))
                        # Hiển thị lại menu nếu còn tools
                        if tools:
                            manager.display_menu(tools)
                        else:
                            print(Colors.warning("⚠️  Tất cả tools đã bị vô hiệu hóa"))
                            print(Colors.info("💡 Sử dụng 'on [số]' hoặc 'disabled' để kích hoạt lại"))
                    
                    if invalid_numbers:
                        print(Colors.error(f"❌ Số không hợp lệ: {', '.join(map(str, invalid_numbers))}"))
                        print(Colors.info(f"💡 Vui lòng nhập số từ 1 đến {len(displayed_tools)}"))
                        
                except Exception as e:
                    print(Colors.error(f"❌ Lỗi: {e}"))
            
            elif command == 'disabled':
                # Hiển thị danh sách tools bị disabled
                disabled_tools = manager.config.get('disabled_tools', [])
                if disabled_tools:
                    # Lấy tất cả tools để mapping số thứ tự
                    all_tools = manager.get_all_tools_including_disabled()
                    # Chỉ lấy những tool disabled và còn tồn tại
                    valid_disabled = [t for t in disabled_tools if t in all_tools]
                    if valid_disabled:
                        manager.display_menu(valid_disabled, title="DISABLED TOOLS", group_by_category=False)
                        print(Colors.info("💡 Sử dụng 'on [số]' để kích hoạt lại tool"))
                    else:
                        print(Colors.warning("⚠️  Không có tool nào bị disabled"))
                else:
                    print(Colors.warning("⚠️  Không có tool nào bị disabled"))
            
            # Settings
            elif command == 'set':
                _show_settings_menu(manager)
            
            # Statistics
            elif command in ['stats', 'statistics', 'stat']:
                _show_statistics(manager)
                manager.display_menu(tools)
            
            # Tool Management (Export/Import/Delete)
            elif command in ['manage', 'mgmt', 'tool-mgmt']:
                _show_tool_management_menu(manager, tools)
                # Refresh tools list sau khi quản lý
                tools = manager.get_tool_list()
                if tools:
                    manager.display_menu(tools)
            
            # Quick Actions Menu
            elif command in ['qa', 'quick', 'quick-actions']:
                _show_quick_actions_menu(manager, tools)
            
            # Logs
            elif command == 'log' or command == 'logs':
                _show_logs_menu(manager)
            
            # Hiển thị hướng dẫn tool (pattern: số+h, ví dụ: 1h, 4h)
            elif command.endswith('h') and len(command) > 1 and command[:-1].isdigit():
                try:
                    # Lấy số từ đầu command (bỏ 'h' ở cuối)
                    idx = int(command[:-1])
                    
                    # Sử dụng displayed_tools_order nếu có (khi hiển thị theo category)
                    # Nếu không có, dùng tools gốc (khi hiển thị flat list)
                    displayed_tools = getattr(manager, 'displayed_tools_order', tools)
                    
                    if 1 <= idx <= len(displayed_tools):
                        tool = displayed_tools[idx - 1]
                        # Hiển thị hướng dẫn của tool
                        manager.show_tool_help(tool)
                    else:
                        print(Colors.error("❌ Số không hợp lệ"))
                except ValueError:
                    # Không phải pattern số+h, xử lý như lệnh khác
                    print(Colors.error(f"❌ Lệnh không hợp lệ: {command}"))
                    print(Colors.info("💡 Nhập 'h' hoặc 'help' để xem hướng dẫn"))
            
            # Chạy tool theo số
            elif command.isdigit():
                idx = int(command)
                
                # Sử dụng displayed_tools_order nếu có (khi hiển thị theo category)
                # Nếu không có, dùng tools gốc (khi hiển thị flat list)
                displayed_tools = getattr(manager, 'displayed_tools_order', tools)
                
                if 1 <= idx <= len(displayed_tools):
                    tool = displayed_tools[idx - 1]
                    # Chạy tool với vòng lặp riêng - quay lại đầu tool khi kết thúc
                    _run_tool_loop(manager, tool, tools)
                else:
                    print(Colors.error("❌ Số không hợp lệ"))
            
            else:
                # Cải thiện error message với suggestions và help
                print()
                print(Colors.error("  ┌─ " + "─" * 63 + " ┐"))
                print(Colors.error("  │") + " " * 65 + Colors.error("│"))
                
                error_msg = f"❌ Lệnh không hợp lệ: '{command}'"
                error_padding = (65 - len(error_msg)) // 2
                print(Colors.error("  │") + " " * error_padding + Colors.bold(error_msg) + " " * (65 - len(error_msg) - error_padding) + Colors.error("│"))
                
                print(Colors.error("  │") + " " * 65 + Colors.error("│"))
                
                # Gợi ý commands
                valid_commands = ['h', 'help', 'q', 'quit', 'l', 'list', 's', 'search', 'f', 'r', 'set', 'log', 'clear', 'clear-log', 'stats', 'qa', 'quick']
                suggestions = suggest_command(command, valid_commands)
                
                if suggestions:
                    if len(suggestions) == 1:
                        suggest_msg = f"💡 Có phải bạn muốn: {Colors.bold(suggestions[0])}?"
                        suggest_plain = strip_ansi(suggest_msg)
                        suggest_padding = (65 - len(suggest_plain)) // 2
                        print(Colors.error("  │") + " " * suggest_padding + Colors.info(suggest_msg) + " " * (65 - len(suggest_plain) - suggest_padding) + Colors.error("│"))
                    else:
                        suggest_title = f"💡 Gợi ý ({len(suggestions)}):"
                        suggest_title_padding = (65 - len(suggest_title)) // 2
                        print(Colors.error("  │") + " " * suggest_title_padding + Colors.info(suggest_title) + " " * (65 - len(suggest_title) - suggest_title_padding) + Colors.error("│"))
                        
                        suggestions_text = ", ".join([Colors.bold(s) for s in suggestions])
                        suggestions_plain = strip_ansi(suggestions_text)
                        suggestions_padding = (65 - len(suggestions_plain)) // 2
                        print(Colors.error("  │") + " " * suggestions_padding + suggestions_text + " " * (65 - len(suggestions_plain) - suggestions_padding) + Colors.error("│"))
                else:
                    help_msg = "💡 Nhập 'h' hoặc 'help' để xem hướng dẫn"
                    help_plain = strip_ansi(help_msg)
                    help_padding = (65 - len(help_plain)) // 2
                    print(Colors.error("  │") + " " * help_padding + Colors.info(help_msg) + " " * (65 - len(help_plain) - help_padding) + Colors.error("│"))
                
                print(Colors.error("  │") + " " * 65 + Colors.error("│"))
                print(Colors.error("  └─ " + "─" * 63 + " ┘"))
                print()
        
        except (EOFError, KeyboardInterrupt):
            # Xử lý EOF error (input stream bị đóng) hoặc Ctrl+C
            try:
                # Lưu command history trước khi thoát
                if command_history:
                    try:
                        import json
                        history_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(history_file, 'w', encoding='utf-8') as f:
                            json.dump(command_history, f, indent=2, ensure_ascii=False)
                    except Exception:
                        pass  # Bỏ qua nếu không lưu được
                
                print()
                print(Colors.info("👋 Tạm biệt!"))
            except (KeyboardInterrupt, EOFError, Exception):
                # Bỏ qua nếu vẫn bị interrupt khi in thông báo
                pass
            sys.exit(0)
        
        except Exception as e:
            # Xử lý các lỗi khác và log vào file
            from utils.logger import log_error_to_file
            
            try:
                # Log lỗi vào file
                log_file = log_error_to_file(
                    error=e,
                    tool_name="Main menu",
                    context="Exception occurred in main menu loop"
                )
                if log_file:
                    print()
                    print(Colors.warning(f"📝 Lỗi đã được ghi vào file: {log_file}"))
                
                print()
                print(Colors.error(f"❌ Lỗi: {e}"))
                import traceback
                traceback.print_exc()
            except Exception as ex:
                # Nếu không print được do encoding, dùng ASCII
                print(f"\nLỗi: {str(ex)}")
                # Log cả exception này nữa nếu có thể
                try:
                    log_error_to_file(ex, "Error handler", "Failed to handle error in main menu")
                except:
                    pass


if __name__ == "__main__":
    main()
