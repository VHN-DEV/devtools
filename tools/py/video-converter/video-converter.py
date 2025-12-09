#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Chuyển đổi và xử lý video
Mục đích: Convert format, compress, trim, extract audio
"""

import os
import sys
import datetime
import subprocess
import importlib
from pathlib import Path


def print_header():
    """In header của tool"""
    print("=" * 60)
    print("  TOOL CHUYỂN ĐỔI VÀ XỬ LÝ VIDEO")
    print("=" * 60)
    print()


def verify_moviepy_installed():
    """
    Kiểm tra xem moviepy có thực sự được cài đặt không
    
    Returns:
        tuple: (bool, str, str) - (is_installed, version_or_error, location_or_empty)
    """
    try:
        # Kiểm tra bằng pip show
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "moviepy"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = "installed"
            location = ""
            # Parse version và location từ output
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split(':', 1)[1].strip()
                elif line.startswith('Location:'):
                    location = line.split(':', 1)[1].strip()
            return True, version, location
        else:
            return False, "not found in pip", ""
    except Exception as e:
        return False, f"error: {str(e)}", ""


def check_moviepy_files(location):
    """
    Kiểm tra xem các file moviepy có tồn tại không
    
    Returns:
        tuple: (bool, str) - (files_exist, error_message)
    """
    if not location:
        return False, "Location không hợp lệ"
    
    moviepy_dir = os.path.join(location, "moviepy")
    if not os.path.exists(moviepy_dir):
        return False, f"Không tìm thấy thư mục: {moviepy_dir}"
    
    __init__file = os.path.join(moviepy_dir, "__init__.py")
    if not os.path.exists(__init__file):
        return False, f"Không tìm thấy file: {__init__file}"
    
    # Kiểm tra xem có module video (moviepy 2.x) hoặc editor (moviepy 1.x)
    video_module = os.path.join(moviepy_dir, "video")
    editor_file = os.path.join(moviepy_dir, "editor.py")
    editor_dir = os.path.join(moviepy_dir, "editor")
    
    # Module video (moviepy 2.x) hoặc editor (moviepy 1.x) đều OK
    if os.path.exists(video_module) or os.path.exists(editor_file) or os.path.exists(editor_dir):
        return True, "OK"
    
    # Thử kiểm tra xem có file nào chứa "video" hoặc "editor" không
    try:
        files = os.listdir(moviepy_dir)
        if any('video' in f.lower() or 'editor' in f.lower() for f in files):
            return True, "OK (cấu trúc khác)"
    except:
        pass
    
    return False, f"Không tìm thấy module video hoặc editor"


def fix_sys_path_and_import():
    """
    Thử tự động sửa sys.path và import moviepy
    
    Returns:
        tuple: (bool, str) - (success, message)
    """
    try:
        # Lấy thông tin từ pip show
        is_installed, version, location = verify_moviepy_installed()
        
        if not is_installed or not location:
            return False, "Không tìm thấy location của moviepy"
        
        # Thêm location vào sys.path nếu chưa có
        if location and location not in sys.path:
            sys.path.insert(0, location)
            print(f"   ✓ Đã thêm vào sys.path: {location}")
        
        # Thử tìm site-packages từ Python executable
        import site
        try:
            # Lấy site-packages paths
            site_packages = site.getsitepackages()
            for sp in site_packages:
                if sp not in sys.path:
                    sys.path.insert(0, sp)
                    print(f"   ✓ Đã thêm site-packages: {sp}")
        except Exception as e:
            print(f"   ⚠️  Không thể lấy site-packages: {e}")
        
        # Clear import cache
        modules_to_remove = [k for k in sys.modules.keys() if k.startswith('moviepy')]
        for module in modules_to_remove:
            del sys.modules[module]
        
        # Invalidate import cache
        import importlib
        importlib.invalidate_caches()
        
        # Debug: Hiển thị sys.path để kiểm tra
        print(f"   📂 sys.path có {len(sys.path)} entries")
        print(f"   📂 Location trong sys.path: {location in sys.path}")
        
        # Thử import từng bước để xem lỗi cụ thể
        try:
            import moviepy
            print(f"   ✓ Import moviepy thành công")
            print(f"   📍 moviepy.__file__: {getattr(moviepy, '__file__', 'N/A')}")
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Lỗi import moviepy: {error_msg}")
            # Kiểm tra xem có phải do dependencies không
            if "decorator" in error_msg.lower() or "imageio" in error_msg.lower() or "proglog" in error_msg.lower():
                return False, f"Thiếu dependencies: {error_msg}"
            return False, f"Không thể import moviepy: {error_msg}"
        
        # Thử import VideoFileClip từ moviepy (moviepy 2.x không có module editor)
        try:
            from moviepy import VideoFileClip
            print(f"   ✓ Import VideoFileClip từ moviepy thành công (moviepy 2.x)")
            return True, f"Đã import thành công moviepy {version}"
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Lỗi import VideoFileClip từ moviepy: {error_msg}")
            
            # Kiểm tra cấu trúc package
            try:
                import os
                moviepy_dir = os.path.dirname(moviepy.__file__)
                print(f"   📁 Thư mục moviepy: {moviepy_dir}")
                
                # Kiểm tra xem có VideoFileClip không
                video_module = os.path.join(moviepy_dir, "video")
                if os.path.exists(video_module):
                    print(f"   ✓ Tìm thấy module video/")
                    try:
                        files = os.listdir(video_module)
                        print(f"   📋 Các file trong video/: {', '.join(files[:5])}")
                    except:
                        pass
                
                # Thử liệt kê các file trong moviepy để debug
                try:
                    files = os.listdir(moviepy_dir)
                    print(f"   📋 Các file/module trong moviepy: {', '.join(files[:10])}")
                except:
                    pass
            except Exception as debug_err:
                print(f"   ⚠️  Không thể kiểm tra cấu trúc: {debug_err}")
            
            # Thử cách import cũ (moviepy 1.x) để tương thích ngược
            try:
                import moviepy.editor as mp
                print(f"   ✓ Import thành công bằng 'moviepy.editor' (phiên bản cũ)")
                return True, f"Đã import thành công moviepy {version} (dùng editor)"
            except Exception as e2:
                print(f"   ❌ Thử 'moviepy.editor' cũng thất bại: {e2}")
            
            # Kiểm tra xem có phải do dependencies không
            if "No module named" in error_msg:
                missing_module = error_msg.split("'")[1] if "'" in error_msg else "unknown"
                return False, f"Thiếu module '{missing_module}'. Có thể cần cài dependencies hoặc package bị hỏng."
            return False, f"Không thể import VideoFileClip từ moviepy: {error_msg}"
        
    except ImportError as e:
        return False, f"ImportError: {str(e)}"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"


def install_moviepy():
    """
    Cài đặt moviepy tự động
    
    Returns:
        bool: True nếu cài đặt thành công
    """
    try:
        print("\n📦 Đang cài đặt moviepy...")
        print("   (Có thể mất vài phút, vui lòng đợi...)\n")
        
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "moviepy>=1.0.3"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Kiểm tra lại để xác nhận
            is_installed, version, location = verify_moviepy_installed()
            if is_installed:
                print(f"✅ Cài đặt moviepy thành công! (version: {version})")
                # Thử import ngay sau khi cài
                try:
                    # Thêm location vào sys.path
                    if location and location not in sys.path:
                        sys.path.insert(0, location)
                    
                    # Clear cache và import
                    modules_to_remove = [k for k in sys.modules.keys() if k.startswith('moviepy')]
                    for module in modules_to_remove:
                        del sys.modules[module]
                    
                    import importlib
                    importlib.invalidate_caches()
                    
                    from moviepy import VideoFileClip
                    print("✅ Đã import moviepy thành công!")
                except:
                    pass  # Nếu không import được ngay, không sao, cần restart process
                return True
            else:
                print("⚠️  Pip báo cài đặt thành công nhưng không tìm thấy package.")
                print("💡 Có thể package được cài vào môi trường Python khác.")
                print(f"   Python hiện tại: {sys.executable}")
                print("\n💡 Thử cài đặt thủ công:")
                print(f"   {sys.executable} -m pip install moviepy")
                return False
        else:
            print("❌ Lỗi khi cài đặt moviepy:")
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Lỗi khi cài đặt: {e}")
        return False


def check_dependencies():
    """
    Kiểm tra các thư viện cần thiết
    
    Mục đích: Đảm bảo user đã cài moviepy và ffmpeg
    Lý do: moviepy cần thiết cho xử lý video, ffmpeg là backend
    """
    try:
        # Thử import theo cách mới (moviepy 2.x)
        from moviepy import VideoFileClip
        print("✅ Thư viện moviepy: OK")
    except ImportError as e:
        # Kiểm tra xem package có được cài không
        is_installed, version, location = verify_moviepy_installed()
        
        print("❌ Thiếu thư viện moviepy!")
        
        if is_installed:
            print(f"\n⚠️  Package đã được cài đặt (version: {version})")
            print("   nhưng không thể import được.")
            print(f"   Python hiện tại: {sys.executable}")
            
            # Thử tự động sửa sys.path
            print("\n🔧 Đang thử tự động sửa vấn đề sys.path...")
            success, message = fix_sys_path_and_import()
            
            if success:
                print(f"✅ {message}")
                print("✅ Thư viện moviepy: OK")
            else:
                print(f"❌ {message}")
                print("\n💡 Lưu ý: Moviepy 2.x đã thay đổi cấu trúc, không còn module 'editor'")
                print("   Cần import trực tiếp: from moviepy import VideoFileClip")
                print("\n💡 Có thể do:")
                print("   - Package bị hỏng hoặc không đầy đủ")
                print("   - Package được cài vào môi trường Python khác")
                print("   - Vấn đề với dependencies")
                print(f"   - Location: {location}")
                
                # Đề xuất cài đặt lại
                print("\n🔧 Bạn có muốn thử cài đặt lại moviepy không?")
                print("1. Có - Cài đặt lại (--force-reinstall)")
                print("2. Không - Tôi sẽ tự xử lý")
                
                choice = input("\nChọn (1/2, mặc định: 2): ").strip()
                
                if choice == "1":
                    print("\n📦 Đang cài đặt lại moviepy...")
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--force-reinstall", "--no-cache-dir", "moviepy>=1.0.3"],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        print("✅ Đã cài đặt lại thành công!")
                        print("💡 Tool cần restart để nhận package mới.")
                        print("💡 Vui lòng chạy lại tool từ menu chính.")
                        return False
                    else:
                        print("❌ Lỗi khi cài đặt lại:")
                        if result.stderr:
                            print(result.stderr)
                        return False
                else:
                    print("\n💡 Giải pháp:")
                    print(f"   1. Kiểm tra: {sys.executable} -m pip list | findstr moviepy")
                    print(f"   2. Cài đặt lại: {sys.executable} -m pip install --force-reinstall moviepy")
                    print("   3. Hoặc restart Python process")
                    return False
        
        print("\nBạn có muốn cài đặt tự động không?")
        print("1. Có - Tự động cài đặt (khuyến nghị)")
        print("2. Không - Tôi sẽ cài đặt thủ công")
        
        choice = input("\nChọn (1/2, mặc định: 1): ").strip()
        
        if not choice or choice == "1":
            if install_moviepy():
                # Thử reload sys.path và import lại
                try:
                    # Clear import cache
                    modules_to_remove = [k for k in sys.modules.keys() if k.startswith('moviepy')]
                    for module in modules_to_remove:
                        del sys.modules[module]
                    
                    # Reload site-packages paths
                    import site
                    import importlib
                    site.main()
                    
                    # Thử thêm site-packages vào sys.path nếu chưa có
                    try:
                        import pkg_resources
                        # pkg_resources tự động cập nhật sys.path
                    except:
                        pass
                    
                    # Thử import lại với importlib
                    importlib.invalidate_caches()
                    
                    # Thử import lại
                    from moviepy import VideoFileClip
                    print("✅ Thư viện moviepy: OK")
                except (ImportError, ModuleNotFoundError) as import_err:
                    # Package đã được cài nhưng cần restart Python process
                    print("\n" + "="*60)
                    print("✅ Package đã được cài đặt thành công!")
                    print("="*60)
                    print("\n📝 Lưu ý quan trọng:")
                    print("   Python process hiện tại cần khởi động lại để nhận package mới.")
                    print("   Đây là hành vi bình thường của Python.")
                    print(f"\n   Python: {sys.executable}")
                    print("\n💡 Các bước tiếp theo:")
                    print("   1. Tool sẽ tự động thoát")
                    print("   2. Quay lại menu chính và chạy lại tool")
                    print("   3. Tool sẽ hoạt động bình thường!")
                    print("\n" + "="*60)
                    print("\n⏳ Đang thoát tool...")
                    return False
            else:
                print("\n💡 Cài đặt thủ công:")
                print(f"   {sys.executable} -m pip install moviepy")
                print("💡 Sau khi cài đặt, chạy lại tool.")
                return False
        else:
            print("\n💡 Cài đặt thủ công:")
            print(f"   {sys.executable} -m pip install moviepy")
            print("💡 Sau khi cài đặt, chạy lại tool.")
            return False
    
    # Check ffmpeg
    ffmpeg_found = False
    ffmpeg_path = None
    ffmpeg_version = None
    
    # Cách 1: Kiểm tra từ moviepy config
    try:
        from moviepy.config import get_setting
        config_path = get_setting("FFMPEG_BINARY")
        if config_path and os.path.exists(config_path):
            ffmpeg_path = config_path
            ffmpeg_found = True
    except Exception:
        pass
    
    # Cách 2: Kiểm tra ffmpeg trong PATH
    if not ffmpeg_found:
        try:
            # Thử chạy ffmpeg -version để kiểm tra
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            if result.returncode == 0:
                ffmpeg_found = True
                # Lấy path từ which/where
                try:
                    if sys.platform == "win32":
                        which_result = subprocess.run(
                            ["where", "ffmpeg"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    else:
                        which_result = subprocess.run(
                            ["which", "ffmpeg"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                    if which_result.returncode == 0:
                        ffmpeg_path = which_result.stdout.strip().split('\n')[0]
                except Exception:
                    ffmpeg_path = "PATH"
                
                # Lấy version từ output
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if 'ffmpeg version' in line.lower():
                            ffmpeg_version = line.strip()
                            break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        except Exception:
            pass
    
    # Cách 3: Tìm trong các vị trí thường gặp trên Windows
    if not ffmpeg_found and sys.platform == "win32":
        common_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            os.path.join(os.environ.get("USERPROFILE", ""), "ffmpeg", "bin", "ffmpeg.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "ffmpeg", "bin", "ffmpeg.exe"),
        ]
        for path in common_paths:
            if os.path.exists(path):
                ffmpeg_path = path
                ffmpeg_found = True
                # Kiểm tra version
                try:
                    result = subprocess.run(
                        [path, "-version"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    if result.stdout:
                        for line in result.stdout.split('\n'):
                            if 'ffmpeg version' in line.lower():
                                ffmpeg_version = line.strip()
                                break
                except Exception:
                    pass
                break
    
    # Hiển thị kết quả
    if ffmpeg_found:
        if ffmpeg_path:
            if os.path.exists(ffmpeg_path):
                print(f"✅ FFmpeg: OK")
                print(f"   📍 Đường dẫn: {ffmpeg_path}")
            else:
                print(f"✅ FFmpeg: OK (tìm thấy trong PATH)")
        else:
            print(f"✅ FFmpeg: OK (tìm thấy trong PATH)")
        
        if ffmpeg_version:
            # Chỉ hiển thị dòng đầu tiên của version
            version_line = ffmpeg_version.split('\n')[0] if '\n' in ffmpeg_version else ffmpeg_version
            print(f"   📦 Phiên bản: {version_line[:80]}")
    else:
        print("⚠️  FFmpeg chưa được cấu hình đúng!")
        print("\n📋 Hướng dẫn cài FFmpeg:")
        
        if sys.platform == "win32":
            print("Windows:")
            print("   1. Tải FFmpeg tại: https://www.gyan.dev/ffmpeg/builds/")
            print("      (Chọn bản 'release builds' → 'ffmpeg-release-essentials.zip')")
            print("   2. Giải nén vào thư mục (vd: C:\\ffmpeg)")
            print("   3. Thêm C:\\ffmpeg\\bin vào PATH:")
            print("      - Mở 'Environment Variables'")
            print("      - Trong 'System variables', tìm 'Path' → Edit")
            print("      - Thêm đường dẫn C:\\ffmpeg\\bin")
            print("   4. Khởi động lại terminal và kiểm tra: ffmpeg -version")
        elif sys.platform == "linux":
            print("Linux:")
            print("   sudo apt-get update")
            print("   sudo apt-get install ffmpeg")
            print("   Hoặc: sudo yum install ffmpeg (cho CentOS/RHEL)")
        elif sys.platform == "darwin":
            print("macOS:")
            print("   brew install ffmpeg")
            print("   Hoặc tải từ: https://evermeet.cx/ffmpeg/")
        else:
            print("   Tải từ: https://ffmpeg.org/download.html")
        
        print("\n⚠️  Tool vẫn có thể hoạt động nhưng có thể gặp lỗi khi xử lý video.")
        print("💡 Sau khi cài FFmpeg, khởi động lại terminal và chạy lại tool.")
    
    return True


def format_size(size_bytes):
    """Format dung lượng dễ đọc"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0


