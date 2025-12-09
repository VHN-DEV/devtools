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


def print_welcome_message():
    """
    In welcome message thân thiện với onboarding tips
    
    Mục đích: Giúp người dùng mới hiểu cách sử dụng nhanh chóng
    """
    print()
    print(Colors.primary("  ┌─ " + "─" * 65 + " ┐"))
    print(Colors.primary("  │") + " " * 67 + Colors.primary("│"))
    
    welcome_text = "👋 Chào mừng đến với DevTools!"
    welcome_padding = (67 - len(welcome_text) + 1) // 2  # +1 cho emoji
    print(Colors.primary("  │") + " " * welcome_padding + Colors.bold(Colors.info(welcome_text)) + " " * (67 - len(welcome_text) - welcome_padding + 1) + Colors.primary("│"))
    
    print(Colors.primary("  │") + " " * 67 + Colors.primary("│"))
    
    quick_start = "🚀 Bắt đầu nhanh:"
    print(Colors.primary("  │") + "  " + Colors.bold(Colors.warning(quick_start)) + " " * (67 - len(quick_start) - 2) + Colors.primary("│"))
    
    tips = [
        ("• Nhập", Colors.muted, "số", Colors.info, "để chạy tool (vd: 1, 2, 3)"),
        ("• Nhập", Colors.muted, "h", Colors.info, "để xem hướng dẫn đầy đủ"),
        ("• Nhập", Colors.muted, "s [từ khóa]", Colors.info, "để tìm kiếm tool"),
        ("• Nhập", Colors.muted, "f+ [số]", Colors.info, "để thêm vào favorites"),
    ]
    
    for tip_parts in tips:
        tip_line = ""
        for part in tip_parts:
            if isinstance(part, str):
                tip_line += part
            else:
                tip_line += part("") if callable(part) else str(part)
        
        # Tính độ dài thực tế (không tính ANSI codes)
        tip_plain = strip_ansi(tip_line)
        tip_padding = 67 - len(tip_plain) - 2
        if tip_padding < 0:
            tip_padding = 0
        
        print(Colors.primary("  │") + "  " + tip_line + " " * tip_padding + Colors.primary("│"))
    
    print(Colors.primary("  │") + " " * 67 + Colors.primary("│"))
    
    help_text = "💡 Tip: Nhập 'h' để xem tất cả lệnh có sẵn"
    help_padding = (67 - len(help_text) + 1) // 2
    print(Colors.primary("  │") + " " * help_padding + Colors.muted(help_text) + " " * (67 - len(help_text) - help_padding + 1) + Colors.primary("│"))
    
    print(Colors.primary("  │") + " " * 67 + Colors.primary("│"))
    print(Colors.primary("  └─ " + "─" * 65 + " ┘"))
    print()


