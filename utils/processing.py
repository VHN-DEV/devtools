#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module processing - Common file processing patterns for tools

Mục đích: Tập trung các pattern xử lý file hàng loạt
Lý do: Giảm code duplication, đảm bảo tính nhất quán xử lý file
"""

import os
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional, Tuple, Union
from .file_ops import get_file_list, get_folder_size
from .format import format_size
from .progress import ProgressBar
from .colors import Colors


class BatchProcessor:
    """
    Base class for batch file processing operations

    Mục đích: Cung cấp framework chung cho việc xử lý file hàng loạt
    """

    def __init__(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        file_extensions: Optional[List[str]] = None,
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None,
        use_multiprocessing: bool = True,
        max_workers: Optional[int] = None
    ):
        """
        Initialize batch processor

        Args:
            input_path: Input directory/file path
            output_path: Output directory path
            file_extensions: List of file extensions to process
            recursive: Whether to process recursively
            exclude_patterns: Patterns to exclude
            use_multiprocessing: Whether to use multiprocessing
            max_workers: Maximum number of workers
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path) if output_path else None
        self.file_extensions = file_extensions or []
        self.recursive = recursive
        self.exclude_patterns = exclude_patterns or []
        self.use_multiprocessing = use_multiprocessing
        self.max_workers = max_workers

        # Results tracking
        self.processed_files = []
        self.failed_files = []
        self.total_input_size = 0
        self.total_output_size = 0

    def discover_files(self) -> List[str]:
        """
        Discover files to process

        Returns:
            List of file paths to process
        """
        return get_file_list(
            str(self.input_path),
            extensions=self.file_extensions,
            recursive=self.recursive,
            exclude_patterns=self.exclude_patterns
        )

    def validate_inputs(self) -> Tuple[bool, str]:
        """
        Validate input parameters

        Returns:
            tuple: (is_valid, error_message)
        """
        if not self.input_path.exists():
            return False, f"Input path does not exist: {self.input_path}"

        if self.output_path and self.output_path.exists() and not self.output_path.is_dir():
            return False, f"Output path is not a directory: {self.output_path}"

        return True, ""

    def prepare_output_directory(self) -> None:
        """Prepare output directory if needed"""
        if self.output_path:
            self.output_path.mkdir(parents=True, exist_ok=True)

    def process_single_file(self, file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Process a single file (to be implemented by subclasses)

        Args:
            file_path: Path to file to process

        Returns:
            tuple: (success, message, result_data)
        """
        raise NotImplementedError("Subclasses must implement process_single_file")

    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics

        Returns:
            dict: Processing statistics
        """
        success_count = len(self.processed_files)
        error_count = len(self.failed_files)
        total_files = success_count + error_count

        return {
            'total_files': total_files,
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': (success_count / total_files * 100) if total_files > 0 else 0,
            'input_size': self.total_input_size,
            'output_size': self.total_output_size,
            'space_saved': self.total_input_size - self.total_output_size,
            'compression_ratio': (self.total_output_size / self.total_input_size * 100) if self.total_input_size > 0 else 0
        }

    def display_processing_results(self, show_detailed: bool = True) -> None:
        """
        Display processing results

        Args:
            show_detailed: Whether to show detailed results
        """
        stats = self.get_processing_stats()

        print(f"\n{'='*60}")
        print(f"✅ KẾT QUẢ XỬ LÝ")
        print(f"{'='*60}")

        print(f"📊 Tổng số file: {Colors.info(stats['total_files'])}")
        print(f"✅ Thành công: {Colors.success(stats['success_count'])}")
        print(f"❌ Lỗi: {Colors.error(stats['error_count'])}")
        success_rate_str = f"{stats['success_rate']:.1f}%"
        print(f"📈 Tỷ lệ thành công: {Colors.info(success_rate_str)}")

        if stats['input_size'] > 0:
            print(f"💾 Kích thước gốc: {Colors.info(format_size(stats['input_size']))}")
            print(f"💾 Kích thước mới: {Colors.info(format_size(stats['output_size']))}")
            print(f"💰 Tiết kiệm: {Colors.success(format_size(stats['space_saved']))} ({stats['compression_ratio']:.1f}%)")

        print(f"{'='*60}")

        if show_detailed and self.failed_files:
            print(f"\n❌ CHI TIẾT LỖI:")
            for error in self.failed_files[:5]:  # Show first 5 errors
                print(f"   • {error['file']}: {error['error']}")
            if len(self.failed_files) > 5:
                print(f"   ... và {len(self.failed_files) - 5} lỗi khác")

    def process_batch(
        self,
        show_progress: bool = True,
        progress_prefix: str = "Đang xử lý"
    ) -> Dict[str, Any]:
        """
        Process files in batch

        Args:
            show_progress: Whether to show progress bar
            progress_prefix: Progress bar prefix

        Returns:
            dict: Processing results and statistics
        """
        # Validate inputs
        is_valid, error_msg = self.validate_inputs()
        if not is_valid:
            return {'error': error_msg}

        # Discover files
        files_to_process = self.discover_files()
        if not files_to_process:
            return {'error': 'No files found to process'}

        print(f"📁 Tìm thấy {len(files_to_process)} file cần xử lý")

        # Prepare output directory
        self.prepare_output_directory()

        # Calculate total input size
        self.total_input_size = sum(
            os.path.getsize(f) for f in files_to_process
            if os.path.exists(f)
        )

        # Setup progress tracking
        progress = ProgressBar(len(files_to_process), prefix=progress_prefix) if show_progress else None

        # Process files
        if self.use_multiprocessing and len(files_to_process) > 1:
            results = self._process_with_multiprocessing(files_to_process, progress)
        else:
            results = self._process_sequentially(files_to_process, progress)

        if progress:
            progress.finish("Hoàn thành xử lý")

        # Collect results
        self.processed_files = [r for r in results if r['success']]
        self.failed_files = [r for r in results if not r['success']]

        # Calculate output size
        if self.output_path:
            self.total_output_size = get_folder_size(str(self.output_path))

        return {
            'stats': self.get_processing_stats(),
            'results': results
        }

    def _process_sequentially(self, files: List[str], progress: Optional[ProgressBar]) -> List[Dict]:
        """
        Process files sequentially

        Args:
            files: List of files to process
            progress: Progress bar instance

        Returns:
            list: Processing results
        """
        results = []

        for file_path in files:
            success, message, result_data = self.process_single_file(file_path)

            result = {
                'file': file_path,
                'success': success,
                'message': message,
                'data': result_data
            }

            if success:
                result.update(result_data)
            else:
                result['error'] = message

            results.append(result)

            if progress:
                status_icon = "✅" if success else "❌"
                progress.update(message=f"{status_icon} {os.path.basename(file_path)}")

        return results

    def _process_with_multiprocessing(self, files: List[str], progress: Optional[ProgressBar]) -> List[Dict]:
        """
        Process files with multiprocessing

        Args:
            files: List of files to process
            progress: Progress bar instance

        Returns:
            list: Processing results
        """
        # Determine number of workers
        if self.max_workers is None:
            self.max_workers = min(multiprocessing.cpu_count(), len(files))

        results = []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.process_single_file, file_path): file_path
                for file_path in files
            }

            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]

                try:
                    success, message, result_data = future.result()

                    result = {
                        'file': file_path,
                        'success': success,
                        'message': message,
                        'data': result_data
                    }

                    if success:
                        result.update(result_data)
                    else:
                        result['error'] = message

                    results.append(result)

                except Exception as e:
                    result = {
                        'file': file_path,
                        'success': False,
                        'message': str(e),
                        'error': str(e)
                    }
                    results.append(result)

                if progress:
                    filename = os.path.basename(file_path)
                    status = "✅" if result['success'] else "❌"
                    progress.update(message=f"{status} {filename}")

        return results


