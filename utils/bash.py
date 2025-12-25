#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module bash - Cross-platform bash/script execution patterns

Mục đích: Tập trung các pattern chạy bash scripts trên đa nền tảng
Lý do: Giảm code duplication, xử lý đúng path conversion và execution
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from .colors import Colors


class BashExecutor:
    """
    Cross-platform bash script executor

    Mục đích: Thống nhất cách chạy bash scripts trên Windows và Unix
    """

    def __init__(self):
        self.bash_cmd = self._find_bash()
        self.is_git_bash = self._is_git_bash()

    def _find_bash(self) -> Optional[List[str]]:
        """
        Find bash executable on the system

        Returns:
            list: Bash command and arguments, or None if not found

        Giải thích:
            - Trên Linux/macOS: dùng bash mặc định
            - Trên Windows: thử Git Bash, WSL, rồi bash.exe
        """
        # Linux/macOS
        if sys.platform.startswith(('linux', 'darwin')):
            bash_path = shutil.which('bash')
            if bash_path:
                return [bash_path]
            return None

        # Windows
        if sys.platform == 'win32':
            # Try Git Bash (most common)
            git_bash_paths = [
                r"C:\Program Files\Git\bin\bash.exe",
                r"C:\Program Files (x86)\Git\bin\bash.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Git\bin\bash.exe")
            ]

            for bash_path in git_bash_paths:
                if os.path.exists(bash_path):
                    return [bash_path]

            # Try WSL
            wsl_path = shutil.which('wsl')
            if wsl_path:
                return ['wsl', 'bash']

            # Try bash.exe in PATH
            bash_exe = shutil.which('bash.exe')
            if bash_exe:
                return [bash_exe]

        return None

    def _is_git_bash(self) -> bool:
        """
        Check if using Git Bash

        Returns:
            bool: True if Git Bash is being used
        """
        if not self.bash_cmd:
            return False

        return 'Git' in str(self.bash_cmd[0])

    def convert_path_for_bash(self, windows_path: str) -> str:
        """
        Convert Windows path to Unix path for bash

        Args:
            windows_path: Windows path (C:\\path\\to\\file)

        Returns:
            str: Unix path (/c/path/to/file)

        Giải thích:
            - Chỉ convert khi dùng Git Bash trên Windows
            - Thay C: thành /c, D: thành /d, etc.
            - Chuyển backslash thành forward slash
        """
        if not self.is_git_bash or ':' not in windows_path:
            return windows_path

        # Convert C:\path\to\file to /c/path/to/file
        drive = windows_path[0].lower()
        unix_path = windows_path.replace('\\', '/').replace(f'{drive}:', f'/{drive}', 1)

        return unix_path

    def execute_script(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        capture_output: bool = False,
        check: bool = False
    ) -> subprocess.CompletedProcess:
        """
        Execute a bash script

        Args:
            script_path: Path to bash script
            args: Additional arguments for the script
            cwd: Working directory
            env: Environment variables
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero exit

        Returns:
            CompletedProcess: Result of script execution

        Raises:
            FileNotFoundError: If bash not found
            subprocess.CalledProcessError: If check=True and script fails
        """
        if not self.bash_cmd:
            raise FileNotFoundError("Bash not found. On Windows, install Git Bash or WSL.")

        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")

        # Convert script path for bash
        bash_script_path = self.convert_path_for_bash(str(script_path))

        # Build command
        cmd = self.bash_cmd + [bash_script_path]
        if args:
            cmd.extend(args)

        # Execute
        return subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=True,
            check=check
        )

    def run_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        capture_output: bool = False,
        check: bool = False
    ) -> subprocess.CompletedProcess:
        """
        Run a bash command directly

        Args:
            command: Bash command to run
            cwd: Working directory
            env: Environment variables
            capture_output: Whether to capture output
            check: Whether to raise exception on failure

        Returns:
            CompletedProcess: Command result
        """
        if not self.bash_cmd:
            raise FileNotFoundError("Bash not found. On Windows, install Git Bash or WSL.")

        # Build command
        cmd = self.bash_cmd + ['-c', command]

        # Execute
        return subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=True,
            check=check
        )

    def get_bash_info(self) -> Dict[str, Any]:
        """
        Get information about the bash environment

        Returns:
            dict: Bash environment information
        """
        return {
            'bash_found': self.bash_cmd is not None,
            'bash_command': self.bash_cmd,
            'is_git_bash': self.is_git_bash,
            'platform': sys.platform
        }


def find_bash_executable() -> Optional[List[str]]:
    """
    Find bash executable (standalone function)

    Returns:
        list: Bash command, or None if not found
    """
    executor = BashExecutor()
    return executor.bash_cmd


def is_git_bash_available() -> bool:
    """
    Check if Git Bash is available

    Returns:
        bool: True if Git Bash found
    """
    executor = BashExecutor()
    return executor.is_git_bash


def convert_windows_path_to_unix(windows_path: str) -> str:
    """
    Convert Windows path to Unix path for bash

    Args:
        windows_path: Windows path

    Returns:
        str: Converted path
    """
    executor = BashExecutor()
    return executor.convert_path_for_bash(windows_path)


