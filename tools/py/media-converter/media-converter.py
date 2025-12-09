#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: Chuyển đổi định dạng media (mp3, mp4, wav, avi...)
Mục đích: Convert giữa các định dạng audio và video
"""

import os
import sys
import subprocess
from pathlib import Path

# Thêm thư mục cha vào sys.path để import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import install_library


def print_header():
    """In header của tool"""
    print("=" * 60)
    print("  TOOL CHUYỂN ĐỔI ĐỊNH DẠNG MEDIA")
    print("=" * 60)
    print()


def check_dependencies():
    """
    Kiểm tra các thư viện cần thiết
    
    Returns:
        bool: True nếu đủ dependencies
    """
    try:
        # Thử import pydub (để xử lý audio)
        import pydub
        print("✅ Thư viện pydub: OK")
    except ImportError:
        install_library(
            package_name="pydub",
            install_command="pip install pydub",
            library_display_name="pydub"
        )
        return False
    
    try:
        # Thử import moviepy (để xử lý video)
        from moviepy import VideoFileClip
        print("✅ Thư viện moviepy: OK")
    except ImportError:
        install_library(
            package_name="moviepy",
            install_command="pip install moviepy",
            library_display_name="moviepy"
        )
        return False
    
    # Kiểm tra ffmpeg
    ffmpeg_found = False
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        if result.returncode == 0:
            ffmpeg_found = True
            print("✅ FFmpeg: OK")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    if not ffmpeg_found:
        print("⚠️  FFmpeg chưa được cấu hình!")
        print("\n💡 Hướng dẫn cài FFmpeg:")
        if sys.platform == "win32":
            print("   Windows: https://www.gyan.dev/ffmpeg/builds/")
        elif sys.platform == "linux":
            print("   Linux: sudo apt-get install ffmpeg")
        elif sys.platform == "darwin":
            print("   macOS: brew install ffmpeg")
        print("\n⚠️  Tool vẫn có thể hoạt động nhưng có thể gặp lỗi.")
    
    return True


def get_file_type(file_path):
    """
    Xác định loại file (audio, video, unknown)
    
    Args:
        file_path: Đường dẫn file
    
    Returns:
        str: 'audio', 'video', hoặc 'unknown'
    """
    ext = Path(file_path).suffix.lower()
    
    audio_extensions = ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma', '.opus']
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg']
    
    if ext in audio_extensions:
        return 'audio'
    elif ext in video_extensions:
        return 'video'
    else:
        return 'unknown'


def convert_audio_format(input_path, output_path, output_format='mp3', bitrate='192k'):
    """
    Chuyển đổi định dạng audio
    
    Args:
        input_path: File audio gốc
        output_path: File audio output
        output_format: Format đích (mp3, wav, aac, flac, ogg)
        bitrate: Bitrate (128k, 192k, 320k)
    """
    try:
        from pydub import AudioSegment
        
        print(f"\n🎵 Đang chuyển đổi audio...")
        print(f"   Format: {output_format.upper()}")
        print(f"   Bitrate: {bitrate}\n")
        
        # Load audio
        audio = AudioSegment.from_file(input_path)
        
        # Export với format mới
        audio.export(output_path, format=output_format, bitrate=bitrate)
        
        # So sánh kích thước
        original_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)
        ratio = (output_size / original_size) * 100
        
        print(f"\n✅ Chuyển đổi thành công!")
        print(f"   📄 File gốc: {format_size(original_size)}")
        print(f"   📄 File mới: {format_size(output_size)} ({ratio:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi chuyển đổi: {e}")
        return False


def convert_video_format(input_path, output_path, output_format='mp4', codec='libx264', preset='medium'):
    """
    Chuyển đổi định dạng video
    
    Args:
        input_path: Video gốc
        output_path: Video output
        output_format: Format đích (mp4, avi, mkv, webm, mov)
        codec: Video codec (libx264, libx265, mpeg4)
        preset: Preset encode (ultrafast, fast, medium, slow)
    """
    try:
        from moviepy import VideoFileClip
        
        print(f"\n🎬 Đang chuyển đổi video...")
        print(f"   Format: {output_format.upper()}")
        print(f"   Codec: {codec}")
        print(f"   Preset: {preset}\n")
        
        # Load video
        clip = VideoFileClip(input_path)
        
        # Write với format mới
        clip.write_videofile(
            output_path,
            codec=codec,
            audio_codec='aac',
            preset=preset,
            verbose=False,
            logger=None
        )
        
        clip.close()
        
        # So sánh kích thước
        original_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)
        ratio = (output_size / original_size) * 100
        
        print(f"\n✅ Chuyển đổi thành công!")
        print(f"   📄 File gốc: {format_size(original_size)}")
        print(f"   📄 File mới: {format_size(output_size)} ({ratio:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi chuyển đổi: {e}")
        return False


def convert_audio_to_video(input_path, output_path, image_path=None, output_format='mp4', bitrate='192k'):
    """
    Chuyển đổi audio thành video (với hình ảnh)
    
    Args:
        input_path: File audio gốc
        output_path: Video output
        image_path: Hình ảnh để làm background (None = màu đen)
        output_format: Format video (mp4, avi, mkv)
        bitrate: Bitrate audio
    """
    try:
        from moviepy import AudioFileClip, ImageClip, CompositeVideoClip
        
        print(f"\n🎬 Đang chuyển đổi audio → video...")
        print(f"   Format: {output_format.upper()}\n")
        
        # Load audio
        audio = AudioFileClip(input_path)
        duration = audio.duration
        
        # Tạo video từ hình ảnh hoặc màu đen
        if image_path and os.path.exists(image_path):
            video = ImageClip(image_path, duration=duration).set_fps(1)
        else:
            # Video màu đen
            video = ImageClip(size=(1280, 720), duration=duration, color=(0, 0, 0)).set_fps(1)
        
        # Kết hợp video và audio
        final = CompositeVideoClip([video.set_audio(audio)])
        
        # Write video
        final.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            bitrate=bitrate,
            verbose=False,
            logger=None
        )
        
        final.close()
        audio.close()
        video.close()
        
        print(f"\n✅ Chuyển đổi thành công!")
        print(f"   📄 File video: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi chuyển đổi: {e}")
        return False


def format_size(size_bytes):
    """Format dung lượng dễ đọc"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def main():
    """Hàm chính - Menu media converter"""
    print_header()
    
    # Kiểm tra dependencies
    if not check_dependencies():
        print("\n💡 Sau khi cài đặt dependencies, chạy lại tool.")
        return
    
    print("\n===== CHỨC NĂNG =====")
    print("1. Chuyển đổi audio (mp3, wav, aac, flac...)")
    print("2. Chuyển đổi video (mp4, avi, mkv, mov...)")
    print("3. Audio → Video (tạo video từ audio + hình ảnh)")
    print("4. Video → Audio (trích xuất audio từ video)")
    print("0. Thoát")
    
    choice = input("\nChọn chức năng (0-4): ").strip()
    
    if choice == "0":
        print("Thoát chương trình.")
        return
    
    elif choice == "1":
        # Convert audio
        print("\n===== CHUYỂN ĐỔI AUDIO =====")
        
        input_file = input("Nhập đường dẫn file audio: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        file_type = get_file_type(input_file)
        if file_type != 'audio':
            print("⚠️  File không phải audio!")
            return
        
        print("\nĐịnh dạng output:")
        print("1. MP3 (phổ biến)")
        print("2. WAV (chất lượng cao)")
        print("3. AAC (nén tốt)")
        print("4. FLAC (không mất dữ liệu)")
        print("5. OGG (mã nguồn mở)")
        
        format_choice = input("\nChọn định dạng (1-5): ").strip()
        formats = {'1': 'mp3', '2': 'wav', '3': 'aac', '4': 'flac', '5': 'ogg'}
        output_format = formats.get(format_choice, 'mp3')
        
        bitrate_input = input("Bitrate (128k/192k/320k, mặc định 192k): ").strip()
        bitrate = bitrate_input if bitrate_input else '192k'
        
        output_file = input("Tên file output (Enter để tự động): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}.{output_format}"
            )
        
        convert_audio_format(input_file, output_file, output_format, bitrate)
    
    elif choice == "2":
        # Convert video
        print("\n===== CHUYỂN ĐỔI VIDEO =====")
        
        input_file = input("Nhập đường dẫn file video: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        file_type = get_file_type(input_file)
        if file_type != 'video':
            print("⚠️  File không phải video!")
            return
        
        print("\nĐịnh dạng output:")
        print("1. MP4 (phổ biến)")
        print("2. AVI")
        print("3. MKV (chất lượng cao)")
        print("4. WEBM (cho web)")
        print("5. MOV (Apple)")
        
        format_choice = input("\nChọn định dạng (1-5): ").strip()
        formats = {'1': 'mp4', '2': 'avi', '3': 'mkv', '4': 'webm', '5': 'mov'}
        output_format = formats.get(format_choice, 'mp4')
        
        print("\nPreset (tốc độ/chất lượng):")
        print("1. ultrafast (nhanh nhất)")
        print("2. fast")
        print("3. medium (cân bằng)")
        print("4. slow (chất lượng tốt)")
        
        preset_choice = input("\nChọn preset (1-4, mặc định 3): ").strip()
        presets = {'1': 'ultrafast', '2': 'fast', '3': 'medium', '4': 'slow'}
        preset = presets.get(preset_choice, 'medium')
        
        output_file = input("Tên file output (Enter để tự động): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}.{output_format}"
            )
        
        convert_video_format(input_file, output_file, output_format, preset=preset)
    
    elif choice == "3":
        # Audio to Video
        print("\n===== AUDIO → VIDEO =====")
        
        input_file = input("Nhập đường dẫn file audio: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        image_file = input("Hình ảnh background (Enter để dùng màu đen): ").strip('"')
        if image_file and not os.path.isfile(image_file):
            print("⚠️  File hình ảnh không tồn tại, sẽ dùng màu đen.")
            image_file = None
        
        print("\nĐịnh dạng video:")
        print("1. MP4")
        print("2. AVI")
        print("3. WEBM")
        
        format_choice = input("\nChọn định dạng (1-3, mặc định 1): ").strip()
        formats = {'1': 'mp4', '2': 'avi', '3': 'webm'}
        output_format = formats.get(format_choice, 'mp4')
        
        bitrate_input = input("Bitrate audio (128k/192k/320k, mặc định 192k): ").strip()
        bitrate = bitrate_input if bitrate_input else '192k'
        
        output_file = input("Tên file output (Enter để tự động): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}.{output_format}"
            )
        
        convert_audio_to_video(input_file, output_file, image_file, output_format, bitrate)
    
    elif choice == "4":
        # Video to Audio
        print("\n===== VIDEO → AUDIO =====")
        
        input_file = input("Nhập đường dẫn file video: ").strip('"')
        if not os.path.isfile(input_file):
            print("❌ File không tồn tại!")
            return
        
        print("\nĐịnh dạng audio:")
        print("1. MP3 (phổ biến)")
        print("2. WAV (chất lượng cao)")
        print("3. AAC (nén tốt)")
        
        format_choice = input("\nChọn định dạng (1-3, mặc định 1): ").strip()
        formats = {'1': 'mp3', '2': 'wav', '3': 'aac'}
        audio_format = formats.get(format_choice, 'mp3')
        
        bitrate_input = input("Bitrate (128k/192k/320k, mặc định 192k): ").strip()
        bitrate = bitrate_input if bitrate_input else '192k'
        
        output_file = input("Tên file output (Enter để tự động): ").strip('"')
        if not output_file:
            base = Path(input_file).stem
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"{base}.{audio_format}"
            )
        
        # Sử dụng hàm từ video-converter
        try:
            from moviepy import VideoFileClip
            
            print(f"\n🎵 Đang trích xuất audio...")
            print(f"   Format: {audio_format.upper()}")
            print(f"   Bitrate: {bitrate}\n")
            
            clip = VideoFileClip(input_file)
            
            if not clip.audio:
                print("❌ Video không có audio!")
                clip.close()
                return
            
            audio = clip.audio
            audio.write_audiofile(
                output_file,
                bitrate=bitrate,
                verbose=False,
                logger=None
            )
            
            audio.close()
            clip.close()
            
            print(f"\n✅ Trích xuất thành công!")
            print(f"   📄 File audio: {output_file}")
            print(f"   📊 Kích thước: {format_size(os.path.getsize(output_file))}")
            
        except Exception as e:
            print(f"\n❌ Lỗi khi trích xuất: {e}")
    
    else:
        print("❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
