#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package utils - Các hàm tiện ích dùng chung cho tất cả tools

Mục đích: Tránh code lặp lại, dễ maintain và mở rộng

Cấu trúc:
- format.py: Format và hiển thị
- validation.py: Validation và xử lý input
- file_ops.py: Thao tác file/folder
- progress.py: Progress bar
- logger.py: Logging system
"""

# Import từ các module mới
from .format import (
    format_size,
    print_header,
    print_separator,
    pluralize
)

from .validation import (
    get_user_input,
    normalize_path,
    confirm_action,
    validate_path,
    parse_size_string,
    install_library
)

from .file_ops import (
    get_file_list,
    get_folder_size,
    safe_delete,
    ensure_directory_exists,
    create_backup_name,
    get_available_space
)

from .progress import (
    ProgressBar,
    Spinner,
    simple_progress
)

from .logger import (
    setup_logger,
    get_logger,
    log_info,
    log_error,
    log_warning,
    log_debug,
    log_success,
    log_operation
)

from .ui import (
    print_success_box,
    print_error_box,
    print_warning_box,
    print_info_box,
    print_table,
    print_steps
)

# Backward compatibility: Import từ common nếu ai đó vẫn import trực tiếp
# from .common import *  # DEPRECATED - sẽ xóa trong tương lai

__all__ = [
    # Format functions
    'format_size',
    'print_header',
    'print_separator',
    'pluralize',
    
    # Validation functions
    'get_user_input',
    'normalize_path',
    'confirm_action',
    'validate_path',
    'parse_size_string',
    'install_library',
    
    # File operations
    'get_file_list',
    'get_folder_size',
    'safe_delete',
    'ensure_directory_exists',
    'create_backup_name',
    'get_available_space',
    
    # Progress
    'ProgressBar',
    'Spinner',
    'simple_progress',
    
    # Logger
    'setup_logger',
    'get_logger',
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_success',
    'log_operation',
    
    # UI components
    'print_success_box',
    'print_error_box',
    'print_warning_box',
    'print_info_box',
    'print_table',
    'print_steps'
]

