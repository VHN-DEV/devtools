#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Quản lý Database MySQL (Bản beta)
Mục đích: Quản lý Database MySQL (Bản beta), backup/restore, chạy SQL queries, export/import
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

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
    print("  TOOL QUẢN LÝ DATABASE MYSQL")
    print("=" * 70)
    print()


def get_config_file():
    """Lấy đường dẫn file config"""
    script_dir = Path(__file__).resolve().parent
    config_file = script_dir / "database_config.json"
    return config_file


def load_config():
    """Load cấu hình từ file"""
    config_file = get_config_file()
    
    default_config = {
        'version': '1.0',
        'default_xampp_path': r'C:\xampp',
        'connections': [
            {
                'name': 'XAMPP Local',
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': '',
                'default_db': '',
                'xampp_path': r'C:\xampp'
            }
        ],
        'backup_folder': 'database_backups',
        'default_connection': 0
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


def get_mysql_path(connection):
    """Lấy đường dẫn MySQL từ XAMPP"""
    xampp_path = connection.get('xampp_path', r'C:\xampp')
    mysql_path = os.path.join(xampp_path, 'mysql', 'bin', 'mysql.exe')
    mysqldump_path = os.path.join(xampp_path, 'mysql', 'bin', 'mysqldump.exe')
    
    return mysql_path, mysqldump_path


def test_connection(connection):
    """Kiểm tra kết nối database"""
    mysql_path, _ = get_mysql_path(connection)
    
    if not os.path.exists(mysql_path):
        return False, "Không tìm thấy MySQL tại: " + mysql_path
    
    try:
        # Test connection bằng cách chạy lệnh mysql
        cmd = [
            mysql_path,
            '-h', connection['host'],
            '-P', str(connection['port']),
            '-u', connection['user']
        ]
        
        if connection.get('password'):
            cmd.extend(['-p' + connection['password']])  # -ppassword (no space)
        
        cmd.extend(['-e', 'SELECT 1'])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return True, "Kết nối thành công"
        else:
            return False, result.stderr or "Kết nối thất bại"
    except Exception as e:
        return False, str(e)


def list_databases(connection):
    """Liệt kê danh sách databases"""
    mysql_path, _ = get_mysql_path(connection)
    
    if not os.path.exists(mysql_path):
        return []
    
    try:
        cmd = [
            mysql_path,
            '-h', connection['host'],
            '-P', str(connection['port']),
            '-u', connection['user']
        ]
        
        if connection.get('password'):
            cmd.append('-p' + connection['password'])  # -ppassword (no space)
        
        cmd.extend([
            '-e', 'SHOW DATABASES;',
            '-s',  # Silent mode
            '-N'   # Skip column names
        ])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            databases = [db.strip() for db in result.stdout.strip().split('\n') if db.strip()]
            # Bỏ qua system databases
            databases = [db for db in databases if db not in ['information_schema', 'performance_schema', 'mysql', 'sys']]
            return databases
        else:
            return []
    except Exception as e:
        print(f"[!] Lỗi: {e}")
        return []


def list_tables(connection, database):
    """Liệt kê danh sách tables trong database"""
    mysql_path, _ = get_mysql_path(connection)
    
    if not os.path.exists(mysql_path):
        return []
    
    try:
        cmd = [
            mysql_path,
            '-h', connection['host'],
            '-P', str(connection['port']),
            '-u', connection['user']
        ]
        
        if connection.get('password'):
            cmd.append('-p' + connection['password'])  # -ppassword (no space)
        
        cmd.extend([
            database,
            '-e', 'SHOW TABLES;',
            '-s',  # Silent mode
            '-N'   # Skip column names
        ])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            tables = [table.strip() for table in result.stdout.strip().split('\n') if table.strip()]
            return tables
        else:
            return []
    except Exception as e:
        print(f"[!] Lỗi: {e}")
        return []


def get_table_structure(connection, database, table):
    """Lấy cấu trúc của table"""
    mysql_path, _ = get_mysql_path(connection)
    
    if not os.path.exists(mysql_path):
        return None
    
    try:
        cmd = [
            mysql_path,
            '-h', connection['host'],
            '-P', str(connection['port']),
            '-u', connection['user']
        ]
        
        if connection.get('password'):
            cmd.append('-p' + connection['password'])  # -ppassword (no space)
        
        cmd.extend([
            database,
            '-e', f'DESCRIBE {table};'
        ])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except Exception as e:
        print(f"[!] Lỗi: {e}")
        return None


def backup_database(connection, database, output_file):
    """Backup database"""
    _, mysqldump_path = get_mysql_path(connection)
    
    if not os.path.exists(mysqldump_path):
        return False, "Không tìm thấy mysqldump tại: " + mysqldump_path
    
    try:
        # Tạo thư mục backup nếu chưa có
        backup_dir = os.path.dirname(output_file)
        if backup_dir and not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        
        cmd = [
            mysqldump_path,
            '-h', connection['host'],
            '-P', str(connection['port']),
            '-u', connection['user']
        ]
        
        if connection.get('password'):
            cmd.append('-p' + connection['password'])  # -ppassword (no space)
        
        cmd.extend([
            '--single-transaction',
            '--routines',
            '--triggers',
            database
        ])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300  # 5 minutes timeout
            )
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            return True, f"Backup thành công! Kích thước: {file_size:.2f} MB"
        else:
            return False, result.stderr or "Backup thất bại"
    except Exception as e:
        return False, str(e)


