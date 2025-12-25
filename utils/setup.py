#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module setup - Common setup patterns for tools

Mục đích: Tập trung các pattern khởi tạo và setup cho tools
Lý do: Giảm code duplication, đảm bảo tính nhất quán setup
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any


def setup_tool_paths(tool_file: str) -> Dict[str, Path]:
    """
    Setup common paths for a tool

    Args:
        tool_file: __file__ of the tool

    Returns:
        dict: Dictionary containing various paths
    """
    tool_path = Path(tool_file).resolve()
    tool_dir = tool_path.parent
    tool_name = tool_path.stem

    # Project root (DevTools directory)
    project_root = tool_dir.parent.parent

    # Utils directory
    utils_dir = project_root / "utils"

    # Tool-specific paths
    tool_info_file = tool_dir / "tool_info.json"
    doc_file = tool_dir / "doc.py"

    return {
        'tool_path': tool_path,
        'tool_dir': tool_dir,
        'tool_name': tool_name,
        'project_root': project_root,
        'utils_dir': utils_dir,
        'tool_info_file': tool_info_file,
        'doc_file': doc_file
    }


def setup_import_paths(tool_file: str) -> None:
    """
    Setup sys.path for importing utilities

    Args:
        tool_file: __file__ of the tool

    Giải thích:
        - Thêm utils vào sys.path
        - Thêm thư mục cha của tool vào sys.path (để import từ tools khác)
        - Đảm bảo imports hoạt động từ bất kỳ vị trí nào
    """
    tool_path = Path(tool_file).resolve()
    tool_dir = tool_path.parent
    project_root = tool_dir.parent.parent
    utils_dir = project_root / "utils"

    # Add utils directory to path
    if str(utils_dir) not in sys.path:
        sys.path.insert(0, str(utils_dir))

    # Add project root to path (for cross-tool imports)
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def setup_tool_logger(tool_name: str, log_to_console: bool = False) -> None:
    """
    Setup logger for a tool

    Args:
        tool_name: Name of the tool
        log_to_console: Whether to log to console

    Giải thích:
        - Tạo logger với tên tool
        - Log to file by default
        - Optional console logging
    """
    try:
        from .logger import setup_logger
        setup_logger(tool_name, log_to_console=log_to_console)
    except ImportError:
        # Fallback if logger not available
        pass


def check_dependencies(dependencies: Dict[str, Dict[str, Any]]) -> bool:
    """
    Check if required dependencies are available

    Args:
        dependencies: Dict of dependency_name -> config
            Config can include:
            - 'import_name': Name to import (default: dependency_name)
            - 'install_command': Command to install
            - 'display_name': Display name for messages

    Returns:
        bool: True if all dependencies available

    Ví dụ:
        check_dependencies({
            'PIL': {
                'import_name': 'PIL',
                'install_command': 'pip install Pillow',
                'display_name': 'Pillow (PIL)'
            }
        })
    """
    missing_deps = []

    for dep_name, config in dependencies.items():
        import_name = config.get('import_name', dep_name)
        display_name = config.get('display_name', dep_name)

        try:
            __import__(import_name)
        except ImportError:
            missing_deps.append((dep_name, config))

    if missing_deps:
        print("❌ Thiếu thư viện phụ thuộc:")
        for dep_name, config in missing_deps:
            display_name = config.get('display_name', dep_name)
            install_cmd = config.get('install_command', f'pip install {dep_name}')
            print(f"   • {display_name}: {install_cmd}")

        print("\n💡 Chạy các lệnh trên để cài đặt, sau đó restart tool.")
        return False

    return True


def install_missing_library(
    package_name: str,
    import_name: Optional[str] = None,
    install_command: Optional[str] = None,
    display_name: Optional[str] = None,
    auto_install: bool = True
) -> bool:
    """
    Install a missing library

    Args:
        package_name: Package name to install
        import_name: Name to import (default: package_name)
        install_command: Install command (default: pip install package_name)
        display_name: Display name (default: package_name)
        auto_install: Whether to auto-install or just show message

    Returns:
        bool: True if library available after operation
    """
    import_name = import_name or package_name
    display_name = display_name or package_name
    install_command = install_command or f'pip install {package_name}'

    # Check if already available
    try:
        __import__(import_name)
        return True
    except ImportError:
        pass

    if not auto_install:
        print(f"❌ Thiếu thư viện {display_name}")
        print(f"   Cài đặt: {install_command}")
        return False

    # Try auto-install
    try:
        from .validation import install_library
        return install_library(package_name, install_command, display_name)
    except ImportError:
        # Fallback to manual message
        print(f"❌ Thiếu thư viện {display_name}")
        print(f"   Cài đặt: {install_command}")
        return False


