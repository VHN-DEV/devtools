#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create new tools using refactored patterns

This demonstrates how the new tool base classes and patterns
can be used to create tools more efficiently.
"""

import os
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import ToolTemplate


def create_example_tool():
    """Create an example tool using the new patterns"""

    # Example: Create a simple text processing tool
    tool_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Text Processor - Xử lý văn bản hàng loạt

Mục đích: Xử lý văn bản, tìm kiếm, thay thế, thống kê
Lý do: Công cụ tiện ích cho việc xử lý văn bản
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any
from utils import (
    BaseTool, InteractiveToolMixin, CLIToolMixin, FileProcessingToolMixin,
    print_header, confirm_action
)


class TextProcessorTool(BaseTool, InteractiveToolMixin, CLIToolMixin, FileProcessingToolMixin):
    """
    Text Processor tool implementation
    """

    def get_description(self) -> str:
        """Get tool description"""
        return "Xử lý văn bản hàng loạt - tìm kiếm, thay thế, thống kê"

    def run_interactive(self) -> int:
        """
        Run tool in interactive mode

        Returns:
            int: Exit code
        """
        print_header("TEXT PROCESSOR")

        # Menu options
        menu_options = {
            "1": "Tìm kiếm văn bản trong file",
            "2": "Thay thế văn bản",
            "3": "Thống kê từ khóa",
            "4": "Xử lý hàng loạt file text",
            "q": "Quit"
        }

        while True:
            choice = self.create_main_menu("Chọn chức năng:", menu_options)

            if choice == "q" or choice is None:
                break

            if choice == "1":
                self._search_text()
            elif choice == "2":
                self._replace_text()
            elif choice == "3":
                self._count_keywords()
            elif choice == "4":
                self._batch_process_text()

        return 0

    def _search_text(self):
        """Search for text in files"""
        print("\n🔍 TÌM KIẾM VĂN BẢN")

        # Get inputs
        search_dir = self.get_user_path("Thư mục cần tìm:")
        if not search_dir:
            return

        search_pattern = input("Nhập từ khóa cần tìm: ").strip()
        if not search_pattern:
            return

        # Setup processor for text files
        processor = self.setup_batch_processor(
            input_path=search_dir,
            file_extensions=['.txt', '.md', '.py', '.js', '.html', '.css']
        )

        # Custom processing for search
        results = []
        for file_path in processor.discover_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                matches = len(re.findall(re.escape(search_pattern), content, re.IGNORECASE))
                if matches > 0:
                    results.append({
                        'file': file_path,
                        'matches': matches,
                        'success': True,
                        'message': f"Tìm thấy {matches} kết quả"
                    })
            except Exception as e:
                results.append({
                    'file': file_path,
                    'success': False,
                    'error': str(e)
                })

        # Display results
        if results:
            print(f"\n📊 KẾT QUẢ TÌM KIẾM '{search_pattern}':")
            for result in results:
                if result.get('success'):
                    print(f"✅ {result['file']}: {result['message']}")
                else:
                    print(f"❌ {result['file']}: {result.get('error', 'Lỗi')}")
        else:
            print("❌ Không tìm thấy kết quả nào.")

    def _replace_text(self):
        """Replace text in files"""
        print("\n🔄 THAY THẾ VĂN BẢN")

        # Get inputs
        file_path = self.get_user_path("File cần xử lý:")
        if not file_path or not os.path.isfile(file_path):
            print("❌ File không tồn tại!")
            return

        old_text = input("Nhập text cần thay thế: ").strip()
        new_text = input("Nhập text thay thế: ").strip()

        if not old_text:
            return

        # Confirm
        if not self.get_user_confirmation(f"Thay thế '{old_text}' thành '{new_text}'?"):
            return

        # Process
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            new_content = content.replace(old_text, new_text)
            replacements = content.count(old_text)

            if replacements > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Đã thay thế {replacements} lần trong {file_path}")
            else:
                print("❌ Không tìm thấy text cần thay thế.")

        except Exception as e:
            print(f"❌ Lỗi: {e}")

    def _count_keywords(self):
        """Count keyword occurrences"""
        print("\n📊 THỐNG KÊ TỪ KHÓA")

        # Get inputs
        search_dir = self.get_user_path("Thư mục cần thống kê:")
        if not search_dir:
            return

        keywords = input("Nhập các từ khóa (cách nhau bởi dấu phẩy): ").strip()
        if not keywords:
            return

        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]

        # Setup processor
        processor = self.setup_batch_processor(
            input_path=search_dir,
            file_extensions=['.txt', '.md', '.py', '.js', '.html', '.css']
        )

        # Process files
        total_stats = {kw: 0 for kw in keyword_list}

        for file_path in processor.discover_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for keyword in keyword_list:
                    count = len(re.findall(re.escape(keyword), content, re.IGNORECASE))
                    total_stats[keyword] += count

            except Exception:
                continue

        # Display results
        print(f"\n📊 THỐNG KÊ TỪ KHÓA:")
        for keyword, count in total_stats.items():
            print(f"   '{keyword}': {count} lần")

    def _batch_process_text(self):
        """Batch process text files"""
        print("\n📝 XỬ LÝ HÀNG LOẠT FILE TEXT")

        # This would use the FileProcessingToolMixin patterns
        print("Tính năng này đang được phát triển...")

    def setup_cli_parser(self, parser):
        """
        Setup CLI argument parser

        Args:
            parser: Argument parser to configure
        """
        self.add_common_args(parser)

        parser.add_argument(
            '--search',
            help='Tìm kiếm text trong file'
        )

        parser.add_argument(
            '--replace',
            nargs=2,
            metavar=('OLD', 'NEW'),
            help='Thay thế text (old new)'
        )

    def run_cli(self, args):
        """
        Run tool in CLI mode

        Args:
            args: Parsed CLI arguments

        Returns:
            int: Exit code
        """
        # Validate arguments
        if not self.validate_cli_inputs(args):
            return 1

        # CLI logic here
        if args.search:
            print(f"Tìm kiếm: {args.search}")
        elif args.replace:
            old_text, new_text = args.replace
            print(f"Thay thế: '{old_text}' -> '{new_text}'")

        return 0


def main():
    """Main entry point"""
    tool = TextProcessorTool(__file__)
    return tool.run()


if __name__ == "__main__":
    exit(main())
'''

    # Write to file
    output_path = Path("tools/py/text-processor/text-processor.py")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tool_code)

    print(f"✅ Đã tạo tool: {output_path}")
    print("💡 Tool này sử dụng các pattern mới và base classes!")


if __name__ == "__main__":
    create_example_tool()