def restore_database(connection, database, input_file):
    """Restore database từ file SQL"""
    mysql_path, _ = get_mysql_path(connection)
    
    if not os.path.exists(mysql_path):
        return False, "Không tìm thấy MySQL tại: " + mysql_path
    
    if not os.path.exists(input_file):
        return False, "File không tồn tại: " + input_file
    
    try:
        cmd = [
            mysql_path,
            '-h', connection['host'],
            '-P', str(connection['port']),
            '-u', connection['user']
        ]
        
        if connection.get('password'):
            cmd.append('-p' + connection['password'])  # -ppassword (no space)
        
        cmd.append(database)
        
        with open(input_file, 'r', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300  # 5 minutes timeout
            )
        
        if result.returncode == 0:
            return True, "Restore thành công!"
        else:
            return False, result.stderr or "Restore thất bại"
    except Exception as e:
        return False, str(e)


def execute_query(connection, database, query):
    """Chạy SQL query"""
    mysql_path, _ = get_mysql_path(connection)
    
    if not os.path.exists(mysql_path):
        return False, None, "Không tìm thấy MySQL tại: " + mysql_path
    
    try:
        cmd = [
            mysql_path,
            '-h', connection['host'],
            '-P', str(connection['port']),
            '-u', connection['user']
        ]
        
        if connection.get('password'):
            cmd.append('-p' + connection['password'])  # -ppassword (no space)
        
        cmd.extend([
            database,
            '-e', query
        ])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, result.stdout, None
        else:
            return False, None, result.stderr or "Query thất bại"
    except Exception as e:
        return False, None, str(e)


def export_table(connection, database, table, output_file):
    """Export table ra file SQL"""
    _, mysqldump_path = get_mysql_path(connection)
    
    if not os.path.exists(mysqldump_path):
        return False, "Không tìm thấy mysqldump tại: " + mysqldump_path
    
    try:
        # Tạo thư mục nếu chưa có
        export_dir = os.path.dirname(output_file)
        if export_dir and not os.path.exists(export_dir):
            os.makedirs(export_dir, exist_ok=True)
        
        cmd = [
            mysqldump_path,
            '-h', connection['host'],
            '-P', str(connection['port']),
            '-u', connection['user']
        ]
        
        if connection.get('password'):
            cmd.append('-p' + connection['password'])  # -ppassword (no space)
        
        cmd.extend([
            '--single-transaction',
            database,
            table
        ])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300
            )
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file) / 1024  # KB
            return True, f"Export thành công! Kích thước: {file_size:.2f} KB"
        else:
            return False, result.stderr or "Export thất bại"
    except Exception as e:
        return False, str(e)


