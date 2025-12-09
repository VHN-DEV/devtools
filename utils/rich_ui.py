#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module rich_ui - Rich TUI components cho DevTools

Mục đích: Sử dụng Rich library để tạo UI đẹp hơn với tables, panels, progress bars
Lý do: Cải thiện UX với components hiện đại và đẹp mắt
"""

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.text import Text
    from rich.layout import Layout
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.prompt import Prompt, Confirm
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback nếu không có Rich
    Console = None
    Table = None
    Panel = None
    Progress = None


class RichUI:
    """Wrapper class cho Rich UI components"""
    
    def __init__(self, use_rich: bool = True):
        """
        Khởi tạo RichUI
        
        Args:
            use_rich: Có sử dụng Rich không (False = fallback về console thường)
        """
        self.use_rich = use_rich and RICH_AVAILABLE
        if self.use_rich:
            self.console = Console()
        else:
            self.console = None
    
    def print_table(self, title: str, headers: list, rows: list, show_header: bool = True):
        """
        In bảng với Rich Table
        
        Args:
            title: Tiêu đề bảng
            headers: Danh sách header columns
            rows: Danh sách rows (mỗi row là list)
            show_header: Có hiển thị header không
        """
        if not self.use_rich:
            # Fallback: in bảng đơn giản
            print(f"\n{title}")
            print("=" * 80)
            if show_header:
                print(" | ".join(headers))
                print("-" * 80)
            for row in rows:
                print(" | ".join(str(cell) for cell in row))
            print()
            return
        
        table = Table(title=title, show_header=show_header, header_style="bold magenta")
        
        # Thêm columns
        for header in headers:
            table.add_column(header, style="cyan")
        
        # Thêm rows
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        
        self.console.print(table)
    
    def print_panel(self, content: str, title: str = "", style: str = "blue", border_style: str = "blue"):
        """
        In panel với Rich Panel
        
        Args:
            content: Nội dung panel
            title: Tiêu đề panel
            style: Style cho content
            border_style: Style cho border
        """
        if not self.use_rich:
            # Fallback: in với border đơn giản
            print()
            if title:
                print(f"╔═ {title} {'═' * (76 - len(title))}╗")
            else:
                print("╔" + "═" * 78 + "╗")
            for line in content.split('\n'):
                print(f"║ {line:<77}║")
            print("╚" + "═" * 78 + "╝")
            print()
            return
        
        panel = Panel(
            content,
            title=title,
            style=style,
            border_style=border_style
        )
        self.console.print(panel)
    
    def print_success(self, message: str):
        """In thông báo success"""
        if self.use_rich:
            self.print_panel(f"✅ {message}", style="green", border_style="green")
        else:
            print(f"✅ {message}")
    
    def print_error(self, message: str):
        """In thông báo error"""
        if self.use_rich:
            self.print_panel(f"❌ {message}", style="red", border_style="red")
        else:
            print(f"❌ {message}")
    
    def print_warning(self, message: str):
        """In thông báo warning"""
        if self.use_rich:
            self.print_panel(f"⚠️  {message}", style="yellow", border_style="yellow")
        else:
            print(f"⚠️  {message}")
    
    def print_info(self, message: str):
        """In thông báo info"""
        if self.use_rich:
            self.print_panel(f"ℹ️  {message}", style="blue", border_style="blue")
        else:
            print(f"ℹ️  {message}")
    
    def create_progress(self, total: int, description: str = "Processing"):
        """
        Tạo Rich Progress bar
        
        Args:
            total: Tổng số items
            description: Mô tả
        
        Returns:
            Progress context manager
        """
        if not self.use_rich:
            # Fallback: dùng ProgressBar từ utils.progress
            from utils.progress import ProgressBar
            return ProgressBar(total, prefix=description)
        
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console
        )
        
        return progress
    
    def print_tree(self, title: str, tree_data: dict):
        """
        In cây thư mục với Rich Tree
        
        Args:
            title: Tiêu đề
            tree_data: Dict chứa cấu trúc cây
        """
        if not self.use_rich:
            # Fallback: in cây đơn giản
            def print_tree_recursive(data, prefix="", is_last=True):
                items = list(data.items())
                for i, (key, value) in enumerate(items):
                    is_last_item = i == len(items) - 1
                    current_prefix = "└── " if is_last_item else "├── "
                    print(f"{prefix}{current_prefix}{key}")
                    
                    if isinstance(value, dict):
                        next_prefix = prefix + ("    " if is_last_item else "│   ")
                        print_tree_recursive(value, next_prefix, is_last_item)
            
            print(f"\n{title}")
            print("=" * 80)
            print_tree_recursive(tree_data)
            print()
            return
        
        tree = Tree(title)
        self._build_tree(tree, tree_data)
        self.console.print(tree)
    
    def _build_tree(self, parent, data: dict):
        """Helper để build Rich Tree"""
        for key, value in data.items():
            if isinstance(value, dict):
                branch = parent.add(key)
                self._build_tree(branch, value)
            else:
                parent.add(f"{key}: {value}")
    
    def print_code(self, code: str, language: str = "python", theme: str = "monokai"):
        """
        In code với syntax highlighting
        
        Args:
            code: Code cần in
            language: Ngôn ngữ (python, bash, json, etc.)
            theme: Theme cho syntax highlighting
        """
        if not self.use_rich:
            # Fallback: in code thường
            print(f"\n```{language}")
            print(code)
            print("```\n")
            return
        
        syntax = Syntax(code, language, theme=theme)
        self.console.print(syntax)
    
    def print_markdown(self, markdown: str):
        """In markdown với Rich"""
        if not self.use_rich:
            # Fallback: in text thường
            print(markdown)
            return
        
        md = Markdown(markdown)
        self.console.print(md)
    
    def prompt(self, message: str, default: str = "") -> str:
        """
        Prompt input với Rich
        
        Args:
            message: Câu hỏi
            default: Giá trị mặc định
        
        Returns:
            str: Input từ user
        """
        if not self.use_rich:
            # Fallback: dùng input thường
            if default:
                return input(f"{message} [{default}]: ").strip() or default
            return input(f"{message}: ").strip()
        
        return Prompt.ask(message, default=default)
    
    def confirm(self, message: str, default: bool = True) -> bool:
        """
        Confirm với Rich
        
        Args:
            message: Câu hỏi
            default: Giá trị mặc định
        
        Returns:
            bool: True nếu user chọn yes
        """
        if not self.use_rich:
            # Fallback: dùng input thường
            default_str = "Y/n" if default else "y/N"
            response = input(f"{message} [{default_str}]: ").strip().lower()
            if not response:
                return default
            return response in ['y', 'yes', 'có', 'c']
        
        return Confirm.ask(message, default=default)


# Global instance
_rich_ui_instance = None

def get_rich_ui(use_rich: bool = True) -> RichUI:
    """Lấy global RichUI instance"""
    global _rich_ui_instance
    if _rich_ui_instance is None:
        _rich_ui_instance = RichUI(use_rich=use_rich)
    return _rich_ui_instance

