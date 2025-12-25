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

from .interactive import (
    get_enhanced_user_input,
    get_user_choice,
    get_path_input,
    get_numeric_input,
    get_boolean_input,
    display_menu,
    select_from_menu,
    get_multiple_choices,
    show_progress_info,
    show_operation_summary
)

from .cli import (
    CommonArgs,
    create_tool_parser,
    create_default_examples,
    validate_cli_args,
    setup_tool_cli,
    print_cli_usage_examples,
    handle_cli_error,
    create_progress_callback
)

from .processing import (
    BatchProcessor,
    create_file_filter,
    process_files_with_callback,
    collect_processing_results,
    display_batch_results
)

from .setup import (
    setup_tool_paths,
    setup_import_paths,
    setup_tool_logger,
    check_dependencies,
    install_missing_library,
    setup_tool_environment,
    create_tool_banner,
    handle_tool_error,
    cleanup_temp_files,
    get_tool_config,
    validate_tool_environment
)

from .bash import (
    BashExecutor,
    find_bash_executable,
    is_git_bash_available,
    convert_windows_path_to_unix,
    run_bash_script,
    run_bash_command,
    check_bash_environment,
    print_bash_diagnostics
)

from .tool_base import (
    BaseTool,
    ToolMode,
    InteractiveToolMixin,
    CLIToolMixin,
    FileProcessingToolMixin,
    ImageProcessingToolMixin,
    CompressionToolMixin,
    ToolTemplate
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

    # Interactive UI functions
    'get_enhanced_user_input',
    'get_user_choice',
    'get_path_input',
    'get_numeric_input',
    'get_boolean_input',
    'display_menu',
    'select_from_menu',
    'get_multiple_choices',
    'show_progress_info',
    'show_operation_summary',

    # CLI functions
    'CommonArgs',
    'create_tool_parser',
    'create_default_examples',
    'validate_cli_args',
    'setup_tool_cli',
    'print_cli_usage_examples',
    'handle_cli_error',
    'create_progress_callback',

    # File processing functions
    'BatchProcessor',
    'create_file_filter',
    'process_files_with_callback',
    'collect_processing_results',
    'display_batch_results',

    # Setup functions
    'setup_tool_paths',
    'setup_import_paths',
    'setup_tool_logger',
    'check_dependencies',
    'install_missing_library',
    'setup_tool_environment',
    'create_tool_banner',
    'handle_tool_error',
    'cleanup_temp_files',
    'get_tool_config',
    'validate_tool_environment',

    # Bash execution functions
    'BashExecutor',
    'find_bash_executable',
    'is_git_bash_available',
    'convert_windows_path_to_unix',
    'run_bash_script',
    'run_bash_command',
    'check_bash_environment',
    'print_bash_diagnostics',

    # Tool base classes
    'BaseTool',
    'ToolMode',
    'InteractiveToolMixin',
    'CLIToolMixin',
    'FileProcessingToolMixin',
    'ImageProcessingToolMixin',
    'CompressionToolMixin',
    'ToolTemplate',

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