def run_bash_script(
    script_path: str,
    args: Optional[List[str]] = None,
    cwd: Optional[str] = None,
    show_output: bool = True,
    title: str = "Running script"
) -> Tuple[bool, str, int]:
    """
    Run bash script with nice output formatting

    Args:
        script_path: Path to script
        args: Script arguments
        cwd: Working directory
        show_output: Whether to show execution output
        title: Title for the operation

    Returns:
        tuple: (success, message, exit_code)
    """
    from .format import print_separator
    from .progress import Spinner

    try:
        executor = BashExecutor()

        if not executor.bash_cmd:
            return False, "Bash not found. On Windows, install Git Bash or WSL.", -1

        print(f"\n{Colors.primary(title)}")
        print(f"📁 Script: {script_path}")
        print(f"💻 Bash: {' '.join(executor.bash_command)}")

        if show_output:
            print_separator("═", 70, Colors.PRIMARY)

        # Show spinner if not showing output
        spinner = None
        if not show_output:
            spinner = Spinner(f"Running {os.path.basename(script_path)}")
            spinner.start()

        # Execute script
        result = executor.execute_script(
            script_path,
            args=args,
            cwd=cwd,
            capture_output=not show_output
        )

        if spinner:
            spinner.stop()

        if show_output:
            print_separator("═", 70, Colors.SUCCESS if result.returncode == 0 else Colors.ERROR)

        success = result.returncode == 0
        message = "Script completed successfully" if success else f"Script failed with exit code {result.returncode}"

        if not show_output and result.returncode != 0:
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)

        return success, message, result.returncode

    except Exception as e:
        if spinner:
            spinner.stop()
        return False, f"Error running script: {e}", -1


def run_bash_command(
    command: str,
    cwd: Optional[str] = None,
    show_output: bool = True,
    title: str = "Running command"
) -> Tuple[bool, str, int]:
    """
    Run bash command with nice output formatting

    Args:
        command: Bash command
        cwd: Working directory
        show_output: Whether to show execution output
        title: Title for the operation

    Returns:
        tuple: (success, message, exit_code)
    """
    from .format import print_separator
    from .progress import Spinner

    try:
        executor = BashExecutor()

        if not executor.bash_cmd:
            return False, "Bash not found. On Windows, install Git Bash or WSL.", -1

        print(f"\n{Colors.primary(title)}")
        print(f"💻 Command: {command}")
        print(f"🖥️  Bash: {' '.join(executor.bash_command)}")

        if show_output:
            print_separator("═", 70, Colors.PRIMARY)

        # Show spinner if not showing output
        spinner = None
        if not show_output:
            spinner = Spinner(f"Running command")
            spinner.start()

        # Execute command
        result = executor.run_command(
            command,
            cwd=cwd,
            capture_output=not show_output
        )

        if spinner:
            spinner.stop()

        if show_output:
            print_separator("═", 70, Colors.SUCCESS if result.returncode == 0 else Colors.ERROR)

        success = result.returncode == 0
        message = "Command completed successfully" if success else f"Command failed with exit code {result.returncode}"

        if not show_output and result.returncode != 0:
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)

        return success, message, result.returncode

    except Exception as e:
        if spinner:
            spinner.stop()
        return False, f"Error running command: {e}", -1


def check_bash_environment() -> Dict[str, Any]:
    """
    Check bash environment and provide diagnostic information

    Returns:
        dict: Environment check results
    """
    result = {
        'bash_available': False,
        'bash_command': None,
        'is_git_bash': False,
        'platform': sys.platform,
        'issues': []
    }

    executor = BashExecutor()

    if executor.bash_cmd:
        result['bash_available'] = True
        result['bash_command'] = executor.bash_cmd
        result['is_git_bash'] = executor.is_git_bash
    else:
        result['issues'].append({
            'level': 'error',
            'message': 'Bash not found. On Windows, install Git Bash or WSL.'
        })

    # Test bash execution
    if result['bash_available']:
        try:
            test_result = executor.run_command('echo "test"', capture_output=True, check=True)
            if test_result.returncode != 0:
                result['issues'].append({
                    'level': 'error',
                    'message': 'Bash execution test failed'
                })
        except Exception as e:
            result['issues'].append({
                'level': 'error',
                'message': f'Bash execution test failed: {e}'
            })

    return result


def print_bash_diagnostics() -> None:
    """
    Print bash environment diagnostics
    """
    print(f"\n{Colors.bold('🔍 BASH ENVIRONMENT DIAGNOSTICS')}")
    print_separator("═", 50, Colors.PRIMARY)

    env_check = check_bash_environment()

    print(f"Platform: {Colors.info(env_check['platform'])}")
    print(f"Bash available: {Colors.success('Yes') if env_check['bash_available'] else Colors.error('No')}")

    if env_check['bash_command']:
        print(f"Bash command: {Colors.info(' '.join(env_check['bash_command']))}")
        print(f"Git Bash: {Colors.success('Yes') if env_check['is_git_bash'] else Colors.muted('No')}")

    if env_check['issues']:
        print(f"\n{Colors.warning('⚠️  ISSUES FOUND:')}")
        for issue in env_check['issues']:
            color = Colors.error if issue['level'] == 'error' else Colors.warning
            print(f"   • {color(issue['message'])}")

    print_separator("═", 50, Colors.PRIMARY)
