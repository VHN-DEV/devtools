#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module marketplace - Quản lý Tool Marketplace

Mục đích: Tải và cài đặt tools từ remote repository
Lý do: Cho phép người dùng chia sẻ và tải tools từ cộng đồng
"""

import os
import json
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import requests
from utils.colors import Colors
from utils.format import print_separator
from utils.progress import ProgressBar, Spinner


class MarketplaceManager:
    """
    Class quản lý Tool Marketplace
    
    Mục đích: Tải, cài đặt, và quản lý tools từ remote repository
    """
    
    # Default marketplace registry URL
    DEFAULT_REGISTRY_URL = "https://raw.githubusercontent.com/VHN-DEV/DevTools-Marketplace/main/registry.json"
    
    # Local registry fallback
    LOCAL_REGISTRY_FILE = Path(__file__).parent.parent / "plugins" / "cache" / "marketplace" / "registry.json"
    
    def __init__(self, tool_dir: str, cache_dir: Optional[str] = None):
        """
        Khởi tạo MarketplaceManager
        
        Args:
            tool_dir: Thư mục chứa tools (tools/)
            cache_dir: Thư mục cache (mặc định: plugins/cache/marketplace)
        """
        self.tool_dir = Path(tool_dir)
        self.cache_dir = Path(cache_dir) if cache_dir else Path(__file__).parent.parent / "plugins" / "cache" / "marketplace"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache registry data
        self.registry_cache_file = self.cache_dir / "registry_cache.json"
        self.registry_cache_ttl = 3600  # 1 giờ
        
        # Config file cho marketplace settings
        self.config_file = self.cache_dir / "marketplace_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load config từ file"""
        default_config = {
            'registry_url': self.DEFAULT_REGISTRY_URL,
            'installed_tools': {},
            'last_update': None
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge với default để đảm bảo có đầy đủ fields
                    default_config.update(loaded)
                    return default_config
            except Exception:
                pass
        
        return default_config
    
    def _save_config(self):
        """Lưu config ra file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(Colors.error(f"❌ Lỗi lưu config: {e}"))
    
    def _is_cache_valid(self, cache_file: Path, ttl: int) -> bool:
        """Kiểm tra cache còn hiệu lực không"""
        if not cache_file.exists():
            return False
        
        try:
            mtime = cache_file.stat().st_mtime
            age = datetime.now().timestamp() - mtime
            return age < ttl
        except Exception:
            return False
    
    def fetch_registry(self, force_refresh: bool = False) -> Optional[Dict]:
        """
        Lấy registry từ remote hoặc cache
        
        Args:
            force_refresh: Bỏ qua cache và fetch mới
        
        Returns:
            dict: Registry data hoặc None nếu lỗi
        """
        # Kiểm tra cache trước
        if not force_refresh and self._is_cache_valid(self.registry_cache_file, self.registry_cache_ttl):
            try:
                with open(self.registry_cache_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                    print(Colors.info("ℹ️  Đang dùng registry từ cache"))
                    return registry
            except Exception:
                pass
        
        # Thử load từ local registry trước (nếu có)
        if self.LOCAL_REGISTRY_FILE.exists():
            try:
                with open(self.LOCAL_REGISTRY_FILE, 'r', encoding='utf-8') as f:
                    local_registry = json.load(f)
                    print(Colors.info("ℹ️  Đang dùng registry local"))
                    return local_registry
            except Exception:
                pass
        
        # Fetch từ remote
        registry_url = self.config.get('registry_url', self.DEFAULT_REGISTRY_URL)
        
        print(Colors.info(f"📥 Đang tải registry từ: {registry_url}"))
        spinner = Spinner("Đang tải registry...")
        spinner.start()
        
        try:
            response = requests.get(registry_url, timeout=30)
            response.raise_for_status()
            
            registry = response.json()
            
            # Lưu vào cache
            try:
                with open(self.registry_cache_file, 'w', encoding='utf-8') as f:
                    json.dump(registry, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
            
            spinner.stop("✅ Đã tải registry thành công")
            return registry
            
        except requests.exceptions.RequestException as e:
            spinner.stop()
            print(Colors.warning(f"⚠️  Không thể tải registry từ remote: {e}"))
            
            # Thử dùng cache cũ nếu có
            if self.registry_cache_file.exists():
                try:
                    with open(self.registry_cache_file, 'r', encoding='utf-8') as f:
                        registry = json.load(f)
                        print(Colors.warning("⚠️  Đang dùng registry cache cũ (có thể không cập nhật)"))
                        return registry
                except Exception:
                    pass
            
            # Thử dùng local registry nếu có
            if self.LOCAL_REGISTRY_FILE.exists():
                try:
                    with open(self.LOCAL_REGISTRY_FILE, 'r', encoding='utf-8') as f:
                        local_registry = json.load(f)
                        print(Colors.info("ℹ️  Đang dùng registry local (fallback)"))
                        return local_registry
                except Exception as e2:
                    print(Colors.error(f"❌ Lỗi khi đọc registry local: {e2}"))
            
            print(Colors.error("❌ Không thể tải registry. Vui lòng kiểm tra kết nối internet hoặc tạo registry local."))
            print(Colors.info("💡 Tạo file registry tại: plugins/cache/marketplace/registry.json"))
            return None
        except Exception as e:
            spinner.stop()
            print(Colors.error(f"❌ Lỗi: {e}"))
            return None
    
    def search_tools(self, query: str, registry: Optional[Dict] = None) -> List[Dict]:
        """
        Tìm kiếm tools trong registry
        
        Args:
            query: Từ khóa tìm kiếm
            registry: Registry data (None = tự động fetch)
        
        Returns:
            list: Danh sách tools phù hợp
        """
        if registry is None:
            registry = self.fetch_registry()
            if not registry:
                return []
        
        tools = registry.get('tools', [])
        query_lower = query.lower()
        
        results = []
        for tool in tools:
            # Tìm trong tên, mô tả, tags
            name = tool.get('name', '').lower()
            description = tool.get('description', '').lower()
            tags = [tag.lower() for tag in tool.get('tags', [])]
            
            if (query_lower in name or 
                query_lower in description or 
                any(query_lower in tag for tag in tags)):
                results.append(tool)
        
        return results
    
    def list_available_tools(self, registry: Optional[Dict] = None, category: Optional[str] = None) -> List[Dict]:
        """
        Liệt kê tất cả tools có sẵn
        
        Args:
            registry: Registry data (None = tự động fetch)
            category: Lọc theo category (None = tất cả)
        
        Returns:
            list: Danh sách tools
        """
        if registry is None:
            registry = self.fetch_registry()
            if not registry:
                return []
        
        tools = registry.get('tools', [])
        
        if category:
            tools = [t for t in tools if t.get('category', '').lower() == category.lower()]
        
        return tools
    
    def get_tool_info(self, tool_id: str, registry: Optional[Dict] = None) -> Optional[Dict]:
        """
        Lấy thông tin chi tiết của một tool
        
        Args:
            tool_id: ID của tool (vd: 'backup-folder')
            registry: Registry data (None = tự động fetch)
        
        Returns:
            dict: Thông tin tool hoặc None nếu không tìm thấy
        """
        if registry is None:
            registry = self.fetch_registry()
            if not registry:
                return None
        
        tools = registry.get('tools', [])
        for tool in tools:
            if tool.get('id') == tool_id:
                return tool
        
        return None
    
    def download_tool(self, tool_info: Dict, show_progress: bool = True) -> Optional[Path]:
        """
        Tải tool từ URL
        
        Args:
            tool_info: Thông tin tool từ registry
            show_progress: Có hiển thị progress bar không
        
        Returns:
            Path: Đường dẫn file zip đã tải hoặc None nếu lỗi
        """
        download_url = tool_info.get('download_url')
        if not download_url:
            print(Colors.error("❌ Tool không có download URL"))
            return None
        
        tool_id = tool_info.get('id', 'unknown')
        temp_file = self.cache_dir / f"{tool_id}_temp.zip"
        
        try:
            if show_progress:
                print(Colors.info(f"📥 Đang tải: {tool_info.get('name', tool_id)}"))
            
            # Download với progress bar
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            if show_progress and total_size > 0:
                progress = ProgressBar(
                    total=total_size,
                    prefix="Tải xuống:",
                    suffix="bytes",
                    show_percentage=True
                )
            
            with open(temp_file, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if show_progress and total_size > 0:
                            progress.update(downloaded)
            
            if show_progress and total_size > 0:
                progress.finish("Tải xuống hoàn tất")
            
            return temp_file
            
        except requests.exceptions.RequestException as e:
            print(Colors.error(f"❌ Lỗi khi tải tool: {e}"))
            if temp_file.exists():
                temp_file.unlink()
            return None
        except Exception as e:
            print(Colors.error(f"❌ Lỗi: {e}"))
            if temp_file.exists():
                temp_file.unlink()
            return None
    
    def install_tool(self, tool_info: Dict, overwrite: bool = False) -> bool:
        """
        Cài đặt tool từ file zip hoặc URL
        
        Args:
            tool_info: Thông tin tool từ registry
            overwrite: Có ghi đè tool đã tồn tại không
        
        Returns:
            bool: True nếu thành công
        """
        tool_id = tool_info.get('id')
        if not tool_id:
            print(Colors.error("❌ Tool không có ID"))
            return False
        
        tool_name = f"{tool_id}.py"
        tool_type = tool_info.get('type', 'py')  # 'py' hoặc 'sh'
        
        # Kiểm tra tool đã tồn tại chưa
        target_dir = self.tool_dir / tool_type / tool_id
        if target_dir.exists() and not overwrite:
            print(Colors.warning(f"⚠️  Tool '{tool_id}' đã tồn tại!"))
            confirm = input(Colors.warning("   Bạn có muốn ghi đè? (yes/no): ")).strip().lower()
            if confirm not in ['yes', 'y', 'có', 'c']:
                print(Colors.info("ℹ️  Đã hủy cài đặt"))
                return False
        
        # Tải tool
        zip_file = self.download_tool(tool_info, show_progress=True)
        if not zip_file or not zip_file.exists():
            return False
        
        try:
            # Giải nén vào thư mục tạm
            temp_extract = self.cache_dir / f"{tool_id}_extract"
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
            temp_extract.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                zipf.extractall(temp_extract)
            
            # Tìm thư mục tool trong extracted files
            tool_dir_found = None
            for item in temp_extract.iterdir():
                if item.is_dir() and (item.name == tool_id or item.name == f"{tool_type}/{tool_id}"):
                    tool_dir_found = item
                    break
                elif item.is_dir() and tool_id in item.name:
                    # Thử tìm trong subdirectory
                    potential_dir = item / tool_id
                    if potential_dir.exists():
                        tool_dir_found = potential_dir
                        break
            
            if not tool_dir_found:
                # Nếu không tìm thấy, coi như toàn bộ temp_extract là tool
                tool_dir_found = temp_extract
            
            # Xóa tool cũ nếu có
            if target_dir.exists():
                shutil.rmtree(target_dir)
            
            # Copy vào vị trí đích
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(tool_dir_found, target_dir)
            
            # Cập nhật config
            self.config['installed_tools'][tool_id] = {
                'name': tool_info.get('name'),
                'version': tool_info.get('version', '1.0.0'),
                'installed_at': datetime.now().isoformat(),
                'source': 'marketplace'
            }
            self._save_config()
            
            # Dọn dẹp
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
            if zip_file.exists():
                zip_file.unlink()
            
            print(Colors.success(f"✅ Đã cài đặt tool: {tool_info.get('name', tool_id)}"))
            return True
            
        except Exception as e:
            print(Colors.error(f"❌ Lỗi khi cài đặt tool: {e}"))
            import traceback
            traceback.print_exc()
            return False
    
    def uninstall_tool(self, tool_id: str) -> bool:
        """
        Gỡ cài đặt tool
        
        Args:
            tool_id: ID của tool cần gỡ
        
        Returns:
            bool: True nếu thành công
        """
        # Tìm tool trong tools/py/ hoặc tools/sh/
        for tool_type in ['py', 'sh']:
            tool_dir = self.tool_dir / tool_type / tool_id
            if tool_dir.exists():
                try:
                    shutil.rmtree(tool_dir)
                    
                    # Xóa khỏi config
                    if tool_id in self.config.get('installed_tools', {}):
                        del self.config['installed_tools'][tool_id]
                        self._save_config()
                    
                    print(Colors.success(f"✅ Đã gỡ cài đặt tool: {tool_id}"))
                    return True
                except Exception as e:
                    print(Colors.error(f"❌ Lỗi khi gỡ cài đặt: {e}"))
                    return False
        
        print(Colors.warning(f"⚠️  Không tìm thấy tool: {tool_id}"))
        return False
    
    def list_installed_tools(self) -> List[Dict]:
        """
        Liệt kê các tools đã cài từ marketplace
        
        Returns:
            list: Danh sách tools đã cài
        """
        installed = self.config.get('installed_tools', {})
        return [
            {
                'id': tool_id,
                **info
            }
            for tool_id, info in installed.items()
        ]
    
    def update_tool(self, tool_id: str, registry: Optional[Dict] = None) -> bool:
        """
        Cập nhật tool lên phiên bản mới nhất
        
        Args:
            tool_id: ID của tool
            registry: Registry data (None = tự động fetch)
        
        Returns:
            bool: True nếu có update và cài đặt thành công
        """
        if registry is None:
            registry = self.fetch_registry()
            if not registry:
                return False
        
        tool_info = self.get_tool_info(tool_id, registry)
        if not tool_info:
            print(Colors.error(f"❌ Không tìm thấy tool: {tool_id}"))
            return False
        
        # Kiểm tra version
        installed_info = self.config.get('installed_tools', {}).get(tool_id, {})
        installed_version = installed_info.get('version', '0.0.0')
        latest_version = tool_info.get('version', '0.0.0')
        
        if installed_version >= latest_version:
            print(Colors.info(f"ℹ️  Tool '{tool_id}' đã ở phiên bản mới nhất ({installed_version})"))
            return False
        
        print(Colors.info(f"🔄 Đang cập nhật '{tool_id}' từ {installed_version} lên {latest_version}"))
        return self.install_tool(tool_info, overwrite=True)

