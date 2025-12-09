#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Kiểm tra hiệu năng dự án website
Mục đích: Phân tích và đưa ra gợi ý tối ưu hóa hiệu năng cho dự án website
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

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
    print("  TOOL KIEM TRA HIEU NANG WEBSITE")
    print("=" * 70)
    print()


def get_config_file():
    """Lấy đường dẫn file config"""
    script_dir = Path(__file__).resolve().parent
    config_file = script_dir / "performance_config.json"
    return config_file


def load_config():
    """Load cấu hình từ file"""
    config_file = get_config_file()
    
    default_config = {
        'version': '1.0',
        'default_htdocs_path': r'C:\xampp\htdocs',
        'check_css': True,
        'check_js': True,
        'check_images': True,
        'check_html': True,
        'check_php': True,
        'max_file_size_mb': 1.0,  # MB
        'max_image_size_kb': 500,  # KB
        'check_minified': True,
        'check_duplicates': True
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


def is_minified_file(file_path):
    """Kiểm tra file có được minified không"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Kiểm tra một số dấu hiệu minified
            lines = content.split('\n')
            if len(lines) > 0:
                # File minified thường có ít dòng, ít khoảng trắng
                avg_line_length = len(content) / len(lines) if len(lines) > 0 else 0
                # Nếu độ dài trung bình dòng > 100 và ít dòng, có thể là minified
                if avg_line_length > 100 and len(lines) < 50:
                    return True
                # Hoặc nếu có ít khoảng trắng và không có comment
                if content.count(' ') < len(content) * 0.1 and '//' not in content[:1000]:
                    return True
        return False
    except Exception:
        return False


def analyze_css_files(project_path, config, issues):
    """Phân tích các file CSS"""
    css_files = []
    total_size = 0
    
    for root, dirs, files in os.walk(project_path):
        # Bỏ qua các thư mục không cần thiết
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'vendor', '.idea']]
        
        for file in files:
            if file.endswith('.css'):
                file_path = os.path.join(root, file)
                size_mb = get_file_size_mb(file_path)
                total_size += size_mb
                css_files.append({
                    'path': os.path.relpath(file_path, project_path),
                    'size_mb': size_mb,
                    'minified': is_minified_file(file_path)
                })
                
                # Kiểm tra file quá lớn
                if size_mb > config.get('max_file_size_mb', 1.0):
                    issues['large_files'].append({
                        'type': 'CSS',
                        'path': os.path.relpath(file_path, project_path),
                        'size_mb': round(size_mb, 2),
                        'recommendation': f'File CSS quá lớn ({round(size_mb, 2)} MB). Nên tách nhỏ hoặc minify.'
                    })
                
                # Kiểm tra file chưa minified
                if config.get('check_minified', True) and not css_files[-1]['minified']:
                    issues['unminified_files'].append({
                        'type': 'CSS',
                        'path': os.path.relpath(file_path, project_path),
                        'size_mb': round(size_mb, 2),
                        'recommendation': 'File CSS chưa được minify. Nên sử dụng công cụ minify để giảm kích thước.'
                    })
    
    return css_files, total_size


def analyze_js_files(project_path, config, issues):
    """Phân tích các file JavaScript"""
    js_files = []
    total_size = 0
    
    for root, dirs, files in os.walk(project_path):
        # Bỏ qua các thư mục không cần thiết
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'vendor', '.idea']]
        
        for file in files:
            if file.endswith('.js') and not file.endswith('.min.js'):
                file_path = os.path.join(root, file)
                size_mb = get_file_size_mb(file_path)
                total_size += size_mb
                js_files.append({
                    'path': os.path.relpath(file_path, project_path),
                    'size_mb': size_mb,
                    'minified': is_minified_file(file_path)
                })
                
                # Kiểm tra file quá lớn
                if size_mb > config.get('max_file_size_mb', 1.0):
                    issues['large_files'].append({
                        'type': 'JavaScript',
                        'path': os.path.relpath(file_path, project_path),
                        'size_mb': round(size_mb, 2),
                        'recommendation': f'File JS quá lớn ({round(size_mb, 2)} MB). Nên tách nhỏ hoặc minify.'
                    })
                
                # Kiểm tra file chưa minified
                if config.get('check_minified', True) and not js_files[-1]['minified']:
                    issues['unminified_files'].append({
                        'type': 'JavaScript',
                        'path': os.path.relpath(file_path, project_path),
                        'size_mb': round(size_mb, 2),
                        'recommendation': 'File JS chưa được minify. Nên sử dụng công cụ minify để giảm kích thước.'
                    })
    
    return js_files, total_size


def analyze_images(project_path, config, issues):
    """Phân tích các file hình ảnh"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    image_files = []
    total_size = 0
    large_images = []
    
    for root, dirs, files in os.walk(project_path):
        # Bỏ qua các thư mục không cần thiết
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'vendor', '.idea']]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in image_extensions:
                file_path = os.path.join(root, file)
                size_kb = get_file_size_kb(file_path)
                size_mb = size_kb / 1024
                total_size += size_mb
                
                image_files.append({
                    'path': os.path.relpath(file_path, project_path),
                    'size_kb': round(size_kb, 2),
                    'extension': ext
                })
                
                # Kiểm tra ảnh quá lớn
                max_size_kb = config.get('max_image_size_kb', 500)
                if size_kb > max_size_kb:
                    large_images.append({
                        'path': os.path.relpath(file_path, project_path),
                        'size_kb': round(size_kb, 2),
                        'extension': ext
                    })
                    
                    issues['large_images'].append({
                        'type': 'Image',
                        'path': os.path.relpath(file_path, project_path),
                        'size_kb': round(size_kb, 2),
                        'recommendation': f'Ảnh quá lớn ({round(size_kb, 2)} KB). Nên nén ảnh hoặc sử dụng format WebP.'
                    })
    
    return image_files, total_size, large_images


