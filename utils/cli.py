#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module cli - Common CLI argument parsing patterns for tools

Mục đích: Tập trung các pattern argparse phổ biến trong tools
Lý do: Giảm code duplication, đảm bảo tính nhất quán CLI interface
"""

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from .colors import Colors


class CommonArgs:
    """Common argument patterns for tools"""

    @staticmethod
    def add_input_path(parser: argparse.ArgumentParser, help_text: str = "Input path (file or directory)") -> None:
        """Add input path argument"""
        parser.add_argument(
            '-i', '--input',
            type=str,
            help=help_text
        )

    @staticmethod
    def add_output_path(parser: argparse.ArgumentParser, help_text: str = "Output path (file or directory)") -> None:
        """Add output path argument"""
        parser.add_argument(
            '-o', '--output',
            type=str,
            help=help_text
        )

    @staticmethod
    def add_quality(parser: argparse.ArgumentParser, default: int = 70,
                   help_text: str = "Quality (1-100)") -> None:
        """Add quality argument for compression/encoding"""
        parser.add_argument(
            '-q', '--quality',
            type=int,
            default=default,
            choices=range(1, 101),
            metavar='[1-100]',
            help=f'{help_text} (default: {default})'
        )

    @staticmethod
    def add_format_choices(parser: argparse.ArgumentParser, formats: List[str],
                          default: Optional[str] = None,
                          help_text: str = "Output format") -> None:
        """Add format choice argument"""
        parser.add_argument(
            '-f', '--format',
            choices=formats,
            default=default,
            help=f"{help_text} (choices: {', '.join(formats)})"
        )

    @staticmethod
    def add_compression_formats(parser: argparse.ArgumentParser, default: str = 'zip') -> None:
        """Add common compression formats"""
        formats = ['zip', 'tar', 'gztar', 'bztar', 'xztar']
        CommonArgs.add_format_choices(
            parser, formats, default,
            "Compression format"
        )

    @staticmethod
    def add_image_formats(parser: argparse.ArgumentParser, default: Optional[str] = None) -> None:
        """Add common image formats"""
        formats = ['jpg', 'jpeg', 'png', 'webp', 'bmp']
        CommonArgs.add_format_choices(
            parser, formats, default,
            "Image format"
        )

    @staticmethod
    def add_video_formats(parser: argparse.ArgumentParser, default: Optional[str] = None) -> None:
        """Add common video formats"""
        formats = ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv']
        CommonArgs.add_format_choices(
            parser, formats, default,
            "Video format"
        )

    @staticmethod
    def add_max_size(parser: argparse.ArgumentParser, help_text: str = "Maximum size in KB") -> None:
        """Add maximum size argument"""
        parser.add_argument(
            '--max-size',
            type=int,
            help=help_text
        )

    @staticmethod
    def add_dimensions(parser: argparse.ArgumentParser) -> None:
        """Add width/height dimensions"""
        parser.add_argument(
            '-w', '--width',
            type=int,
            help='Width in pixels'
        )
        parser.add_argument(
            '-H', '--height',  # Capital H to avoid conflict with -h/--help
            type=int,
            help='Height in pixels'
        )

    @staticmethod
    def add_exclude_patterns(parser: argparse.ArgumentParser,
                           help_text: str = "Exclude patterns (comma-separated)") -> None:
        """Add exclude patterns argument"""
        parser.add_argument(
            '-e', '--exclude',
            type=str,
            help=help_text
        )

    @staticmethod
    def add_recursive(parser: argparse.ArgumentParser, default: bool = True) -> None:
        """Add recursive flag"""
        parser.add_argument(
            '--no-recursive',
            action='store_false',
            dest='recursive',
            help='Disable recursive processing'
        )
        parser.set_defaults(recursive=default)

    @staticmethod
    def add_quiet_mode(parser: argparse.ArgumentParser) -> None:
        """Add quiet mode flag"""
        parser.add_argument(
            '-q', '--quiet',
            action='store_true',
            help='Quiet mode (no progress output)'
        )

    @staticmethod
    def add_dry_run(parser: argparse.ArgumentParser) -> None:
        """Add dry run flag"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Dry run mode (show what would be done without executing)'
        )

    @staticmethod
    def add_force(parser: argparse.ArgumentParser) -> None:
        """Add force flag for overwriting"""
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force overwrite existing files'
        )

    @staticmethod
    def add_threads(parser: argparse.ArgumentParser, default: int = 4) -> None:
        """Add thread count argument"""
        parser.add_argument(
            '--threads',
            type=int,
            default=default,
            metavar='N',
            help=f'Number of threads (default: {default})'
        )


