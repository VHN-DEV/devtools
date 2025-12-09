#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module logger - Logging cho các tools

Mục đích: Ghi lại các thao tác và lỗi để debug
Lý do: Dễ theo dõi và khắc phục sự cố
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


# Global logger instance
_logger: Optional[logging.Logger] = None


def _get_project_root():
    """
    Tìm project root dựa trên vị trí file hiện tại
    
    Returns:
        Path: Đường dẫn đến project root
    """
    from pathlib import Path
    
    # Lấy đường dẫn của file logger.py
    # __file__ trong module này sẽ là đường dẫn đến utils/logger.py
    # Project root sẽ là parent của thư mục utils
    try:
        current_file = Path(__file__).resolve()
        # current_file sẽ là: .../devtools/utils/logger.py
        # Project root sẽ là: .../devtools/
        project_root = current_file.parent.parent
        
        # Kiểm tra xem có phải project root không (có file __main__.py hoặc pyproject.toml)
        if (project_root / '__main__.py').exists() or (project_root / 'pyproject.toml').exists():
            return project_root
    except Exception:
        pass
    
    # Fallback: tìm từ working directory
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / '__main__.py').exists() or (parent / 'pyproject.toml').exists():
            return parent
    
    # Nếu không tìm thấy, dùng thư mục hiện tại
    return current


def setup_logger(name: str = 'DevTools', 
                 log_dir: str = 'logs',
                 log_to_file: bool = True,
                 log_to_console: bool = True,
                 level: int = logging.INFO) -> logging.Logger:
    """
    Thiết lập logger cho tool
    
    Args:
        name: Tên logger
        log_dir: Thư mục chứa log files
        log_to_file: Có ghi log ra file không
        log_to_console: Có hiển thị log trên console không
        level: Mức độ logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logging.Logger: Logger instance
    
    Giải thích:
    - Tạo logger với config linh hoạt
    - Hỗ trợ ghi cả file và console
    - Tự động tạo thư mục logs nếu chưa có
    - Format log message rõ ràng, dễ đọc
    """
    global _logger
    
    # Nếu logger đã tồn tại, trả về luôn
    if _logger is not None:
        return _logger
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Xóa handlers cũ nếu có
    logger.handlers.clear()
    
    # Format log message
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        # Tạo thư mục logs
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Tên file log với timestamp
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(log_dir, f'{name}_{timestamp}.log')
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """
    Lấy logger instance hiện tại
    
    Returns:
        logging.Logger: Logger instance
    
    Giải thích:
    - Nếu logger chưa được setup, tự động setup với config mặc định
    - Đảm bảo luôn có logger để sử dụng
    """
    global _logger
    
    if _logger is None:
        _logger = setup_logger()
    
    return _logger


def log_info(message: str) -> None:
    """
    Ghi log thông tin
    
    Args:
        message: Thông báo cần log
    
    Mục đích: Wrapper ngắn gọn cho logger.info()
    """
    logger = get_logger()
    logger.info(message)


def log_error(message: str, exc_info: bool = False) -> None:
    """
    Ghi log lỗi
    
    Args:
        message: Thông báo lỗi
        exc_info: Có ghi exception traceback không
    
    Mục đích: Wrapper ngắn gọn cho logger.error()
    """
    logger = get_logger()
    logger.error(message, exc_info=exc_info)


def log_warning(message: str) -> None:
    """
    Ghi log cảnh báo
    
    Args:
        message: Thông báo cảnh báo
    
    Mục đích: Wrapper ngắn gọn cho logger.warning()
    """
    logger = get_logger()
    logger.warning(message)


def log_debug(message: str) -> None:
    """
    Ghi log debug
    
    Args:
        message: Thông báo debug
    
    Mục đích: Wrapper ngắn gọn cho logger.debug()
    """
    logger = get_logger()
    logger.debug(message)


def log_success(message: str) -> None:
    """
    Ghi log thành công
    
    Args:
        message: Thông báo thành công
    
    Giải thích:
    - Custom log level cho thông báo thành công
    - Dùng INFO level nhưng có prefix đặc biệt
    """
    logger = get_logger()
    logger.info(f"✅ {message}")


def log_operation(operation: str, details: str = '') -> None:
    """
    Ghi log thao tác
    
    Args:
        operation: Tên thao tác
        details: Chi tiết thao tác
    
    Mục đích: Theo dõi các thao tác người dùng thực hiện
    """
    logger = get_logger()
    if details:
        logger.info(f"🔧 {operation} - {details}")
    else:
        logger.info(f"🔧 {operation}")


