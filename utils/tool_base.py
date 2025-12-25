#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module tool_base - Base classes and mixins for Python tools

Mục đích: Cung cấp framework thống nhất cho việc phát triển tools
Lý do: Đảm bảo tính nhất quán, giảm code duplication, dễ maintain
"""

import sys
import argparse
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .colors import Colors
from .format import print_header
from .setup import setup_tool_environment, handle_tool_error
from .cli import setup_tool_cli, CommonArgs
from .interactive import display_menu, select_from_menu


class ToolMode:
    """Enumeration of tool execution modes"""
    INTERACTIVE = "interactive"
    CLI = "cli"


class BaseTool(ABC):
    """
    Base class for all Python tools

    Provides common functionality:
    - Setup and initialization
    - Mode detection (interactive/CLI)
    - Error handling
    - Logging
    """

    def __init__(self, tool_file: str):
        """
        Initialize tool

        Args:
            tool_file: __file__ of the tool
        """
        self.tool_file = tool_file
        self.tool_name = Path(tool_file).stem

        # Setup environment
        self.env = setup_tool_environment(tool_file, self.tool_name)

        # Tool configuration
        self.config = {}
        self.dependencies = {}

        # Execution mode
        self.mode = self._detect_mode()

    def _detect_mode(self) -> str:
        """
        Detect execution mode based on command line arguments

        Returns:
            str: ToolMode.INTERACTIVE or ToolMode.CLI
        """
        # If no arguments or first arg is not a path/input, assume interactive
        if len(sys.argv) == 1:
            return ToolMode.INTERACTIVE

        # Check if any CLI-specific arguments are provided
        cli_indicators = ['--help', '-h', '-i', '--input', '-o', '--output']
        for arg in sys.argv[1:]:
            if arg in cli_indicators or arg.startswith('-'):
                return ToolMode.CLI

        return ToolMode.INTERACTIVE

    def set_dependencies(self, dependencies: Dict[str, Dict[str, Any]]) -> None:
        """
        Set tool dependencies

        Args:
            dependencies: Dict of dependencies (same format as check_dependencies)
        """
        self.dependencies = dependencies

    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Set tool configuration

        Args:
            config: Tool configuration dict
        """
        self.config = config

    def validate_environment(self) -> bool:
        """
        Validate tool environment before execution

        Returns:
            bool: True if environment is valid
        """
        if not self.env['dependencies_ok']:
            return False

        return True

    @abstractmethod
    def get_description(self) -> str:
        """Get tool description"""
        pass

    @abstractmethod
    def run_interactive(self) -> int:
        """
        Run tool in interactive mode

        Returns:
            int: Exit code
        """
        pass

    @abstractmethod
    def setup_cli_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Setup CLI argument parser

        Args:
            parser: Argument parser to configure
        """
        pass

    @abstractmethod
    def run_cli(self, args: argparse.Namespace) -> int:
        """
        Run tool in CLI mode

        Args:
            args: Parsed CLI arguments

        Returns:
            int: Exit code
        """
        pass

    def run(self) -> int:
        """
        Main entry point - run the tool

        Returns:
            int: Exit code
        """
        try:
            # Validate environment
            if not self.validate_environment():
                return 1

            # Run in appropriate mode
            if self.mode == ToolMode.INTERACTIVE:
                return self.run_interactive()
            else:
                return self.run_cli_mode()

        except KeyboardInterrupt:
            print(f"\n{Colors.warning('❌ Đã hủy!')}")
            return 130
        except Exception as e:
            return handle_tool_error(e, self.tool_name)

    def run_cli_mode(self) -> int:
        """
        Run tool in CLI mode with proper setup

        Returns:
            int: Exit code
        """
        def setup_parser(parser):
            self.setup_cli_parser(parser)
            return parser

        try:
            parser, args = setup_tool_cli(
                self.tool_name,
                self.get_description(),
                setup_parser
            )

            return self.run_cli(args)

        except SystemExit as e:
            # argparse exits with SystemExit, let it propagate
            raise
        except Exception as e:
            return handle_tool_error(e, self.tool_name, "CLI mode")


class InteractiveToolMixin:
    """
    Mixin for tools with interactive menu interface

    Provides common patterns for:
    - Menu display
    - Option selection
    - Input validation
    """

    def create_main_menu(self, title: str, options: Dict[str, str]) -> str:
        """
        Create and display main menu

        Args:
            title: Menu title
            options: Dict of option_key -> option_description

        Returns:
            str: Selected option key, or None if quit
        """
        menu_options = {}
        for key, desc in options.items():
            menu_options[key] = {
                'name': desc,
                'description': ''
            }

        return select_from_menu(title, menu_options)

    def get_user_confirmation(self, message: str, default: bool = False) -> bool:
        """
        Get user confirmation

        Args:
            message: Confirmation message
            default: Default value

        Returns:
            bool: User choice
        """
        from .validation import confirm_action
        return confirm_action(message, default)

    def get_user_path(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Get path input from user

        Args:
            prompt: Input prompt
            **kwargs: Additional arguments for get_path_input

        Returns:
            str: Path input, or None if canceled
        """
        from .interactive import get_path_input
        return get_path_input(prompt, **kwargs)

    def get_user_choice(self, prompt: str, choices: List[str], **kwargs) -> Optional[int]:
        """
        Get choice from user

        Args:
            prompt: Choice prompt
            choices: List of choices
            **kwargs: Additional arguments for get_user_choice

        Returns:
            int: Index of selected choice, or None if canceled
        """
        from .interactive import get_user_choice
        return get_user_choice(prompt, choices, **kwargs)

    def show_progress(self, message: str = "") -> None:
        """
        Show progress message

        Args:
            message: Progress message
        """
        from .interactive import show_progress_info
        show_progress_info(0, 0, message)  # Basic progress display