def show_connections_menu(config):
    """Hiển thị menu quản lý connections"""
    while True:
        print("\n" + "=" * 70)
        print("  QUẢN LÝ KẾT NỐI DATABASE")
        print("=" * 70)
        
        connections = config.get('connections', [])
        
        if connections:
            print("\nDanh sách kết nối:")
            for idx, conn in enumerate(connections):
                default_marker = " (Mặc định)" if idx == config.get('default_connection', 0) else ""
                print(f"  {idx + 1}. {conn['name']}{default_marker}")
                print(f"     Host: {conn['host']}:{conn['port']}, User: {conn['user']}")
        else:
            print("\n[!] Chưa có kết nối nào")
        
        print("\n" + "-" * 70)
        print("LỆNH:")
        print("  a - Thêm kết nối mới")
        print("  e [số] - Sửa kết nối")
        print("  d [số] - Xóa kết nối")
        print("  t [số] - Test kết nối")
        print("  s [số] - Đặt làm mặc định")
        print("  0 - Quay lại")
        print("=" * 70)
        
        choice = input("\nChọn lệnh: ").strip().lower()
        
        if choice == '0':
            break
        elif choice == 'a':
            add_connection(config, connections)
        elif choice.startswith('e '):
            idx_str = choice.replace('e ', '').strip()
            try:
                idx = int(idx_str) - 1
                if 0 <= idx < len(connections):
                    edit_connection(config, connections, idx)
                else:
                    print("[X] Số thứ tự không hợp lệ!")
            except ValueError:
                print("[X] Vui lòng nhập số hợp lệ!")
        elif choice.startswith('d '):
            idx_str = choice.replace('d ', '').strip()
            try:
                idx = int(idx_str) - 1
                if 0 <= idx < len(connections):
                    delete_connection(config, connections, idx)
                else:
                    print("[X] Số thứ tự không hợp lệ!")
            except ValueError:
                print("[X] Vui lòng nhập số hợp lệ!")
        elif choice.startswith('t '):
            idx_str = choice.replace('t ', '').strip()
            try:
                idx = int(idx_str) - 1
                if 0 <= idx < len(connections):
                    test_connection_result = test_connection(connections[idx])
                    if test_connection_result[0]:
                        print(f"[OK] {test_connection_result[1]}")
                    else:
                        print(f"[X] {test_connection_result[1]}")
                else:
                    print("[X] Số thứ tự không hợp lệ!")
            except ValueError:
                print("[X] Vui lòng nhập số hợp lệ!")
        elif choice.startswith('s '):
            idx_str = choice.replace('s ', '').strip()
            try:
                idx = int(idx_str) - 1
                if 0 <= idx < len(connections):
                    config['default_connection'] = idx
                    save_config(config)
                    print(f"[OK] Đã đặt '{connections[idx]['name']}' làm kết nối mặc định")
                else:
                    print("[X] Số thứ tự không hợp lệ!")
            except ValueError:
                print("[X] Vui lòng nhập số hợp lệ!")
        else:
            print("[X] Lenh khong hop le!")


def add_connection(config, connections):
    """Thêm kết nối mới"""
    print("\n" + "=" * 70)
    print("  THÊM KẾT NỐI MỚI")
    print("=" * 70)
    
    try:
        name = input("\nTên kết nối: ").strip()
        if not name:
            print("[X] Tên kết nối không được để trống!")
            return
        
        host = input("Host (mặc định: localhost): ").strip() or 'localhost'
        port = input("Port (mặc định: 3306): ").strip() or '3306'
        try:
            port = int(port)
        except ValueError:
            print("[X] Port phải là số!")
            return
        
        user = input("Username (mặc định: root): ").strip() or 'root'
        password = input("Password (Enter để để trống): ").strip()
        
        xampp_path = input(f"Đường dẫn XAMPP (mặc định: {config.get('default_xampp_path', r'C:\xampp')}): ").strip()
        if not xampp_path:
            xampp_path = config.get('default_xampp_path', r'C:\xampp')
        
        default_db = input("Database mặc định (Enter để để trống): ").strip()
        
        new_connection = {
            'name': name,
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'default_db': default_db,
            'xampp_path': xampp_path
        }
        
        connections.append(new_connection)
        config['connections'] = connections
        
        if save_config(config):
            print(f"\n[OK] Đã thêm kết nối: {name}")
        else:
            print("[X] Lỗi lưu config!")
            connections.pop()
    except Exception as e:
        print(f"[X] Lỗi: {e}")


