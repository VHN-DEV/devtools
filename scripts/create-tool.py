#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tạo tool mới nhanh chóng

Cách dùng:
    python scripts/create-tool.py
    hoặc
    python -m scripts.create-tool
"""

import os
import sys
import json
from pathlib import Path


def normalize_tool_name(name: str) -> str:
    """
    Chuẩn hóa tên tool (chuyển về dạng kebab-case)
    
    Ví dụ:
        "My Awesome Tool" -> "my-awesome-tool"
        "my_awesome_tool" -> "my-awesome-tool"
        "MyAwesomeTool" -> "my-awesome-tool"
    """
    import re
    
    # Thay thế spaces và underscores bằng hyphens
    name = re.sub(r'[\s_]+', '-', name)
    
    # Chuyển về lowercase
    name = name.lower()
    
    # Xóa các ký tự không hợp lệ (chỉ giữ alphanumeric và hyphens)
    name = re.sub(r'[^a-z0-9\-]', '', name)
    
    # Xóa hyphens ở đầu/cuối và nhiều hyphens liên tiếp
    name = re.sub(r'^-+|-+$', '', name)
    name = re.sub(r'-+', '-', name)
    
    return name or "new-tool"


def create_python_tool(tool_name: str, tool_dir: Path, display_name: str, description: str):
    """Tạo tool Python"""
    
    # Tạo thư mục
    tool_dir.mkdir(parents=True, exist_ok=True)
    
    # Template __init__.py
    init_content = f'''"""
Tool: {tool_name}
"""

'''
    
    # Template tool.py
    tool_file = tool_dir / f"{tool_name}.py"
    tool_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: {display_name}

Mục đích: {description}
"""

import os
import sys
from pathlib import Path

# Thêm thư mục cha vào sys.path để import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import (
    print_header, get_user_input, confirm_action,
    ensure_directory_exists, log_info, log_error, normalize_path
)
from utils.colors import Colors


def main():
    """Hàm chính"""
    print_header("TOOL {display_name.upper()}", width=70)
    print(Colors.primary(f"  {display_name}"))
    print()
    
    # TODO: Thêm logic của tool ở đây
    
    print()
    print(Colors.success("✅ Tool đã chạy xong!"))
    print()