def analyze_html_files(project_path, config, issues):
    """Phân tích các file HTML"""
    html_files = []
    total_size = 0
    
    for root, dirs, files in os.walk(project_path):
        # Bỏ qua các thư mục không cần thiết
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'vendor', '.idea']]
        
        for file in files:
            if file.endswith(('.html', '.htm', '.php')):
                file_path = os.path.join(root, file)
                size_mb = get_file_size_mb(file_path)
                total_size += size_mb
                
                html_files.append({
                    'path': os.path.relpath(file_path, project_path),
                    'size_mb': size_mb
                })
                
                # Kiểm tra file HTML quá lớn
                if size_mb > 0.5:  # HTML > 500KB là quá lớn
                    issues['large_files'].append({
                        'type': 'HTML/PHP',
                        'path': os.path.relpath(file_path, project_path),
                        'size_mb': round(size_mb, 2),
                        'recommendation': f'File HTML/PHP quá lớn ({round(size_mb, 2)} MB). Nên tối ưu code, loại bỏ code không cần thiết.'
                    })
    
    return html_files, total_size


def analyze_php_files(project_path, config, issues):
    """Phân tích các file PHP"""
    php_files = []
    total_size = 0
    
    for root, dirs, files in os.walk(project_path):
        # Bỏ qua các thư mục không cần thiết
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'vendor', '.idea']]
        
        for file in files:
            if file.endswith('.php'):
                file_path = os.path.join(root, file)
                size_mb = get_file_size_mb(file_path)
                total_size += size_mb
                
                php_files.append({
                    'path': os.path.relpath(file_path, project_path),
                    'size_mb': size_mb
                })
                
                # Kiểm tra file PHP quá lớn (> 100KB thường có vấn đề)
                if size_mb > 0.1:
                    issues['large_php_files'].append({
                        'type': 'PHP',
                        'path': os.path.relpath(file_path, project_path),
                        'size_mb': round(size_mb, 2),
                        'recommendation': f'File PHP quá lớn ({round(size_mb, 2)} MB). Nên tách thành các module nhỏ hơn.'
                    })
    
    return php_files, total_size