class CLIToolMixin:
    """
    Mixin for tools with CLI interface

    Provides common CLI patterns:
    - Standard argument setup
    - Input/output validation
    - Progress reporting
    """

    def add_common_args(self, parser: argparse.ArgumentParser) -> None:
        """
        Add common CLI arguments

        Args:
            parser: Argument parser
        """
        CommonArgs.add_input_path(parser)
        CommonArgs.add_output_path(parser)
        CommonArgs.add_quiet_mode(parser)
        CommonArgs.add_force(parser)

    def validate_cli_inputs(self, args: argparse.Namespace) -> bool:
        """
        Validate CLI inputs

        Args:
            args: Parsed arguments

        Returns:
            bool: True if valid
        """
        from .cli import validate_cli_args
        is_valid, error_msg = validate_cli_args(args)
        if not is_valid:
            print(Colors.error(f"❌ {error_msg}"))
            return False
        return True

    def create_progress_callback(self, quiet: bool = False):
        """
        Create progress callback for CLI operations

        Args:
            quiet: Whether to suppress output

        Returns:
            callable: Progress callback function
        """
        from .cli import create_progress_callback
        return create_progress_callback(quiet)


class FileProcessingToolMixin:
    """
    Mixin for tools that process files

    Provides common file processing patterns:
    - Batch processing setup
    - Progress tracking
    - Result display
    """

    def setup_batch_processor(self, **kwargs) -> 'BatchProcessor':
        """
        Setup batch processor

        Args:
            **kwargs: Arguments for BatchProcessor

        Returns:
            BatchProcessor: Configured processor
        """
        from .processing import BatchProcessor
        return BatchProcessor(**kwargs)

    def process_files_batch(self, processor: 'BatchProcessor', **kwargs) -> Dict[str, Any]:
        """
        Process files in batch with standard handling

        Args:
            processor: Configured BatchProcessor
            **kwargs: Additional arguments for process_batch

        Returns:
            dict: Processing results
        """
        return processor.process_batch(**kwargs)

    def display_processing_results(self, results: Dict[str, Any]) -> None:
        """
        Display processing results

        Args:
            results: Results from process_files_batch
        """
        from .processing import display_batch_results

        if 'error' in results:
            print(Colors.error(f"❌ {results['error']}"))
            return

        stats = results.get('stats', {})
        file_results = results.get('results', [])

        display_batch_results(
            f"KẾT QUẢ XỬ LÝ {self.tool_name.upper()}",
            file_results
        )