def main_cli():
    """Chế độ CLI (nếu cần)"""
    import argparse
    
    parser = argparse.ArgumentParser(description=f'{display_name}')
    # TODO: Thêm arguments nếu cần
    
    args = parser.parse_args()
    main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Colors.warning("\\n⚠️  Đã hủy bởi người dùng!"))
        sys.exit(130)
    except Exception as e:
        log_error(f"❌ Lỗi không mong muốn: {{e}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
'''
    
    # Template tool_info.json
    tool_info_content = {
        "name": display_name,
        "tags": tool_name.split("-") + [tool_name]
    }
    
    # Template doc.py
    doc_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hướng dẫn sử dụng: {display_name}
"""

def get_help():
    """
    Trả về hướng dẫn sử dụng tool
    
    Returns:
        str: Nội dung hướng dẫn
    """
    return """
══════════════════════════════════════════════════════════════════════
  📖 HƯỚNG DẪN SỬ DỤNG: {display_name}
══════════════════════════════════════════════════════════════════════

📝 MÔ TẢ:
  {description}

🚀 CÁCH SỬ DỤNG:
  1. Chọn tool từ menu chính
  2. [TODO: Thêm hướng dẫn sử dụng]

💡 VÍ DỤ:
  [TODO: Thêm ví dụ sử dụng]

📌 LƯU Ý:
  [TODO: Thêm lưu ý nếu có]

══════════════════════════════════════════════════════════════════════
"""
'''
    
    # Ghi các file
    print(f"📁 Đang tạo thư mục: {tool_dir}")
    
    # __init__.py
    init_file = tool_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text(init_content, encoding='utf-8')
        print(f"✅ Đã tạo: {init_file}")
    else:
        print(f"⚠️  File đã tồn tại: {init_file}")
    
    # tool.py
    if not tool_file.exists():
        tool_file.write_text(tool_content, encoding='utf-8')
        print(f"✅ Đã tạo: {tool_file}")
    else:
        print(f"⚠️  File đã tồn tại: {tool_file}")
        overwrite = input(f"   Bạn có muốn ghi đè không? (y/N): ").strip().lower()
        if overwrite == 'y':
            tool_file.write_text(tool_content, encoding='utf-8')
            print(f"✅ Đã cập nhật: {tool_file}")
    
    # tool_info.json
    tool_info_file = tool_dir / "tool_info.json"
    if not tool_info_file.exists():
        tool_info_file.write_text(json.dumps(tool_info_content, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"✅ Đã tạo: {tool_info_file}")
    else:
        print(f"⚠️  File đã tồn tại: {tool_info_file}")
    
    # doc.py (hỏi trước)
    doc_file = tool_dir / "doc.py"
    if not doc_file.exists():
        create_doc = input(f"\n📖 Có muốn tạo file doc.py (hướng dẫn sử dụng) không? (Y/n): ").strip().lower()
        if create_doc != 'n':
            doc_file.write_text(doc_content, encoding='utf-8')
            print(f"✅ Đã tạo: {doc_file}")
    else:
        print(f"⚠️  File đã tồn tại: {doc_file}")
    
    return tool_dir


def main():
    """Hàm chính tạo tool"""
    print("=" * 70)
    print("  🛠️  TẠO TOOL MỚI")
    print("=" * 70)
    print()
    
    # Xác định project root
    script_path = Path(__file__).resolve()
    if script_path.name == "create-tool.py":
        # Chạy trực tiếp: scripts/create-tool.py
        project_root = script_path.parent.parent
    else:
        # Chạy như module: python -m scripts.create_tool
        project_root = script_path.parent.parent
    
    tools_py_dir = project_root / "tools" / "py"
    tools_sh_dir = project_root / "tools" / "sh"
    
    # Nhập thông tin tool
    print("Nhập thông tin tool mới:")
    print()
    
    tool_name_input = input("Tên tool (vd: my-awesome-tool hoặc My Awesome Tool): ").strip()
    if not tool_name_input:
        print("❌ Tên tool không được để trống!")
        return
    
    tool_name = normalize_tool_name(tool_name_input)
    
    # Kiểm tra tool đã tồn tại chưa
    if (tools_py_dir / tool_name).exists() or (tools_sh_dir / tool_name).exists():
        print(f"❌ Tool '{tool_name}' đã tồn tại!")
        return
    
    display_name = input(f"Tên hiển thị (mặc định: {tool_name.replace('-', ' ').title()}): ").strip()
    if not display_name:
        display_name = tool_name.replace('-', ' ').title()
    
    description = input("Mô tả ngắn gọn về tool: ").strip()
    if not description:
        description = f"Tool {display_name}"
    
    # Chọn loại tool
    print()
    print("Chọn loại tool:")
    print("  1. Python tool (tools/py/)")
    print("  2. Shell script tool (tools/sh/)")
    tool_type = input("Chọn (1 hoặc 2, mặc định: 1): ").strip() or "1"
    
    if tool_type == "1":
        tool_dir = tools_py_dir / tool_name
        tool_type_name = "Python"
    elif tool_type == "2":
        tool_dir = tools_sh_dir / tool_name
        tool_type_name = "Shell"
    else:
        print("❌ Lựa chọn không hợp lệ!")
        return
    
    print()
    print(f"📋 Thông tin tool:")
    print(f"   Tên: {tool_name}")
    print(f"   Tên hiển thị: {display_name}")
    print(f"   Mô tả: {description}")
    print(f"   Loại: {tool_type_name}")
    print(f"   Thư mục: {tool_dir}")
    print()
    
    confirm = input("Tạo tool? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("❌ Đã hủy!")
        return
    
    print()
    try:
        create_python_tool(tool_name, tool_dir, display_name, description)
        
        print()
        print("=" * 70)
        print(f"✅ Đã tạo tool '{tool_name}' thành công!")
        print("=" * 70)
        print()
        print(f"📁 Thư mục: {tool_dir}")
        print(f"📄 File chính: {tool_dir / f'{tool_name}.py'}")
        print()
        print("💡 Tiếp theo:")
        print(f"   1. Mở file {tool_name}.py và thêm logic của tool")
        print(f"   2. (Optional) Cập nhật tool_info.json với tags phù hợp")
        print(f"   3. (Optional) Hoàn thiện doc.py với hướng dẫn chi tiết")
        print(f"   4. Chạy lại chương trình để tool xuất hiện trong menu")
        print()
        
    except Exception as e:
        print(f"❌ Lỗi khi tạo tool: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