def create_tool_parser(
    tool_name: str,
    description: str,
    epilog: Optional[str] = None,
    add_help_examples: bool = True
) -> argparse.ArgumentParser:
    """
    Create a standard tool argument parser

    Args:
        tool_name: Name of the tool
        description: Tool description
        epilog: Epilog text (usually examples)
        add_help_examples: Whether to add help examples

    Returns:
        argparse.ArgumentParser: Configured parser
    """
    parser = argparse.ArgumentParser(
        prog=tool_name,
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog or create_default_examples(tool_name) if add_help_examples else None
    )

    return parser


def create_default_examples(tool_name: str) -> str:
    """
    Create default examples for a tool

    Args:
        tool_name: Name of the tool

    Returns:
        str: Examples text
    """
    return f"""
Ví dụ sử dụng:
  # Chế độ interactive (khuyến nghị)
  python {tool_name}.py

  # Chế độ CLI cơ bản
  python {tool_name}.py [options]

  # Xem help
  python {tool_name}.py --help
"""


def validate_cli_args(args: argparse.Namespace) -> Tuple[bool, str]:
    """
    Validate parsed CLI arguments

    Args:
        args: Parsed arguments

    Returns:
        tuple: (is_valid, error_message)
    """
    # Check input path if exists
    if hasattr(args, 'input') and args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            return False, f"Input path does not exist: {args.input}"

    # Check output directory if exists
    if hasattr(args, 'output') and args.output:
        output_path = Path(args.output)
        if hasattr(args, 'input') and args.input:
            input_path = Path(args.input)
            # Don't allow output to be inside input for safety
            if output_path.is_relative_to(input_path):
                return False, "Output path cannot be inside input path"

    return True, ""


def setup_tool_cli(
    tool_name: str,
    description: str,
    setup_parser_func: callable,
    validate_func: Optional[callable] = None
) -> Tuple[argparse.ArgumentParser, argparse.Namespace]:
    """
    Setup CLI for a tool with common patterns

    Args:
        tool_name: Tool name
        description: Tool description
        setup_parser_func: Function to setup parser arguments
        validate_func: Optional validation function

    Returns:
        tuple: (parser, args)
    """
    parser = create_tool_parser(tool_name, description)

    # Let the tool add its specific arguments
    if setup_parser_func:
        setup_parser_func(parser)

    # Parse arguments
    args, unknown = parser.parse_known_args()

    # Validate arguments
    if validate_func:
        is_valid, error_msg = validate_func(args)
        if not is_valid:
            parser.error(error_msg)

    # Default validation
    is_valid, error_msg = validate_cli_args(args)
    if not is_valid:
        parser.error(error_msg)

    return parser, args


def print_cli_usage_examples(tool_name: str, examples: List[Dict[str, str]]) -> None:
    """
    Print CLI usage examples in a nice format

    Args:
        tool_name: Tool name
        examples: List of example dicts with 'desc' and 'cmd' keys
    """
    if not examples:
        return

    print(f"\n{Colors.bold('📋 CÁCH SỬ DỤNG CLI:')}")
    print(f"{Colors.muted('=' * 50)}")

    for i, example in enumerate(examples, 1):
        desc = example.get('desc', '')
        cmd = example.get('cmd', '')

        print(f"{i}. {Colors.bold(desc)}")
        print(f"   {Colors.secondary(f'python {tool_name}.py {cmd}')}")
        print()

    print(f"{Colors.muted('💡 Chạy với --help để xem tất cả options')}")


def handle_cli_error(error: Exception, tool_name: str) -> int:
    """
    Handle CLI execution errors consistently

    Args:
        error: The exception that occurred
        tool_name: Tool name for logging

    Returns:
        int: Exit code
    """
    print(Colors.error(f"❌ Lỗi: {error}"))

    # Log error if logger is available
    try:
        from .logger import log_error
        log_error(f"CLI Error in {tool_name}: {error}", exc_info=True)
    except ImportError:
        pass

    return 1


def create_progress_callback(quiet: bool = False) -> callable:
    """
    Create a progress callback function for CLI operations

    Args:
        quiet: Whether to suppress progress output

    Returns:
        callable: Progress callback function
    """
    if quiet:
        return lambda *args, **kwargs: None

    def progress_callback(message: str = "", current: int = 0, total: int = 0):
        if total > 0 and current > 0:
            percentage = (current / total * 100)
            print(f"📊 {current}/{total} ({percentage:.1f}%) {message}")
        elif message:
            print(f"ℹ️  {message}")

    return progress_callback
