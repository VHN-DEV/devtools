#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Kết nối Git và push source code lên repository

Mục đích: Tự động hóa quá trình kết nối Git, commit và push code lên GitHub
Lý do: Tiết kiệm thời gian, tránh lỗi khi thao tác Git thủ công
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from datetime import datetime

# Thêm thư mục cha vào sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import (
    print_header, get_user_input, confirm_action,
    log_info, log_error, setup_logger, normalize_path
)
from utils.colors import Colors


class RepoConfigManager:
    """
    Class quản lý cấu hình repository
    
    Mục đích: Lưu và quản lý danh sách repository yêu thích
    """
    
    def __init__(self):
        """Khởi tạo RepoConfigManager"""
        self.config_file = Path(__file__).parent / "git_repos_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load config từ file"""
        default_config = {
            'repositories': [],
            'default_repo': 'https://github.com/VHN-DEV/laravel-botble-cms',
            'history': []
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Migration: đảm bảo các field mới có trong config cũ
                    for key, value in default_config.items():
                        if key not in loaded:
                            loaded[key] = value
                    return loaded
            except Exception:
                pass
        
        # Tạo config mặc định
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Optional[Dict] = None):
        """Lưu config ra file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_error(f"Lỗi lưu config: {e}")
    
    def add_repository(self, name: str, repo_url: str, local_path: str) -> bool:
        """Thêm repository vào danh sách"""
        repo = {
            'name': name,
            'repo_url': repo_url,
            'local_path': local_path,
            'created_at': datetime.now().isoformat()
        }
        
        # Kiểm tra trùng
        for existing in self.config['repositories']:
            if existing['name'] == name or existing['repo_url'] == repo_url:
                return False
        
        self.config['repositories'].append(repo)
        self._save_config()
        return True
    
    def remove_repository(self, name: str) -> bool:
        """Xóa repository khỏi danh sách"""
        self.config['repositories'] = [
            r for r in self.config['repositories'] if r['name'] != name
        ]
        self._save_config()
        return True
    
    def get_repositories(self) -> List[Dict]:
        """Lấy danh sách repository"""
        return self.config.get('repositories', [])
    
    def add_history(self, action: str, repo_url: str, local_path: str, success: bool):
        """Thêm vào lịch sử"""
        history_item = {
            'action': action,
            'repo_url': repo_url,
            'local_path': local_path,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        self.config['history'].insert(0, history_item)
        # Giữ tối đa 100 records
        self.config['history'] = self.config['history'][:100]
        self._save_config()
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Lấy lịch sử gần đây"""
        return self.config.get('history', [])[:limit]