def edit_connection(config, connections, idx):
    """Sửa kết nối"""
    conn = connections[idx]
    
    print("\n" + "=" * 70)
    print(f"  SỬA KẾT NỐI: {conn['name']}")
    print("=" * 70)
    print("(Nhấn Enter để giữ nguyên giá trị cũ)\n")
    
    try:
        new_name = input(f"Tên kết nối [{conn['name']}]: ").strip()
        if new_name:
            conn['name'] = new_name
        
        new_host = input(f"Host [{conn['host']}]: ").strip()
        if new_host:
            conn['host'] = new_host
        
        new_port = input(f"Port [{conn['port']}]: ").strip()
        if new_port:
            try:
                conn['port'] = int(new_port)
            except ValueError:
                print("[!] Port không hợp lệ, giữ nguyên giá trị cũ")
        
        new_user = input(f"Username [{conn['user']}]: ").strip()
        if new_user:
            conn['user'] = new_user
        
        new_password = input("Password (Enter để giữ nguyên, 'none' để xóa): ").strip()
        if new_password:
            if new_password.lower() == 'none':
                conn['password'] = ''
            else:
                conn['password'] = new_password
        
        new_xampp = input(f"Đường dẫn XAMPP [{conn.get('xampp_path', '')}]: ").strip()
        if new_xampp:
            conn['xampp_path'] = new_xampp
        
        new_db = input(f"Database mặc định [{conn.get('default_db', '')}]: ").strip()
        if new_db:
            conn['default_db'] = new_db
        
        if save_config(config):
            print(f"\n[OK] Đã lưu thay đổi!")
        else:
            print("[X] Lỗi lưu config!")
    except Exception as e:
        print(f"[X] Lỗi: {e}")


def delete_connection(config, connections, idx):
    """Xóa kết nối"""
    conn = connections[idx]
    
    print(f"\n[!] Bạn sắp xóa kết nối: {conn['name']}")
    confirm = input("Xác nhận xóa? (YES để xác nhận): ").strip()
    
    if confirm == "YES":
        connections.pop(idx)
        config['connections'] = connections
        
        # Nếu xóa connection mặc định, chuyển sang connection đầu tiên
        if config.get('default_connection', 0) == idx:
            if connections:
                config['default_connection'] = 0
            else:
                config['default_connection'] = 0
        
        # Điều chỉnh default_connection nếu cần
        if config.get('default_connection', 0) > idx:
            config['default_connection'] -= 1
        
        if save_config(config):
            print(f"\n[OK] Đã xóa kết nối: {conn['name']}")
        else:
            print("[X] Lỗi lưu config!")
            connections.insert(idx, conn)
    else:
        print("[*] Đã hủy")


def show_databases_menu(connection, config):
    """Hiển thị menu quản lý databases"""
    while True:
        print("\n" + "=" * 70)
        print(f"  DATABASES - {connection['name']}")
        print("=" * 70)
        print(f"Host: {connection['host']}:{connection['port']}, User: {connection['user']}\n")
        
        databases = list_databases(connection)
        
        if databases:
            print("Danh sach databases:")
            for idx, db in enumerate(databases, start=1):
                print(f"  {idx}. {db}")
        else:
            print("[!] Không tìm thấy database nào hoặc không thể kết nối")
        
        print("\n" + "-" * 70)
        print("LỆNH:")
        print("  [số] - Chọn database")
        print("  b [số] - Backup database")
        print("  r - Restore database")
        print("  q - Chạy SQL query")
        print("  0 - Quay lại")
        print("=" * 70)
        
        choice = input("\nChọn lệnh: ").strip().lower()
        
        if choice == '0':
            break
        elif choice.startswith('b '):
            idx_str = choice.replace('b ', '').strip()
            try:
                idx = int(idx_str) - 1
                if 0 <= idx < len(databases):
                    backup_db_menu(connection, databases[idx], config)
                else:
                    print("[X] Số thứ tự không hợp lệ!")
            except ValueError:
                print("[X] Vui lòng nhập số hợp lệ!")
        elif choice == 'r':
            restore_db_menu(connection, config)
        elif choice == 'q':
            query_menu(connection, config)
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(databases):
                    show_tables_menu(connection, databases[idx], config)
                else:
                    print("[X] Số thứ tự không hợp lệ!")
            except ValueError:
                print("[X] Lệnh không hợp lệ!")


def backup_db_menu(connection, database, config):
    """Menu backup database"""
    print(f"\n[>] Backup database: {database}")
    
    # Tạo thư mục backup
    backup_folder = config.get('backup_folder', 'database_backups')
    backup_dir = os.path.join(os.path.expanduser('~'), backup_folder)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)
    
    # Tên file backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'{database}_{timestamp}.sql')
    
    print(f"[>] Đang backup...")
    success, message = backup_database(connection, database, backup_file)
    
    if success:
        print(f"[OK] {message}")
        print(f"     File: {backup_file}")
    else:
        print(f"[X] {message}")
    
    input("\nNhấn Enter để tiếp tục...")