def print_keyboard_shortcuts():
    """
    In danh sách keyboard shortcuts phổ biến
    
    Mục đích: Giúp người dùng biết các shortcuts tiện lợi
    """
    shortcuts = [
        ("Số (1-9)", "Chạy tool theo số thứ tự"),
        ("s [keyword]", "Tìm kiếm tool"),
        ("f", "Xem favorites"),
        ("r", "Xem recent tools"),
        ("h", "Xem help"),
        ("q", "Thoát"),
        ("clear", "Xóa màn hình"),
    ]
    
    # Tính chiều dài của từng dòng (không màu) để tìm dòng dài nhất
    max_line_length = 0
    formatted_lines = []
    title = " ⌨️  KEYBOARD SHORTCUTS"
    
    # Tính chiều dài của từng dòng nội dung (không tính border)
    for shortcut, description in shortcuts:
        # Format text không màu trước để tính padding chính xác
        shortcut_formatted = f"{shortcut:20s}"
        # Tính chiều dài hiển thị thực tế của nội dung
        # Format: "  " + "║" + " " + "  " + line_content + padding + "║"
        # Có thêm 2 spaces ở đầu mỗi dòng content (tổng 3 spaces sau ║)
        # Vậy line_content = "  " + shortcut_formatted + "  " + description
        line_content = f"  {shortcut_formatted}  {description}"
        line_length = len(line_content)
        
        if line_length > max_line_length:
            max_line_length = line_length
        
        formatted_lines.append({
            'shortcut': shortcut,
            'description': description,
            'shortcut_formatted': shortcut_formatted,
            'line_content': line_content,
        })
    
    # Dùng cùng border_width với khối "VÍ DỤ SỬ DỤNG" để đồng đều
    # border_width = 67 (tính từ khối "VÍ DỤ SỬ DỤNG")
    border_width = 71
    
    print()
    # Render với double box drawing characters để đồng đều với các khối khác
    # Top border: "  " + "╔" + "═" * border_width + "╗"
    print("  " + Colors.primary("╔" + "═" * border_width + "╗"))
    
    # Title line: "  " + "║" + " " + title với padding + "║"
    # Tính padding để center title
    total_padding = border_width - 1 - len(title)
    padding_before = total_padding // 2
    padding_after = total_padding - padding_before
    title_colored = Colors.bold(Colors.info(title))
    print("  " + Colors.primary("║") + " " + " " * padding_before + title_colored + " " * padding_after + Colors.primary("║"))
    
    # Separator: "  " + "╠" + "═" * border_width + "╣"
    print("  " + Colors.primary("╠" + "═" * border_width + "╣"))
    
    # Empty line
    print("  " + Colors.primary("║") + " " * border_width + Colors.primary("║"))
    
    # Render các dòng với padding chính xác
    for line_data in formatted_lines:
        shortcut = line_data['shortcut']
        description = line_data['description']
        shortcut_formatted = line_data['shortcut_formatted']
        line_content = line_data['line_content']
        
        # Thêm màu vào từng phần đã được format
        shortcut_colored = Colors.bold(Colors.info(shortcut))
        desc_colored = Colors.muted(description)
        
        # Tính padding cho shortcut để giữ nguyên chiều dài hiển thị
        shortcut_padding = len(shortcut_formatted) - len(shortcut)
        
        # Tạo line với màu và padding chính xác (có "  " ở đầu để khớp với output mẫu)
        line = f"  {shortcut_colored}{' ' * shortcut_padding}  {desc_colored}"
        
        # Tính độ dài thực tế của line (không tính ANSI codes) để đảm bảo padding chính xác
        line_plain = strip_ansi(line)
        actual_padding = (border_width - 1) - len(line_plain)
        if actual_padding < 0:
            actual_padding = 0
        
        print("  " + Colors.primary("║") + " " + line + " " * actual_padding + Colors.primary("║"))
    
    # Empty line
    print("  " + Colors.primary("║") + " " * border_width + Colors.primary("║"))
    
    # Bottom border: "  " + "╚" + "═" * border_width + "╝"
    print("  " + Colors.primary("╚" + "═" * border_width + "╝"))
    print()


def print_command_suggestions(user_input: str, suggestions: List[str]):
    """
    In gợi ý commands khi user nhập sai với UI đẹp hơn
    
    Args:
        user_input: Input từ user
        suggestions: Danh sách suggestions
    """
    if not suggestions:
        return
    
    print()
    print(Colors.error("  ┌─ " + "─" * 63 + " ┐"))
    print(Colors.error("  │") + " " * 65 + Colors.error("│"))
    
    error_msg = f"⚠️  Không tìm thấy lệnh: '{user_input}'"
    error_padding = (65 - len(error_msg) + 1) // 2
    print(Colors.error("  │") + " " * error_padding + Colors.bold(error_msg) + " " * (65 - len(error_msg) - error_padding + 1) + Colors.error("│"))
    
    print(Colors.error("  │") + " " * 65 + Colors.error("│"))
    
    if len(suggestions) == 1:
        suggest_msg = f"💡 Có phải bạn muốn: {Colors.bold(suggestions[0])}?"
        suggest_plain = strip_ansi(suggest_msg)
        suggest_padding = (65 - len(suggest_plain) + 1) // 2
        print(Colors.error("  │") + " " * suggest_padding + Colors.info(suggest_msg) + " " * (65 - len(suggest_plain) - suggest_padding + 1) + Colors.error("│"))
    else:
        suggest_title = f"💡 Gợi ý ({len(suggestions)}):"
        suggest_title_padding = (65 - len(suggest_title) + 1) // 2
        print(Colors.error("  │") + " " * suggest_title_padding + Colors.info(suggest_title) + " " * (65 - len(suggest_title) - suggest_title_padding + 1) + Colors.error("│"))
        
        suggestions_text = ", ".join([Colors.bold(s) for s in suggestions])
        suggestions_plain = strip_ansi(suggestions_text)
        suggestions_padding = (65 - len(suggestions_plain)) // 2
        print(Colors.error("  │") + " " * suggestions_padding + suggestions_text + " " * (65 - len(suggestions_plain) - suggestions_padding) + Colors.error("│"))
    
    print(Colors.error("  │") + " " * 65 + Colors.error("│"))
    print(Colors.error("  └─ " + "─" * 63 + " ┘"))
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