def format_time(seconds):
    """Format thời gian dễ đọc (HH:MM:SS)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def get_video_info(video_path):
    """
    Lấy thông tin video
    
    Returns:
        dict: Thông tin video (duration, fps, resolution, size...)
    
    Giải thích:
    - Dùng moviepy để đọc metadata
    - Hiển thị info cơ bản để user biết
    """
    from moviepy import VideoFileClip
    
    try:
        clip = VideoFileClip(video_path)
        
        info = {
            'duration': clip.duration,
            'fps': clip.fps,
            'size': clip.size,  # (width, height)
            'file_size': os.path.getsize(video_path),
            'audio': clip.audio is not None
        }
        
        clip.close()
        return info
        
    except Exception as e:
        print(f"❌ Lỗi khi đọc video: {e}")
        return None


def display_video_info(video_path):
    """Hiển thị thông tin video"""
    print(f"\n📹 Video: {os.path.basename(video_path)}")
    print("=" * 60)
    
    info = get_video_info(video_path)
    
    if not info:
        return
    
    width, height = info['size']
    
    print(f"Thoi luong: {format_time(info['duration'])}")
    print(f"Do phan giai: {width}x{height}")
    print(f"FPS: {info['fps']:.2f}")
    print(f"Audio: {'Co' if info['audio'] else 'Khong'}")
    print(f"Kich thuoc: {format_size(info['file_size'])}")
    print("=" * 60)


def convert_video_format(input_path, output_path, output_format='mp4', 
                        codec='libx264', audio_codec='aac', bitrate=None,
                        fps=None, preset='medium'):
    """
    Chuyển đổi định dạng video
    
    Args:
        input_path: Video gốc
        output_path: Video output
        output_format: Format đích (mp4, avi, mkv, webm, mov)
        codec: Video codec (libx264, libx265, mpeg4, libvpx)
        audio_codec: Audio codec (aac, mp3, libvorbis)
        bitrate: Bitrate (None = auto)
        fps: FPS mới (None = giữ nguyên)
        preset: Preset encode (ultrafast, fast, medium, slow, veryslow)
    
    Giải thích:
    - Load video với moviepy
    - Convert sang format mới với codec chỉ định
    - Preset ảnh hưởng tốc độ/chất lượng
      + ultrafast: Nhanh nhưng file lớn
      + slow: Chậm nhưng file nhỏ, chất lượng tốt
    """
    from moviepy import VideoFileClip
    
    try:
        print(f"\n🎬 Dang chuyen doi...")
        print(f"   Format: {output_format.upper()}")
        print(f"   Codec: {codec}")
        print(f"   Preset: {preset}\n")
        
        # Load video
        clip = VideoFileClip(input_path)
        
        # Điều chỉnh FPS nếu có
        if fps and fps != clip.fps:
            clip = clip.set_fps(fps)
            print(f"   ✓ Dieu chinh FPS: {clip.fps} → {fps}")
        
        # Write video
        clip.write_videofile(
            output_path,
            codec=codec,
            audio_codec=audio_codec,
            bitrate=bitrate,
            preset=preset,
            verbose=False,
            logger=None
        )
        
        clip.close()
        
        # So sánh kích thước
        original_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)
        ratio = (output_size / original_size) * 100
        
        print(f"\n✅ Chuyen doi thanh cong!")
        print(f"   📄 File goc: {format_size(original_size)}")
        print(f"   📄 File moi: {format_size(output_size)} ({ratio:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi chuyển đổi: {e}")
        return False


def compress_video(input_path, output_path, target_size_mb=None, 
                   quality='medium', resolution_scale=1.0):
    """
    Nén video giảm dung lượng
    
    Args:
        input_path: Video gốc
        output_path: Video nén
        target_size_mb: Dung lượng mục tiêu (MB)
        quality: Chất lượng (low, medium, high)
        resolution_scale: Tỷ lệ giảm resolution (0.5 = giảm 50%)
    
    Giải thích:
    - Giảm resolution nếu cần
    - Điều chỉnh bitrate theo target size
    - Nén với preset phù hợp
    """
    from moviepy import VideoFileClip
    
    try:
        print(f"\n📦 Dang nen video...")
        print(f"   Quality: {quality}")
        
        # Load video
        clip = VideoFileClip(input_path)
        
        # Resize nếu cần
        if resolution_scale < 1.0:
            new_width = int(clip.w * resolution_scale)
            new_height = int(clip.h * resolution_scale)
            # Đảm bảo width/height là số chẵn (yêu cầu của codec)
            new_width = new_width if new_width % 2 == 0 else new_width - 1
            new_height = new_height if new_height % 2 == 0 else new_height - 1
            
            clip = clip.resize((new_width, new_height))
            print(f"   ✓ Resize: {clip.w}x{clip.h} → {new_width}x{new_height}")
        
        # Tính bitrate dựa trên target size
        bitrate = None
        if target_size_mb:
            # Tính bitrate cần thiết (kbps)
            target_size_bits = target_size_mb * 8 * 1024 * 1024
            duration = clip.duration
            bitrate = f"{int(target_size_bits / duration / 1000)}k"
            print(f"   ✓ Target size: {target_size_mb}MB → Bitrate: {bitrate}")
        
        # Preset theo quality
        presets = {
            'low': 'ultrafast',
            'medium': 'fast',
            'high': 'slow'
        }
        preset = presets.get(quality, 'fast')
        
        # Write
        clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            bitrate=bitrate,
            preset=preset,
            verbose=False,
            logger=None
        )
        
        clip.close()
        
        # Kết quả
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        print(f"\n✅ Nen thanh cong!")
        print(f"   📄 File goc: {format_size(original_size)}")
        print(f"   📄 File nen: {format_size(compressed_size)}")
        print(f"   💯 Giam: {reduction:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi nén video: {e}")
        return False


def trim_video(input_path, output_path, start_time, end_time):
    """
    Cắt video
    
    Args:
        input_path: Video gốc
        output_path: Video đã cắt
        start_time: Thời điểm bắt đầu (giây hoặc "MM:SS" hoặc "HH:MM:SS")
        end_time: Thời điểm kết thúc
    
    Giải thích:
    - Cắt video từ start_time đến end_time
    - Giữ nguyên codec và quality
    """
    from moviepy import VideoFileClip
    
    try:
        # Parse time string to seconds
        def parse_time(time_str):
            if isinstance(time_str, (int, float)):
                return time_str
            
            parts = time_str.split(':')
            if len(parts) == 2:  # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:  # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            else:
                return float(time_str)
        
        start = parse_time(start_time)
        end = parse_time(end_time)
        
        print(f"\n✂️  Dang cat video...")
        print(f"   Tu: {format_time(start)}")
        print(f"   Den: {format_time(end)}")
        print(f"   Thoi luong: {format_time(end - start)}\n")
        
        # Load và cắt
        clip = VideoFileClip(input_path).subclip(start, end)
        
        # Write
        clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        clip.close()
        
        print(f"\n✅ Cat thanh cong!")
        print(f"   📄 File output: {output_path}")
        print(f"   📊 Kich thuoc: {format_size(os.path.getsize(output_path))}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi cắt video: {e}")
        return False


def extract_audio(input_path, output_path, audio_format='mp3', bitrate='192k'):
    """
    Trích xuất audio từ video
    
    Args:
        input_path: Video gốc
        output_path: File audio output
        audio_format: Format audio (mp3, wav, aac)
        bitrate: Bitrate audio (128k, 192k, 320k)
    
    Giải thích:
    - Extract audio track từ video
    - Convert sang format mong muốn
    """
    from moviepy import VideoFileClip
    
    try:
        print(f"\n🎵 Dang trich xuat audio...")
        print(f"   Format: {audio_format.upper()}")
        print(f"   Bitrate: {bitrate}\n")
        
        # Load video
        clip = VideoFileClip(input_path)
        
        if not clip.audio:
            print("❌ Video khong co audio!")
            clip.close()
            return False
        
        # Extract audio
        audio = clip.audio
        audio.write_audiofile(
            output_path,
            bitrate=bitrate,
            verbose=False,
            logger=None
        )
        
        audio.close()
        clip.close()
        
        print(f"\n✅ Trich xuat thanh cong!")
        print(f"   📄 File audio: {output_path}")
        print(f"   📊 Kich thuoc: {format_size(os.path.getsize(output_path))}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi trích xuất audio: {e}")
        return False


def change_resolution(input_path, output_path, width=None, height=None, keep_aspect=True):
    """
    Thay đổi resolution video
    
    Args:
        input_path: Video gốc
        output_path: Video mới
        width: Chiều rộng mới
        height: Chiều cao mới
        keep_aspect: Giữ tỷ lệ khung hình
    
    Giải thích:
    - Resize video về resolution mới
    - Nếu keep_aspect=True, tự tính height/width để giữ tỷ lệ
    """
    from moviepy import VideoFileClip
    
    try:
        print(f"\n🖼️  Dang thay doi resolution...")
        
        # Load video
        clip = VideoFileClip(input_path)
        
        original_width, original_height = clip.size
        
        # Tính new size
        if keep_aspect:
            if width and not height:
                # Tính height dựa trên width
                aspect_ratio = original_height / original_width
                height = int(width * aspect_ratio)
            elif height and not width:
                # Tính width dựa trên height
                aspect_ratio = original_width / original_height
                width = int(height * aspect_ratio)
        
        # Đảm bảo width/height chẵn
        if width:
            width = width if width % 2 == 0 else width - 1
        if height:
            height = height if height % 2 == 0 else height - 1
        
        print(f"   Resolution: {original_width}x{original_height} → {width}x{height}\n")
        
        # Resize
        clip_resized = clip.resize((width, height))
        
        # Write
        clip_resized.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        clip_resized.close()
        clip.close()
        
        print(f"\n✅ Thay doi thanh cong!")
        print(f"   📄 File output: {output_path}")
        print(f"   📊 Kich thuoc: {format_size(os.path.getsize(output_path))}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi thay đổi resolution: {e}")
        return False


def batch_convert(input_folder, output_folder, output_format='mp4', preset='medium'):
    """
    Convert hàng loạt video
    
    Giải thích:
    - Quét tất cả video trong thư mục
    - Convert từng video sang format mới
    """
    from moviepy import VideoFileClip
    
    # Các format video hỗ trợ
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg']
    
    # Tìm video files
    video_files = [
        f for f in os.listdir(input_folder)
        if os.path.isfile(os.path.join(input_folder, f))
        and os.path.splitext(f)[1].lower() in video_extensions
    ]
    
    if not video_files:
        print("❌ Khong tim thay video nao!")
        return 0, 0
    
    print(f"🎬 Tim thay {len(video_files)} video\n")
    
    # Tạo output folder
    os.makedirs(output_folder, exist_ok=True)
    
    success_count = 0
    error_count = 0
    
    for idx, filename in enumerate(video_files, 1):
        input_path = os.path.join(input_folder, filename)
        
        # Output filename với extension mới
        base_name = Path(filename).stem
        output_filename = f"{base_name}.{output_format}"
        output_path = os.path.join(output_folder, output_filename)
        
        print(f"\n[{idx}/{len(video_files)}] {filename}")
        print("-" * 60)
        
        try:
            clip = VideoFileClip(input_path)
            
            clip.write_videofile(
                output_path,
                codec='libx264' if output_format == 'mp4' else 'mpeg4',
                audio_codec='aac',
                preset=preset,
                verbose=False,
                logger=None
            )
            
            clip.close()
            
            output_size = format_size(os.path.getsize(output_path))
            print(f"✅ Thanh cong! ({output_size})")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            error_count += 1
    
    return success_count, error_count


def main():
    """
    Hàm chính - Menu video tools
    
    Giải thích:
    - Hiển thị menu các chức năng
    - Xử lý input từ user
    - Gọi hàm tương ứng
    """
    print_header()
    
    # Kiểm tra dependencies
    if not check_dependencies():
        print("\n💡 Sau khi cài đặt, chạy lại tool.")
        return
    
    print("\n===== CHỨC NĂNG =====")
    print("1. Chuyển đổi định dạng (Convert Format)")
    print("2. Nén video (Compress)")
    print("3. Cắt video (Trim)")
    print("4. Trích xuất audio (Extract Audio)")
    print("5. Thay đổi resolution")
    print("6. Xem thông tin video")
    print("7. Chuyển đổi hàng loạt (Batch Convert)")
    print("0. Thoát")
    
    choice = input("\nChọn chức năng (0-7): ").strip()
    
    if choice == "0":
        print("Thoát chương trình.")
        return
    
    elif choice == "1":
        # Convert format
        print("\n===== CHUYEN DOI DINH DANG =====")
        
        input_file = input("Nhap duong dan video: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File khong ton tai!")
            return
        
        display_video_info(input_file)
        
        print("\nDinh dang output:")
        print("1. MP4 (pho bien nhat)")
        print("2. AVI")
        print("3. MKV (chat luong cao)")
        print("4. WEBM (cho web)")
        print("5. MOV (Apple)")
        
        format_choice = input("\nChon dinh dang (1-5): ").strip()
        formats = {'1': 'mp4', '2': 'avi', '3': 'mkv', '4': 'webm', '5': 'mov'}
        output_format = formats.get(format_choice, 'mp4')
        
        output_file = input("Ten file output (Enter de tu dong): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}_converted.{output_format}"
            )
        
        print("\nPreset (toc do/chat luong):")
        print("1. ultrafast (nhanh nhat)")
        print("2. fast")
        print("3. medium (can bang)")
        print("4. slow (chat luong tot)")
        
        preset_choice = input("\nChon preset (1-4, mac dinh 3): ").strip()
        presets = {'1': 'ultrafast', '2': 'fast', '3': 'medium', '4': 'slow'}
        preset = presets.get(preset_choice, 'medium')
        
        convert_video_format(input_file, output_file, output_format, preset=preset)
    
    elif choice == "2":
        # Compress
        print("\n===== NEN VIDEO =====")
        
        input_file = input("Nhap duong dan video: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File khong ton tai!")
            return
        
        display_video_info(input_file)
        
        output_file = input("\nTen file output (Enter de tu dong): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            ext = Path(input_file).suffix
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}_compressed{ext}"
            )
        
        print("\nChat luong:")
        print("1. Low (nen manh, kich thuoc nho)")
        print("2. Medium (can bang)")
        print("3. High (nen nhe, chat luong tot)")
        
        quality_choice = input("\nChon chat luong (1-3, mac dinh 2): ").strip()
        qualities = {'1': 'low', '2': 'medium', '3': 'high'}
        quality = qualities.get(quality_choice, 'medium')
        
        resolution_input = input("\nGiam resolution? (%, 100=giu nguyen, 50=giam 50%): ").strip()
        resolution_scale = float(resolution_input) / 100 if resolution_input else 1.0
        
        target_size = input("\nDung luong muc tieu (MB, Enter de bo qua): ").strip()
        target_size_mb = int(target_size) if target_size else None
        
        compress_video(input_file, output_file, target_size_mb, quality, resolution_scale)
    
    elif choice == "3":
        # Trim
        print("\n===== CAT VIDEO =====")
        
        input_file = input("Nhap duong dan video: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File khong ton tai!")
            return
        
        display_video_info(input_file)
        
        print("\nNhap thoi gian (dinh dang: MM:SS hoac HH:MM:SS hoac giay)")
        start_time = input("Bat dau tu (vd: 00:30 hoac 30): ").strip()
        end_time = input("Ket thuc tai (vd: 02:15 hoac 135): ").strip()
        
        output_file = input("\nTen file output (Enter de tu dong): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            ext = Path(input_file).suffix
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}_trimmed{ext}"
            )
        
        trim_video(input_file, output_file, start_time, end_time)
    
    elif choice == "4":
        # Extract audio
        print("\n===== TRICH XUAT AUDIO =====")
        
        input_file = input("Nhap duong dan video: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File khong ton tai!")
            return
        
        display_video_info(input_file)
        
        print("\nDinh dang audio:")
        print("1. MP3 (pho bien)")
        print("2. WAV (khong mat du lieu)")
        print("3. AAC (chat luong tot)")
        
        format_choice = input("\nChon dinh dang (1-3, mac dinh 1): ").strip()
        formats = {'1': 'mp3', '2': 'wav', '3': 'aac'}
        audio_format = formats.get(format_choice, 'mp3')
        
        bitrate_input = input("Bitrate (128k/192k/320k, mac dinh 192k): ").strip()
        bitrate = bitrate_input if bitrate_input else '192k'
        
        output_file = input("\nTen file output (Enter de tu dong): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}.{audio_format}"
            )
        
        extract_audio(input_file, output_file, audio_format, bitrate)
    
    elif choice == "5":
        # Change resolution
        print("\n===== THAY DOI RESOLUTION =====")
        
        input_file = input("Nhap duong dan video: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File khong ton tai!")
            return
        
        display_video_info(input_file)
        
        print("\nPreset resolution:")
        print("1. 1920x1080 (Full HD)")
        print("2. 1280x720 (HD)")
        print("3. 854x480 (SD)")
        print("4. 640x360 (Low)")
        print("5. Custom")
        
        res_choice = input("\nChon (1-5): ").strip()
        
        if res_choice == "5":
            width = int(input("Chieu rong (width): "))
            height = int(input("Chieu cao (height, Enter de giu ty le): ").strip() or 0)
        else:
            resolutions = {
                '1': (1920, 1080),
                '2': (1280, 720),
                '3': (854, 480),
                '4': (640, 360)
            }
            width, height = resolutions.get(res_choice, (1280, 720))
        
        output_file = input("\nTen file output (Enter de tu dong): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            ext = Path(input_file).suffix
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}_{width}x{height if height else 'auto'}{ext}"
            )
        
        change_resolution(input_file, output_file, width, height if height else None)
    
    elif choice == "6":
        # Video info
        print("\n===== THONG TIN VIDEO =====")
        
        input_file = input("Nhap duong dan video: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File khong ton tai!")
            return
        
        display_video_info(input_file)
    
    elif choice == "7":
        # Batch convert
        print("\n===== CHUYEN DOI HANG LOAT =====")
        
        input_folder = input("Thu muc chua video: ").strip('"')
        if not os.path.isdir(input_folder):
            print("❌ Thu muc khong ton tai!")
            return
        
        output_folder = input("Thu muc output (Enter de tao 'converted'): ").strip('"')
        if not output_folder:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = os.path.join(input_folder, f"converted_{timestamp}")
        
        format_choice = input("\nDinh dang output (mp4/avi/mkv, mac dinh mp4): ").strip()
        output_format = format_choice if format_choice else 'mp4'
        
        preset_choice = input("Preset (ultrafast/fast/medium/slow, mac dinh medium): ").strip()
        preset = preset_choice if preset_choice else 'medium'
        
        success, errors = batch_convert(input_folder, output_folder, output_format, preset)
        
        print(f"\n{'='*60}")
        print(f"✅ Hoan thanh!")
        print(f"   - Thanh cong: {success} video")
        print(f"   - Lỗi: {errors} video")
        print(f"   - Thu muc output: {output_folder}")
        print(f"{'='*60}")
    
    else:
        print("❌ Lua chon khong hop le!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")

