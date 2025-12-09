#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module theme - Quản lý themes cho UI

Mục đích: Cho phép người dùng tùy chỉnh màu sắc và giao diện
Lý do: Cải thiện UX với dark/light mode và custom themes
"""

import json
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class ThemeColors:
    """Class chứa màu sắc của theme"""
    primary: str = "#3498db"      # Blue
    success: str = "#2ecc71"      # Green
    warning: str = "#f39c12"      # Orange
    error: str = "#e74c3c"        # Red
    info: str = "#3498db"         # Blue
    secondary: str = "#95a5a6"    # Gray
    muted: str = "#7f8c8d"        # Dark gray
    background: str = "#ffffff"    # White
    foreground: str = "#000000"   # Black
    border: str = "#bdc3c7"       # Light gray


class ThemeManager:
    """Class quản lý themes"""
    
    # Built-in themes
    THEMES = {
        'default': ThemeColors(
            primary="#3498db",
            success="#2ecc71",
            warning="#f39c12",
            error="#e74c3c",
            info="#3498db",
            secondary="#95a5a6",
            muted="#7f8c8d",
            background="#ffffff",
            foreground="#000000",
            border="#bdc3c7"
        ),
        'dark': ThemeColors(
            primary="#5dade2",
            success="#52b788",
            warning="#f4a261",
            error="#e76f51",
            info="#5dade2",
            secondary="#adb5bd",
            muted="#6c757d",
            background="#1a1a1a",
            foreground="#e0e0e0",
            border="#404040"
        ),
        'light': ThemeColors(
            primary="#2980b9",
            success="#27ae60",
            warning="#d68910",
            error="#c0392b",
            info="#2980b9",
            secondary="#7f8c8d",
            muted="#95a5a6",
            background="#ffffff",
            foreground="#2c3e50",
            border="#ecf0f1"
        ),
        'blue': ThemeColors(
            primary="#3498db",
            success="#2ecc71",
            warning="#f39c12",
            error="#e74c3c",
            info="#3498db",
            secondary="#34495e",
            muted="#7f8c8d",
            background="#ecf0f1",
            foreground="#2c3e50",
            border="#bdc3c7"
        ),
        'green': ThemeColors(
            primary="#27ae60",
            success="#2ecc71",
            warning="#f39c12",
            error="#e74c3c",
            info="#16a085",
            secondary="#7f8c8d",
            muted="#95a5a6",
            background="#ffffff",
            foreground="#2c3e50",
            border="#ecf0f1"
        )
    }
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Khởi tạo ThemeManager
        
        Args:
            config_file: Đường dẫn file config (mặc định: menus/theme_config.json)
        """
        if config_file is None:
            config_file = Path(__file__).parent.parent / "menus" / "theme_config.json"
        
        self.config_file = config_file
        self.current_theme = self._load_theme()
    
    def _load_theme(self) -> str:
        """Load theme hiện tại từ config"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    theme_name = config.get('theme', 'default')
                    if theme_name in self.THEMES:
                        return theme_name
            except Exception:
                pass
        
        return 'default'
    
    def _save_theme(self, theme_name: str):
        """Lưu theme vào config"""
        try:
            config = {'theme': theme_name}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.current_theme = theme_name
        except Exception as e:
            print(f"Lỗi lưu theme: {e}")
    
    def get_theme(self, theme_name: Optional[str] = None) -> ThemeColors:
        """
        Lấy theme colors
        
        Args:
            theme_name: Tên theme (None = dùng theme hiện tại)
        
        Returns:
            ThemeColors: Màu sắc của theme
        """
        if theme_name is None:
            theme_name = self.current_theme
        
        return self.THEMES.get(theme_name, self.THEMES['default'])
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Đặt theme mới
        
        Args:
            theme_name: Tên theme
        
        Returns:
            bool: True nếu thành công
        """
        if theme_name not in self.THEMES:
            return False
        
        self._save_theme(theme_name)
        return True
    
    def list_themes(self) -> Dict[str, ThemeColors]:
        """Liệt kê tất cả themes"""
        return self.THEMES.copy()
    
    def create_custom_theme(self, name: str, colors: Dict[str, str]) -> bool:
        """
        Tạo theme tùy chỉnh
        
        Args:
            name: Tên theme
            colors: Dict chứa màu sắc (hex codes)
        
        Returns:
            bool: True nếu thành công
        """
        try:
            # Validate colors
            theme_colors = ThemeColors()
            for key, value in colors.items():
                if hasattr(theme_colors, key):
                    setattr(theme_colors, key, value)
            
            self.THEMES[name] = theme_colors
            return True
        except Exception:
            return False