class ImageProcessingToolMixin(FileProcessingToolMixin):
    """
    Mixin for image processing tools

    Provides common image processing patterns:
    - Image format validation
    - Resize/compress options
    - Quality settings
    """

    def add_image_args(self, parser: argparse.ArgumentParser) -> None:
        """
        Add common image processing arguments

        Args:
            parser: Argument parser
        """
        CommonArgs.add_image_formats(parser)
        CommonArgs.add_quality(parser)
        CommonArgs.add_max_size(parser)
        CommonArgs.add_dimensions(parser)
        CommonArgs.add_exclude_patterns(parser)

    def validate_image_args(self, args: argparse.Namespace) -> bool:
        """
        Validate image processing arguments

        Args:
            args: Parsed arguments

        Returns:
            bool: True if valid
        """
        if hasattr(args, 'quality') and args.quality:
            if not (1 <= args.quality <= 100):
                print(Colors.error("❌ Quality must be between 1-100"))
                return False

        if hasattr(args, 'max_size') and args.max_size:
            if args.max_size <= 0:
                print(Colors.error("❌ Max size must be positive"))
                return False

        return True


class CompressionToolMixin(ImageProcessingToolMixin):
    """
    Mixin for compression tools

    Provides compression-specific patterns:
    - Compression format selection
    - Archive creation
    - Size optimization
    """

    def add_compression_args(self, parser: argparse.ArgumentParser) -> None:
        """
        Add compression-specific arguments

        Args:
            parser: Argument parser
        """
        CommonArgs.add_compression_formats(parser)
        CommonArgs.add_exclude_patterns(parser)

    def validate_compression_args(self, args: argparse.Namespace) -> bool:
        """
        Validate compression arguments

        Args:
            args: Parsed arguments

        Returns:
            bool: True if valid
        """
        # Add compression-specific validation here
        return True


class ToolTemplate:
    """
    Template class for creating new tools

    This provides a complete template that tools can inherit from
    and customize as needed.
    """

    @staticmethod
    def create_basic_tool(tool_file: str):
        """
        Create a basic tool template

        Args:
            tool_file: Tool file path

        Returns:
            str: Tool template code
        """
        tool_name = Path(tool_file).stem

        template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: {tool_name} - Tool description here

Mục đích: Describe what this tool does
Lý do: Explain why this tool is useful
"""

import argparse
from utils.tool_base import BaseTool, InteractiveToolMixin, CLIToolMixin
from utils import print_header


class {tool_name.title().replace("-", "")}Tool(BaseTool, InteractiveToolMixin, CLIToolMixin):
    """
    {tool_name} tool implementation
    """

    def __init__(self, tool_file: str):
        super().__init__(tool_file)

        # Set tool dependencies
        self.set_dependencies({{
            # Add dependencies here, e.g.:
            # 'requests': {{
            #     'install_command': 'pip install requests',
            #     'display_name': 'Requests library'
            # }}
        }})

        # Set tool configuration
        self.set_config({{
            # Add configuration here
        }})

    def get_description(self) -> str:
        """Get tool description"""
        return "{tool_name} - Tool description here"

    def run_interactive(self) -> int:
        """
        Run tool in interactive mode

        Returns:
            int: Exit code
        """
        print_header("{tool_name.upper()}")

        # Main menu
        menu_options = {{
            "1": "Option 1 description",
            "2": "Option 2 description",
            "q": "Quit"
        }}

        while True:
            choice = self.create_main_menu("Main Menu", menu_options)

            if choice == "q" or choice is None:
                break

            if choice == "1":
                # Handle option 1
                print("Option 1 selected")
                # Add your logic here

            elif choice == "2":
                # Handle option 2
                print("Option 2 selected")
                # Add your logic here

            else:
                print("Invalid choice")

        return 0

    def setup_cli_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Setup CLI argument parser

        Args:
            parser: Argument parser to configure
        """
        # Add common arguments
        self.add_common_args(parser)

        # Add tool-specific arguments
        parser.add_argument(
            '--custom-option',
            help='Custom option description'
        )

    def run_cli(self, args: argparse.Namespace) -> int:
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

        # Run tool logic
        print(f"Running {self.tool_name} with args: {{args}}")

        # Add your CLI logic here

        return 0