def restore_db_menu(connection, config):
    """Menu restore database"""
    print("\n" + "=" * 70)
    print("  RESTORE DATABASE")
    print("=" * 70)
    
    backup_folder = config.get('backup_folder', 'database_backups')
    backup_dir = os.path.join(os.path.expanduser('~'), backup_folder)
    
    # Hiển thị danh sách file backup
    if os.path.exists(backup_dir):
        backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]
        if backup_files:
            print("\nDanh sach file backup:")
            for idx, file in enumerate(sorted(backup_files, reverse=True)[:20], start=1):
                file_path = os.path.join(backup_dir, file)
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                print(f"  {idx}. {file} ({file_size:.2f} MB)")
        else:
            print("\n[!] Không có file backup nào")
    else:
        print(f"\n[!] Thư mục backup không tồn tại: {backup_dir}")
    
    backup_file = input("\nNhập đường dẫn file SQL (hoặc tên file): ").strip().strip('"')
    
    if not backup_file:
        print("[*] Đã hủy")
        return
    
    # Nếu chỉ là tên file, tìm trong thư mục backup
    if not os.path.isabs(backup_file) and os.path.exists(backup_dir):
        backup_file = os.path.join(backup_dir, backup_file)
    
    if not os.path.exists(backup_file):
        print(f"[X] File không tồn tại: {backup_file}")
        input("\nNhấn Enter để tiếp tục...")
        return
    
    database = input("Nhập tên database để restore (sẽ tạo mới nếu chưa có): ").strip()
    if not database:
        print("[X] Tên database không được để trống!")
        input("\nNhấn Enter để tiếp tục...")
        return
    
    print(f"\n[!] Bạn sắp restore database '{database}' từ file: {backup_file}")
    print("[!] CẢNH BÁO: Database hiện tại sẽ bị ghi đè!")
    confirm = input("Xác nhận? (YES để xác nhận): ").strip()
    
    if confirm != "YES":
        print("[*] Đã hủy")
        return
    
    print(f"\n[>] Đang restore...")
    success, message = restore_database(connection, database, backup_file)
    
    if success:
        print(f"[OK] {message}")
    else:
        print(f"[X] {message}")
    
    input("\nNhấn Enter để tiếp tục...")


def query_menu(connection, config):
    """Menu chạy SQL query"""
    print("\n" + "=" * 70)
    print("  CHẠY SQL QUERY")
    print("=" * 70)
    
    database = input("\nNhập tên database: ").strip()
    if not database:
        print("[X] Tên database không được để trống!")
        return
    
    print("\nNhập SQL query (kết thúc bằng ';'):")
    print("(Nhấn Enter để kết thúc nhập, 'exit' để thoát)")
    
    query_lines = []
    while True:
        line = input("SQL> " if not query_lines else "   > ").strip()
        if line.lower() == 'exit':
            return
        if not line and query_lines:
            break
        if line:
            query_lines.append(line)
    
    if not query_lines:
        print("[*] Không có query nào")
        return
    
    query = ' '.join(query_lines)
    
    print(f"\n[>] Đang chạy query...")
    success, output, error = execute_query(connection, database, query)
    
    if success:
        if output:
            print("\nKết quả:")
            print(output)
        else:
            print("[OK] Query đã chạy thành công")
    else:
        print(f"[X] Lỗi: {error}")
    
    input("\nNhấn Enter để tiếp tục...")


def show_tables_menu(connection, database, config):
    """Hiển thị menu quản lý tables"""
    while True:
        print("\n" + "=" * 70)
        print(f"  TABLES - {database}")
        print("=" * 70)
        
        tables = list_tables(connection, database)
        
        if tables:
            print("\nDanh sách tables:")
            for idx, table in enumerate(tables, start=1):
                print(f"  {idx}. {table}")
        else:
            print("\n[!] Không có table nào hoặc không thể kết nối")
        
        print("\n" + "-" * 70)
        print("LỆNH:")
        print("  [số] - Xem cấu trúc table")
        print("  e [số] - Export table")
        print("  b - Backup toàn bộ database")
        print("  0 - Quay lại")
        print("=" * 70)
        
        choice = input("\nChọn lệnh: ").strip().lower()
        
        if choice == '0':
            break
        elif choice.startswith('e '):
            idx_str = choice.replace('e ', '').strip()
            try:
                idx = int(idx_str) - 1
                if 0 <= idx < len(tables):
                    export_table_menu(connection, database, tables[idx], config)
                else:
                    print("[X] Số thứ tự không hợp lệ!")
            except ValueError:
                print("[X] Vui lòng nhập số hợp lệ!")
        elif choice == 'b':
            backup_db_menu(connection, database, config)
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(tables):
                    structure = get_table_structure(connection, database, tables[idx])
                    if structure:
                        print(f"\nCấu trúc table '{tables[idx]}':")
                        print(structure)
                    else:
                        print("[X] Không thể lấy cấu trúc table")
                    input("\nNhấn Enter để tiếp tục...")
                else:
                    print("[X] Số thứ tự không hợp lệ!")
            except ValueError:
                print("[X] Lệnh không hợp lệ!")