def create_file_filter(
    extensions: Optional[List[str]] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    exclude_patterns: Optional[List[str]] = None
) -> Callable[[str], bool]:
    """
    Create a file filter function

    Args:
        extensions: Allowed file extensions
        min_size: Minimum file size in bytes
        max_size: Maximum file size in bytes
        exclude_patterns: Patterns to exclude

    Returns:
        callable: Filter function that takes file path and returns bool
    """
    def file_filter(file_path: str) -> bool:
        # Check extension
        if extensions:
            file_ext = Path(file_path).suffix.lower().lstrip('.')
            if file_ext not in [ext.lower().lstrip('.') for ext in extensions]:
                return False

        # Check size
        if min_size is not None or max_size is not None:
            try:
                file_size = os.path.getsize(file_path)
                if min_size is not None and file_size < min_size:
                    return False
                if max_size is not None and file_size > max_size:
                    return False
            except OSError:
                return False  # Can't get size, exclude

        # Check exclude patterns
        if exclude_patterns:
            file_str = str(file_path).lower()
            for pattern in exclude_patterns:
                if pattern.lower() in file_str:
                    return False

        return True

    return file_filter


def process_files_with_callback(
    files: List[str],
    callback: Callable[[str], Tuple[bool, str, Dict[str, Any]]],
    use_threads: bool = False,
    max_workers: Optional[int] = None,
    show_progress: bool = True,
    progress_prefix: str = "Processing"
) -> Dict[str, Any]:
    """
    Process files with a callback function

    Args:
        files: List of files to process
        callback: Function that takes file_path and returns (success, message, data)
        use_threads: Whether to use threads instead of processes
        max_workers: Maximum number of workers
        show_progress: Whether to show progress
        progress_prefix: Progress prefix

    Returns:
        dict: Processing results
    """
    if not files:
        return {'error': 'No files to process'}

    # Setup progress
    progress = ProgressBar(len(files), prefix=progress_prefix) if show_progress else None

    # Determine executor type
    executor_class = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

    # Determine max workers
    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), len(files))

    results = []
    success_count = 0
    error_count = 0

    if len(files) == 1 or max_workers == 1:
        # Process sequentially
        for file_path in files:
            success, message, data = callback(file_path)

            result = {
                'file': file_path,
                'success': success,
                'message': message,
                'data': data
            }

            if success:
                success_count += 1
            else:
                error_count += 1
                result['error'] = message

            results.append(result)

            if progress:
                status = "✅" if success else "❌"
                progress.update(message=f"{status} {os.path.basename(file_path)}")

    else:
        # Process in parallel
        with executor_class(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(callback, file_path): file_path
                for file_path in files
            }

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]

                try:
                    success, message, data = future.result()

                    result = {
                        'file': file_path,
                        'success': success,
                        'message': message,
                        'data': data
                    }

                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        result['error'] = message

                    results.append(result)

                except Exception as e:
                    result = {
                        'file': file_path,
                        'success': False,
                        'message': str(e),
                        'error': str(e)
                    }
                    results.append(result)
                    error_count += 1

                if progress:
                    status = "✅" if result['success'] else "❌"
                    progress.update(message=f"{status} {os.path.basename(file_path)}")

    if progress:
        progress.finish("Processing complete")

    return {
        'results': results,
        'stats': {
            'total': len(files),
            'success': success_count,
            'errors': error_count,
            'success_rate': (success_count / len(files) * 100) if files else 0
        }
    }


