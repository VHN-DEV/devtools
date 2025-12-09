#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module ui - Các UI components và utilities cho UX tốt hơn

Mục đích: Tập trung các component UI tái sử dụng
Lý do: Tách riêng logic UI để dễ maintain và mở rộng
"""

from typing import Optional, List
from .colors import Colors


def print_success_box(message: str, title: Optional[str] = "Thành công"):
    """In thông báo thành công trong box đẹp"""
    print()
    print("  " + Colors.success("╔" + "═" * 66 + "╗"))
    title_padding = (66 - len(title) - 2) // 2
    print("  " + Colors.success("║") + " " * title_padding + Colors.bold(title) + " " * (66 - len(title) - title_padding - 2) + Colors.success("║"))
    print("  " + Colors.success("╠" + "═" * 66 + "╣"))
    
    # Wrap message nếu quá dài
    max_width = 64
    words = message.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + word) <= max_width:
            current_line += word + " "
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    for line in lines:
        padding = max(0, 64 - len(line))
        print("  " + Colors.success("║") + " " + line + " " * padding + " " + Colors.success("║"))
    
    print("  " + Colors.success("╚" + "═" * 66 + "╝"))
    print()


def print_error_box(message: str, title: Optional[str] = "Lỗi", suggestions: Optional[List[str]] = None, solutions: Optional[List[str]] = None):
    """
    In thông báo lỗi trong box đẹp với suggestions và solutions
    
    Args:
        message: Thông báo lỗi
        title: Tiêu đề (mặc định: "Lỗi")
        suggestions: Danh sách gợi ý
        solutions: Danh sách giải pháp cụ thể
    """
    print()
    print("  " + Colors.error("╔" + "═" * 66 + "╗"))
    title_padding = (66 - len(title) - 2) // 2
    print("  " + Colors.error("║") + " " * title_padding + Colors.bold(title) + " " * (66 - len(title) - title_padding - 2) + Colors.error("║"))
    print("  " + Colors.error("╠" + "═" * 66 + "╣"))
    
    # Wrap message
    max_width = 64
    words = message.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + word) <= max_width:
            current_line += word + " "
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    for line in lines:
        padding = max(0, 64 - len(line))
        print("  " + Colors.error("║") + " " + line + " " * padding + " " + Colors.error("║"))
    
    if suggestions:
        print("  " + Colors.error("╠" + "─" * 66 + "╣"))
        print("  " + Colors.error("║") + " " + Colors.info("💡 Gợi ý:") + " " * (66 - 12) + Colors.error("║"))
        for suggestion in suggestions:
            sug_text = f"   • {suggestion}"
            padding = max(0, 64 - len(sug_text))
            print("  " + Colors.error("║") + " " + Colors.muted(sug_text) + " " * padding + " " + Colors.error("║"))
    
    if solutions:
        print("  " + Colors.error("╠" + "─" * 66 + "╣"))
        print("  " + Colors.error("║") + " " + Colors.success("✅ Giải pháp:") + " " * (66 - 16) + Colors.error("║"))
        for solution in solutions:
            sol_text = f"   • {solution}"
            padding = max(0, 64 - len(sol_text))
            print("  " + Colors.error("║") + " " + Colors.success(sol_text) + " " * padding + " " + Colors.error("║"))
    
    print("  " + Colors.error("╚" + "═" * 66 + "╝"))
    print()


def print_warning_box(message: str, title: Optional[str] = "Cảnh báo"):
    """In thông báo cảnh báo trong box đẹp"""
    print()
    print("  " + Colors.warning("╔" + "═" * 66 + "╗"))
    title_padding = (66 - len(title) - 2) // 2
    print("  " + Colors.warning("║") + " " * title_padding + Colors.bold(title) + " " * (66 - len(title) - title_padding - 2) + Colors.warning("║"))
    print("  " + Colors.warning("╠" + "═" * 66 + "╣"))
    
    # Wrap message
    max_width = 64
    words = message.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + word) <= max_width:
            current_line += word + " "
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    for line in lines:
        padding = max(0, 64 - len(line))
        print("  " + Colors.warning("║") + " " + line + " " * padding + " " + Colors.warning("║"))
    
    print("  " + Colors.warning("╚" + "═" * 66 + "╝"))
    print()


def print_info_box(message: str, title: Optional[str] = "Thông tin"):
    """In thông báo thông tin trong box đẹp"""
    print()
    print("  " + Colors.info("╔" + "═" * 66 + "╗"))
    title_padding = (66 - len(title) - 2) // 2
    print("  " + Colors.info("║") + " " * title_padding + Colors.bold(title) + " " * (66 - len(title) - title_padding - 2) + Colors.info("║"))
    print("  " + Colors.info("╠" + "═" * 66 + "╣"))
    
    # Wrap message
    max_width = 64
    words = message.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + word) <= max_width:
            current_line += word + " "
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    for line in lines:
        padding = max(0, 64 - len(line))
        print("  " + Colors.info("║") + " " + line + " " * padding + " " + Colors.info("║"))
    
    print("  " + Colors.info("╚" + "═" * 66 + "╝"))
    print()


def print_table(headers: List[str], rows: List[List[str]], title: Optional[str] = None):
    """
    In bảng với format đẹp
    
    Args:
        headers: Danh sách tiêu đề cột
        rows: Danh sách các dòng dữ liệu
        title: Tiêu đề bảng (optional)
    """
    if not headers or not rows:
        return
    
    # Tính độ rộng cột
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Thêm padding
    col_widths = [w + 2 for w in col_widths]
    total_width = sum(col_widths) + len(headers) + 1
    
    print()
    
    # Title
    if title:
        title_padding = (total_width - len(title) - 2) // 2
        print("  " + Colors.primary("╔" + "═" * (total_width - 2) + "╗"))
        print("  " + Colors.primary("║") + " " * title_padding + Colors.bold(title) + " " * (total_width - len(title) - title_padding - 2) + Colors.primary("║"))
        print("  " + Colors.primary("╠" + "═" * (total_width - 2) + "╣"))
    else:
        print("  " + Colors.primary("╔" + "═" * (total_width - 2) + "╗"))
    
    # Header
    header_line = "  " + Colors.primary("║")
    for i, header in enumerate(headers):
        padding = col_widths[i] - len(str(header))
        header_line += " " + Colors.bold(Colors.info(str(header))) + " " * padding + Colors.primary("║")
    print(header_line)
    print("  " + Colors.primary("╠" + "═" * (total_width - 2) + "╣"))
    
    # Rows
    for row in rows:
        row_line = "  " + Colors.primary("║")
        for i, cell in enumerate(row):
            if i < len(col_widths):
                padding = col_widths[i] - len(str(cell))
                row_line += " " + str(cell) + " " * padding + Colors.primary("║")
        print(row_line)
    
    print("  " + Colors.primary("╚" + "═" * (total_width - 2) + "╝"))
    print()


def print_steps(steps: List[str], title: Optional[str] = "Hướng dẫn"):
    """In danh sách các bước với format đẹp"""
    print()
    print("  " + Colors.primary("╔" + "═" * 66 + "╗"))
    title_padding = (66 - len(title) - 2) // 2
    print("  " + Colors.primary("║") + " " * title_padding + Colors.bold(title) + " " * (66 - len(title) - title_padding - 2) + Colors.primary("║"))
    print("  " + Colors.primary("╠" + "═" * 66 + "╣"))
    
    for idx, step in enumerate(steps, start=1):
        step_text = f"{idx}. {step}"
        # Wrap if too long
        max_width = 62
        if len(step_text) > max_width:
            words = step_text.split()
            lines = []
            current_line = f"{idx}. "
            for word in words[1:]:  # Skip number
                if len(current_line + word) <= max_width:
                    current_line += word + " "
                else:
                    lines.append(current_line.strip())
                    current_line = "   " + word + " "  # Indent continuation
            
            if current_line:
                lines.append(current_line.strip())
            
            for i, line in enumerate(lines):
                if i == 0:
                    padding = max(0, 64 - len(line))
                    print("  " + Colors.primary("║") + " " + Colors.info(line) + " " * padding + " " + Colors.primary("║"))
                else:
                    padding = max(0, 64 - len(line))
                    print("  " + Colors.primary("║") + " " + Colors.muted(line) + " " * padding + " " + Colors.primary("║"))
        else:
            padding = max(0, 64 - len(step_text))
            print("  " + Colors.primary("║") + " " + Colors.info(step_text) + " " * padding + " " + Colors.primary("║"))
    
    print("  " + Colors.primary("╚" + "═" * 66 + "╝"))
    print()