def export_table_menu(connection, database, table, config):
    """Menu export table"""
    print(f"\n[>] Export table: {table}")
    
    # Tạo thư mục export
    backup_folder = config.get('backup_folder', 'database_backups')
    export_dir = os.path.join(os.path.expanduser('~'), backup_folder, 'exports')
    if not os.path.exists(export_dir):
        os.makedirs(export_dir, exist_ok=True)
    
    # Tên file export
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_file = os.path.join(export_dir, f'{database}_{table}_{timestamp}.sql')
    
    print(f"[>] Dang export...")
    success, message = export_table(connection, database, table, export_file)
    
    if success:
        print(f"[OK] {message}")
        print(f"     File: {export_file}")
    else:
        print(f"[X] {message}")
    
    input("\nNhấn Enter để tiếp tục...")


def main():
    """Hàm chính của tool"""
    print_header()
    
    config = load_config()
    connections = config.get('connections', [])
    
    if not connections:
        print("[!] Chưa có kết nối nào. Vui lòng thêm kết nối trước.")
        show_connections_menu(config)
        config = load_config()
        connections = config.get('connections', [])
        
        if not connections:
            print("\n[!] Vẫn chưa có kết nối. Thoát tool.")
            return
    
    while True:
        # Lấy connection mặc định
        default_idx = config.get('default_connection', 0)
        if default_idx >= len(connections):
            default_idx = 0
            config['default_connection'] = 0
        
        current_connection = connections[default_idx]
        
        print("\n" + "=" * 70)
        print("  MENU CHÍNH")
        print("=" * 70)
        print(f"\nKết nối hiện tại: {current_connection['name']}")
        print(f"Host: {current_connection['host']}:{current_connection['port']}")
        print(f"User: {current_connection['user']}")
        
        print("\n" + "-" * 70)
        print("LỆNH:")
        print("  1 - Quản lý databases")
        print("  2 - Quản lý kết nối")
        print("  s - Cài đặt")
        print("  0 - Thoát")
        print("=" * 70)
        
        choice = input("\nChọn lệnh: ").strip().lower()
        
        if choice == '0':
            print("\n[*] Thoát tool")
            break
        elif choice == '1':
            show_databases_menu(current_connection, config)
        elif choice == '2':
            show_connections_menu(config)
            config = load_config()  # Reload config
            connections = config.get('connections', [])
        elif choice == 's':
            show_settings_menu(config)
            config = load_config()  # Reload config
        else:
            print("[X] Lệnh không hợp lệ!")


def show_settings_menu(config):
    """Hiển thị menu cài đặt"""
    while True:
        print("\n" + "=" * 70)
        print("  CÀI ĐẶT")
        print("=" * 70)
        print(f"\n1. Đường dẫn XAMPP mặc định: {config.get('default_xampp_path', 'Chưa cấu hình')}")
        print(f"2. Thư mục backup: {config.get('backup_folder', 'database_backups')}")
        print("\n0. Quay lại")
        print("=" * 70)
        
        choice = input("\nChọn mục cần chỉnh sửa (số): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            new_path = input("Nhập đường dẫn XAMPP mặc định: ").strip().strip('"')
            if new_path:
                config['default_xampp_path'] = new_path
                save_config(config)
                print("[OK] Đã cập nhật!")
            else:
                print("[X] Đường dẫn không hợp lệ!")
        elif choice == '2':
            new_folder = input("Nhập tên thư mục backup: ").strip()
            if new_folder:
                config['backup_folder'] = new_folder
                save_config(config)
                print("[OK] Đã cập nhật!")
            else:
                print("[X] Tên thư mục không hợp lệ!")
        else:
            print("[X] Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[X] Đã hủy!")
    except Exception as e:
        print(f"\n[X] Lỗi: {e}")
        import traceback
        traceback.print_exc()