def log_error_to_file(error: Exception, tool_name: str = "", context: str = "", log_dir: str = 'logs') -> str:
    """
    Ghi lỗi ra file với format log-ngày-giờ
    
    Args:
        error: Exception object hoặc error message
        tool_name: Tên tool gây lỗi
        context: Thông tin bổ sung về context
        log_dir: Thư mục chứa log files
    
    Returns:
        str: Đường dẫn đến file log đã tạo
    
    Giải thích:
    - Tạo file log với format: log-YYYY-MM-DD-HH-MM-SS.txt
    - Ghi lại thông tin chi tiết về lỗi, bao gồm traceback
    - Tự động tạo thư mục logs nếu chưa có
    """
    import traceback
    from pathlib import Path
    
    # Nếu log_dir là đường dẫn tương đối, tìm project root và tạo đường dẫn tuyệt đối
    log_path = Path(log_dir)
    
    # Nếu không phải đường dẫn tuyệt đối, tìm project root
    if not log_path.is_absolute():
        project_root = _get_project_root()
        log_path = project_root / log_dir
    
    # Tạo thư mục logs nếu chưa có
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Tạo tên file với format: log-ngày-giờ
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    log_file = log_path / f"log-{timestamp}.log"
    
    # Chuẩn bị nội dung log
    lines = []
    lines.append("=" * 80)
    lines.append(f"ERROR LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")
    
    if tool_name:
        lines.append(f"Tool: {tool_name}")
        lines.append("")
    
    if context:
        lines.append(f"Context: {context}")
        lines.append("")
    
    lines.append(f"Error Type: {type(error).__name__}")
    lines.append(f"Error Message: {str(error)}")
    lines.append("")
    lines.append("Traceback:")
    lines.append("-" * 80)
    
    # Lấy traceback
    if isinstance(error, Exception):
        tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
        lines.extend(tb_lines)
    else:
        lines.append(str(error))
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("")
    
    # Ghi vào file
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return str(log_file)
    except Exception as e:
        # Nếu không ghi được file, in ra console
        print(f"⚠️  Không thể ghi log file: {e}")
        return ""


def clear_logs(log_dir: str = 'logs', pattern: str = "log-*.log") -> int:
    """
    Xóa các file log
    
    Args:
        log_dir: Thư mục chứa log files
        pattern: Pattern để tìm file log (mặc định: log-*.txt)
    
    Returns:
        int: Số lượng file đã xóa
    
    Giải thích:
    - Xóa tất cả file log khớp với pattern
    - Hỗ trợ cả pattern đơn giản (log-*.txt)
    """
    from pathlib import Path
    import glob
    
    # Nếu log_dir là đường dẫn tương đối, tìm project root và tạo đường dẫn tuyệt đối
    log_path = Path(log_dir)
    
    # Nếu không phải đường dẫn tuyệt đối, tìm project root
    if not log_path.is_absolute():
        project_root = _get_project_root()
        log_path = project_root / log_dir
    
    if not log_path.exists():
        return 0
    
    # Đếm số file trước khi xóa
    deleted_count = 0
    
    try:
        # Tìm tất cả file log khớp với pattern (ưu tiên .log, nhưng cũng tìm .txt để tương thích)
        log_files = list(log_path.glob(pattern))
        # Cũng tìm file .txt cũ để tương thích
        if pattern == "log-*.log":
            log_files.extend(log_path.glob("log-*.txt"))
        
        # Loại bỏ duplicate
        log_files = list(set(log_files))
        
        for log_file in log_files:
            try:
                log_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"⚠️  Không thể xóa file {log_file}: {e}")
        
        return deleted_count
    except Exception as e:
        print(f"⚠️  Lỗi khi xóa log files: {e}")
        return 0


def get_log_files(log_dir: str = 'logs', pattern: str = "log-*.log") -> list:
    """
    Lấy danh sách các file log
    
    Args:
        log_dir: Thư mục chứa log files
        pattern: Pattern để tìm file log (mặc định: log-*.txt)
    
    Returns:
        list: Danh sách đường dẫn đến các file log (sorted by modification time, newest first)
    """
    from pathlib import Path
    import os
    
    # Nếu log_dir là đường dẫn tương đối, tìm project root và tạo đường dẫn tuyệt đối
    log_path = Path(log_dir)
    
    # Nếu không phải đường dẫn tuyệt đối, tìm project root
    if not log_path.is_absolute():
        project_root = _get_project_root()
        log_path = project_root / log_dir
    
    if not log_path.exists():
        return []
    
    try:
        # Tìm tất cả file log khớp với pattern (ưu tiên .log, nhưng cũng tìm .txt để tương thích)
        log_files = list(log_path.glob(pattern))
        # Cũng tìm file .txt cũ để tương thích
        if pattern == "log-*.log":
            log_files.extend(log_path.glob("log-*.txt"))
        
        # Loại bỏ duplicate và sắp xếp theo thời gian sửa đổi (mới nhất trước)
        log_files = list(set(log_files))  # Remove duplicates
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return [str(f) for f in log_files]
    except Exception as e:
        print(f"⚠️  Lỗi khi lấy danh sách log files: {e}")
        return []