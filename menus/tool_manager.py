#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module tool_manager - Quản lý và chạy tools

Mục đích: Tách logic quản lý tools ra khỏi menu chính
Lý do: Dễ maintain, test và mở rộng
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
from utils.colors import Colors
from utils.format import print_header, print_separator
from utils.categories import group_tools_by_category, get_category_info
from utils.helpers import highlight_keyword, strip_ansi
from utils.logger import log_error_to_file


class ToolManager:
    """
    Class quản lý tools
    
    Mục đích: Tập trung logic quản lý tools, favorites, history
    """
    
    def __init__(self, tool_dir: str):
        """
        Khởi tạo ToolManager
        
        Args:
            tool_dir: Thư mục chứa tools
        """
        self.tool_dir = Path(tool_dir)
        # Config file nằm trong thư mục menu
        self.config_file = Path(__file__).parent / "tool_config.json"
        self.config = self._load_config()
        
        # Cache metadata của tools (tự động load khi cần)
        self.tool_names = {}
        self.tool_tags = {}
        self.tool_types = {}  # Cache loại tool: 'py' hoặc 'sh'
        
        # Cache tool list để tránh scan lại nhiều lần
        self._cached_tool_list = None
        self._cache_timestamp = None
        self._cache_ttl = 60  # Cache trong 60 giây
        
        # Danh sách tools theo đúng thứ tự hiển thị (được cập nhật mỗi khi hiển thị menu)
        self.displayed_tools_order = []
        
        # Tools ưu tiên hiển thị lên đầu danh sách
        # Mục đích: Các tools hay dùng nhất hoặc quan trọng nhất sẽ hiển thị trước
        # Lý do: Dễ dàng truy cập nhanh các tools thường xuyên sử dụng
        self.priority_tools = [
            "ssh-manager.py",  # Tool SSH Manager - hay dùng nhất
            # Có thể thêm các tools khác vào đây để ưu tiên
        ]
    
    def _load_config(self) -> Dict:
        """
        Load config từ file
        
        Returns:
            dict: Config data
        
        Giải thích:
        - Lưu favorites, recent tools, settings, disabled_tools
        - Tạo config mặc định nếu chưa có
        - Đảm bảo các field mới được thêm vào config cũ (migration)
        """
        default_config = {
            'favorites': [],
            'recent': [],
            'disabled_tools': [],  # Danh sách tools bị vô hiệu hóa
            'settings': {
                'show_descriptions': True,
                'max_recent': 10
            },
            'statistics': {
                'tool_usage': {},  # Số lần sử dụng mỗi tool
                'last_used': {}    # Timestamp lần cuối sử dụng
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Đảm bảo các field mới có trong config cũ (migration)
                    if 'disabled_tools' not in loaded_config:
                        loaded_config['disabled_tools'] = []
                    # Đảm bảo settings có đầy đủ các field
                    if 'settings' not in loaded_config:
                        loaded_config['settings'] = default_config['settings']
                    else:
                        # Thêm các field settings mới nếu thiếu
                        for key, value in default_config['settings'].items():
                            if key not in loaded_config['settings']:
                                loaded_config['settings'][key] = value
                    
                    # Đảm bảo statistics có trong config
                    if 'statistics' not in loaded_config:
                        loaded_config['statistics'] = default_config['statistics']
                    else:
                        # Đảm bảo các field statistics có đầy đủ
                        if 'tool_usage' not in loaded_config['statistics']:
                            loaded_config['statistics']['tool_usage'] = {}
                        if 'last_used' not in loaded_config['statistics']:
                            loaded_config['statistics']['last_used'] = {}
                    
                    return loaded_config
            except Exception:
                pass
        
        # Config mặc định
        return default_config
    
    def _save_config(self):
        """Lưu config ra file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            # Invalidate cache khi config thay đổi
            self._cached_tool_list = None
            self._cache_timestamp = None
        except Exception as e:
            print(f"⚠️  Lỗi lưu config: {e}")
    
    def _get_tool_metadata_file(self, tool: str) -> Path:
        """
        Tìm file tool_info.json cho tool
        
        Args:
            tool: Tên file tool (vd: backup-folder.py)
        
        Returns:
            Path: Đường dẫn đến tool_info.json hoặc None
        """
        tool_name = tool.replace('.py', '')
        
        # Thử tìm trong tools/py/
        py_tool_dir = self.tool_dir / "py" / tool_name
        py_metadata = py_tool_dir / "tool_info.json"
        if py_metadata.exists():
            return py_metadata
        
        # Thử tìm trong tools/sh/
        sh_tool_dir = self.tool_dir / "sh" / tool_name
        sh_metadata = sh_tool_dir / "tool_info.json"
        if sh_metadata.exists():
            return sh_metadata
        
        # Thử cấu trúc cũ
        old_tool_dir = self.tool_dir / tool_name
        old_metadata = old_tool_dir / "tool_info.json"
        if old_metadata.exists():
            return old_metadata
        
        return None
    
    def _load_tool_metadata(self, tool: str) -> Dict:
        """
        Load metadata cho tool từ tool_info.json hoặc tự động generate
        
        Args:
            tool: Tên file tool (vd: backup-folder.py)
        
        Returns:
            dict: Metadata gồm 'name' và 'tags'
        """
        # Kiểm tra cache trước
        if tool in self.tool_names:
            return {
                'name': self.tool_names[tool],
                'tags': self.tool_tags.get(tool, [])
            }
        
        # Thử đọc từ tool_info.json
        metadata_file = self._get_tool_metadata_file(tool)
        if metadata_file and metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                    # Lưu vào cache
                    self.tool_names[tool] = metadata.get('name', self._generate_display_name(tool))
                    self.tool_tags[tool] = metadata.get('tags', [])
                    
                    return {
                        'name': self.tool_names[tool],
                        'tags': self.tool_tags[tool]
                    }
            except Exception:
                pass  # Nếu đọc lỗi, fallback sang generate tự động
        
        # Tự động generate metadata từ tên file
        display_name = self._generate_display_name(tool)
        tags = self._generate_tags(tool)
        
        # Lưu vào cache
        self.tool_names[tool] = display_name
        self.tool_tags[tool] = tags
        
        return {
            'name': display_name,
            'tags': tags
        }
    
    def _generate_display_name(self, tool: str) -> str:
        """
        Tự động generate tên hiển thị từ tên file tool
        
        Args:
            tool: Tên file tool (vd: backup-folder.py)
        
        Returns:
            str: Tên hiển thị tiếng Việt
        """
        tool_name = tool.replace('.py', '')
        
        # Dictionary ánh xạ từ khóa -> tiếng Việt
        keyword_map = {
            'backup': 'Sao lưu',
            'folder': 'thư mục',
            'clean': 'Dọn dẹp',
            'temp': 'file tạm',
            'compress': 'Nén',
            'image': 'ảnh',
            'copy': 'Sao chép',
            'changed': 'thay đổi',
            'duplicate': 'trùng lặp',
            'finder': 'Tìm',
            'extract': 'Giải nén',
            'archive': 'file nén',
            'file': 'file',
            'organizer': 'Sắp xếp',
            'find': 'Tìm',
            'replace': 'thay thế',
            'generate': 'Tạo',
            'tree': 'cây thư mục',
            'watermark': 'watermark',
            'pdf': 'PDF',
            'rename': 'Đổi tên',
            'setup': 'Cài đặt',
            'project': 'dự án',
            'linux': 'Linux',
            'text': 'text',
            'encoding': 'encoding',
            'converter': 'chuyển đổi',
            'video': 'video',
            'ssh': 'SSH',
            'manager': 'Quản lý',
            'server': 'Server'
        }
        
        # Convert kebab-case sang từng từ và translate
        words = tool_name.split('-')
        translated_words = []
        
        for word in words:
            if word in keyword_map:
                translated_words.append(keyword_map[word])
            else:
                # Nếu không tìm thấy, giữ nguyên nhưng capitalize
                translated_words.append(word.capitalize())
        
        # Ghép lại thành tên hiển thị
        display_name = ' '.join(translated_words)
        
        # Thêm mô tả ngắn nếu cần (tùy chọn)
        return display_name
    
    def _generate_tags(self, tool: str) -> List[str]:
        """
        Tự động generate tags từ tên file tool
        
        Args:
            tool: Tên file tool (vd: backup-folder.py)
        
        Returns:
            list: Danh sách tags
        """
        tool_name = tool.replace('.py', '').lower()
        
        # Extract tags từ tên file (các từ trong kebab-case)
        tags = tool_name.split('-')
        
        # Thêm tên file đầy đủ làm tag
        tags.append(tool_name)
        
        # Thêm tags phổ biến dựa trên keywords
        if 'image' in tool_name or 'photo' in tool_name:
            tags.extend(['anh', 'hinh', 'picture'])
        elif 'video' in tool_name:
            tags.extend(['video', 'phim'])
        elif 'pdf' in tool_name:
            tags.extend(['pdf', 'document'])
        elif 'backup' in tool_name:
            tags.extend(['backup', 'sao luu'])
        elif 'compress' in tool_name or 'zip' in tool_name:
            tags.extend(['compress', 'nen'])
        elif 'ssh' in tool_name:
            tags.extend(['ssh', 'remote', 'server'])
        
        return list(set(tags))  # Remove duplicates
    
    def _get_tool_type(self, tool: str) -> str:
        """
        Xác định loại tool: 'py' hoặc 'sh'
        
        Args:
            tool: Tên file tool (vd: backup-folder.py)
        
        Returns:
            str: 'py' nếu là Python tool, 'sh' nếu là Shell tool
        """
        if tool in self.tool_types:
            return self.tool_types[tool]
        
        tool_name = tool.replace('.py', '')
        
        # Kiểm tra trong tools/py/
        py_tool_path = self.tool_dir / "py" / tool_name / tool
        if py_tool_path.exists():
            self.tool_types[tool] = 'py'
            return 'py'
        
        # Kiểm tra trong tools/sh/
        sh_tool_path = self.tool_dir / "sh" / tool_name / tool
        if sh_tool_path.exists():
            self.tool_types[tool] = 'sh'
            return 'sh'
        
        # Mặc định là py nếu không tìm thấy (tương thích với cấu trúc cũ)
        self.tool_types[tool] = 'py'
        return 'py'
    
    def get_tool_display_name(self, tool: str) -> str:
        """
        Lấy tên hiển thị của tool (tự động load metadata nếu chưa có)
        
        Args:
            tool: Tên file tool (vd: backup-folder.py)
        
        Returns:
            str: Tên hiển thị tiếng Việt với ký hiệu phân biệt py/sh
        """
        if tool not in self.tool_names:
            self._load_tool_metadata(tool)
        
        display_name = self.tool_names.get(tool, tool)
        tool_type = self._get_tool_type(tool)
        
        # Thêm ký hiệu phân biệt
        if tool_type == 'py':
            return f"[PY] {display_name}"  # Python tool
        elif tool_type == 'sh':
            return f"[SH] {display_name}"  # Shell tool
        else:
            return display_name
    
    def get_tool_tags(self, tool: str) -> List[str]:
        """
        Lấy tags của tool (tự động load metadata nếu chưa có)
        
        Args:
            tool: Tên file tool (vd: backup-folder.py)
        
        Returns:
            list: Danh sách tags
        """
        if tool not in self.tool_tags:
            self._load_tool_metadata(tool)
        return self.tool_tags.get(tool, [])
    
    def _scan_tools_from_directory(self) -> List[str]:
        """
        Scan tất cả tools từ thư mục tools (private method)
        
        Returns:
            list: Danh sách tên file tool (chưa sắp xếp, chưa filter disabled)
        
        Giải thích:
        - Tách logic scan ra khỏi get_tool_list để tái sử dụng
        - Xử lý cả cấu trúc mới (py/sh) và cấu trúc cũ
        - Bắt PermissionError khi quét thư mục
        """
        if not self.tool_dir.exists():
            return []
        
        all_tools = []
        
        # Tìm tools trong tools/py/ (các tool Python thông thường)
        py_dir = self.tool_dir / "py"
        if py_dir.exists() and py_dir.is_dir():
            try:
                for item in os.listdir(py_dir):
                    item_path = py_dir / item
                    if item_path.is_dir():
                        # Tìm file có tên giống thư mục
                        main_file = item_path / f"{item}.py"
                        if main_file.exists():
                            all_tools.append(f"{item}.py")
            except (PermissionError, OSError):
                # Bỏ qua thư mục không có quyền truy cập
                pass
        
        # Tìm tools trong tools/sh/ (các tool đặc biệt như shell scripts)
        sh_dir = self.tool_dir / "sh"
        if sh_dir.exists() and sh_dir.is_dir():
            try:
                for item in os.listdir(sh_dir):
                    item_path = sh_dir / item
                    if item_path.is_dir():
                        # Tìm file .py trong thư mục con
                        main_file = item_path / f"{item}.py"
                        if main_file.exists():
                            all_tools.append(f"{item}.py")
            except (PermissionError, OSError):
                # Bỏ qua thư mục không có quyền truy cập
                pass
        
        # Tương thích với cấu trúc cũ: tìm trực tiếp trong tools/ (nếu còn)
        try:
            for item in os.listdir(self.tool_dir):
                item_path = self.tool_dir / item
                # Bỏ qua thư mục py và sh (đã xử lý ở trên)
                if item in ['py', 'sh']:
                    continue
                # Nếu là thư mục, tìm file .py chính trong đó
                if item_path.is_dir():
                    main_file = item_path / f"{item}.py"
                    if main_file.exists():
                        all_tools.append(f"{item}.py")
                # Nếu là file .py (để tương thích với cấu trúc cũ)
                elif item.endswith('.py'):
                    all_tools.append(item)
        except (PermissionError, OSError):
            # Bỏ qua nếu không có quyền truy cập
            pass
        
        return all_tools
    
    def _sort_and_prioritize_tools(self, tools: List[str]) -> List[str]:
        """
        Sắp xếp tools: priority tools trước, sau đó alphabet
        
        Args:
            tools: Danh sách tools chưa sắp xếp
        
        Returns:
            list: Danh sách tools đã sắp xếp
        """
        # Tách priority tools và tools thường
        priority = []
        regular = []
        
        for tool in tools:
            if tool in self.priority_tools:
                priority.append(tool)
            else:
                regular.append(tool)
        
        # Sắp xếp priority tools theo thứ tự định sẵn
        priority.sort(key=lambda x: self.priority_tools.index(x))
        
        # Sắp xếp tools thường theo alphabet
        regular.sort()
        
        # Ghép lại: priority + regular
        return priority + regular
    
    def get_tool_list(self, force_refresh: bool = False) -> List[str]:
        """
        Lấy danh sách file .py trong thư mục tool (với caching)
        
        Args:
            force_refresh: Bỏ qua cache và scan lại (mặc định: False)
        
        Returns:
            list: Danh sách tên file tool (priority tools trước, sau đó alphabet, đã filter disabled)
        
        Giải thích:
        - Sử dụng cache để tránh scan lại nhiều lần
        - Cache tự động expire sau TTL (60 giây)
        - Có thể force refresh nếu cần
        
        Lý do tìm trong thư mục con:
        - Hỗ trợ cấu trúc mới: mỗi tool có thư mục riêng
        - Ví dụ: tools/py/backup-folder/backup-folder.py
        - Ví dụ: tools/sh/setup-project-linux/setup-project-linux.py
        """
        import time
        
        # Kiểm tra cache
        if not force_refresh and self._cached_tool_list is not None and self._cache_timestamp is not None:
            elapsed = time.time() - self._cache_timestamp
            if elapsed < self._cache_ttl:
                # Cache còn hiệu lực, trả về cache
                return self._cached_tool_list
        
        # Scan tools từ thư mục
        all_tools = self._scan_tools_from_directory()
        
        # Loại bỏ duplicate (giữ thứ tự đầu tiên)
        seen = set()
        unique_tools = []
        for tool in all_tools:
            if tool not in seen:
                seen.add(tool)
                unique_tools.append(tool)
        
        # Sắp xếp và ưu tiên
        sorted_tools = self._sort_and_prioritize_tools(unique_tools)
        
        # Filter ra các tool bị disabled
        disabled_tools = set(self.config.get('disabled_tools', []))
        active_tools = [t for t in sorted_tools if t not in disabled_tools]
        
        # Lưu vào cache
        self._cached_tool_list = active_tools
        self._cache_timestamp = time.time()
        
        return active_tools
    
    def get_all_tools_including_disabled(self) -> List[str]:
        """
        Lấy danh sách tất cả tools (bao gồm cả disabled)
        
        Returns:
            list: Danh sách tất cả tools (đã sắp xếp, bao gồm cả disabled)
        """
        # Scan tools từ thư mục
        all_tools = self._scan_tools_from_directory()
        
        # Loại bỏ duplicate (giữ thứ tự đầu tiên)
        seen = set()
        unique_tools = []
        for tool in all_tools:
            if tool not in seen:
                seen.add(tool)
                unique_tools.append(tool)
        
        # Sắp xếp và ưu tiên (bao gồm cả disabled)
        return self._sort_and_prioritize_tools(unique_tools)
    
    def search_tools(self, query: str, use_fuzzy: bool = True) -> List[str]:
        """
        Tìm kiếm tool theo keyword với fuzzy matching
        
        Args:
            query: Từ khóa tìm kiếm
            use_fuzzy: Sử dụng fuzzy matching (mặc định: True)
        
        Returns:
            list: Danh sách tool phù hợp (sắp xếp theo độ liên quan)
        
        Giải thích:
        - Tìm trong tên file (exact match có điểm cao nhất)
        - Tìm trong description (exact match)
        - Tìm trong tags (exact match)
        - Sử dụng fuzzy matching để tìm gần đúng
        - Sắp xếp kết quả theo độ liên quan
        """
        from difflib import SequenceMatcher
        
        query_lower = query.lower()
        results_with_score = []
        
        for tool in self.get_tool_list():
            score = 0.0
            matched = False
            
            # Tìm trong tên file (exact match = điểm cao nhất)
            tool_lower = tool.lower()
            if query_lower in tool_lower:
                if tool_lower == query_lower:
                    score = 1.0  # Exact match
                elif tool_lower.startswith(query_lower):
                    score = 0.9  # Starts with
                else:
                    score = 0.7  # Contains
                matched = True
            
            # Tìm trong description
            description = self.get_tool_display_name(tool)
            description_lower = description.lower()
            if query_lower in description_lower:
                if description_lower.startswith(query_lower):
                    score = max(score, 0.8)
                else:
                    score = max(score, 0.6)
                matched = True
            
            # Tìm trong tags
            tags = self.get_tool_tags(tool)
            for tag in tags:
                tag_lower = tag.lower()
                if query_lower in tag_lower:
                    score = max(score, 0.5)
                    matched = True
                    break
            
            # Fuzzy matching nếu chưa tìm thấy exact match
            if use_fuzzy and not matched:
                # So sánh với tên file
                file_ratio = SequenceMatcher(None, query_lower, tool_lower).ratio()
                if file_ratio > 0.5:  # Ngưỡng 50%
                    score = file_ratio * 0.4  # Fuzzy match có điểm thấp hơn
                    matched = True
                
                # So sánh với description
                desc_ratio = SequenceMatcher(None, query_lower, description_lower).ratio()
                if desc_ratio > 0.5:
                    score = max(score, desc_ratio * 0.3)
                    matched = True
            
            if matched:
                results_with_score.append((tool, score))
        
        # Sắp xếp theo điểm số (cao -> thấp)
        results_with_score.sort(key=lambda x: x[1], reverse=True)
        
        # Trả về danh sách tools (không có điểm số)
        return [tool for tool, score in results_with_score]
    
    def add_to_favorites(self, tool: str):
        """Thêm tool vào favorites"""
        if tool not in self.config['favorites']:
            self.config['favorites'].append(tool)
            self._save_config()
            tool_name = self.get_tool_display_name(tool)
            print(Colors.success(f"⭐ Đã thêm vào favorites: {Colors.bold(tool_name)}"))
        else:
            tool_name = self.get_tool_display_name(tool)
            print(Colors.warning(f"ℹ️  Tool đã có trong favorites: {tool_name}"))
    
    def remove_from_favorites(self, tool: str):
        """Xóa tool khỏi favorites"""
        if tool in self.config['favorites']:
            self.config['favorites'].remove(tool)
            self._save_config()
            tool_name = self.get_tool_display_name(tool)
            print(Colors.info(f"❌ Đã xóa khỏi favorites: {tool_name}"))
        else:
            tool_name = self.get_tool_display_name(tool)
            print(Colors.warning(f"ℹ️  Tool không có trong favorites: {tool_name}"))
    
    def activate_tool(self, tool: str):
        """Kích hoạt tool (xóa khỏi danh sách disabled)"""
        if tool in self.config['disabled_tools']:
            self.config['disabled_tools'].remove(tool)
            self._save_config()
            tool_name = self.get_tool_display_name(tool)
            print(Colors.success(f"✅ Đã kích hoạt tool: {Colors.bold(tool_name)}"))
        else:
            tool_name = self.get_tool_display_name(tool)
            print(Colors.warning(f"ℹ️  Tool đã được kích hoạt: {tool_name}"))
    
    def deactivate_tool(self, tool: str):
        """Vô hiệu hóa tool (thêm vào danh sách disabled)"""
        if tool not in self.config['disabled_tools']:
            self.config['disabled_tools'].append(tool)
            self._save_config()
            tool_name = self.get_tool_display_name(tool)
            print(Colors.warning(f"⚠️  Đã vô hiệu hóa tool: {Colors.bold(tool_name)}"))
        else:
            tool_name = self.get_tool_display_name(tool)
            print(Colors.warning(f"ℹ️  Tool đã bị vô hiệu hóa: {tool_name}"))
    
    def is_tool_active(self, tool: str) -> bool:
        """Kiểm tra tool có đang active không"""
        return tool not in self.config.get('disabled_tools', [])
    
    def add_to_recent(self, tool: str):
        """
        Thêm tool vào recent và cập nhật statistics
        
        Args:
            tool: Tên file tool
        
        Giải thích:
        - Xóa tool nếu đã có trong list (để move lên đầu)
        - Thêm vào đầu list
        - Giới hạn số lượng recent
        - Tự động dọn dẹp tools đã bị xóa (chỉ giữ tools còn tồn tại)
        - Cập nhật usage statistics
        """
        if tool in self.config['recent']:
            self.config['recent'].remove(tool)
        
        self.config['recent'].insert(0, tool)
        
        # Dọn dẹp: Loại bỏ tools không còn tồn tại
        all_tools = self._scan_tools_from_directory()
        all_tools_set = set(all_tools)
        self.config['recent'] = [t for t in self.config['recent'] if t in all_tools_set]
        
        # Giới hạn số recent
        max_recent = self.config['settings'].get('max_recent', 10)
        self.config['recent'] = self.config['recent'][:max_recent]
        
        # Cập nhật usage statistics
        if 'statistics' not in self.config:
            self.config['statistics'] = {}
        if 'tool_usage' not in self.config['statistics']:
            self.config['statistics']['tool_usage'] = {}
        
        # Tăng usage count
        if tool not in self.config['statistics']['tool_usage']:
            self.config['statistics']['tool_usage'][tool] = 0
        self.config['statistics']['tool_usage'][tool] += 1
        
        # Cập nhật last used timestamp
        import time
        if 'last_used' not in self.config['statistics']:
            self.config['statistics']['last_used'] = {}
        self.config['statistics']['last_used'][tool] = time.time()
        
        self._save_config()
    
    def run_tool(self, tool: str) -> int:
        """
        Chạy tool
        
        Args:
            tool: Tên file tool
        
        Returns:
            int: Exit code
        
        Giải thích:
        - Tìm và chạy tool từ thư mục tool/ hoặc thư mục con
        - Lưu vào recent
        - Hiển thị thông báo
        
        Lý do xử lý cả 2 cấu trúc:
        - Cấu trúc cũ: tool/backup-folder.py
        - Cấu trúc mới: tool/backup-folder/backup-folder.py
        
        Đặc biệt: setup-project-linux.py chạy trực tiếp bash app.sh
        """
        # Tool đặc biệt: setup-project-linux - chạy trực tiếp bash app.sh
        if tool == "setup-project-linux.py":
            return self._run_setup_project_linux()
        
        # Tìm đường dẫn thực tế của tool
        tool_path = self._find_tool_path(tool)
        
        if not tool_path or not tool_path.exists():
            error_msg = FileNotFoundError(f"Tool not found: {tool}")
            log_file = log_error_to_file(
                error=error_msg,
                tool_name=tool,
                context="Tool file not found"
            )
            if log_file:
                print()
                print(Colors.warning(f"📝 Lỗi đã được ghi vào file: {log_file}"))
            
            print(Colors.error(f"❌ Tool không tồn tại: {tool}"))
            return 1
        
        tool_display_name = self.get_tool_display_name(tool)
        print()
        print_separator("═", 70, Colors.PRIMARY)
        
        # Hiển thị loading indicator với spinner
        from utils.progress import Spinner
        spinner = Spinner(f"Đang khởi động: {tool_display_name}")
        spinner.start()
        
        # Dừng spinner sau một chút để hiển thị loading
        import time
        time.sleep(0.3)  # Hiển thị spinner trong 0.3 giây
        spinner.stop()
        
        print(Colors.primary(f"  ▶ Đang chạy: {Colors.bold(tool_display_name)}"))
        print(Colors.muted(f"  📁 Đường dẫn: {tool_path}"))
        print_separator("═", 70, Colors.PRIMARY)
        print()
        
        try:
            # Chạy tool bình thường để người dùng thấy output trực tiếp
            result = subprocess.run(["python", str(tool_path)])
            
            # Nếu tool chạy thành công (exit code 0), không cần log
            # Nếu tool chạy thất bại (exit code != 0), log lỗi
            if result.returncode != 0:
                # Log lỗi vào file
                error_msg = Exception(f"Tool exited with code {result.returncode}")
                log_file = log_error_to_file(
                    error=error_msg,
                    tool_name=tool_display_name,
                    context=f"Tool execution failed with exit code {result.returncode}. Check console output above for details."
                )
                if log_file:
                    print()
                    print(Colors.warning(f"📝 Lỗi đã được ghi vào file: {log_file}"))
            
            print()
            print_separator("═", 70, Colors.SUCCESS if result.returncode == 0 else Colors.ERROR)
            
            if result.returncode == 0:
                print(Colors.success(f"  ✅ Tool đã chạy xong thành công!"))
                print(Colors.muted(f"  📊 Exit code: {Colors.info('0')} (Success)"))
            else:
                print(Colors.error(f"  ❌ Tool đã kết thúc với lỗi"))
                print(Colors.error(f"  📊 Exit code: {Colors.bold(str(result.returncode))}"))
                print(Colors.muted(f"  💡 Kiểm tra output phía trên để xem chi tiết lỗi"))
            
            print_separator("═", 70, Colors.SUCCESS if result.returncode == 0 else Colors.ERROR)
            print()
            
            # Lưu vào recent
            self.add_to_recent(tool)
            
            return result.returncode
            
        except KeyboardInterrupt:
            print()
            print(Colors.warning("⚠️  Tool bị ngắt bởi người dùng"))
            return 130
            
        except Exception as e:
            # Log lỗi vào file
            log_file = log_error_to_file(
                error=e,
                tool_name=tool_display_name,
                context="Exception occurred while running tool"
            )
            if log_file:
                print()
                print(Colors.warning(f"📝 Lỗi đã được ghi vào file: {log_file}"))
            
            print()
            print(Colors.error(f"❌ Lỗi khi chạy tool: {e}"))
            return 1
    
    def _run_setup_project_linux(self) -> int:
        """
        Chạy setup-project-linux trực tiếp bằng bash app.sh
        Tránh lỗi với editable install khi chạy qua Python
        """
        import shutil
        
        # Tìm đường dẫn app.sh
        script_dir = self.tool_dir / "sh" / "setup-project-linux"
        app_sh = script_dir / "app.sh"
        
        if not app_sh.exists():
            error_msg = FileNotFoundError(f"File app.sh not found at {app_sh}")
            log_file = log_error_to_file(
                error=error_msg,
                tool_name=self.get_tool_display_name('setup-project-linux.py'),
                context="setup-project-linux: File app.sh not found"
            )
            if log_file:
                print()
                print(Colors.warning(f"📝 Lỗi đã được ghi vào file: {log_file}"))
            
            print(f"❌ Không tìm thấy file app.sh!")
            print(f"   Đường dẫn: {app_sh}")
            return 1
        
        tool_display_name = self.get_tool_display_name('setup-project-linux.py')
        print()
        print_separator("═", 70, Colors.PRIMARY)
        
        # Hiển thị loading indicator
        from utils.progress import Spinner
        spinner = Spinner(f"Đang khởi động: {tool_display_name}")
        spinner.start()
        
        import time
        time.sleep(0.3)
        spinner.stop()
        
        print(Colors.primary(f"  ▶ Đang chạy: {Colors.bold(tool_display_name)}"))
        print(Colors.muted(f"  📁 Script: {app_sh}"))
        print_separator("═", 70, Colors.PRIMARY)
        print()
        
        try:
            # Tìm bash
            bash_cmd = None
            
            # Trên Windows, tìm Git Bash
            if sys.platform == 'win32':
                git_bash_paths = [
                    r"C:\Program Files\Git\bin\bash.exe",
                    r"C:\Program Files (x86)\Git\bin\bash.exe",
                    os.path.expanduser(r"~\AppData\Local\Programs\Git\bin\bash.exe")
                ]
                
                for bash_path in git_bash_paths:
                    if os.path.exists(bash_path):
                        bash_cmd = [bash_path]
                        break
                
                # Thử WSL nếu không có Git Bash
                if not bash_cmd:
                    wsl_path = shutil.which('wsl')
                    if wsl_path:
                        bash_cmd = ['wsl', 'bash']
                
                # Thử bash.exe trong PATH
                if not bash_cmd:
                    bash_exe = shutil.which('bash.exe')
                    if bash_exe:
                        bash_cmd = [bash_exe]
            else:
                # Linux/macOS
                bash_path = shutil.which('bash')
                if bash_path:
                    bash_cmd = [bash_path]
            
            if not bash_cmd:
                error_msg = FileNotFoundError("Bash not found. On Windows, need Git Bash or WSL")
                log_file = log_error_to_file(
                    error=error_msg,
                    tool_name=self.get_tool_display_name('setup-project-linux.py'),
                    context="setup-project-linux: Bash command not found"
                )
                if log_file:
                    print()
                    print(Colors.warning(f"📝 Lỗi đã được ghi vào file: {log_file}"))
                
                print("❌ Không tìm thấy bash!")
                print("   Trên Windows, cần cài Git Bash hoặc WSL")
                return 1
            
            # Chuyển đổi đường dẫn cho Git Bash trên Windows
            if sys.platform == 'win32' and 'Git' in str(bash_cmd[0]):
                # Chuyển D:\path\to\app.sh thành /d/path/to/app.sh
                script_path_str = str(app_sh.resolve())
                if ':' in script_path_str:
                    drive = script_path_str[0].lower()
                    unix_path = script_path_str.replace('\\', '/').replace(f'{drive}:', f'/{drive}', 1)
                else:
                    unix_path = script_path_str.replace('\\', '/')
                cmd = bash_cmd + [unix_path]
            else:
                cmd = bash_cmd + [str(app_sh)]
            
            # Chạy bash app.sh
            result = subprocess.run(cmd, check=False)
            
            print()
            print_separator("═", 70, Colors.SUCCESS if result.returncode == 0 else Colors.ERROR)
            
            if result.returncode == 0:
                print(Colors.success(f"  ✅ Tool đã chạy xong thành công!"))
                print(Colors.muted(f"  📊 Exit code: {Colors.info('0')} (Success)"))
            else:
                print(Colors.error(f"  ❌ Tool đã kết thúc với lỗi"))
                print(Colors.error(f"  📊 Exit code: {Colors.bold(str(result.returncode))}"))
                print(Colors.muted(f"  💡 Kiểm tra output phía trên để xem chi tiết lỗi"))
            
            print_separator("═", 70, Colors.SUCCESS if result.returncode == 0 else Colors.ERROR)
            print()
            
            # Lưu vào recent
            self.add_to_recent("setup-project-linux.py")
            
            return result.returncode
            
        except KeyboardInterrupt:
            print()
            print(Colors.warning("⚠️  Tool bị ngắt bởi người dùng"))
            return 130
            
        except Exception as e:
            # Log lỗi vào file
            log_file = log_error_to_file(
                error=e,
                tool_name=self.get_tool_display_name('setup-project-linux.py'),
                context="setup-project-linux: Exception occurred while running bash script"
            )
            if log_file:
                print()
                print(Colors.warning(f"📝 Lỗi đã được ghi vào file: {log_file}"))
            
            print()
            print(Colors.error(f"❌ Lỗi khi chạy tool: {e}"))
            return 1
    
    def _find_tool_path(self, tool: str) -> Optional[Path]:
        """
        Tìm đường dẫn thực tế của tool
        
        Args:
            tool: Tên file tool (vd: backup-folder.py)
        
        Returns:
            Path: Đường dẫn đầy đủ đến file tool, hoặc None nếu không tìm thấy
        
        Giải thích:
        - Bước 1: Thử tìm trong tools/py/ (các tool Python)
        - Bước 2: Thử tìm trong tools/sh/ (các tool đặc biệt)
        - Bước 3: Thử tìm trực tiếp trong tools/ (cấu trúc cũ)
        
        Lý do:
        - Hỗ trợ cấu trúc mới: tools/py/ và tools/sh/
        - Ưu tiên cấu trúc mới (tools/py/ và tools/sh/)
        - Vẫn tương thích với cấu trúc cũ
        """
        tool_name = tool.replace('.py', '')
        
        # Thử tìm trong tools/py/ (cấu trúc mới)
        py_tool_path = self.tool_dir / "py" / tool_name / tool
        if py_tool_path.exists():
            return py_tool_path
        
        # Thử tìm trong tools/sh/ (các tool đặc biệt)
        sh_tool_path = self.tool_dir / "sh" / tool_name / tool
        if sh_tool_path.exists():
            return sh_tool_path
        
        # Thử cấu trúc cũ: tool/backup-folder/backup-folder.py
        old_structure_path = self.tool_dir / tool_name / tool
        if old_structure_path.exists():
            return old_structure_path
        
        # Thử cấu trúc cũ: tool/backup-folder.py
        old_file_path = self.tool_dir / tool
        if old_file_path.exists():
            return old_file_path
        
        return None
    
    def display_menu(self, tools: Optional[List[str]] = None, title: str = "DANH SÁCH TOOL", group_by_category: bool = True, search_query: Optional[str] = None):
        """
        Hiển thị menu tools với UI/UX đẹp hơn
        
        Args:
            tools: Danh sách tools (None = hiển thị tất cả)
            title: Tiêu đề menu
            group_by_category: Có nhóm theo categories không
        
        Giải thích:
        - Hiển thị danh sách đẹp với số thứ tự
        - Highlight favorites với màu sắc
        - Nhóm tools theo categories nếu có
        - Sử dụng màu sắc và icons đẹp hơn
        - Hiển thị stats nhanh
        """
        if tools is None:
            tools = self.get_tool_list()
        
        if not tools:
            print(Colors.error("❌ Không tìm thấy tool nào!"))
            return
        
        # Helper function để tính display width (bao gồm emoji)
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
        
        # Tính dòng dài nhất nếu có group_by_category để xác định width
        max_line_width = 0
        if group_by_category and len(tools) > 5:
            for tool in tools:
                tool_name = self.get_tool_display_name(tool)
                is_favorite = tool in self.config['favorites']
                star_plain = "⭐" if is_favorite else "  "
                # Giả sử index là 2 chữ số (max 99)
                idx_str = "99."
                line_plain = f"{star_plain} {idx_str} {tool_name}"
                line_display_width = get_display_width(line_plain)
                if line_display_width > max_line_width:
                    max_line_width = line_display_width
        
        # Category box width = max_line_width + padding (│  + line + │)
        # Format: "│  " (3) + line + padding + " │" (1) = category_box_width
        # Vậy: category_box_width >= 3 + max_line_width + 1 = max_line_width + 4
        # Xác định content_width dựa trên dòng dài nhất
        required_content_width = max_line_width + 4 if max_line_width > 0 else 68
        initial_content_width = 68  # Width mặc định
        
        # Dùng width lớn hơn giữa required và initial
        content_width = max(required_content_width, initial_content_width)
        box_width = content_width + 2  # Content area + 2 borders
        
        # Header với box design
        print()
        print("  " + Colors.primary("╔" + "═" * content_width + "╗"))
        title_plain = title  # Plain text để tính độ dài
        title_padding = (content_width - len(title_plain)) // 2
        title_padding_right = content_width - len(title_plain) - title_padding
        title_line = "  " + Colors.primary("║") + " " * title_padding + Colors.bold(Colors.info(title)) + " " * title_padding_right + Colors.primary("║")
        print(title_line)
        print("  " + Colors.primary("╠" + "═" * content_width + "╣"))
        
        # Stats nhanh với icon đẹp
        total = len(tools)
        all_tools_count = len(self.get_all_tools_including_disabled())
        disabled_count = all_tools_count - total
        favorites_count = len([t for t in tools if t in self.config['favorites']])
        recent_count = len([t for t in self.config['recent'] if t in tools])
        
        # Tính tổng số lần sử dụng từ statistics
        total_usage = sum(self.config.get('statistics', {}).get('tool_usage', {}).values())
        
        # Build stats text
        stats_text_parts = []
        if disabled_count > 0:
            stats_text_parts.extend([f"📊 Active: {total}", f"🔒 Disabled: {disabled_count}", f"⭐ Favorites: {favorites_count}", f"📚 Recent: {recent_count}"])
        else:
            stats_text_parts.extend([f"📊 Active: {total}", f"⭐ Favorites: {favorites_count}", f"📚 Recent: {recent_count}"])
        
        if total_usage > 0:
            stats_text_parts.append(f"📈 Usage: {total_usage}")
        
        stats_text = " | ".join(stats_text_parts)
        stats_display_width = get_display_width(stats_text)
        
        # Build colored stats
        stats_parts = [
            Colors.info(f"📊 Active: {Colors.bold(str(total))}"),
        ]
        if disabled_count > 0:
            stats_parts.append(Colors.error(f"🔒 Disabled: {Colors.bold(str(disabled_count))}"))
        stats_parts.append(Colors.warning(f"⭐ Favorites: {Colors.bold(str(favorites_count))}"))
        stats_parts.append(Colors.secondary(f"📚 Recent: {Colors.bold(str(recent_count))}"))
        if total_usage > 0:
            stats_parts.append(Colors.primary(f"📈 Usage: {Colors.bold(str(total_usage))}"))
        
        stats_colored = " | ".join(stats_parts)
        # Tính padding: 1 space + stats + padding = content_width
        padding = content_width - 1 - stats_display_width
        if padding < 0:
            padding = 0
        stats_line = "  " + Colors.primary("║") + " " + stats_colored + " " * padding + Colors.primary("║")
        print(stats_line)
        print("  " + Colors.primary("╠" + "═" * content_width + "╣"))
        print()
        
        # Tạo danh sách tools theo đúng thứ tự hiển thị
        displayed_tools_order = []
        
        # Nhóm theo categories hoặc hiển thị flat list
        if group_by_category and len(tools) > 5:
            grouped = group_tools_by_category(tools, self)
            current_idx = 1
            
            category_box_width = content_width
            
            for category, category_tools in grouped.items():
                cat_info = get_category_info(category)
                icon = cat_info['icon']
                cat_name = cat_info['name']
                
                # Category header với box style - đồng nhất width
                print()
                cat_title = f"{icon} {cat_name} ({len(category_tools)})"
                cat_title_plain = cat_title  # Plain text để tính độ dài
                cat_title_display_width = get_display_width(cat_title_plain)
                cat_title_padding = category_box_width - cat_title_display_width - 3
                if cat_title_padding < 0:
                    cat_title_padding = 0
                print("  " + Colors.secondary("┌─ ") + Colors.bold(Colors.info(cat_title)) + Colors.secondary(" " + "─" * cat_title_padding + "┐"))
                
                # Tools trong category
                for tool in category_tools:
                    # Lưu tool vào danh sách theo đúng thứ tự hiển thị
                    displayed_tools_order.append(tool)
                    is_favorite = tool in self.config['favorites']
                    tool_name = self.get_tool_display_name(tool)
                    idx_str = f"{current_idx:2d}."
                    
                    if is_favorite:
                        star = Colors.warning("⭐")
                        star_plain = "⭐"
                        idx_colored = Colors.info(idx_str)
                    else:
                        star = "  "
                        star_plain = "  "
                        idx_colored = Colors.muted(idx_str)
                    
                    # Highlight search query nếu có
                    if search_query:
                        tool_name_colored = highlight_keyword(tool_name, search_query)
                        tool_name_plain = tool_name  # Approximate, vì highlight có thể thay đổi
                    else:
                        tool_name_colored = Colors.bold(tool_name) if is_favorite else Colors.muted(tool_name)
                        tool_name_plain = tool_name
                    
                    line_plain = f"{star_plain} {idx_str} {tool_name_plain}"
                    line_display_width = get_display_width(line_plain)
                    padding_right = category_box_width - line_display_width - 3
                    if padding_right < 0:
                        padding_right = 0
                    
                    print(f"  {Colors.secondary('│')}  {star} {idx_colored} {tool_name_colored}" + " " * padding_right + f" {Colors.secondary('│')}")
                    current_idx += 1
                
                print("  " + Colors.secondary("└" + "─" * category_box_width + "┘"))
        else:
            # Hiển thị flat list (không nhóm) với border
            displayed_tools_order = tools.copy()  # Flat list giữ nguyên thứ tự
            print()
            for idx, tool in enumerate(tools, start=1):
                is_favorite = tool in self.config['favorites']
                tool_name = self.get_tool_display_name(tool)
                idx_str = f"{idx:2d}."
                
                if is_favorite:
                    star = Colors.warning("⭐")
                    idx_colored = Colors.info(idx_str)
                else:
                    star = "  "
                    idx_colored = Colors.muted(idx_str)
                
                # Highlight search query nếu có
                if search_query:
                    tool_name_colored = highlight_keyword(tool_name, search_query)
                else:
                    tool_name_colored = Colors.bold(tool_name) if is_favorite else Colors.muted(tool_name)
                
                # Padding để align với border
                padding = " " * 2
                print(f"  {padding}{star} {idx_colored} {tool_name_colored}")
        
        # Footer
        print()
        print("  " + Colors.primary("╚" + "═" * content_width + "╝"))
        print()
        
        # Lưu danh sách tools theo đúng thứ tự hiển thị để dùng khi chọn số
        self.displayed_tools_order = displayed_tools_order
    
    def show_help(self, show_examples: bool = True):
        """
        Hiển thị help với UI/UX đẹp hơn
        
        Args:
            show_examples: Có hiển thị ví dụ sử dụng không
        """
        # Độ rộng content area = độ dài của dòng dài nhất (note4 = 71 ký tự)
        content_width = 71
        
        def get_display_width(text: str) -> int:
            """
            Tính độ dài hiển thị thực tế của text (bao gồm cả emoji)
            Emoji chiếm 2 cột terminal, ký tự thường chiếm 1 cột
            """
            import unicodedata
            # Loại bỏ ANSI codes trước
            plain_text = strip_ansi(text)
            width = 0
            for char in plain_text:
                # Kiểm tra nếu là emoji hoặc ký tự wide (chiếm 2 cột)
                # Các emoji thường có category So (Symbol, other) hoặc Sk (Symbol, modifier)
                # Hoặc có East Asian Width = Wide hoặc Fullwidth
                try:
                    eaw = unicodedata.east_asian_width(char)
                    if eaw in ('W', 'F'):  # Wide hoặc Fullwidth
                        width += 2
                    else:
                        width += 1
                except:
                    # Fallback: nếu không xác định được, coi như 1 cột
                    width += 1
            return width
        
        def print_box_line(content_colored, content_plain, left_spaces=3):
            """Helper function để in một dòng trong box với padding chính xác"""
            # Tính độ dài thực tế của content (không có ANSI codes)
            actual_len = len(content_plain)
            # Tính padding cần thiết để tổng độ dài = content_width
            # Format: left_spaces + content + padding = content_width
            padding = content_width - left_spaces - actual_len
            if padding < 0:
                # Nếu content quá dài, không thêm padding (nhưng sẽ tràn)
                padding = 0
            print("  " + Colors.primary("║") + " " * left_spaces + content_colored + " " * padding + Colors.primary("║"))
        
        def print_box_title(title_colored, title_plain):
            """Helper function để in tiêu đề section"""
            # Tính display width thực tế (bao gồm emoji chiếm 2 cột)
            display_width = get_display_width(title_plain)
            # Format: 1 space + title + padding = content_width
            padding = content_width - 1 - display_width
            if padding < 0:
                padding = 0
            print("  " + Colors.primary("║") + " " + title_colored + " " * padding + Colors.primary("║"))
        
        def print_box_empty():
            """Helper function để in dòng trống"""
            print("  " + Colors.primary("║") + " " * content_width + Colors.primary("║"))
        
        print("  " + Colors.primary("╔" + "═" * content_width + "╗"))
        title = "HƯỚNG DẪN SỬ DỤNG"
        title_padding = (content_width - len(title) - 2) // 2
        title_line = "  " + Colors.primary("║") + " " * title_padding + Colors.bold(Colors.info(title)) + " " * (content_width - len(title) - title_padding) + Colors.primary("║")
        print(title_line)
        print("  " + Colors.primary("╠" + "═" * content_width + "╣"))
        
        # Lệnh cơ bản
        basic_title = "📋 LỆNH CƠ BẢN:"
        print_box_title(Colors.bold(Colors.warning(basic_title)), basic_title)
        
        cmd_basic1 = f"{Colors.info('[số]')}         - Chạy tool theo số thứ tự"
        print_box_line(cmd_basic1, "[số]         - Chạy tool theo số thứ tự")
        
        cmd_basic2 = f"{Colors.info('[số]h')}        - Xem hướng dẫn của tool (ví dụ: 1h, 4h)"
        print_box_line(cmd_basic2, "[số]h        - Xem hướng dẫn của tool (ví dụ: 1h, 4h)")
        
        cmd_basic3 = f"{Colors.info('h, help')}      - Hiển thị hướng dẫn này"
        print_box_line(cmd_basic3, "h, help      - Hiển thị hướng dẫn này")
        
        cmd_basic4 = f"{Colors.info('v')}            - Kiểm tra version hiện tại"
        print_box_line(cmd_basic4, "v            - Kiểm tra version hiện tại")
        
        cmd_basic5 = f"{Colors.info('u')}            - Cập nhật version mới"
        print_box_line(cmd_basic5, "u            - Cập nhật version mới")
        
        cmd_basic6 = f"{Colors.info('q, quit, 0')}   - Thoát chương trình"
        print_box_line(cmd_basic6, "q, quit, 0   - Thoát chương trình")
        
        print_box_empty()
        
        # Tìm kiếm
        search_title = "🔍 TÌM KIẾM:"
        print_box_title(Colors.bold(Colors.warning(search_title)), search_title)
        
        cmd1 = f"{Colors.info('s [keyword]')}  - Tìm kiếm tool"
        print_box_line(cmd1, "s [keyword]  - Tìm kiếm tool")
        
        cmd2 = f"{Colors.info('/[keyword]')}   - Tìm kiếm tool (cách khác)"
        print_box_line(cmd2, "/[keyword]   - Tìm kiếm tool (cách khác)")
        
        print_box_empty()
        
        example1 = f"{Colors.muted('Ví dụ:')} {Colors.secondary('s backup')}, {Colors.secondary('/image')}"
        print_box_line(example1, "Ví dụ: s backup, /image")
        
        print_box_empty()
        
        # Favorites
        fav_title = "⭐ FAVORITES:"
        print_box_title(Colors.bold(Colors.warning(fav_title)), fav_title)
        
        fav1 = f"{Colors.info('f')}            - Hiển thị danh sách favorites"
        print_box_line(fav1, "f            - Hiển thị danh sách favorites")
        
        fav2 = f"{Colors.info('f+ [số]')}      - Thêm tool vào favorites"
        print_box_line(fav2, "f+ [số]      - Thêm tool vào favorites")
        
        fav3 = f"{Colors.info('f- [số]')}      - Xóa tool khỏi favorites"
        print_box_line(fav3, "f- [số]      - Xóa tool khỏi favorites")
        
        print_box_empty()
        
        example2 = f"{Colors.muted('Ví dụ:')} {Colors.secondary('f+ 3')}, {Colors.secondary('f- 1')}"
        print_box_line(example2, "Ví dụ: f+ 3, f- 1")
        
        print_box_empty()
        
        # Recent
        recent_title = "📚 RECENT:"
        print_box_title(Colors.bold(Colors.warning(recent_title)), recent_title)
        
        rec1 = f"{Colors.info('r')}            - Hiển thị recent tools"
        print_box_line(rec1, "r            - Hiển thị recent tools")
        
        rec2 = f"{Colors.info('r[số]')}        - Chạy recent tool"
        print_box_line(rec2, "r[số]        - Chạy recent tool")
        
        print_box_empty()
        
        example3 = f"{Colors.muted('Ví dụ:')} {Colors.secondary('r1')} (chạy tool recent đầu tiên)"
        print_box_line(example3, "Ví dụ: r1 (chạy tool recent đầu tiên)")
        
        print_box_empty()
        
        # Activate/Deactivate
        act_title = "🔧 ACTIVATE/DEACTIVATE:"
        print_box_title(Colors.bold(Colors.warning(act_title)), act_title)
        
        act1 = f"{Colors.info('off [số]')}      - Vô hiệu hóa tool từ menu hiện tại"
        print_box_line(act1, "off [số]      - Vô hiệu hóa tool từ menu hiện tại")
        
        act2 = f"{Colors.info('on [số]')}       - Kích hoạt tool từ danh sách disabled"
        print_box_line(act2, "on [số]       - Kích hoạt tool từ danh sách disabled")
        
        act3 = f"{Colors.info('disabled')}      - Hiển thị danh sách tools bị disabled"
        print_box_line(act3, "disabled      - Hiển thị danh sách tools bị disabled")
        
        print_box_empty()
        
        note1 = f"{Colors.muted('Hỗ trợ nhiều tool:')} {Colors.secondary('off 1 2 3')} hoặc {Colors.secondary('off 1,2,3')}"
        print_box_line(note1, "Hỗ trợ nhiều tool: off 1 2 3 hoặc off 1,2,3")
        
        note2 = f"{Colors.muted('Ví dụ:')} {Colors.secondary('off 3')}, {Colors.secondary('off 1 2 3')}, {Colors.secondary('on 2 5')}"
        print_box_line(note2, "Ví dụ: off 3, off 1 2 3, on 2 5")
        
        print_box_empty()
        
        note3 = f"{Colors.muted('Lưu ý:')} {Colors.secondary('off [số]')} dùng số từ menu active,"
        print_box_line(note3, "Lưu ý: off [số] dùng số từ menu active,")
        
        note4 = f"          {Colors.secondary('on [số]')} dùng số từ danh sách disabled (xem bằng 'disabled')"
        print_box_line(note4, "            on [số] dùng số từ danh sách disabled (xem bằng 'disabled')", left_spaces=-2)
        
        print_box_empty()
        
        # Settings
        set_title = "⚙️  SETTINGS:"
        print_box_title(Colors.bold(Colors.warning(set_title)), set_title)
        
        set1 = f"{Colors.info('set')}          - Xem/chỉnh sửa settings"
        print_box_line(set1, "set          - Xem/chỉnh sửa settings")
        
        print_box_empty()
        
        # Tool Management
        mgmt_title = "🛠️  QUẢN LÝ TOOL:"
        print_box_title(Colors.bold(Colors.warning(mgmt_title)), mgmt_title)
        
        mgmt1 = f"{Colors.info('manage')}       - Export/Import/Xóa tool"
        print_box_line(mgmt1, "manage       - Export/Import/Xóa tool")
        
        print_box_empty()
        
        mgmt_note1 = f"{Colors.muted('Export:')} Xuất tool thành file .zip"
        print_box_line(mgmt_note1, "Export: Xuất tool thành file .zip")
        
        mgmt_note2 = f"{Colors.muted('Import:')} Nhập tool từ file .zip hoặc thư mục"
        print_box_line(mgmt_note2, "Import: Nhập tool từ file .zip hoặc thư mục")
        
        mgmt_note3 = f"{Colors.muted('Xóa:')} Xóa tool riêng lẻ (có xác nhận)"
        print_box_line(mgmt_note3, "Xóa: Xóa tool riêng lẻ (có xác nhận)")
        
        print_box_empty()
        
        # Khác
        other_title = "🔄 KHÁC:"
        print_box_title(Colors.bold(Colors.warning(other_title)), other_title)
        
        other1 = f"{Colors.info('l, list')}      - Hiển thị lại danh sách"
        print_box_line(other1, "l, list      - Hiển thị lại danh sách")
        
        other2 = f"{Colors.info('clear')}        - Xóa màn hình"
        print_box_line(other2, "clear        - Xóa màn hình")
        
        other3 = f"{Colors.info('log')}          - Xem và quản lý file log"
        print_box_line(other3, "log          - Xem và quản lý file log")
        
        other4 = f"{Colors.info('stats')}         - Xem thống kê sử dụng tools"
        print_box_line(other4, "stats         - Xem thống kê sử dụng tools")
        
        other5 = f"{Colors.info('qa, quick')}     - Quick actions menu"
        print_box_line(other5, "qa, quick     - Quick actions menu")
        
        print("  " + Colors.primary("╚" + "═" * content_width + "╝"))
        print()
        
        # Hiển thị ví dụ sử dụng nếu được yêu cầu
        if show_examples:
            self._show_help_examples()
    
    def _show_help_examples(self):
        """Hiển thị các ví dụ sử dụng phổ biến"""
        examples = [
            ("Chạy tool", "1", "Chạy tool số 1"),
            ("Xem hướng dẫn tool", "1h", "Xem hướng dẫn của tool số 1"),
            ("Tìm kiếm", "s backup", "Tìm các tool liên quan đến backup"),
            ("Thêm favorite", "f+ 3", "Thêm tool số 3 vào favorites"),
            ("Chạy recent", "r1", "Chạy tool recent đầu tiên"),
            ("Vô hiệu hóa", "off 2 3", "Vô hiệu hóa tool số 2 và 3"),
        ]
        
        # Tính chiều dài của từng dòng (không màu) để tìm dòng dài nhất
        max_line_length = 0
        formatted_lines = []
        
        for desc, cmd, explanation in examples:
            # Format text không màu trước để tính padding chính xác
            desc_text = desc + ":"
            cmd_text = f"'{cmd}'"
            expl_text = explanation
            
            # Format với padding chính xác (không màu)
            desc_formatted = f"{desc_text:20s}"
            cmd_formatted = f"{cmd_text:15s}"
            
            # Tính chiều dài hiển thị thực tế của nội dung (không có "  " ở đầu)
            # Format: "  " + "║" + " " + line_content + padding + "║"
            # Vậy line_content = desc_formatted + " " + cmd_formatted + " " + expl_text
            line_content = f"{desc_formatted} {cmd_formatted} {expl_text}"
            line_length = len(line_content)
            
            if line_length > max_line_length:
                max_line_length = line_length
            
            formatted_lines.append({
                'desc_text': desc_text,
                'cmd_text': cmd_text,
                'expl_text': expl_text,
                'desc_formatted': desc_formatted,
                'cmd_formatted': cmd_formatted,
                'line_content': line_content,
            })
        
        # Dùng chiều dài dòng dài nhất làm content_width
        content_width = max_line_length
        
        # Thêm 1 ký tự để các dòng border đều với nội dung
        border_width = content_width + 1
        
        print("  " + Colors.primary("╔" + "═" * border_width + "╗"))
        title = "VÍ DỤ SỬ DỤNG"
        # Format: "  " + "║" + " " + title_with_padding + "║"
        # title_with_padding phải có chiều dài = border_width - 1 (trừ 1 space trước ║)
        # Tính padding để center title
        total_padding = border_width - 1 - len(title)
        padding_before = total_padding // 2
        padding_after = total_padding - padding_before
        title_line = "  " + Colors.primary("║") + " " + " " * padding_before + Colors.bold(Colors.info(title)) + " " * padding_after + Colors.primary("║")
        print(title_line)
        print("  " + Colors.primary("╠" + "═" * border_width + "╣"))
        
        # Render các dòng với padding chính xác
        for line_data in formatted_lines:
            desc_text = line_data['desc_text']
            cmd_text = line_data['cmd_text']
            expl_text = line_data['expl_text']
            desc_formatted = line_data['desc_formatted']
            cmd_formatted = line_data['cmd_formatted']
            line_content = line_data['line_content']
            
            # Tính padding để đảm bảo tất cả dòng có cùng chiều dài
            # border_width - 1 vì có 1 space trước ║
            padding = (border_width - 1) - len(line_content)
            if padding < 0:
                padding = 0
            
            # Thêm màu vào từng phần đã được format
            desc_colored = Colors.bold(Colors.warning(desc_text))
            cmd_colored = Colors.info(cmd_text)
            expl_colored = Colors.muted(expl_text)
            
            # Tính padding cho desc và cmd để giữ nguyên chiều dài hiển thị
            desc_padding = len(desc_formatted) - len(desc_text)
            cmd_padding = len(cmd_formatted) - len(cmd_text)
            
            # Tạo line với màu và padding chính xác (không có "  " ở đầu)
            line = f"{desc_colored}{' ' * desc_padding} {cmd_colored}{' ' * cmd_padding} {expl_colored}"
            
            print("  " + Colors.primary("║") + " " + line + " " * padding + Colors.primary("║"))
        
        print("  " + Colors.primary("╚" + "═" * border_width + "╝"))
        print()
    
    def show_tool_help(self, tool: str) -> bool:
        """
        Hiển thị hướng dẫn sử dụng của tool (từ doc.py)
        
        Args:
            tool: Tên file tool (vd: backup-folder.py)
        
        Returns:
            bool: True nếu đọc được doc.py, False nếu không tìm thấy
        
        Giải thích:
        - Bước 1: Tìm thư mục chứa tool (tools/py/ hoặc tools/sh/)
        - Bước 2: Import module doc.py từ thư mục đó
        - Bước 3: Gọi hàm get_help() hoặc đọc biến HELP_TEXT
        - Bước 4: Hiển thị nội dung hướng dẫn
        - Bước 5: Nếu không có doc.py, hiển thị thông báo
        """
        tool_name = tool.replace('.py', '')
        
        # Tìm file doc.py trong tools/py/ trước
        tool_dir_path = self.tool_dir / "py" / tool_name
        doc_path = tool_dir_path / "doc.py"
        
        # Nếu không có trong py/, thử tìm trong sh/
        if not doc_path.exists():
            tool_dir_path = self.tool_dir / "sh" / tool_name
            doc_path = tool_dir_path / "doc.py"
        
        # Nếu vẫn không có, thử cấu trúc cũ
        if not doc_path.exists():
            tool_dir_path = self.tool_dir / tool_name
            doc_path = tool_dir_path / "doc.py"
        
        if not doc_path.exists():
            # Thông báo không tìm thấy doc.py
            tool_display_name = self.get_tool_display_name(tool)
            print()
            print_separator("═", 70, Colors.ERROR)
            print(Colors.error(f"❌ Không tìm thấy hướng dẫn cho tool: {tool_display_name}"))
            print(Colors.muted(f"   File doc.py không tồn tại trong {tool_name}/"))
            print_separator("═", 70, Colors.ERROR)
            print()
            return False
        
        # Import và đọc doc.py
        try:
            # Thêm thư mục tool vào sys.path để import
            if str(tool_dir_path) not in sys.path:
                sys.path.insert(0, str(tool_dir_path))
            
            # Import module doc
            import importlib.util
            spec = importlib.util.spec_from_file_location(f"{tool_name}.doc", doc_path)
            doc_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(doc_module)
            
            # Lấy hướng dẫn từ module
            # Ưu tiên hàm get_help(), nếu không có thì dùng biến HELP_TEXT
            if hasattr(doc_module, 'get_help'):
                help_text = doc_module.get_help()
            elif hasattr(doc_module, 'HELP_TEXT'):
                help_text = doc_module.HELP_TEXT
            else:
                tool_display_name = self.get_tool_display_name(tool)
                print()
                print_separator("═", 70, Colors.ERROR)
                print(Colors.error(f"❌ File doc.py không có hàm get_help() hoặc biến HELP_TEXT"))
                print(Colors.muted(f"   Tool: {tool_display_name}"))
                print_separator("═", 70, Colors.ERROR)
                print()
                return False
            
            # Hiển thị hướng dẫn
            tool_display_name = self.get_tool_display_name(tool)
            print()
            print_separator("═", 70, Colors.INFO)
            title = Colors.info(f"📖 HƯỚNG DẪN SỬ DỤNG: {Colors.bold(tool_display_name)}")
            print(f"  {title}")
            print_separator("═", 70, Colors.INFO)
            print()
            print(help_text)
            print()
            print_separator("═", 70, Colors.INFO)
            print()
            
            return True
            
        except Exception as e:
            tool_display_name = self.get_tool_display_name(tool)
            print()
            print_separator("═", 70, Colors.ERROR)
            print(Colors.error(f"❌ Lỗi khi đọc hướng dẫn cho tool: {tool_display_name}"))
            print(Colors.muted(f"   Lỗi: {e}"))
            print_separator("═", 70, Colors.ERROR)
            print()
            import traceback
            traceback.print_exc()
            return False
    
    def export_tool(self, tool: str, export_path: Optional[str] = None) -> Optional[str]:
        """
        Export tool thành file zip
        
        Args:
            tool: Tên file tool (vd: backup-folder.py)
            export_path: Đường dẫn file zip output (None = tự động tạo tên)
        
        Returns:
            str: Đường dẫn file zip đã tạo, hoặc None nếu lỗi
        
        Giải thích:
        - Tìm thư mục tool
        - Nén toàn bộ thư mục thành file zip
        - Lưu vào thư mục exports/ hoặc đường dẫn chỉ định
        """
        import shutil
        import zipfile
        from datetime import datetime
        
        tool_name = tool.replace('.py', '')
        
        # Tìm đường dẫn thư mục tool
        tool_dir = None
        tool_type = None
        
        # Thử tìm trong tools/py/
        py_tool_dir = self.tool_dir / "py" / tool_name
        if py_tool_dir.exists() and py_tool_dir.is_dir():
            tool_dir = py_tool_dir
            tool_type = 'py'
        
        # Thử tìm trong tools/sh/
        if not tool_dir:
            sh_tool_dir = self.tool_dir / "sh" / tool_name
            if sh_tool_dir.exists() and sh_tool_dir.is_dir():
                tool_dir = sh_tool_dir
                tool_type = 'sh'
        
        # Thử cấu trúc cũ
        if not tool_dir:
            old_tool_dir = self.tool_dir / tool_name
            if old_tool_dir.exists() and old_tool_dir.is_dir():
                tool_dir = old_tool_dir
                tool_type = 'py'  # Mặc định
        
        if not tool_dir or not tool_dir.exists():
            print(Colors.error(f"❌ Không tìm thấy thư mục tool: {tool_name}"))
            return None
        
        # Tạo thư mục exports nếu chưa có
        project_root = Path(__file__).parent.parent
        exports_dir = project_root / "exports"
        exports_dir.mkdir(exist_ok=True)
        
        # Tạo tên file zip
        if export_path:
            zip_path = Path(export_path)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"{tool_name}_{timestamp}.zip"
            zip_path = exports_dir / zip_filename
        
        try:
            # Tạo file zip
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Duyệt tất cả files trong thư mục tool
                for root, dirs, files in os.walk(tool_dir):
                    # Bỏ qua __pycache__ và .pyc files
                    dirs[:] = [d for d in dirs if d != '__pycache__']
                    
                    for file in files:
                        if file.endswith('.pyc'):
                            continue
                        
                        file_path = Path(root) / file
                        # Tạo đường dẫn tương đối trong zip (giữ nguyên cấu trúc: py/tool-name/ hoặc sh/tool-name/)
                        # arcname phải là: py/tool-name/file hoặc sh/tool-name/file
                        arcname = f"{tool_type}/{tool_name}/{file_path.relative_to(tool_dir)}"
                        zipf.write(file_path, arcname)
            
            return str(zip_path)
        except Exception as e:
            print(Colors.error(f"❌ Lỗi khi export tool: {e}"))
            import traceback
            traceback.print_exc()
            return None
    
    def import_tool(self, import_path: str, overwrite: bool = False) -> bool:
        """
        Import tool từ file zip hoặc thư mục
        
        Args:
            import_path: Đường dẫn file zip hoặc thư mục tool
            overwrite: Có ghi đè tool đã tồn tại không
        
        Returns:
            bool: True nếu thành công, False nếu lỗi
        
        Giải thích:
        - Nếu là file zip: giải nén vào tools/py/ hoặc tools/sh/
        - Nếu là thư mục: copy vào tools/py/ hoặc tools/sh/
        - Kiểm tra tool đã tồn tại và hỏi ghi đè nếu cần
        """
        import shutil
        import zipfile
        
        import_path_obj = Path(import_path)
        
        if not import_path_obj.exists():
            print(Colors.error(f"❌ Không tìm thấy file/thư mục: {import_path}"))
            return False
        
        # Xác định tool name và type
        tool_name = None
        tool_type = None
        
        if import_path_obj.is_file() and import_path_obj.suffix == '.zip':
            # File zip - cần giải nén và xác định tool name
            try:
                with zipfile.ZipFile(import_path_obj, 'r') as zipf:
                    # Tìm file .py đầu tiên để xác định tool name
                    for name in zipf.namelist():
                        # Pattern: py/tool-name/tool-name.py hoặc sh/tool-name/tool-name.py
                        parts = name.split('/')
                        if len(parts) >= 3 and parts[0] in ['py', 'sh']:
                            if parts[2].endswith('.py') and parts[2].replace('.py', '') == parts[1]:
                                tool_name = parts[1]
                                tool_type = parts[0]
                                break
                    
                    # Nếu không tìm thấy, thử pattern cũ: tool-name/tool-name.py
                    if not tool_name:
                        for name in zipf.namelist():
                            parts = name.split('/')
                            if len(parts) >= 2 and parts[1].endswith('.py'):
                                potential_name = parts[1].replace('.py', '')
                                if parts[0] == potential_name:
                                    tool_name = potential_name
                                    tool_type = 'py'  # Mặc định
                                    break
                    
                    if not tool_name:
                        print(Colors.error("❌ Không thể xác định tên tool từ file zip"))
                        return False
                    
                    # Kiểm tra tool đã tồn tại
                    target_dir = self.tool_dir / tool_type / tool_name
                    if target_dir.exists():
                        if not overwrite:
                            print(Colors.warning(f"⚠️  Tool '{tool_name}' đã tồn tại!"))
                            confirm = input(Colors.warning("   Bạn có muốn ghi đè? (yes/no): ")).strip().lower()
                            if confirm not in ['yes', 'y', 'có', 'c']:
                                print(Colors.info("ℹ️  Đã hủy import"))
                                return False
                        # Xóa tool cũ
                        shutil.rmtree(target_dir)
                    
                    # Giải nén vào thư mục tương ứng
                    # Tạo thư mục đích nếu chưa có
                    target_dir.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Giải nén từng file và đặt vào đúng vị trí
                    for name in zipf.namelist():
                        # Bỏ qua thư mục
                        if name.endswith('/'):
                            continue
                        
                        # Lấy đường dẫn đích
                        if name.startswith(f'{tool_type}/{tool_name}/'):
                            # Loại bỏ prefix py/tool-name/ hoặc sh/tool-name/
                            dest_name = name[len(f'{tool_type}/{tool_name}/'):]
                            dest_path = target_dir / dest_name
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Ghi file
                            with zipf.open(name) as source:
                                with open(dest_path, 'wb') as target:
                                    target.write(source.read())
                        elif name.startswith(f'{tool_name}/'):
                            # Pattern cũ: tool-name/file
                            dest_name = name[len(f'{tool_name}/'):]
                            dest_path = target_dir / dest_name
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Ghi file
                            with zipf.open(name) as source:
                                with open(dest_path, 'wb') as target:
                                    target.write(source.read())
                    
                    print(Colors.success(f"✅ Đã import tool: {tool_name}"))
                    return True
            except Exception as e:
                print(Colors.error(f"❌ Lỗi khi giải nén file zip: {e}"))
                import traceback
                traceback.print_exc()
                return False
        
        elif import_path_obj.is_dir():
            # Thư mục - copy vào tools/
            tool_name = import_path_obj.name
            
            # Kiểm tra xem có file .py chính không
            main_file = import_path_obj / f"{tool_name}.py"
            if not main_file.exists():
                print(Colors.error(f"❌ Không tìm thấy file chính: {main_file.name}"))
                return False
            
            # Xác định tool type (mặc định là py)
            tool_type = 'py'
            
            # Kiểm tra tool đã tồn tại
            target_dir = self.tool_dir / tool_type / tool_name
            if target_dir.exists():
                if not overwrite:
                    print(Colors.warning(f"⚠️  Tool '{tool_name}' đã tồn tại!"))
                    confirm = input(Colors.warning("   Bạn có muốn ghi đè? (yes/no): ")).strip().lower()
                    if confirm not in ['yes', 'y', 'có', 'c']:
                        print(Colors.info("ℹ️  Đã hủy import"))
                        return False
                # Xóa tool cũ
                shutil.rmtree(target_dir)
            
            # Copy thư mục vào tools/
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(import_path_obj, target_dir)
            
            print(Colors.success(f"✅ Đã import tool: {tool_name}"))
            return True
        
        else:
            print(Colors.error("❌ Đường dẫn không hợp lệ (phải là file .zip hoặc thư mục)"))
            return False
    
    def delete_tool(self, tool: str, confirm: bool = True) -> bool:
        """
        Xóa tool riêng lẻ
        
        Args:
            tool: Tên file tool (vd: backup-folder.py)
            confirm: Có hỏi xác nhận trước khi xóa không
        
        Returns:
            bool: True nếu thành công, False nếu lỗi hoặc hủy
        
        Giải thích:
        - Tìm thư mục tool
        - Xóa toàn bộ thư mục
        - Xóa khỏi favorites và recent nếu có
        """
        import shutil
        
        tool_name = tool.replace('.py', '')
        tool_display_name = self.get_tool_display_name(tool)
        
        # Tìm đường dẫn thư mục tool
        tool_dir = None
        
        # Thử tìm trong tools/py/
        py_tool_dir = self.tool_dir / "py" / tool_name
        if py_tool_dir.exists() and py_tool_dir.is_dir():
            tool_dir = py_tool_dir
        
        # Thử tìm trong tools/sh/
        if not tool_dir:
            sh_tool_dir = self.tool_dir / "sh" / tool_name
            if sh_tool_dir.exists() and sh_tool_dir.is_dir():
                tool_dir = sh_tool_dir
        
        # Thử cấu trúc cũ
        if not tool_dir:
            old_tool_dir = self.tool_dir / tool_name
            if old_tool_dir.exists() and old_tool_dir.is_dir():
                tool_dir = old_tool_dir
        
        if not tool_dir or not tool_dir.exists():
            print(Colors.error(f"❌ Không tìm thấy thư mục tool: {tool_name}"))
            return False
        
        # Xác nhận xóa
        if confirm:
            print()
            print(Colors.warning(f"⚠️  Bạn có chắc chắn muốn xóa tool: {Colors.bold(tool_display_name)}?"))
            print(Colors.muted(f"   Đường dẫn: {tool_dir}"))
            print()
            user_confirm = input(Colors.warning("   Nhập 'yes' để xác nhận: ")).strip().lower()
            if user_confirm not in ['yes', 'y', 'có', 'c']:
                print(Colors.info("ℹ️  Đã hủy xóa"))
                return False
        
        try:
            # Xóa thư mục tool
            shutil.rmtree(tool_dir)
            
            # Xóa khỏi favorites nếu có
            if tool in self.config.get('favorites', []):
                self.config['favorites'].remove(tool)
            
            # Xóa khỏi recent nếu có
            if tool in self.config.get('recent', []):
                self.config['recent'].remove(tool)
            
            # Xóa khỏi disabled nếu có
            if tool in self.config.get('disabled_tools', []):
                self.config['disabled_tools'].remove(tool)
            
            # Lưu config
            self._save_config()
            
            print(Colors.success(f"✅ Đã xóa tool: {tool_display_name}"))
            return True
            
        except PermissionError:
            print(Colors.error(f"❌ Không có quyền xóa thư mục: {tool_dir}"))
            return False
        except Exception as e:
            print(Colors.error(f"❌ Lỗi khi xóa tool: {e}"))
            import traceback
            traceback.print_exc()
            return False

