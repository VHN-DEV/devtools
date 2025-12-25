#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module interactive - Common interactive UI patterns for tools

Mục đích: Tập trung các pattern UI/UX phổ biến trong chế độ interactive
Lý do: Giảm code duplication, đảm bảo tính nhất quán UI/UX
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Union
from .colors import Colors
from .format import print_header, print_separator
from .validation import get_user_input as base_get_user_input, confirm_action


def get_enhanced_user_input(
    prompt: str,
    default: Optional[str] = None,
    validator: Optional[Callable[[str], Union[bool, str]]] = None,
    required: bool = False,
    strip: bool = True
) -> Optional[str]:
    """
    Nhận input từ user với enhanced validation và default value

    Args:
        prompt: Thông báo hiển thị
        default: Giá trị mặc định (None = không có)
        validator: Hàm validate input (return True/False hoặc error message)
        required: Có bắt buộc nhập không (nếu True, không accept empty)
        strip: Có strip whitespace không

    Returns:
        str: Input từ user (đã validate), hoặc None nếu hủy

    Giải thích:
        - Hiển thị prompt với [default] nếu có
        - Validate input nếu có validator
        - Retry cho đến khi input hợp lệ
        - Support Ctrl+C để hủy
    """
    def enhanced_validator(input_str: str) -> tuple:
        if not input_str and required:
            return False, "Vui lòng nhập giá trị!"

        if validator:
            validation_result = validator(input_str)
            if isinstance(validation_result, str):
                return False, validation_result
            elif validation_result is False:
                return False, "Giá trị không hợp lệ!"
            elif validation_result is True:
                return True, ""
            else:
                return validation_result

        return True, ""

    try:
        return base_get_user_input(
            prompt=prompt,
            default=default,
            strip_quotes=strip,
            validator=enhanced_validator if (validator or required) else None,
            max_retries=3,
            error_message=None
        )
    except (EOFError, KeyboardInterrupt, ValueError):
        return None


def get_user_choice(
    prompt: str,
    choices: List[str],
    default: Optional[int] = None,
    allow_custom: bool = False
) -> Optional[Union[int, str]]:
    """
    Nhận lựa chọn từ danh sách options

    Args:
        prompt: Thông báo hiển thị
        choices: Danh sách lựa chọn
        default: Index mặc định (0-based)
        allow_custom: Cho phép nhập tùy chỉnh không trong list

    Returns:
        int/str: Index của lựa chọn (0-based) hoặc string tùy chỉnh
    """
    print(f"\n{prompt}:")
    for i, choice in enumerate(choices, 1):
        default_marker = " (mặc định)" if default is not None and i-1 == default else ""
        print(f"  {i}. {choice}{default_marker}")

    if allow_custom:
        print("  Hoặc nhập tùy chỉnh:")

    while True:
        try:
            user_input = input("\nChọn (nhập số hoặc giá trị): ").strip()

            # Nếu không nhập và có default
            if not user_input and default is not None:
                return default

            # Nếu là số
            if user_input.isdigit():
                choice_idx = int(user_input) - 1
                if 0 <= choice_idx < len(choices):
                    return choice_idx

            # Nếu allow_custom, trả về string
            if allow_custom and user_input:
                return user_input

            print(Colors.error("❌ Lựa chọn không hợp lệ!"))

        except KeyboardInterrupt:
            print()
            print(Colors.warning("❌ Đã hủy!"))
            return None


def get_path_input(
    prompt: str,
    default: Optional[str] = None,
    must_exist: bool = False,
    must_be_dir: bool = False,
    must_be_file: bool = False,
    create_if_not_exists: bool = False
) -> Optional[str]:
    """
    Nhận đường dẫn từ user với validation

    Args:
        prompt: Thông báo hiển thị
        default: Đường dẫn mặc định
        must_exist: Phải tồn tại
        must_be_dir: Phải là thư mục
        must_be_file: Phải là file
        create_if_not_exists: Tạo thư mục nếu không tồn tại

    Returns:
        str: Đường dẫn đã normalize
    """
    def validate_path(path_str: str) -> Union[bool, str]:
        if not path_str:
            return True  # Allow empty for defaults

        path = Path(path_str).expanduser().resolve()

        if must_exist and not path.exists():
            return f"Đường dẫn không tồn tại: {path_str}"

        if must_be_dir and path.exists() and not path.is_dir():
            return f"Phải là thư mục: {path_str}"

        if must_be_file and path.exists() and not path.is_file():
            return f"Phải là file: {path_str}"

        return True

    path_input = get_user_input(
        prompt,
        default=default,
        validator=validate_path if (must_exist or must_be_dir or must_be_file) else None
    )

    if path_input:
        path = Path(path_input).expanduser().resolve()
        if create_if_not_exists and not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(Colors.success(f"✅ Đã tạo thư mục: {path}"))
            except Exception as e:
                print(Colors.error(f"❌ Không thể tạo thư mục: {e}"))
                return None
        return str(path)

    return path_input


