#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Tối ưu hóa hiệu năng website (Bản beta)
Mục đích: Tự động tối ưu hóa các file CSS, JavaScript, hình ảnh, HTML và cấu hình cache
"""

import os
import json
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def print_header():
    """In header của tool"""
    print("=" * 70)
    print("  TOOL TOI UU HOA HIEU NANG WEBSITE")
    print("=" * 70)
    print()


def get_config_file():
    """Lấy đường dẫn file config"""
    script_dir = Path(__file__).resolve().parent
    config_file = script_dir / "optimizer_config.json"
    return config_file


def load_config():
    """Load cấu hình từ file"""
    config_file = get_config_file()
    
    default_config = {
        'version': '1.0',
        'default_htdocs_path': r'C:\xampp\htdocs',
        'optimize_css': True,
        'optimize_js': True,
        'optimize_images': True,
        'optimize_html': True,
        'create_htaccess': True,
        'backup_files': True,
        'backup_folder': 'backup_original',
        'minify_css': True,
        'minify_js': True,
        'compress_images': True,
        'remove_html_comments': True,
        'remove_whitespace': True
    }
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                # Merge với default config
                for key in default_config:
                    if key not in loaded_config:
                        loaded_config[key] = default_config[key]
                return loaded_config
        except Exception as e:
            print(f"[!] Lỗi đọc config: {e}")
            return default_config
    else:
        save_config(default_config)
        return default_config


def save_config(config):
    """Lưu cấu hình vào file"""
    config_file = get_config_file()
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[X] Lỗi lưu config: {e}")
        return False


def get_file_size_mb(file_path):
    """Lấy kích thước file theo MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0