class GitManager:
    """
    Class quản lý Git operations
    
    Mục đích: Tập trung logic Git, dễ mở rộng và maintain
    """
    
    def __init__(self, repo_url: str, local_path: str):
        """
        Khởi tạo GitManager
        
        Args:
            repo_url: URL repository (vd: https://github.com/VHN-DEV/laravel-botble-cms)
            local_path: Đường dẫn thư mục local
        """
        self.repo_url = repo_url
        self.local_path = Path(local_path).resolve()
        
        # Đảm bảo thư mục tồn tại
        if not self.local_path.exists():
            self.local_path.mkdir(parents=True, exist_ok=True)
    
    def check_git_installed(self) -> bool:
        """
        Kiểm tra Git đã được cài đặt chưa
        
        Returns:
            bool: True nếu Git đã cài đặt
        """
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            log_info(f"Git version: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            log_error("Git chưa được cài đặt hoặc không có trong PATH")
            return False
    
    def run_git_command(self, command: list, cwd: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Chạy lệnh Git và trả về kết quả
        
        Args:
            command: Danh sách lệnh Git (vd: ["git", "status"])
            cwd: Thư mục làm việc (mặc định: self.local_path)
        
        Returns:
            tuple: (success, output)
        """
        if cwd is None:
            cwd = self.local_path
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                cwd=str(cwd)
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            return False, error_msg
        except Exception as e:
            return False, str(e)
    
    def is_git_repo(self) -> bool:
        """
        Kiểm tra thư mục có phải Git repository không
        
        Returns:
            bool: True nếu là Git repo
        """
        git_dir = self.local_path / ".git"
        return git_dir.exists() and git_dir.is_dir()
    
    def init_repo(self) -> bool:
        """
        Khởi tạo Git repository mới
        
        Returns:
            bool: True nếu thành công
        """
        print("📦 Đang khởi tạo Git repository...")
        success, output = self.run_git_command(["git", "init"])
        
        if success:
            log_info("Git repository đã được khởi tạo")
            print("✅ Đã khởi tạo Git repository")
            return True
        else:
            log_error(f"Lỗi khởi tạo repository: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def clone_repo(self) -> bool:
        """
        Clone repository từ remote
        
        Returns:
            bool: True nếu thành công
        """
        print(f"📥 Đang clone repository từ: {self.repo_url}")
        print(f"   Đến: {self.local_path}")
        
        success, output = self.run_git_command(
            ["git", "clone", self.repo_url, str(self.local_path)],
            cwd=self.local_path.parent
        )
        
        if success:
            log_info(f"Đã clone repository thành công")
            print("✅ Đã clone repository thành công")
            return True
        else:
            log_error(f"Lỗi clone repository: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def setup_remote(self, remote_name: str = "origin") -> bool:
        """
        Thiết lập remote repository
        
        Args:
            remote_name: Tên remote (mặc định: origin)
        
        Returns:
            bool: True nếu thành công
        """
        # Kiểm tra remote đã tồn tại chưa
        success, output = self.run_git_command(["git", "remote", "get-url", remote_name])
        if success:
            print(f"ℹ️  Remote '{remote_name}' đã tồn tại: {output}")
            # Cập nhật URL nếu khác
            if output != self.repo_url:
                if confirm_action(f"Remote URL khác với URL mới. Cập nhật?"):
                    success, output = self.run_git_command(
                        ["git", "remote", "set-url", remote_name, self.repo_url]
                    )
                    if success:
                        print(f"✅ Đã cập nhật remote URL")
                        return True
                    else:
                        print(f"❌ Lỗi cập nhật remote: {output}")
                        return False
            return True
        
        # Thêm remote mới
        print(f"🔗 Đang thêm remote '{remote_name}'...")
        success, output = self.run_git_command(
            ["git", "remote", "add", remote_name, self.repo_url]
        )
        
        if success:
            log_info(f"Đã thêm remote: {remote_name} -> {self.repo_url}")
            print(f"✅ Đã thêm remote '{remote_name}'")
            return True
        else:
            log_error(f"Lỗi thêm remote: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def get_status(self) -> Tuple[bool, str]:
        """
        Lấy trạng thái Git
        
        Returns:
            tuple: (success, status_output)
        """
        return self.run_git_command(["git", "status", "--short"])
    
    def add_files(self, pattern: str = ".") -> bool:
        """
        Thêm files vào staging area
        
        Args:
            pattern: Pattern files cần add (mặc định: "." = tất cả)
        
        Returns:
            bool: True nếu thành công
        """
        print(f"📝 Đang thêm files vào staging area...")
        success, output = self.run_git_command(["git", "add", pattern])
        
        if success:
            log_info(f"Đã thêm files: {pattern}")
            print("✅ Đã thêm files vào staging area")
            return True
        else:
            log_error(f"Lỗi thêm files: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def commit(self, message: str) -> bool:
        """
        Commit changes
        
        Args:
            message: Commit message
        
        Returns:
            bool: True nếu thành công
        """
        print(f"💾 Đang commit với message: {message}")
        success, output = self.run_git_command(
            ["git", "commit", "-m", message]
        )
        
        if success:
            log_info(f"Đã commit: {message}")
            print("✅ Đã commit thành công")
            return True
        else:
            log_error(f"Lỗi commit: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def push(self, branch: str = "main", remote: str = "origin", force: bool = False) -> bool:
        """
        Push code lên remote repository
        
        Args:
            branch: Tên branch (mặc định: main)
            remote: Tên remote (mặc định: origin)
            force: Có force push không
        
        Returns:
            bool: True nếu thành công
        """
        print(f"🚀 Đang push code lên {remote}/{branch}...")
        
        cmd = ["git", "push", remote, branch]
        if force:
            cmd.append("--force")
        
        success, output = self.run_git_command(cmd)
        
        if success:
            log_info(f"Đã push thành công lên {remote}/{branch}")
            print(f"✅ Đã push thành công lên {remote}/{branch}")
            return True
        else:
            log_error(f"Lỗi push: {output}")
            print(f"❌ Lỗi push: {output}")
            if "authentication" in output.lower() or "permission" in output.lower():
                print("\n💡 Gợi ý:")
                print("   - Kiểm tra quyền truy cập repository")
                print("   - Sử dụng Personal Access Token nếu cần")
                print("   - Kiểm tra SSH key nếu dùng SSH URL")
            return False
    
    def get_current_branch(self) -> Optional[str]:
        """
        Lấy tên branch hiện tại
        
        Returns:
            str: Tên branch hoặc None
        """
        success, output = self.run_git_command(["git", "branch", "--show-current"])
        if success and output:
            return output.strip()
        return None
    
    def create_branch(self, branch_name: str) -> bool:
        """
        Tạo branch mới
        
        Args:
            branch_name: Tên branch
        
        Returns:
            bool: True nếu thành công
        """
        print(f"🌿 Đang tạo branch: {branch_name}")
        success, output = self.run_git_command(["git", "checkout", "-b", branch_name])
        
        if success:
            log_info(f"Đã tạo branch: {branch_name}")
            print(f"✅ Đã tạo và chuyển sang branch: {branch_name}")
            return True
        else:
            log_error(f"Lỗi tạo branch: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def list_branches(self) -> List[str]:
        """Lấy danh sách branches"""
        success, output = self.run_git_command(["git", "branch", "--format=%(refname:short)"])
        if success:
            return [b.strip() for b in output.splitlines() if b.strip()]
        return []
    
    def switch_branch(self, branch_name: str) -> bool:
        """Chuyển sang branch khác"""
        print(f"🔄 Đang chuyển sang branch: {branch_name}")
        success, output = self.run_git_command(["git", "checkout", branch_name])
        
        if success:
            log_info(f"Đã chuyển sang branch: {branch_name}")
            print(f"✅ Đã chuyển sang branch: {branch_name}")
            return True
        else:
            log_error(f"Lỗi chuyển branch: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """Xóa branch"""
        print(f"🗑️  Đang xóa branch: {branch_name}")
        cmd = ["git", "branch", "-D" if force else "-d", branch_name]
        success, output = self.run_git_command(cmd)
        
        if success:
            log_info(f"Đã xóa branch: {branch_name}")
            print(f"✅ Đã xóa branch: {branch_name}")
            return True
        else:
            log_error(f"Lỗi xóa branch: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def pull(self, remote: str = "origin", branch: Optional[str] = None) -> bool:
        """Pull code từ remote"""
        if branch is None:
            branch = self.get_current_branch() or "main"
        
        print(f"📥 Đang pull từ {remote}/{branch}...")
        success, output = self.run_git_command(["git", "pull", remote, branch])
        
        if success:
            log_info(f"Đã pull thành công từ {remote}/{branch}")
            print(f"✅ Đã pull thành công")
            return True
        else:
            log_error(f"Lỗi pull: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def fetch(self, remote: str = "origin") -> bool:
        """Fetch từ remote"""
        print(f"📥 Đang fetch từ {remote}...")
        success, output = self.run_git_command(["git", "fetch", remote])
        
        if success:
            log_info(f"Đã fetch thành công từ {remote}")
            print(f"✅ Đã fetch thành công")
            return True
        else:
            log_error(f"Lỗi fetch: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def merge(self, branch: str, no_ff: bool = False) -> bool:
        """Merge branch vào branch hiện tại"""
        print(f"🔀 Đang merge branch: {branch}")
        cmd = ["git", "merge", branch]
        if no_ff:
            cmd.append("--no-ff")
        
        success, output = self.run_git_command(cmd)
        
        if success:
            log_info(f"Đã merge thành công: {branch}")
            print(f"✅ Đã merge thành công")
            return True
        else:
            log_error(f"Lỗi merge: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def rebase(self, branch: str) -> bool:
        """Rebase branch hiện tại lên branch"""
        print(f"🔄 Đang rebase lên branch: {branch}")
        success, output = self.run_git_command(["git", "rebase", branch])
        
        if success:
            log_info(f"Đã rebase thành công lên {branch}")
            print(f"✅ Đã rebase thành công")
            return True
        else:
            log_error(f"Lỗi rebase: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def stash(self, message: Optional[str] = None) -> bool:
        """Stash changes"""
        print("💾 Đang stash changes...")
        cmd = ["git", "stash"]
        if message:
            cmd.extend(["push", "-m", message])
        
        success, output = self.run_git_command(cmd)
        
        if success:
            log_info("Đã stash thành công")
            print("✅ Đã stash thành công")
            return True
        else:
            log_error(f"Lỗi stash: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def stash_pop(self) -> bool:
        """Pop stash"""
        print("📤 Đang pop stash...")
        success, output = self.run_git_command(["git", "stash", "pop"])
        
        if success:
            log_info("Đã pop stash thành công")
            print("✅ Đã pop stash thành công")
            return True
        else:
            log_error(f"Lỗi pop stash: {output}")
            print(f"❌ Lỗi: {output}")
            return False
    
    def list_remotes(self) -> List[Dict[str, str]]:
        """Lấy danh sách remotes"""
        success, output = self.run_git_command(["git", "remote", "-v"])
        remotes = []
        
        if success:
            for line in output.splitlines():
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        remotes.append({
                            'name': parts[0],
                            'url': parts[1]
                        })
        
        return remotes
    
    def list_stashes(self) -> List[str]:
        """Lấy danh sách stashes"""
        success, output = self.run_git_command(["git", "stash", "list"])
        if success:
            return [s.strip() for s in output.splitlines() if s.strip()]
        return []


def select_repository(config_manager: RepoConfigManager) -> Tuple[str, str]:
    """
    Chọn repository từ danh sách hoặc nhập mới
    
    Returns:
        tuple: (repo_url, local_path)
    """
    repos = config_manager.get_repositories()
    default_repo = config_manager.config.get('default_repo', 'https://github.com/VHN-DEV/laravel-botble-cms')
    
    if repos:
        print("\n📚 DANH SÁCH REPOSITORY ĐÃ LƯU:")
        for idx, repo in enumerate(repos, 1):
            print(f"   {idx}. {Colors.info(repo['name'])}")
            print(f"      URL: {repo['repo_url']}")
            print(f"      Path: {repo['local_path']}")
        
        print(f"\n   {len(repos) + 1}. Nhập repository mới")
        print(f"   {len(repos) + 2}. Sử dụng repository mặc định: {Colors.info(default_repo)}")
        
        choice = get_user_input(f"\nChọn repository (1-{len(repos) + 2})", default=str(len(repos) + 2))
        
        try:
            idx = int(choice)
            if 1 <= idx <= len(repos):
                selected = repos[idx - 1]
                return selected['repo_url'], selected['local_path']
            elif idx == len(repos) + 1:
                # Nhập mới
                pass
            elif idx == len(repos) + 2:
                # Dùng mặc định
                local_path = get_user_input(
                    "Nhập đường dẫn local (Enter để dùng thư mục hiện tại)",
                    default="."
                )
                return default_repo, normalize_path(local_path)
        except ValueError:
            pass
    
    # Nhập repository mới
    print(f"\n📋 Repository mặc định: {Colors.info(default_repo)}")
    use_default = get_user_input(
        "Sử dụng repository mặc định? (y/n)",
        default="y"
    ).lower() == "y"
    
    if use_default:
        repo_url = default_repo
    else:
        repo_url = get_user_input("Nhập URL repository", default=default_repo)
    
    print("\n💡 Mẹo: Bạn có thể kéo thả thư mục vào terminal để nhập đường dẫn")
    local_path_input = get_user_input(
        "Nhập đường dẫn thư mục local (Enter để dùng thư mục hiện tại)",
        default="."
    )
    local_path = normalize_path(local_path_input)
    
    # Hỏi có muốn lưu không
    if confirm_action("Lưu repository này vào danh sách?"):
        repo_name = get_user_input("Nhập tên cho repository", default=Path(repo_url).stem)
        config_manager.add_repository(repo_name, repo_url, local_path)
        print(f"✅ Đã lưu repository: {repo_name}")
    
    return repo_url, local_path


def main_interactive():
    """
    Chế độ interactive
    
    Giải thích:
    - Hỏi người dùng từng bước
    - Hiển thị menu lựa chọn
    """
    print_header("TOOL KẾT NỐI GIT VÀ PUSH SOURCE CODE")
    
    # Khởi tạo config manager
    config_manager = RepoConfigManager()
    
    # Chọn repository
    repo_url, local_path = select_repository(config_manager)
    
    # Khởi tạo GitManager
    git_manager = GitManager(repo_url, local_path)
    
    # Kiểm tra Git đã cài đặt
    if not git_manager.check_git_installed():
        print("❌ Git chưa được cài đặt!")
        print("   Vui lòng cài đặt Git từ: https://git-scm.com/downloads")
        return
    
    print(f"\n✅ Đã chọn:")
    print(f"   Repository: {repo_url}")
    print(f"   Local path: {local_path}\n")
    
    while True:
        # Menu chính
        print("===== MENU CHÍNH =====")
        print("📦 QUẢN LÝ REPOSITORY:")
        print("  1. Clone repository (nếu chưa có)")
        print("  2. Khởi tạo repository mới")
        print("  3. Thiết lập remote")
        print("  4. Xem trạng thái")
        print("  5. Quản lý repository (thêm/xóa)")
        print("")
        print("📝 THAO TÁC CODE:")
        print("  6. Add files và commit")
        print("  7. Push code lên remote")
        print("  8. Pull code từ remote")
        print("  9. Fetch từ remote")
        print(" 10. Thực hiện đầy đủ (add + commit + push)")
        print("")
        print("🌿 QUẢN LÝ BRANCH:")
        print(" 11. Tạo branch mới")
        print(" 12. Chuyển branch")
        print(" 13. Xem danh sách branches")
        print(" 14. Xóa branch")
        print("")
        print("🔀 TÍNH NĂNG NÂNG CAO:")
        print(" 15. Merge branch")
        print(" 16. Rebase branch")
        print(" 17. Stash changes")
        print(" 18. Pop stash")
        print(" 19. Xem danh sách remotes")
        print("")
        print("📊 KHÁC:")
        print(" 20. Xem lịch sử thao tác")
        print(" 21. Chọn repository khác")
        print("  0. Thoát")
        
        choice = get_user_input("\nChọn chức năng (0-21)", default="10")
    
        if choice == "0":
            print("Thoát chương trình.")
            break
        
        # Xử lý các lựa chọn
        if choice == "1":
            # Clone repository
            if git_manager.local_path.exists() and any(git_manager.local_path.iterdir()):
                if not confirm_action("Thư mục không trống. Tiếp tục?"):
                    continue
            if git_manager.clone_repo():
                config_manager.add_history("clone", repo_url, local_path, True)
        
        elif choice == "2":
            # Khởi tạo repository
            if git_manager.is_git_repo():
                print("ℹ️  Thư mục đã là Git repository")
            else:
                if git_manager.init_repo():
                    git_manager.setup_remote()
                    config_manager.add_history("init", repo_url, local_path, True)
        
        elif choice == "3":
            # Thiết lập remote
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                if confirm_action("Khởi tạo repository mới?"):
                    git_manager.init_repo()
            if git_manager.setup_remote():
                config_manager.add_history("setup_remote", repo_url, local_path, True)
        
        elif choice == "4":
            # Xem trạng thái
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            success, status = git_manager.get_status()
            if success:
                print("\n📊 Trạng thái Git:")
                print(status if status else "Không có thay đổi")
                
                # Hiển thị branch hiện tại
                branch = git_manager.get_current_branch()
                if branch:
                    print(f"\n🌿 Branch hiện tại: {Colors.info(branch)}")
                
                # Hiển thị remotes
                remotes = git_manager.list_remotes()
                if remotes:
                    print(f"\n🔗 Remotes:")
                    for remote in remotes:
                        print(f"   {remote['name']}: {remote['url']}")
            else:
                print(f"❌ Lỗi: {status}")
        
        elif choice == "5":
            # Quản lý repository
            print("\n===== QUẢN LÝ REPOSITORY =====")
            print("1. Thêm repository mới")
            print("2. Xóa repository")
            print("3. Xem danh sách repository")
            
            sub_choice = get_user_input("Chọn (1-3)", default="3")
            
            if sub_choice == "1":
                name = get_user_input("Nhập tên repository")
                repo_url = get_user_input("Nhập URL repository")
                local_path = normalize_path(get_user_input("Nhập đường dẫn local", default="."))
                
                if config_manager.add_repository(name, repo_url, local_path):
                    print(f"✅ Đã thêm repository: {name}")
                else:
                    print("❌ Repository đã tồn tại!")
            
            elif sub_choice == "2":
                repos = config_manager.get_repositories()
                if not repos:
                    print("❌ Không có repository nào!")
                else:
                    print("\nDanh sách repository:")
                    for idx, repo in enumerate(repos, 1):
                        print(f"  {idx}. {repo['name']}")
                    
                    idx = get_user_input("Chọn số thứ tự để xóa")
                    try:
                        idx = int(idx) - 1
                        if 0 <= idx < len(repos):
                            name = repos[idx]['name']
                            if confirm_action(f"Xóa repository '{name}'?"):
                                config_manager.remove_repository(name)
                                print(f"✅ Đã xóa repository: {name}")
                    except ValueError:
                        print("❌ Số không hợp lệ!")
            
            elif sub_choice == "3":
                repos = config_manager.get_repositories()
                if repos:
                    print("\n📚 DANH SÁCH REPOSITORY:")
                    for idx, repo in enumerate(repos, 1):
                        print(f"\n  {idx}. {Colors.info(repo['name'])}")
                        print(f"     URL: {repo['repo_url']}")
                        print(f"     Path: {repo['local_path']}")
                else:
                    print("❌ Không có repository nào!")
        
        elif choice == "6":
            # Add files và commit
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            # Xem trạng thái trước
            success, status = git_manager.get_status()
            if success and status:
                print("\n📊 Files thay đổi:")
                print(status)
            else:
                print("ℹ️  Không có files thay đổi")
                continue
            
            # Add files
            pattern = get_user_input(
                "Nhập pattern files cần add (Enter để add tất cả)",
                default="."
            )
            if git_manager.add_files(pattern):
                # Commit
                commit_msg = get_user_input(
                    "Nhập commit message",
                    default="Update source code"
                )
                if git_manager.commit(commit_msg):
                    config_manager.add_history(f"commit:{commit_msg}", repo_url, local_path, True)
        
        elif choice == "7":
            # Push code
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            branch = git_manager.get_current_branch()
            if not branch:
                branch = get_user_input("Nhập tên branch", default="main")
            else:
                use_current = get_user_input(
                    f"Sử dụng branch hiện tại '{branch}'? (y/n)",
                    default="y"
                ).lower() == "y"
                if not use_current:
                    branch = get_user_input("Nhập tên branch", default=branch)
            
            force = confirm_action("Force push? (Cẩn thận!)", require_yes=True)
            if git_manager.push(branch=branch, force=force):
                config_manager.add_history(f"push:{branch}", repo_url, local_path, True)
        
        elif choice == "8":
            # Pull code
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            remote = get_user_input("Nhập tên remote (Enter để dùng origin)", default="origin")
            branch = get_user_input("Nhập tên branch (Enter để dùng branch hiện tại)", default="")
            git_manager.pull(remote=remote, branch=branch if branch else None)
            config_manager.add_history("pull", repo_url, local_path, True)
        
        elif choice == "9":
            # Fetch
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            remote = get_user_input("Nhập tên remote (Enter để dùng origin)", default="origin")
            git_manager.fetch(remote=remote)
            config_manager.add_history("fetch", repo_url, local_path, True)
        
        elif choice == "11":
            # Tạo branch mới
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            branch_name = get_user_input("Nhập tên branch mới")
            if branch_name:
                if git_manager.create_branch(branch_name):
                    config_manager.add_history(f"create_branch:{branch_name}", repo_url, local_path, True)
        
        elif choice == "12":
            # Chuyển branch
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            branches = git_manager.list_branches()
            if branches:
                print("\n🌿 Danh sách branches:")
                for idx, b in enumerate(branches, 1):
                    current = "*" if b == git_manager.get_current_branch() else " "
                    print(f"  {current} {idx}. {b}")
                
                choice_branch = get_user_input("Chọn số thứ tự hoặc nhập tên branch")
                try:
                    idx = int(choice_branch) - 1
                    if 0 <= idx < len(branches):
                        branch_name = branches[idx]
                    else:
                        branch_name = choice_branch
                except ValueError:
                    branch_name = choice_branch
                
                if git_manager.switch_branch(branch_name):
                    config_manager.add_history(f"switch_branch:{branch_name}", repo_url, local_path, True)
            else:
                print("❌ Không có branch nào!")
        
        elif choice == "13":
            # Xem danh sách branches
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            branches = git_manager.list_branches()
            current = git_manager.get_current_branch()
            
            if branches:
                print("\n🌿 DANH SÁCH BRANCHES:")
                for branch in branches:
                    marker = " *" if branch == current else "  "
                    print(f"{marker} {branch}")
            else:
                print("❌ Không có branch nào!")
        
        elif choice == "14":
            # Xóa branch
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            branches = git_manager.list_branches()
            current = git_manager.get_current_branch()
            
            if branches:
                print("\n🌿 Danh sách branches:")
                for idx, b in enumerate(branches, 1):
                    marker = "*" if b == current else " "
                    print(f"  {marker} {idx}. {b}")
                
                choice_branch = get_user_input("Chọn số thứ tự hoặc nhập tên branch để xóa")
                try:
                    idx = int(choice_branch) - 1
                    if 0 <= idx < len(branches):
                        branch_name = branches[idx]
                    else:
                        branch_name = choice_branch
                except ValueError:
                    branch_name = choice_branch
                
                if branch_name == current:
                    print("❌ Không thể xóa branch hiện tại!")
                else:
                    force = confirm_action("Force delete? (Cẩn thận!)", require_yes=True)
                    if git_manager.delete_branch(branch_name, force=force):
                        config_manager.add_history(f"delete_branch:{branch_name}", repo_url, local_path, True)
            else:
                print("❌ Không có branch nào!")
        
        elif choice == "15":
            # Merge branch
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            branches = git_manager.list_branches()
            if branches:
                print("\n🌿 Danh sách branches:")
                for idx, b in enumerate(branches, 1):
                    print(f"  {idx}. {b}")
                
                choice_branch = get_user_input("Chọn số thứ tự hoặc nhập tên branch để merge")
                try:
                    idx = int(choice_branch) - 1
                    if 0 <= idx < len(branches):
                        branch_name = branches[idx]
                    else:
                        branch_name = choice_branch
                except ValueError:
                    branch_name = choice_branch
                
                no_ff = confirm_action("No fast-forward merge?")
                if git_manager.merge(branch_name, no_ff=no_ff):
                    config_manager.add_history(f"merge:{branch_name}", repo_url, local_path, True)
            else:
                print("❌ Không có branch nào!")
        
        elif choice == "16":
            # Rebase branch
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            branches = git_manager.list_branches()
            if branches:
                print("\n🌿 Danh sách branches:")
                for idx, b in enumerate(branches, 1):
                    print(f"  {idx}. {b}")
                
                choice_branch = get_user_input("Chọn số thứ tự hoặc nhập tên branch để rebase lên")
                try:
                    idx = int(choice_branch) - 1
                    if 0 <= idx < len(branches):
                        branch_name = branches[idx]
                    else:
                        branch_name = choice_branch
                except ValueError:
                    branch_name = choice_branch
                
                if git_manager.rebase(branch_name):
                    config_manager.add_history(f"rebase:{branch_name}", repo_url, local_path, True)
            else:
                print("❌ Không có branch nào!")
        
        elif choice == "17":
            # Stash
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            message = get_user_input("Nhập message cho stash (Enter để bỏ qua)", default="")
            if git_manager.stash(message if message else None):
                config_manager.add_history("stash", repo_url, local_path, True)
        
        elif choice == "18":
            # Pop stash
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            stashes = git_manager.list_stashes()
            if stashes:
                print("\n💾 Danh sách stashes:")
                for idx, s in enumerate(stashes, 1):
                    print(f"  {idx}. {s}")
            
            if git_manager.stash_pop():
                config_manager.add_history("stash_pop", repo_url, local_path, True)
        
        elif choice == "19":
            # Xem remotes
            if not git_manager.is_git_repo():
                print("❌ Thư mục chưa phải Git repository!")
                continue
            
            remotes = git_manager.list_remotes()
            if remotes:
                print("\n🔗 DANH SÁCH REMOTES:")
                for remote in remotes:
                    print(f"  {remote['name']}: {remote['url']}")
            else:
                print("❌ Không có remote nào!")
        
        elif choice == "20":
            # Xem lịch sử
            history = config_manager.get_history(20)
            if history:
                print("\n📊 LỊCH SỬ THAO TÁC (20 gần nhất):")
                for idx, item in enumerate(history, 1):
                    status = "✅" if item['success'] else "❌"
                    timestamp = item['timestamp'][:19].replace('T', ' ')
                    print(f"\n  {idx}. {status} {item['action']}")
                    print(f"     Repository: {item['repo_url']}")
                    print(f"     Path: {item['local_path']}")
                    print(f"     Thời gian: {timestamp}")
            else:
                print("❌ Chưa có lịch sử!")
        
        elif choice == "21":
            # Chọn repository khác
            repo_url, local_path = select_repository(config_manager)
            git_manager = GitManager(repo_url, local_path)
            print(f"\n✅ Đã chuyển sang:")
            print(f"   Repository: {repo_url}")
            print(f"   Local path: {local_path}\n")
        
        else:
            print(f"❌ Lựa chọn không hợp lệ: {choice}")
        
        print()  # Dòng trống giữa các lần lặp


def main_cli(args):
    """
    Chế độ CLI
    
    Args:
        args: Arguments từ argparse
    """
    git_manager = GitManager(args.repo, args.path)
    
    # Kiểm tra Git
    if not git_manager.check_git_installed():
        print("❌ Git chưa được cài đặt!")
        return 1
    
    # Khởi tạo/clone nếu cần
    if args.clone:
        if not git_manager.is_git_repo():
            if not git_manager.clone_repo():
                return 1
        else:
            print("ℹ️  Thư mục đã là Git repository")
    
    if args.init:
        if not git_manager.is_git_repo():
            if not git_manager.init_repo():
                return 1
            if not git_manager.setup_remote():
                return 1
        else:
            print("ℹ️  Thư mục đã là Git repository")
    
    # Setup remote
    if args.setup_remote:
        if not git_manager.is_git_repo():
            print("❌ Thư mục chưa phải Git repository!")
            return 1
        if not git_manager.setup_remote():
            return 1
    
    # Add files
    if args.add:
        if not git_manager.is_git_repo():
            print("❌ Thư mục chưa phải Git repository!")
            return 1
        if not git_manager.add_files(args.add):
            return 1
    
    # Commit
    if args.commit:
        if not git_manager.is_git_repo():
            print("❌ Thư mục chưa phải Git repository!")
            return 1
        if not git_manager.commit(args.commit):
            return 1
    
    # Push
    if args.push:
        if not git_manager.is_git_repo():
            print("❌ Thư mục chưa phải Git repository!")
            return 1
        branch = args.branch or git_manager.get_current_branch() or "main"
        if not git_manager.push(branch=branch, force=args.force):
            return 1
    
    # Status
    if args.status:
        if not git_manager.is_git_repo():
            print("❌ Thư mục chưa phải Git repository!")
            return 1
        success, status = git_manager.get_status()
        if success:
            print(status if status else "Không có thay đổi")
        else:
            print(f"❌ Lỗi: {status}")
            return 1
    
    return 0


def main():
    """Hàm main"""
    # Setup logger
    setup_logger('git-push-source', log_to_console=False)
    
    # Argument parser
    parser = argparse.ArgumentParser(
        description='Tool kết nối Git và push source code lên repository',
        epilog="""
Ví dụ:
  # Interactive mode
  python git-push-source.py
  
  # Clone repository
  python git-push-source.py --clone --repo https://github.com/user/repo --path ./project
  
  # Add, commit và push
  python git-push-source.py --add . --commit "Update code" --push --branch main
  
  # Xem trạng thái
  python git-push-source.py --status
        """
    )
    
    parser.add_argument('--repo', default='https://github.com/VHN-DEV/laravel-botble-cms',
                       help='URL repository (mặc định: https://github.com/VHN-DEV/laravel-botble-cms)')
    parser.add_argument('--path', default='.',
                       help='Đường dẫn thư mục local (mặc định: thư mục hiện tại)')
    parser.add_argument('--clone', action='store_true',
                       help='Clone repository')
    parser.add_argument('--init', action='store_true',
                       help='Khởi tạo Git repository mới')
    parser.add_argument('--setup-remote', action='store_true',
                       help='Thiết lập remote')
    parser.add_argument('--add', metavar='PATTERN',
                       help='Add files (pattern, mặc định: .)')
    parser.add_argument('--commit', metavar='MESSAGE',
                       help='Commit với message')
    parser.add_argument('--push', action='store_true',
                       help='Push code lên remote')
    parser.add_argument('--branch', default='main',
                       help='Tên branch (mặc định: main)')
    parser.add_argument('--force', action='store_true',
                       help='Force push')
    parser.add_argument('--status', action='store_true',
                       help='Xem trạng thái Git')
    
    args, unknown = parser.parse_known_args()
    
    if any([args.clone, args.init, args.setup_remote, args.add, args.commit, args.push, args.status]):
        sys.exit(main_cli(args))
    else:
        try:
            main_interactive()
        except KeyboardInterrupt:
            print("\n\n❌ Đã hủy!")
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            log_error(f"Exception: {e}", exc_info=True)


if __name__ == "__main__":
    main()