def check_caching_headers(project_path, issues):
    """Kiểm tra cấu hình caching (htaccess, nginx config)"""
    htaccess_path = os.path.join(project_path, '.htaccess')
    
    if os.path.exists(htaccess_path):
        try:
            with open(htaccess_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if 'Cache-Control' not in content and 'Expires' not in content:
                    issues['caching'].append({
                        'type': 'Cache Headers',
                        'path': '.htaccess',
                        'recommendation': 'Thiếu cấu hình cache headers. Nên thêm Cache-Control và Expires headers để tăng tốc độ tải trang.'
                    })
        except Exception:
            pass
    else:
        issues['caching'].append({
            'type': 'Cache Headers',
            'path': 'Không có file .htaccess',
            'recommendation': 'Nên tạo file .htaccess với cấu hình cache headers để tối ưu hiệu năng.'
        })


def generate_report(project_path, config, analysis_results, issues, output_file):
    """Tạo báo cáo gợi ý tối ưu hóa"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = []
    report.append("=" * 80)
    report.append("  BÁO CÁO Kiểm tra hiệu năng dự án website")
    report.append("=" * 80)
    report.append(f"\n📁 Dự án: {project_path}")
    report.append(f"📅 Thời gian: {timestamp}")
    report.append("\n" + "=" * 80)
    
    # Tổng quan
    report.append("\n📊 TỔNG QUAN")
    report.append("-" * 80)
    report.append(f"Tổng số file CSS: {len(analysis_results['css_files'])}")
    report.append(f"Tổng kích thước CSS: {round(analysis_results['css_size'], 2)} MB")
    report.append(f"Tổng số file JavaScript: {len(analysis_results['js_files'])}")
    report.append(f"Tổng kích thước JavaScript: {round(analysis_results['js_size'], 2)} MB")
    report.append(f"Tổng số file hình ảnh: {len(analysis_results['image_files'])}")
    report.append(f"Tổng kích thước hình ảnh: {round(analysis_results['image_size'], 2)} MB")
    report.append(f"Tổng số file HTML/PHP: {len(analysis_results['html_files'])}")
    report.append(f"Tổng kích thước HTML/PHP: {round(analysis_results['html_size'], 2)} MB")
    report.append(f"Tổng số file PHP: {len(analysis_results['php_files'])}")
    report.append(f"Tổng kích thước PHP: {round(analysis_results['php_size'], 2)} MB")
    
    # Các vấn đề phát hiện
    total_issues = sum(len(v) for v in issues.values())
    report.append("\n" + "=" * 80)
    report.append("🔍 CÁC VẤN ĐỀ PHÁT HIỆN")
    report.append("=" * 80)
    report.append(f"\nTổng số vấn đề: {total_issues}")
    
    if issues['large_files']:
        report.append(f"\n📦 File quá lớn ({len(issues['large_files'])}):")
        report.append("-" * 80)
        for item in issues['large_files']:
            report.append(f"  • {item['type']}: {item['path']}")
            report.append(f"    Kích thước: {item['size_mb']} MB")
            report.append(f"    💡 Gợi ý: {item['recommendation']}")
            report.append("")
    
    if issues['large_images']:
        report.append(f"\n🖼️  Hình ảnh quá lớn ({len(issues['large_images'])}):")
        report.append("-" * 80)
        for item in issues['large_images']:
            report.append(f"  • {item['path']}")
            report.append(f"    Kích thước: {item['size_kb']} KB")
            report.append(f"    💡 Gợi ý: {item['recommendation']}")
            report.append("")
    
    if issues['unminified_files']:
        report.append(f"\n📝 File chưa minify ({len(issues['unminified_files'])}):")
        report.append("-" * 80)
        for item in issues['unminified_files'][:20]:  # Chỉ hiển thị 20 file đầu
            report.append(f"  • {item['type']}: {item['path']}")
            report.append(f"    💡 Gợi ý: {item['recommendation']}")
            report.append("")
        if len(issues['unminified_files']) > 20:
            report.append(f"  ... và {len(issues['unminified_files']) - 20} file khác")
            report.append("")
    
    if issues['large_php_files']:
        report.append(f"\n🐘 File PHP quá lớn ({len(issues['large_php_files'])}):")
        report.append("-" * 80)
        for item in issues['large_php_files']:
            report.append(f"  • {item['path']}")
            report.append(f"    Kích thước: {item['size_mb']} MB")
            report.append(f"    💡 Gợi ý: {item['recommendation']}")
            report.append("")
    
    if issues['caching']:
        report.append(f"\n⚡ Vấn đề về Cache ({len(issues['caching'])}):")
        report.append("-" * 80)
        for item in issues['caching']:
            report.append(f"  • {item['type']}: {item['path']}")
            report.append(f"    💡 Gợi ý: {item['recommendation']}")
            report.append("")
    
    # Gợi ý tối ưu hóa tổng thể
    report.append("\n" + "=" * 80)
    report.append("💡 GỢI Ý TỐI ƯU HÓA TỔNG THỂ")
    report.append("=" * 80)
    
    recommendations = []
    
    if issues['unminified_files']:
        recommendations.append({
            'priority': 'Cao',
            'title': 'Minify CSS và JavaScript',
            'description': 'Sử dụng các công cụ như UglifyJS, Terser, cssnano để minify code. Giảm kích thước file lên đến 50-70%.'
        })
    
    if issues['large_images']:
        recommendations.append({
            'priority': 'Cao',
            'title': 'Tối ưu hóa hình ảnh',
            'description': 'Nén ảnh bằng TinyPNG, ImageOptim hoặc chuyển sang format WebP. Giảm kích thước ảnh lên đến 80%.'
        })
    
    if issues['caching']:
        recommendations.append({
            'priority': 'Trung bình',
            'title': 'Thiết lập Cache Headers',
            'description': 'Thêm Cache-Control và Expires headers trong .htaccess để browser cache static files.'
        })
    
    if issues['large_php_files']:
        recommendations.append({
            'priority': 'Trung bình',
            'title': 'Tách nhỏ file PHP',
            'description': 'Chia nhỏ file PHP lớn thành các module/class nhỏ hơn để dễ bảo trì và tối ưu hiệu năng.'
        })
    
    if analysis_results['css_size'] + analysis_results['js_size'] > 5:
        recommendations.append({
            'priority': 'Trung bình',
            'title': 'Code Splitting',
            'description': 'Tách CSS và JS thành nhiều file nhỏ, chỉ load khi cần thiết (lazy loading).'
        })
    
    recommendations.append({
        'priority': 'Thấp',
        'title': 'Sử dụng CDN',
        'description': 'Sử dụng CDN để host các thư viện như jQuery, Bootstrap để giảm tải server và tăng tốc độ.'
    })
    
    recommendations.append({
        'priority': 'Thấp',
        'title': 'Gzip Compression',
        'description': 'Kích hoạt Gzip compression trong Apache/Nginx để nén response, giảm bandwidth lên đến 70%.'
    })
    
    for rec in recommendations:
        report.append(f"\n🎯 {rec['priority']}: {rec['title']}")
        report.append(f"   {rec['description']}")
    
    report.append("\n" + "=" * 80)
    report.append("📚 TÀI LIỆU THAM KHẢO")
    report.append("=" * 80)
    report.append("\n• Google PageSpeed Insights: https://pagespeed.web.dev/")
    report.append("• GTmetrix: https://gtmetrix.com/")
    report.append("• WebPageTest: https://www.webpagetest.org/")
    report.append("• Minify CSS: https://cssnano.co/")
    report.append("• Minify JS: https://terser.org/")
    report.append("• Optimize Images: https://tinypng.com/")
    report.append("• WebP Converter: https://developers.google.com/speed/webp")
    
    report.append("\n" + "=" * 80)
    report.append(f"\nBáo cáo được tạo tự động bởi Website Performance Checker")
    report.append("=" * 80)
    
    # Ghi file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        return True
    except Exception as e:
        print(f"[X] Lỗi ghi file báo cáo: {e}")
        return False


def show_settings_menu(config):
    """Hiển thị menu cài đặt"""
    while True:
        print("\n" + "=" * 70)
        print("  CAI DAT")
        print("=" * 70)
        print(f"\n1. Đường dẫn htdocs mặc định: {config.get('default_htdocs_path', 'Chưa cấu hình')}")
        print(f"2. Kích thước file tối đa (MB): {config.get('max_file_size_mb', 1.0)}")
        print(f"3. Kích thước ảnh tối đa (KB): {config.get('max_image_size_kb', 500)}")
        print(f"4. Kiểm tra file minified: {'Bật' if config.get('check_minified', True) else 'Tắt'}")
        print(f"5. Kiểm tra CSS: {'Bật' if config.get('check_css', True) else 'Tắt'}")
        print(f"6. Kiểm tra JavaScript: {'Bật' if config.get('check_js', True) else 'Tắt'}")
        print(f"7. Kiểm tra hình ảnh: {'Bật' if config.get('check_images', True) else 'Tắt'}")
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
            try:
                new_size = float(input("Nhập kích thước file tối đa (MB): ").strip())
                if new_size > 0:
                    config['max_file_size_mb'] = new_size
                    save_config(config)
                    print("[OK] Đã cập nhật!")
                else:
                    print("[X] Giá trị phải lớn hơn 0!")
            except ValueError:
                print("[X] Giá trị không hợp lệ!")
        elif choice == '3':
            try:
                new_size = int(input("Nhập kích thước ảnh tối đa (KB): ").strip())
                if new_size > 0:
                    config['max_image_size_kb'] = new_size
                    save_config(config)
                    print("[OK] Đã cập nhật!")
                else:
                    print("[X] Giá trị phải lớn hơn 0!")
            except ValueError:
                print("[X] Giá trị không hợp lệ!")
        elif choice == '4':
            config['check_minified'] = not config.get('check_minified', True)
            save_config(config)
            print(f"[OK] Đã {'bật' if config['check_minified'] else 'tắt'} kiểm tra file minified!")
        elif choice == '5':
            config['check_css'] = not config.get('check_css', True)
            save_config(config)
            print(f"[OK] Đã {'bật' if config['check_css'] else 'tắt'} kiểm tra CSS!")
        elif choice == '6':
            config['check_js'] = not config.get('check_js', True)
            save_config(config)
            print(f"[OK] Đã {'bật' if config['check_js'] else 'tắt'} kiểm tra JavaScript!")
        elif choice == '7':
            config['check_images'] = not config.get('check_images', True)
            save_config(config)
            print(f"[OK] Đã {'bật' if config['check_images'] else 'tắt'} kiểm tra hình ảnh!")
        else:
            print("[X] Lựa chọn không hợp lệ!")


def run_performance_check(project_path, config):
    """Chạy kiểm tra hiệu năng cho dự án"""
    # Kiểm tra đường dẫn hợp lệ
    if not project_path or not os.path.exists(project_path):
        print(f"[X] Đường dẫn không hợp lệ hoặc không tồn tại: {project_path}")
        return False
    
    if not os.path.isdir(project_path):
        print(f"[X] Đường dẫn không phải là thư mục: {project_path}")
        return False
    
    print(f"\n[>] Đang kiểm tra dự án: {project_path}")
    print("[>] Vui lòng chờ...\n")
    
    # Khởi tạo kết quả phân tích
    issues = {
        'large_files': [],
        'large_images': [],
        'unminified_files': [],
        'large_php_files': [],
        'caching': []
    }
    
    analysis_results = {
        'css_files': [],
        'css_size': 0,
        'js_files': [],
        'js_size': 0,
        'image_files': [],
        'image_size': 0,
        'html_files': [],
        'html_size': 0,
        'php_files': [],
        'php_size': 0
    }
    
    # Phân tích các loại file
    if config.get('check_css', True):
        print("[>] Đang phân tích CSS...")
        css_files, css_size = analyze_css_files(project_path, config, issues)
        analysis_results['css_files'] = css_files
        analysis_results['css_size'] = css_size
        print(f"[OK] Đã phân tích {len(css_files)} file CSS")
    
    if config.get('check_js', True):
        print("[>] Đang phân tích JavaScript...")
        js_files, js_size = analyze_js_files(project_path, config, issues)
        analysis_results['js_files'] = js_files
        analysis_results['js_size'] = js_size
        print(f"[OK] Đã phân tích {len(js_files)} file JavaScript")
    
    if config.get('check_images', True):
        print("[>] Đang phân tích hình ảnh...")
        image_files, image_size, large_images = analyze_images(project_path, config, issues)
        analysis_results['image_files'] = image_files
        analysis_results['image_size'] = image_size
        print(f"[OK] Đã phân tích {len(image_files)} file hình ảnh")
    
    if config.get('check_html', True):
        print("[>] Đang phân tích HTML/PHP...")
        html_files, html_size = analyze_html_files(project_path, config, issues)
        analysis_results['html_files'] = html_files
        analysis_results['html_size'] = html_size
        print(f"[OK] Đã phân tích {len(html_files)} file HTML/PHP")
    
    if config.get('check_php', True):
        print("[>] Đang phân tích PHP...")
        php_files, php_size = analyze_php_files(project_path, config, issues)
        analysis_results['php_files'] = php_files
        analysis_results['php_size'] = php_size
        print(f"[OK] Đã phân tích {len(php_files)} file PHP")
    
    print("[>] Đang kiểm tra cache headers...")
    check_caching_headers(project_path, issues)
    
    # Tạo file báo cáo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    project_name = os.path.basename(project_path.rstrip('\\/'))
    output_file = os.path.join(project_path, f'performance_report_{project_name}_{timestamp}.txt')
    
    print(f"\n[>] Đang tạo báo cáo...")
    if generate_report(project_path, config, analysis_results, issues, output_file):
        print(f"\n[OK] Đã tạo báo cáo thành công!")
        print(f"    File: {output_file}")
        print(f"\n[>] Tổng số vấn đề phát hiện: {sum(len(v) for v in issues.values())}")
        return True
    else:
        print("\n[X] Lỗi tạo báo cáo!")
        return False


def get_projects_list(htdocs_path):
    """Lấy danh sách dự án từ thư mục htdocs"""
    projects = []
    
    if not os.path.exists(htdocs_path):
        return projects
    
    try:
        for item in os.listdir(htdocs_path):
            item_path = os.path.join(htdocs_path, item)
            # Bỏ qua các thư mục đặc biệt
            if (os.path.isdir(item_path) and 
                item not in ['.git', 'node_modules', '.idea', '__pycache__', 'vendor'] and
                not item.startswith('.')):
                projects.append(item)
    except Exception as e:
        print(f"[!] Lỗi đọc thư mục: {e}")
    
    return sorted(projects)


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
                project_path = os.path.join(default_path, project)
                # Hiển thị thêm thông tin nếu có
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
        print("  [duong dan] - Nhap duong dan du an de kiem tra")
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
                run_performance_check(project_path, config)
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
            
            # Kiểm tra và chạy
            run_performance_check(project_path, config)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[X] Đã hủy!")
    except Exception as e:
        print(f"\n[X] Lỗi: {e}")
        import traceback
        traceback.print_exc()

