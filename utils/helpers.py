#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module helpers - Các hàm tiện ích hỗ trợ UI/UX

Mục đích: Tập trung các hàm helper cho UI/UX
"""

import difflib
import re
from typing import List, Optional
from .colors import Colors


def strip_ansi(text: str) -> str:
    """
    Loại bỏ ANSI color codes từ text để tính độ dài thực tế
    
    Args:
        text: Text có thể chứa ANSI codes
    
    Returns:
        str: Text không có ANSI codes
    """
    # ANSI escape sequence pattern
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def get_text_width(text: str) -> int:
    """
    Lấy độ dài thực tế của text (không tính ANSI codes)
    
    Args:
        text: Text có thể chứa ANSI codes
    
    Returns:
        int: Độ dài thực tế của text
    """
    return len(strip_ansi(text))


def highlight_keyword(text: str, keyword: str) -> str:
    """
    Highlight keyword trong text
    
    Args:
        text: Text gốc
        keyword: Keyword cần highlight
    
    Returns:
        str: Text với keyword được highlight
    """
    if not keyword:
        return text
    
    keyword_lower = keyword.lower()
    text_lower = text.lower()
    
    if keyword_lower not in text_lower:
        return text
    
    # Tìm vị trí keyword
    start = text_lower.find(keyword_lower)
    end = start + len(keyword)
    
    # Highlight
    highlighted = (
        text[:start] +
        Colors.bold(Colors.success(text[start:end])) +
        text[end:]
    )
    
    return highlighted


def suggest_command(user_input: str, valid_commands: List[str], max_suggestions: int = 3) -> List[str]:
    """
    Gợi ý command gần đúng khi user nhập sai
    
    Args:
        user_input: Input từ user
        valid_commands: Danh sách commands hợp lệ
        max_suggestions: Số lượng gợi ý tối đa
    
    Returns:
        list: Danh sách commands gợi ý
    """
    if not user_input:
        return []
    
    # Tìm commands tương tự
    suggestions = difflib.get_close_matches(
        user_input.lower(),
        [cmd.lower() for cmd in valid_commands],
        n=max_suggestions,
        cutoff=0.3
    )
    
    # Map về commands gốc
    result = []
    for sug in suggestions:
        for cmd in valid_commands:
            if cmd.lower() == sug:
                result.append(cmd)
                break
    
    return result


def format_tips() -> List[str]:
    """
    Tạo danh sách tips ngẫu nhiên
    
    Returns:
        list: Danh sách tips
    """
    tips = [
        "💡 Tip: Nhập 'h' để xem hướng dẫn đầy đủ",
        "💡 Tip: Dùng 's [keyword]' để tìm kiếm nhanh",
        "💡 Tip: Thêm tool vào favorites bằng 'f+ [số]'",
        "💡 Tip: Nhập số + 'h' (vd: '1h') để xem hướng dẫn tool",
        "💡 Tip: Dùng 'r' để xem recent tools",
        "💡 Tip: Nhập 'clear' để xóa màn hình",
        "💡 Tip: Dùng 'f' để xem tất cả favorites",
        "💡 Tip: Nhập 'set' để xem settings",
        "💡 Tip: Nhập 'log' để xem logs",
    ]
    
    return tips


def print_welcome_tip():
    """
    In một tip ngẫu nhiên khi khởi động
    """
    import random
    tips = format_tips()
    tip = random.choice(tips)
    print(Colors.muted(f"  {tip}"))


def print_command_suggestions(user_input: str, suggestions: List[str]):
    """
    In gợi ý commands khi user nhập sai
    
    Args:
        user_input: Input từ user
        suggestions: Danh sách suggestions
    """
    if not suggestions:
        return
    
    print()
    print(Colors.warning(f"⚠️  Không tìm thấy lệnh: '{user_input}'"))
    
    if len(suggestions) == 1:
        print(Colors.info(f"💡 Có phải bạn muốn: {Colors.bold(suggestions[0])}?"))
    else:
        print(Colors.info(f"💡 Gợi ý ({len(suggestions)}): {', '.join([Colors.bold(s) for s in suggestions])}"))
    
    print()


def print_banner():
    """
    In banner đẹp với design hiện đại
    
    Mục đích: Tạo ấn tượng ban đầu tốt, thu hút người dùng
    """
    width = 55
    
    # Tính toán padding chính xác (không tính ANSI codes)
    title1 = "DEV TOOLS"
    title1_len = len(title1)
    title1_padding_left = (width - title1_len) // 2
    title1_padding_right = width - title1_len - title1_padding_left
    
    title2 = "Bộ công cụ Python tiện ích"
    title2_len = len(title2)
    title2_padding_left = (width - title2_len) // 2
    title2_padding_right = width - title2_len - title2_padding_left
    
    title3 = "Nhập 'h' hoặc 'help' để xem hướng dẫn"
    title3_len = len(title3)
    title3_padding_left = (width - title3_len) // 2
    title3_padding_right = width - title3_len - title3_padding_left
    
    print()
    print("  " + Colors.primary("╔" + "═" * width + "╗"))
    print("  " + Colors.primary("║") + " " * title1_padding_left + Colors.bold(Colors.info(title1)) + " " * title1_padding_right + Colors.primary("║"))
    print("  " + Colors.primary("║") + " " * title2_padding_left + Colors.secondary(title2) + " " * title2_padding_right + Colors.primary("║"))
    print("  " + Colors.primary("║") + " " * width + Colors.primary("║"))
    print("  " + Colors.primary("║") + " " * title3_padding_left + Colors.muted(title3) + " " * title3_padding_right + Colors.primary("║"))
    print("  " + Colors.primary("╚" + "═" * width + "╝"))
    print()


def print_boxed_text(text: str, title: Optional[str] = None, color: Optional[str] = Colors.PRIMARY, width: int = 70) -> None:
    """
    In text trong box đẹp
    
    Args:
        text: Nội dung text
        title: Tiêu đề (optional)
        color: Màu sắc cho box
        width: Độ rộng của box
    """
    lines = text.split('\n')
    if not lines:
        lines = ['']
    
    # Top border
    if title:
        title_len = len(title)  # Plain text length
        title_padding = (width - title_len - 2) // 2
        top_line = "  " + Colors.colorize("╔" + "═" * (width - 2) + "╗", color)
        title_line = "  " + Colors.colorize("║", color) + " " * title_padding + Colors.bold(title) + " " * (width - title_len - title_padding - 2) + Colors.colorize("║", color)
        print(top_line)
        print(title_line)
        print("  " + Colors.colorize("╠" + "═" * (width - 2) + "╣", color))
    else:
        print("  " + Colors.colorize("╔" + "═" * (width - 2) + "╗", color))
    
    # Content
    for line in lines:
        # Strip ANSI để tính độ dài thực tế
        line_plain = strip_ansi(line)
        
        # Wrap long lines
        max_content_width = width - 4
        while len(line_plain) > max_content_width:
            wrapped_line_plain = line_plain[:max_content_width]
            line_plain = line_plain[max_content_width:]
            # Cần tìm lại line có ANSI tương ứng
            wrapped_line = line[:max_content_width] if len(strip_ansi(line)) == len(line) else wrapped_line_plain
            content = wrapped_line + " " * (max_content_width - len(wrapped_line_plain))
            print("  " + Colors.colorize("║", color) + f" {content} " + Colors.colorize("║", color))
            line = line[max_content_width:] if len(line) > max_content_width else ""
        
        content_plain = line_plain + " " * (max_content_width - len(line_plain))
        print("  " + Colors.colorize("║", color) + f" {line if line else ' ' * max_content_width} " + Colors.colorize("║", color))
    
    # Bottom border
    print("  " + Colors.colorize("╚" + "═" * (width - 2) + "╝", color))
    print()


def print_card(title: str, content: str, icon: Optional[str] = None, color: Optional[str] = Colors.INFO) -> None:
    """
    In card-style UI component
    
    Args:
        title: Tiêu đề card
        content: Nội dung card
        icon: Icon (optional)
        color: Màu sắc
    """
    if icon:
        title_text = f"{icon} {title}"
    else:
        title_text = title
    
    print()
    print(Colors.colorize(f"┌─ {title_text} {'─' * (65 - len(title_text))}", color))
    print(Colors.colorize("│", color))
    
    for line in content.split('\n'):
        if line.strip():
            print(Colors.colorize(f"│  {line}", color))
        else:
            print(Colors.colorize("│", color))
    
    print(Colors.colorize("│", color))
    print(Colors.colorize("└" + "─" * 68, color))
    print()


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Xác nhận hành động với user
    
    Args:
        message: Thông báo xác nhận
        default: Giá trị mặc định (True = Y, False = n)
    
    Returns:
        bool: True nếu user xác nhận, False nếu không
    """
    default_text = "Y/n" if default else "y/N"
    default_char = "Y" if default else "N"
    
    prompt = Colors.warning(f"⚠️  {message} ({default_text}): ")
    
    try:
        response = input(prompt).strip().lower()
        
        if not response:
            return default
        
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print(Colors.error("❌ Vui lòng nhập 'y' hoặc 'n'"))
            return confirm_action(message, default)
    except (KeyboardInterrupt, EOFError):
        return False