def get_file_size_kb(file_path):
    """Lấy kích thước file theo KB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / 1024
    except Exception:
        return 0


def backup_file(file_path, backup_dir):
    """Backup file trước khi tối ưu"""
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        
        # Tạo đường dẫn backup giữ nguyên cấu trúc thư mục
        rel_path = os.path.relpath(file_path, os.path.dirname(backup_dir))
        backup_path = os.path.join(backup_dir, rel_path)
        backup_file_dir = os.path.dirname(backup_path)
        
        if not os.path.exists(backup_file_dir):
            os.makedirs(backup_file_dir, exist_ok=True)
        
        shutil.copy2(file_path, backup_path)
        return True
    except Exception as e:
        print(f"[!] Lỗi backup file {file_path}: {e}")
        return False


def minify_css(content):
    """Minify CSS content"""
    # Loại bỏ comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Loại bỏ khoảng trắng thừa
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\s*{\s*', '{', content)
    content = re.sub(r'\s*}\s*', '}', content)
    content = re.sub(r'\s*:\s*', ':', content)
    content = re.sub(r'\s*;\s*', ';', content)
    content = re.sub(r'\s*,\s*', ',', content)
    
    # Loại bỏ khoảng trắng trước và sau
    content = content.strip()
    
    return content


def minify_js(content):
    """Minify JavaScript content (basic)"""
    # Loại bỏ single-line comments (nhưng giữ lại trong strings)
    lines = content.split('\n')
    result = []
    in_string = False
    string_char = None
    
    for line in lines:
        new_line = ''
        i = 0
        while i < len(line):
            char = line[i]
            
            # Xử lý escape trong string
            if in_string and i > 0 and line[i-1] == '\\':
                new_line += char
                i += 1
                continue
            
            # Kiểm tra string
            if char in ['"', "'"] and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
            
            # Bỏ comment nếu không trong string
            if not in_string and char == '/' and i + 1 < len(line):
                if line[i+1] == '/':
                    break  # Bỏ phần còn lại của dòng
                elif line[i+1] == '*':
                    # Multi-line comment
                    i += 2
                    while i < len(line) - 1:
                        if line[i] == '*' and line[i+1] == '/':
                            i += 2
                            break
                        i += 1
                    continue
            
            new_line += char
            i += 1
        
        if new_line.strip():
            result.append(new_line.strip())
    
    content = ' '.join(result)
    
    # Loại bỏ khoảng trắng thừa
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\s*{\s*', '{', content)
    content = re.sub(r'\s*}\s*', '}', content)
    content = re.sub(r'\s*;\s*', ';', content)
    content = re.sub(r'\s*,\s*', ',', content)
    
    return content.strip()


def minify_html(content):
    """Minify HTML content"""
    # Loại bỏ HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    # Loại bỏ khoảng trắng thừa giữa các tags
    content = re.sub(r'>\s+<', '><', content)
    
    # Loại bỏ khoảng trắng ở đầu và cuối dòng
    lines = content.split('\n')
    content = '\n'.join(line.strip() for line in lines if line.strip())
    
    # Loại bỏ nhiều khoảng trắng liên tiếp
    content = re.sub(r' +', ' ', content)
    
    return content.strip()


def optimize_css_file(file_path, config, backup_dir=None):
    """Tối ưu hóa file CSS"""
    try:
        # Backup nếu cần
        if config.get('backup_files', True) and backup_dir:
            backup_file(file_path, backup_dir)
        
        # Đọc file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_size = len(content)
        
        # Minify
        if config.get('minify_css', True):
            content = minify_css(content)
        
        # Ghi file
        with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)
        
        new_size = len(content)
        saved = original_size - new_size
        saved_percent = (saved / original_size * 100) if original_size > 0 else 0
        
        return {
            'success': True,
            'original_size': original_size,
            'new_size': new_size,
            'saved': saved,
            'saved_percent': saved_percent
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def optimize_js_file(file_path, config, backup_dir=None):
    """Tối ưu hóa file JavaScript"""
    try:
        # Bỏ qua file đã minified
        if file_path.endswith('.min.js'):
            return {
                'success': True,
                'skipped': True,
                'reason': 'File đã được minify'
            }
        
        # Backup nếu cần
        if config.get('backup_files', True) and backup_dir:
            backup_file(file_path, backup_dir)
        
        # Đọc file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_size = len(content)
        
        # Minify
        if config.get('minify_js', True):
            content = minify_js(content)
        
        # Ghi file
        with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)
        
        new_size = len(content)
        saved = original_size - new_size
        saved_percent = (saved / original_size * 100) if original_size > 0 else 0
        
        return {
            'success': True,
            'original_size': original_size,
            'new_size': new_size,
            'saved': saved,
            'saved_percent': saved_percent
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def optimize_html_file(file_path, config, backup_dir=None):
    """Tối ưu hóa file HTML"""
    try:
        # Backup nếu cần
        if config.get('backup_files', True) and backup_dir:
            backup_file(file_path, backup_dir)
        
        # Đọc file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_size = len(content)
        
        # Minify HTML
        if config.get('remove_html_comments', True) or config.get('remove_whitespace', True):
            content = minify_html(content)
        
        # Ghi file
        with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)
        
        new_size = len(content)
        saved = original_size - new_size
        saved_percent = (saved / original_size * 100) if original_size > 0 else 0
        
        return {
            'success': True,
            'original_size': original_size,
            'new_size': new_size,
            'saved': saved,
            'saved_percent': saved_percent
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_htaccess(project_path, config):
    """Tạo hoặc cập nhật file .htaccess với cache headers"""
    htaccess_path = os.path.join(project_path, '.htaccess')
    
    cache_config = """
# Cache Headers - Tự động tạo bởi Website Performance Optimizer
<IfModule mod_expires.c>
    ExpiresActive On
    
    # Images
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/webp "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
    ExpiresByType image/x-icon "access plus 1 year"
    
    # CSS and JavaScript
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType text/javascript "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType application/x-javascript "access plus 1 month"
    
    # Fonts
    ExpiresByType font/woff "access plus 1 year"
    ExpiresByType font/woff2 "access plus 1 year"
    ExpiresByType application/font-woff "access plus 1 year"
    ExpiresByType application/font-woff2 "access plus 1 year"
    
    # HTML
    ExpiresByType text/html "access plus 0 seconds"
</IfModule>

# Gzip Compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE text/javascript
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/json
</IfModule>

# Browser Caching
<IfModule mod_headers.c>
    <FilesMatch "\.(ico|jpg|jpeg|png|gif|webp|svg|css|js|woff|woff2)$">
        Header set Cache-Control "max-age=31536000, public"
    </FilesMatch>
