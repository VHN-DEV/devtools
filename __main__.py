#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__main__.py - Entry point cho DevTools

Mục đích: Cho phép chạy tool bằng lệnh "python ." hoặc "python DevTools/"

Cách dùng:
    python .                # Từ trong thư mục
    python DevTools         # Từ bên ngoài
"""

import sys
import os

# Fix Windows console encoding - Improved
if sys.platform == 'win32':
    try:
        # Thiết lập UTF-8 cho console (output và input)
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        sys.stdin.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        # Fallback: sử dụng wrapper
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

# Đảm bảo thư mục hiện tại trong sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import và chạy menu
if __name__ == "__main__":
    try:
        # Import menu module từ menus package
        from menus import main
        
        # Chạy menu
        main()
    
    except EOFError:
        # Xử lý EOF error (input stream bị đóng)
        try:
            print("\n\nInput stream đã đóng. Thoát chương trình...")
        except Exception:
            pass
        sys.exit(0)
    
    except KeyboardInterrupt:
        # Xử lý Ctrl+C
        try:
            print("\n\nTạm biệt!")
        except Exception:
            pass
        sys.exit(0)
    
    except Exception as e:
        # Xử lý các lỗi khác với encoding safety
        try:
            print(f"\nLỗi: {e}")
            import traceback
            traceback.print_exc()
        except UnicodeEncodeError:
            # Nếu không in được emoji, dùng ASCII
            print(f"\nLỗi: {str(e)}")
            import traceback
            traceback.print_exc()
        sys.exit(1)