def setup_tool_environment(
    tool_file: str,
    tool_name: Optional[str] = None,
    dependencies: Optional[Dict[str, Dict[str, Any]]] = None,
    log_to_console: bool = False
) -> Dict[str, Any]:
    """
    Setup complete tool environment

    Args:
        tool_file: __file__ of the tool
        tool_name: Override tool name (auto-detected if None)
        dependencies: Dependencies to check
        log_to_console: Whether to log to console

    Returns:
        dict: Setup information and paths
    """
    # Setup paths
    paths = setup_tool_paths(tool_file)
    if tool_name:
        paths['tool_name'] = tool_name

    # Setup import paths
    setup_import_paths(tool_file)

    # Setup logger
    setup_tool_logger(paths['tool_name'], log_to_console)

    # Check dependencies
    deps_ok = True
    if dependencies:
        deps_ok = check_dependencies(dependencies)

    return {
        'paths': paths,
        'dependencies_ok': deps_ok,
        'tool_name': paths['tool_name']
    }


def create_tool_banner(tool_name: str, description: str = "", version: str = "") -> str:
    """
    Create a tool banner

    Args:
        tool_name: Name of the tool
        description: Tool description
        version: Tool version

    Returns:
        str: Formatted banner
    """
    from .format import print_header

    # This would create a banner string, but since print_header prints directly,
    # this is more of a helper for consistent banner creation
    banner_lines = []

    if version:
        banner_lines.append(f"{tool_name} v{version}")
    else:
        banner_lines.append(tool_name.upper())

    if description:
        banner_lines.append(description)

    return "\n".join(banner_lines)


def handle_tool_error(error: Exception, tool_name: str, context: str = "") -> int:
    """
    Handle tool execution errors consistently

    Args:
        error: The exception that occurred
        tool_name: Tool name
        context: Additional context

    Returns:
        int: Exit code
    """
    from .colors import Colors

    print(Colors.error(f"❌ Lỗi trong {tool_name}: {error}"))

    if context:
        print(Colors.muted(f"   Context: {context}"))

    # Log error
    try:
        from .logger import log_error
        log_error(f"Tool error in {tool_name}: {error}", exc_info=True)
    except ImportError:
        pass

    return 1


def cleanup_temp_files(temp_dir: Optional[str] = None) -> None:
    """
    Cleanup temporary files created during tool execution

    Args:
        temp_dir: Temporary directory to clean (default: auto-detect)
    """
    import shutil

    if temp_dir is None:
        # Try to find common temp directories
        temp_dirs = [
            Path.cwd() / "temp",
            Path.cwd() / ".temp",
            Path.cwd() / "__temp__"
        ]

        for temp_path in temp_dirs:
            if temp_path.exists() and temp_path.is_dir():
                temp_dir = str(temp_path)
                break

    if temp_dir and Path(temp_dir).exists():
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass  # Ignore cleanup errors


def get_tool_config(tool_name: str) -> Dict[str, Any]:
    """
    Get tool configuration from tool_info.json

    Args:
        tool_name: Tool name

    Returns:
        dict: Tool configuration
    """
    try:
        paths = setup_tool_paths(__file__)  # This is a bit hacky, but works
        tool_info_file = paths.get('project_root') / 'tools' / 'py' / tool_name / 'tool_info.json'

        if tool_info_file.exists():
            import json
            with open(tool_info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass

    return {}


def validate_tool_environment() -> Dict[str, Any]:
    """
    Validate the tool execution environment

    Returns:
        dict: Environment validation results
    """
    issues = []

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 7):
        issues.append({
            'level': 'error',
            'message': f'Python {python_version.major}.{python_version.minor} detected. Minimum required: 3.7'
        })

    # Check if running from correct directory
    cwd = Path.cwd()
    if not (cwd / 'utils').exists():
        issues.append({
            'level': 'warning',
            'message': 'Not running from DevTools root directory. Some features may not work.'
        })

    # Check write permissions
    try:
        test_file = cwd / '.test_write'
        test_file.write_text('test')
        test_file.unlink()
    except Exception:
        issues.append({
            'level': 'error',
            'message': 'No write permissions in current directory'
        })

    return {
        'valid': len([i for i in issues if i['level'] == 'error']) == 0,
        'issues': issues
    }