</IfModule>
"""
    
    try:
        # Nếu file đã tồn tại, kiểm tra xem đã có cache config chưa
        if os.path.exists(htaccess_path):
            with open(htaccess_path, 'r', encoding='utf-8', errors='ignore') as f:
                existing_content = f.read()
            
            # Nếu đã có cache config, không ghi đè
            if 'Cache Headers' in existing_content or 'mod_expires' in existing_content:
                return {
                    'success': True,
                    'skipped': True,
                    'reason': 'File .htaccess đã có cấu hình cache'
                }
            
            # Thêm vào cuối file
            with open(htaccess_path, 'a', encoding='utf-8', errors='ignore') as f:
                f.write(cache_config)
        else:
            # Tạo file mới
            with open(htaccess_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(cache_config)
        
        return {
            'success': True,
            'created': not os.path.exists(htaccess_path) if os.path.exists(htaccess_path) else True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def optimize_project(project_path, config):
    """Tối ưu hóa toàn bộ dự án"""
    print(f"\n[>] Đang tối ưu hóa dự án: {project_path}")
    print("[>] Vui lòng chờ...\n")
    
    # Tạo thư mục backup nếu cần
    backup_dir = None
    if config.get('backup_files', True):
        backup_folder_name = config.get('backup_folder', 'backup_original')
        backup_dir = os.path.join(project_path, backup_folder_name)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        print(f"[i] Thư mục backup: {backup_dir}\n")
    
    stats = {
        'css': {'processed': 0, 'saved': 0, 'errors': 0},
        'js': {'processed': 0, 'saved': 0, 'errors': 0, 'skipped': 0},
        'html': {'processed': 0, 'saved': 0, 'errors': 0},
        'images': {'processed': 0, 'errors': 0}
    }
    
    # Tối ưu hóa CSS
    if config.get('optimize_css', True):
        print("[>] Đang tối ưu hóa CSS...")
        backup_folder_name = config.get('backup_folder', 'backup_original')
        css_files = []
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'vendor', '.idea', backup_folder_name if backup_dir else '']]
            for file in files:
                if file.endswith('.css'):
                    css_files.append(os.path.join(root, file))
        
        for css_file in css_files:
            result = optimize_css_file(css_file, config, backup_dir)
            if result.get('success'):
                stats['css']['processed'] += 1
                if 'saved' in result:
                    stats['css']['saved'] += result['saved']
                    rel_path = os.path.relpath(css_file, project_path)
                    print(f"  ✓ {rel_path} - Giảm {result['saved_percent']:.1f}%")
            else:
                stats['css']['errors'] += 1
                print(f"  ✗ {os.path.relpath(css_file, project_path)} - Lỗi: {result.get('error', 'Unknown')}")
        
        print(f"[OK] Đã tối ưu {stats['css']['processed']} file CSS\n")
    
    # Tối ưu hóa JavaScript
    if config.get('optimize_js', True):
        print("[>] Đang tối ưu hóa JavaScript...")
        backup_folder_name = config.get('backup_folder', 'backup_original')
        js_files = []
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'vendor', '.idea', backup_folder_name if backup_dir else '']]
            for file in files:
                if file.endswith('.js') and not file.endswith('.min.js'):
                    js_files.append(os.path.join(root, file))
        
        for js_file in js_files:
            result = optimize_js_file(js_file, config, backup_dir)
            if result.get('success'):
                if result.get('skipped'):
                    stats['js']['skipped'] += 1
                else:
                    stats['js']['processed'] += 1
                    if 'saved' in result:
                        stats['js']['saved'] += result['saved']
                        rel_path = os.path.relpath(js_file, project_path)
                        print(f"  ✓ {rel_path} - Giảm {result['saved_percent']:.1f}%")
            else:
                stats['js']['errors'] += 1
                print(f"  ✗ {os.path.relpath(js_file, project_path)} - Lỗi: {result.get('error', 'Unknown')}")
        
        print(f"[OK] Đã tối ưu {stats['js']['processed']} file JavaScript")
        if stats['js']['skipped'] > 0:
            print(f"[i] Bỏ qua {stats['js']['skipped']} file đã minify\n")
        else:
            print()
    
    # Tối ưu hóa HTML
    if config.get('optimize_html', True):
        print("[>] Đang tối ưu hóa HTML...")
        backup_folder_name = config.get('backup_folder', 'backup_original')
        html_files = []
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'vendor', '.idea', backup_folder_name if backup_dir else '']]
            for file in files:
                if file.endswith(('.html', '.htm')):
                    html_files.append(os.path.join(root, file))
        
        for html_file in html_files:
            result = optimize_html_file(html_file, config, backup_dir)
            if result.get('success'):
                stats['html']['processed'] += 1
                if 'saved' in result:
                    stats['html']['saved'] += result['saved']
                    rel_path = os.path.relpath(html_file, project_path)
                    print(f"  ✓ {rel_path} - Giảm {result['saved_percent']:.1f}%")
            else:
                stats['html']['errors'] += 1
                print(f"  ✗ {os.path.relpath(html_file, project_path)} - Lỗi: {result.get('error', 'Unknown')}")
        
        print(f"[OK] Đã tối ưu {stats['html']['processed']} file HTML\n")
    
    # Tạo .htaccess
    if config.get('create_htaccess', True):
        print("[>] Đang tạo/cập nhật file .htaccess...")
        result = create_htaccess(project_path, config)
        if result.get('success'):
            if result.get('skipped'):
                print(f"[i] {result.get('reason', 'File đã có cấu hình cache')}\n")
            else:
                print("[OK] Đã tạo/cập nhật file .htaccess với cache headers\n")
        else:
            print(f"[X] Lỗi tạo .htaccess: {result.get('error', 'Unknown')}\n")
    
    # Tổng kết
    print("=" * 70)
    print("  TONG KET")
    print("=" * 70)
    print(f"\nCSS: {stats['css']['processed']} file - Tiết kiệm: {stats['css']['saved'] / 1024:.2f} KB")
    print(f"JavaScript: {stats['js']['processed']} file - Tiết kiệm: {stats['js']['saved'] / 1024:.2f} KB")
    print(f"HTML: {stats['html']['processed']} file - Tiết kiệm: {stats['html']['saved'] / 1024:.2f} KB")
    
    total_saved = stats['css']['saved'] + stats['js']['saved'] + stats['html']['saved']
    print(f"\nTổng tiết kiệm: {total_saved / 1024:.2f} KB ({total_saved / (1024 * 1024):.2f} MB)")
    
    if backup_dir:
        print(f"\n[i] File gốc đã được backup tại: {backup_dir}")
    
    print("\n[OK] Hoàn thành tối ưu hóa!")


def get_projects_list(htdocs_path):
    """Lấy danh sách dự án từ thư mục htdocs"""
    projects = []
    
    if not os.path.exists(htdocs_path):
        return projects
    
    try:
        for item in os.listdir(htdocs_path):
            item_path = os.path.join(htdocs_path, item)
            if (os.path.isdir(item_path) and 
                item not in ['.git', 'node_modules', '.idea', '__pycache__', 'vendor'] and
                not item.startswith('.')):
                projects.append(item)
    except Exception as e:
        print(f"[!] Lỗi đọc thư mục: {e}")
    
    return sorted(projects)


def show_settings_menu(config):
    """Hiển thị menu cài đặt"""
    while True:
        print("\n" + "=" * 70)
        print("  CAI DAT")
        print("=" * 70)
        print(f"\n1. Đường dẫn htdocs mặc định: {config.get('default_htdocs_path', 'Chưa cấu hình')}")
        print(f"2. Tối ưu CSS: {'Bật' if config.get('optimize_css', True) else 'Tắt'}")
        print(f"3. Tối ưu JavaScript: {'Bật' if config.get('optimize_js', True) else 'Tắt'}")
        print(f"4. Tối ưu HTML: {'Bật' if config.get('optimize_html', True) else 'Tắt'}")
        print(f"5. Tạo .htaccess: {'Bật' if config.get('create_htaccess', True) else 'Tắt'}")
        print(f"6. Backup file gốc: {'Bật' if config.get('backup_files', True) else 'Tắt'}")
        print(f"7. Thư mục backup: {config.get('backup_folder', 'backup_original')}")
        print("\n0. Quay lại menu chính")
        print("=" * 70)
        
        choice = input("\nChọn mục cần chỉnh sửa (số): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            new_path = input("Nhập đường dẫn htdocs mặc định: ").strip().strip('"')
            if new_path:
                config['default_htdocs_path'] = new_path
                save_config(config)
                print("[OK] Đã cập nhật!")
            else:
                print("[X] Đường dẫn không hợp lệ!")
        elif choice == '2':
            config['optimize_css'] = not config.get('optimize_css', True)
            save_config(config)
            print(f"[OK] Đã {'bật' if config['optimize_css'] else 'tắt'} tối ưu CSS!")
        elif choice == '3':
            config['optimize_js'] = not config.get('optimize_js', True)
            save_config(config)
            print(f"[OK] Đã {'bật' if config['optimize_js'] else 'tắt'} tối ưu JavaScript!")
        elif choice == '4':
            config['optimize_html'] = not config.get('optimize_html', True)
            save_config(config)
            print(f"[OK] Đã {'bật' if config['optimize_html'] else 'tắt'} tối ưu HTML!")
        elif choice == '5':
            config['create_htaccess'] = not config.get('create_htaccess', True)
            save_config(config)
            print(f"[OK] Đã {'bật' if config['create_htaccess'] else 'tắt'} tạo .htaccess!")
        elif choice == '6':
            config['backup_files'] = not config.get('backup_files', True)
            save_config(config)
            print(f"[OK] Đã {'bật' if config['backup_files'] else 'tắt'} backup file gốc!")
        elif choice == '7':
            new_folder = input("Nhập tên thư mục backup: ").strip()
            if new_folder:
                config['backup_folder'] = new_folder
                save_config(config)
                print("[OK] Đã cập nhật!")
            else:
                print("[X] Tên thư mục không hợp lệ!")
        else:
            print("[X] Lựa chọn không hợp lệ!")


def main():
    """Hàm chính của tool"""
    print_header()
    
    config = load_config()
    default_path = config.get('default_htdocs_path', r'C:\xampp\htdocs')
    
    while True:
        # Hiển thị danh sách dự án
        print("\n" + "=" * 70)
        print("  DANH SACH DU AN")
        print("=" * 70)
        print(f"\n📁 Đường dẫn: {default_path}")
        
        projects = get_projects_list(default_path)
        
        if projects:
            print(f"\nTìm thấy {len(projects)} dự án:\n")
            for idx, project in enumerate(projects, start=1):
                print(f"  {idx}. {project}")
        else:
            if not os.path.exists(default_path):
                print(f"\n[!] Đường dẫn không tồn tại: {default_path}")
                print("[i] Vui lòng cấu hình lại đường dẫn trong menu Cài đặt (s)")
            else:
                print("\n[!] Không tìm thấy dự án nào trong thư mục này")
        
        print("\n" + "-" * 70)
        print("HUONG DAN:")
        print("  [so]      - Chon du an theo so thu tu")
        print("  [duong dan] - Nhap duong dan du an de toi uu")
        print("  s          - Cai dat")
        print("  0 hoac q   - Thoat")
        print("=" * 70)
        
        choice = input("\nChon du an hoac lenh: ").strip().strip('"')
        
        if not choice:
            continue
        
        choice_lower = choice.lower()
        
        # Thoát
        if choice_lower in ['0', 'q', 'quit', 'exit']:
            print("\n[*] Thoat tool")
            break
        
        # Cài đặt
        elif choice_lower in ['s', 'settings', 'cai dat']:
            show_settings_menu(config)
            config = load_config()  # Reload config sau khi thay đổi
            default_path = config.get('default_htdocs_path', r'C:\xampp\htdocs')
            continue
        
        # Kiểm tra xem có phải là số không
        try:
            idx = int(choice)
            if 1 <= idx <= len(projects):
                # Chọn dự án từ danh sách
                project_path = os.path.join(default_path, projects[idx - 1])
            else:
                print(f"[X] So thu tu khong hop le! (1-{len(projects)})")
                continue
        except ValueError:
            # Không phải số, coi như đường dẫn
            project_path = choice
            
            # Nếu đường dẫn tương đối, thử kết hợp với default_path
            if not os.path.isabs(project_path):
                # Có thể là tên dự án
                if project_path in projects:
                    project_path = os.path.join(default_path, project_path)
                else:
                    # Thử kết hợp với default_path
                    possible_path = os.path.join(default_path, project_path)
                    if os.path.exists(possible_path):
                        project_path = possible_path
        
        # Kiểm tra đường dẫn hợp lệ
        if not project_path or not os.path.exists(project_path):
            print(f"[X] Đường dẫn không hợp lệ hoặc không tồn tại: {project_path}")
            continue
        
        if not os.path.isdir(project_path):
            print(f"[X] Đường dẫn không phải là thư mục: {project_path}")
            continue
        
        # Xác nhận trước khi tối ưu
        print(f"\n[!] Bạn sắp tối ưu hóa dự án: {project_path}")
        if config.get('backup_files', True):
            print(f"[i] File gốc sẽ được backup vào thư mục: {config.get('backup_folder', 'backup_original')}")
        else:
            print("[!] CẢNH BÁO: Backup đã tắt, file gốc sẽ bị thay đổi!")
        
        confirm = input("\nXác nhận tối ưu hóa? (y/N): ").strip().lower()
        if confirm != 'y':
            print("[*] Đã hủy")
            continue
        
        # Thực hiện tối ưu hóa
        optimize_project(project_path, config)
        
        input("\nNhấn Enter để tiếp tục...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[X] Đã hủy!")
    except Exception as e:
        print(f"\n[X] Lỗi: {e}")
        import traceback
        traceback.print_exc()