def get_numeric_input(
    prompt: str,
    default: Optional[Union[int, float]] = None,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    value_type: type = int
) -> Optional[Union[int, float]]:
    """
    Nhận số từ user với validation

    Args:
        prompt: Thông báo hiển thị
        default: Giá trị mặc định
        min_value: Giá trị tối thiểu
        max_value: Giá trị tối đa
        value_type: Kiểu số (int hoặc float)

    Returns:
        int/float: Số đã validate
    """
    def validate_number(num_str: str) -> Union[bool, str]:
        try:
            num = value_type(num_str)
            if min_value is not None and num < min_value:
                return f"Giá trị phải >= {min_value}"
            if max_value is not None and num > max_value:
                return f"Giá trị phải <= {max_value}"
            return True
        except ValueError:
            return f"Phải là số {value_type.__name__} hợp lệ"

    while True:
        input_str = get_user_input(prompt, default=str(default) if default is not None else None)
        if input_str is None:
            return None

        if input_str == "" and default is not None:
            return default

        validation = validate_number(input_str)
        if validation is True:
            return value_type(input_str)
        else:
            print(Colors.error(f"❌ {validation}"))


def get_boolean_input(prompt: str, default: bool = False) -> bool:
    """
    Nhận boolean từ user (y/n)

    Args:
        prompt: Thông báo hiển thị
        default: Giá trị mặc định

    Returns:
        bool: True/False
    """
    return confirm_action(prompt, default)


def display_menu(
    title: str,
    options: Dict[str, Dict],
    footer_message: Optional[str] = None,
    show_numbers: bool = True
) -> None:
    """
    Hiển thị menu với options

    Args:
        title: Tiêu đề menu
        options: Dict với key là số thứ tự, value là dict {'name': str, 'description': str}
        footer_message: Thông báo ở cuối menu
        show_numbers: Có hiển thị số thứ tự không
    """
    print_header(title)

    for key, option in options.items():
        name = option.get('name', '')
        description = option.get('description', '')

        if show_numbers:
            print(f"{key}. {Colors.bold(name)}")
        else:
            print(f"• {Colors.bold(name)}")

        if description:
            print(f"   {Colors.muted(description)}")
        print()

    if footer_message:
        print(Colors.muted(footer_message))
        print()


def select_from_menu(
    title: str,
    options: Dict[str, Dict],
    footer_message: Optional[str] = "Nhập số để chọn hoặc 'q' để thoát:",
    allow_quit: bool = True
) -> Optional[str]:
    """
    Hiển thị menu và nhận lựa chọn từ user

    Args:
        title: Tiêu đề menu
        options: Dict options như display_menu
        footer_message: Thông báo footer
        allow_quit: Cho phép nhập 'q' để thoát

    Returns:
        str: Key của option được chọn, hoặc None nếu thoát
    """
    while True:
        display_menu(title, options, footer_message)

        choice = get_user_input("Lựa chọn của bạn").strip().lower()

        if allow_quit and choice in ['q', 'quit', '0']:
            return None

        if choice in options:
            return choice

        print(Colors.error("❌ Lựa chọn không hợp lệ!"))
        print()


def get_multiple_choices(
    prompt: str,
    options: List[str],
    allow_all: bool = True,
    allow_none: bool = True
) -> List[int]:
    """
    Nhận nhiều lựa chọn từ danh sách

    Args:
        prompt: Thông báo hiển thị
        options: Danh sách options
        allow_all: Cho phép chọn "all"
        allow_none: Cho phép chọn "none"

    Returns:
        list: Danh sách index được chọn (0-based)
    """
    print(f"\n{prompt}")
    print("Nhập số cách nhau bởi dấu cách (vd: 1 2 3)")

    if allow_all:
        print("• Nhập 'all' để chọn tất cả")
    if allow_none:
        print("• Nhập 'none' để không chọn gì")

    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    while True:
        try:
            user_input = input("\nLựa chọn: ").strip().lower()

            if allow_all and user_input == 'all':
                return list(range(len(options)))

            if allow_none and user_input == 'none':
                return []

            # Parse numbers
            choices = []
            parts = user_input.split()

            for part in parts:
                if part.isdigit():
                    idx = int(part) - 1
                    if 0 <= idx < len(options) and idx not in choices:
                        choices.append(idx)
                elif part == 'q':
                    return []

            if choices:
                return sorted(choices)

            print(Colors.error("❌ Không có lựa chọn hợp lệ!"))

        except KeyboardInterrupt:
            print()
            print(Colors.warning("❌ Đã hủy!"))
            return []


def show_progress_info(current: int, total: int, message: str = "") -> None:
    """
    Hiển thị thông tin progress

    Args:
        current: Số lượng hiện tại
        total: Tổng số
        message: Thông báo bổ sung
    """
    percentage = (current / total * 100) if total > 0 else 0
    print(f"📊 {current}/{total} ({percentage:.1f}%) {message}")


def show_operation_summary(
    title: str,
    stats: Dict[str, Any],
    success_color: str = Colors.SUCCESS,
    error_color: str = Colors.ERROR
) -> None:
    """
    Hiển thị tóm tắt kết quả operation

    Args:
        title: Tiêu đề tóm tắt
        stats: Dict chứa các thống kê
        success_color: Màu cho success items
        error_color: Màu cho error items
    """
    print(f"\n{'='*60}")
    print(f"✅ {title.upper()}")
    print(f"{'='*60}")

    for key, value in stats.items():
        if isinstance(value, dict):
            # Nested stats (vd: {'count': 5, 'size': '10MB'})
            count = value.get('count', 0)
            extra = value.get('size', value.get('info', ''))
            if extra:
                print(f"   • {key}: {Colors.info(count)} ({extra})")
            else:
                print(f"   • {key}: {Colors.info(count)}")
        else:
            # Simple value
            print(f"   • {key}: {Colors.info(value)}")

    print(f"{'='*60}\n")