def collect_processing_results(results: List[Dict]) -> Dict[str, Any]:
    """
    Collect and summarize processing results

    Args:
        results: List of processing result dicts

    Returns:
        dict: Summary statistics
    """
    total = len(results)
    success_count = sum(1 for r in results if r.get('success', False))
    error_count = total - success_count

    # Collect file sizes if available
    total_input_size = 0
    total_output_size = 0

    for result in results:
        if result.get('success'):
            total_input_size += result.get('old_size', 0)
            total_output_size += result.get('new_size', 0)

    return {
        'total_files': total,
        'success_count': success_count,
        'error_count': error_count,
        'success_rate': (success_count / total * 100) if total > 0 else 0,
        'total_input_size': total_input_size,
        'total_output_size': total_output_size,
        'space_saved': total_input_size - total_output_size,
        'compression_ratio': (total_output_size / total_input_size * 100) if total_input_size > 0 else 0
    }


def display_batch_results(
    title: str,
    results: List[Dict],
    show_details: bool = True,
    max_errors_to_show: int = 5
) -> None:
    """
    Display batch processing results in a nice format

    Args:
        title: Title for the results
        results: List of result dicts
        show_details: Whether to show detailed results
        max_errors_to_show: Maximum number of errors to display
    """
    stats = collect_processing_results(results)

    print(f"\n{'='*60}")
    print(f"✅ {title.upper()}")
    print(f"{'='*60}")

    print(f"📊 Tổng số: {Colors.info(stats['total_files'])}")
    print(f"✅ Thành công: {Colors.success(stats['success_count'])}")
    print(f"❌ Lỗi: {Colors.error(stats['error_count'])}")
    success_rate_str = f"{stats['success_rate']:.1f}%"
    print(f"📈 Tỷ lệ: {Colors.info(success_rate_str)}")

    if stats['total_input_size'] > 0:
        print(f"💾 Kích thước gốc: {Colors.info(format_size(stats['total_input_size']))}")
        print(f"💾 Kích thước mới: {Colors.info(format_size(stats['total_output_size']))}")
        print(f"💰 Tiết kiệm: {Colors.success(format_size(stats['space_saved']))} ({stats['compression_ratio']:.1f}%)")

    if show_details and stats['error_count'] > 0:
        print(f"\n❌ CHI TIẾT LỖI:")
        error_count = 0
        for result in results:
            if not result.get('success', False):
                print(f"   • {os.path.basename(result['file'])}: {result.get('error', 'Unknown error')}")
                error_count += 1
                if error_count >= max_errors_to_show:
                    break

        if stats['error_count'] > max_errors_to_show:
            print(f"   ... và {stats['error_count'] - max_errors_to_show} lỗi khác")

    print(f"{'='*60}\n")