def main():
    """Main entry point"""
    tool = {tool_name.title().replace("-", "")}Tool(__file__)
    return tool.run()


if __name__ == "__main__":
    exit(main())
'''

        return template

    @staticmethod
    def create_image_tool(tool_file: str):
        """
        Create an image processing tool template

        Args:
            tool_file: Tool file path

        Returns:
            str: Tool template code
        """
        tool_name = Path(tool_file).stem

        template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: {tool_name} - Image processing tool

Mục đích: Process images in various ways
Lý do: Common image processing operations
"""

import argparse
from utils.tool_base import BaseTool, InteractiveToolMixin, CLIToolMixin, ImageProcessingToolMixin
from utils import print_header, install_missing_library


class {tool_name.title().replace("-", "")}Tool(BaseTool, InteractiveToolMixin, CLIToolMixin, ImageProcessingToolMixin):
    """
    {tool_name} tool implementation
    """

    def __init__(self, tool_file: str):
        super().__init__(tool_file)

        # Set tool dependencies
        self.set_dependencies({{
            'PIL': {{
                'import_name': 'PIL',
                'install_command': 'pip install Pillow',
                'display_name': 'Pillow (PIL)'
            }}
        }})

    def get_description(self) -> str:
        """Get tool description"""
        return "{tool_name} - Image processing tool"

    def run_interactive(self) -> int:
        """
        Run tool in interactive mode

        Returns:
            int: Exit code
        """
        print_header("{tool_name.upper()}")

        # Get input directory
        input_dir = self.get_user_path("Nhập thư mục chứa ảnh")
        if not input_dir:
            return 1

        # Get output directory
        output_dir = self.get_user_path("Nhập thư mục đầu ra", create_if_not_exists=True)
        if not output_dir:
            return 1

        # Get quality
        quality = self.get_user_choice(
            "Chọn chất lượng nén:",
            ["Thấp (50%)", "Trung bình (70%)", "Cao (90%)"],
            default=1
        )

        quality_map = [50, 70, 90]
        selected_quality = quality_map[quality] if quality is not None else 70

        # Confirm and process
        if not self.get_user_confirmation("Bắt đầu xử lý ảnh?"):
            return 0

        # Setup processor
        processor = self.setup_batch_processor(
            input_path=input_dir,
            output_path=output_dir,
            file_extensions=['.jpg', '.jpeg', '.png']
        )

        # Process files
        results = self.process_files_batch(processor, show_progress=True)

        # Display results
        self.display_processing_results(results)

        return 0

    def setup_cli_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Setup CLI argument parser

        Args:
            parser: Argument parser to configure
        """
        # Add image processing arguments
        self.add_image_args(parser)

    def run_cli(self, args: argparse.Namespace) -> int:
        """
        Run tool in CLI mode

        Args:
            args: Parsed CLI arguments

        Returns:
            int: Exit code
        """
        # Validate arguments
        if not self.validate_cli_inputs(args) or not self.validate_image_args(args):
            return 1

        # Check PIL availability
        if not install_missing_library('PIL', display_name='Pillow'):
            return 1

        # Run tool logic
        print(f"Running {self.tool_name} with args: {{args}}")

        # Add your image processing logic here

        return 0


def main():
    """Main entry point"""
    tool = {tool_name.title().replace("-", "")}Tool(__file__)
    return tool.run()


if __name__ == "__main__":
    exit(main())
'''

        return template
