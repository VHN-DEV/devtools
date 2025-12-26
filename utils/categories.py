#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module categories - Phân loại tools theo categories

Mục đích: Tổ chức tools theo categories để dễ tìm kiếm và hiển thị
Lý do: Khi có nhiều tools, cần phân loại để UX tốt hơn
"""

from typing import Dict, List, Optional


# 6 Categories chính với unique keys
CATEGORIES = {
    'development': {
        'icon': '💻',
        'name': 'Development Tools',
        'description': 'Công cụ phát triển và version control',
        'color': 'GREEN',
        'keywords': ['git', 'commit', 'ssh', 'server', 'remote', 'database'],
        'tools': []
    },
    'media': {
        'icon': '🎬',
        'name': 'Media & Multimedia',
        'description': 'Xử lý hình ảnh, video và multimedia',
        'color': 'MAGENTA',
        'keywords': ['image', 'video', 'photo', 'picture', 'watermark', 'compress', 'converter', 'media'],
        'tools': []
    },
    'file': {
        'icon': '📁',
        'name': 'File System',
        'description': 'Quản lý file, thư mục, backup và tổ chức',
        'color': 'BLUE',
        'keywords': ['backup', 'folder', 'clean', 'temp', 'organizer', 'rename', 'duplicate', 'copy', 'changed'],
        'tools': []  # Sẽ được populate tự động
    },
    'system': {
        'icon': '⚙️',
        'name': 'System Tools',
        'description': 'Công cụ quản lý hệ thống và setup',
        'color': 'YELLOW',
        'keywords': ['setup', 'project', 'linux', 'docker', 'tree', 'xampp', 'bootstrap'],
        'tools': []
    },
    'network': {
        'icon': '🌐',
        'name': 'Network & Web',
        'description': 'Công cụ mạng và phân tích web',
        'color': 'CYAN',
        'keywords': ['website', 'performance', 'check', 'qr', 'code', 'json', 'format'],
        'tools': []
    },
    'utility': {
        'icon': '🔧',
        'name': 'Utility Tools',
        'description': 'Các công cụ tiện ích khác',
        'color': 'WHITE',
        'keywords': ['pdf', 'text', 'encoding', 'find', 'replace', 'scan', 'malware'],
        'tools': []
    }
}

# Backward compatibility - mapping từ category key -> category info
CATEGORY_INFO = {key: cat for key, cat in CATEGORIES.items()}

# Default category cho tools không match
DEFAULT_CATEGORY = 'utility'


def detect_tool_category(tool_name: str, tool_tags: Optional[List[str]] = None) -> str:
    """
    Phát hiện category của tool dựa trên tên và tags
    Mỗi tool chỉ thuộc 1 category duy nhất

    Args:
        tool_name: Tên file tool (vd: backup-folder.py)
        tool_tags: Danh sách tags của tool (optional)

    Returns:
        str: Category key (vd: 'file', 'media', 'development')
    """
    tool_lower = tool_name.lower()

    # Check trong tags trước (ưu tiên cao hơn)
    if tool_tags:
        for tag in tool_tags:
            tag_lower = tag.lower()
            for category_key, category_info in CATEGORIES.items():
                if any(kw in tag_lower for kw in category_info['keywords']):
                    return category_key

    # Check trong tên file theo thứ tự ưu tiên của categories
    for category_key, category_info in CATEGORIES.items():
        if any(kw in tool_lower for kw in category_info['keywords']):
            return category_key

    # Default category
    return DEFAULT_CATEGORY


def group_tools_by_category(tools: List[str], tool_manager) -> Dict[str, List[str]]:
    """
    Nhóm tools theo categories (mỗi tool chỉ thuộc 1 category)

    Args:
        tools: Danh sách tools
        tool_manager: ToolManager instance để lấy tags

    Returns:
        dict: Dictionary với key là category, value là list tools
    """
    grouped = {}

    # Khởi tạo tất cả categories
    for category_key in CATEGORIES.keys():
        grouped[category_key] = []

    # Phân loại tools vào categories
    for tool in tools:
        # Check manual assignment trước
        manual_category = tool_manager.get_manual_category_assignment(tool)
        if manual_category and manual_category in CATEGORIES:
            category = manual_category
        else:
            # Auto-detect category
            tags = tool_manager.get_tool_tags(tool)
            category = detect_tool_category(tool, tags)

        grouped[category].append(tool)

    # Sắp xếp tools trong mỗi category theo alphabet
    for category in grouped:
        grouped[category].sort()

    # Populate tools vào CATEGORIES (cho việc quản lý)
    for category_key in CATEGORIES:
        CATEGORIES[category_key]['tools'] = grouped[category_key]

    return grouped


def get_category_info(category: str) -> Dict:
    """
    Lấy thông tin category (icon, name, color)

    Args:
        category: Tên category

    Returns:
        dict: Thông tin category
    """
    return CATEGORIES.get(category, CATEGORIES[DEFAULT_CATEGORY])


def get_all_categories() -> Dict[str, Dict]:
    """
    Lấy tất cả categories với thông tin chi tiết

    Returns:
        dict: Dictionary của tất cả categories
    """
    return CATEGORIES.copy()


def add_category(key: str, name: str, icon: str, description: str = "", color: str = "WHITE") -> bool:
    """
    Thêm category mới

    Args:
        key: Unique key cho category
        name: Tên hiển thị
        icon: Emoji icon
        description: Mô tả category
        color: Màu sắc (Colors constant)

    Returns:
        bool: True nếu thành công, False nếu key đã tồn tại
    """
    if key in CATEGORIES:
        return False

    CATEGORIES[key] = {
        'icon': icon,
        'name': name,
        'description': description or f"Category {name}",
        'color': color,
        'keywords': [],
        'tools': []
    }
    return True


def update_category(key: str, name: str = None, icon: str = None, description: str = None, color: str = None) -> bool:
    """
    Cập nhật thông tin category

    Args:
        key: Category key cần update
        name: Tên mới (optional)
        icon: Icon mới (optional)
        description: Mô tả mới (optional)
        color: Màu mới (optional)

    Returns:
        bool: True nếu thành công, False nếu category không tồn tại
    """
    if key not in CATEGORIES:
        return False

    if name is not None:
        CATEGORIES[key]['name'] = name
    if icon is not None:
        CATEGORIES[key]['icon'] = icon
    if description is not None:
        CATEGORIES[key]['description'] = description
    if color is not None:
        CATEGORIES[key]['color'] = color

    return True


def delete_category(key: str) -> bool:
    """
    Xóa category (chỉ cho phép xóa categories custom, không xóa built-in)

    Args:
        key: Category key cần xóa

    Returns:
        bool: True nếu thành công, False nếu không thể xóa
    """
    # Không cho phép xóa 6 categories built-in
    built_in_categories = ['file', 'media', 'development', 'system', 'network', 'utility']
    if key in built_in_categories:
        return False

    if key in CATEGORIES:
        del CATEGORIES[key]
        return True

    return False


def assign_tool_to_category(tool_name: str, category_key: str) -> bool:
    """
    Gán tool vào category cụ thể (manual override)

    Args:
        tool_name: Tên file tool
        category_key: Category key đích

    Returns:
        bool: True nếu thành công
    """
    # Hàm này sẽ được implement trong tool_config để lưu manual assignments
    # Hiện tại chỉ return True để tương thích
    return True


def get_category_stats() -> Dict[str, Dict]:
    """
    Lấy thống kê categories

    Returns:
        dict: Thống kê số tools trong mỗi category
    """
    stats = {}
    for key, category in CATEGORIES.items():
        stats[key] = {
            'name': category['name'],
            'icon': category['icon'],
            'tool_count': len(category['tools']),
            'color': category['color']
        }
    return stats

