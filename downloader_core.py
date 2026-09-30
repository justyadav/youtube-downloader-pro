import os
import re
import sys
import shutil
import logging
from typing import Callable, Optional, Dict, Any, List
from urllib.parse import urlparse

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("yt_downloader")

# Detect FFmpeg: prefer system ffmpeg if installed, else fallback to bundled imageio-ffmpeg
def detect_ffmpeg() -> str:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:
        logger.warning(f"Could not load imageio-ffmpeg: {e}")
        return "ffmpeg"

FFMPEG_PATH = detect_ffmpeg()

def get_default_download_dir() -> str:
    """Returns the default cross-platform download directory."""
    user_home = os.path.expanduser("~")
    downloads_dir = os.path.join(user_home, "Downloads", "YouTube_Downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    return downloads_dir

def sanitize_url(url: str) -> bool:
    """Validates if input string is a valid HTTP/HTTPS URL."""
    try:
        res = urlparse(url.strip())
        return res.scheme in ["http", "https"] and bool(res.netloc)
    except Exception:
        return False

def build_format_string(mode: str, quality: str) -> Dict[str, Any]:
    """
    Build yt-dlp format selector and postprocessors based on:
    - mode: 'auto', 'both', 'video', 'audio'
    - quality: 'best', '2160', '1440', '1080', '720', '480', '360'
    """
    opts: Dict[str, Any] = {
        'ffmpeg_location': FFMPEG_PATH,
        'quiet': True,
        'no_warnings': True,
    }

    # Normalize quality string
    q_filter = ""
    if quality and quality.lower() != 'best':
        h = quality.lower().replace('p', '')
        if h.isdigit():
            q_filter = f"[height<={h}]"

    if mode == 'audio':
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    elif mode == 'video':
        # Pure video stream without audio
        if q_filter:
            opts['format'] = f'bestvideo{q_filter}[ext=mp4]/bestvideo{q_filter}/best{q_filter}'
        else:
            opts['format'] = 'bestvideo[ext=mp4]/bestvideo/best'
    elif mode == 'both':
        # Video + Audio merged into MP4 container
        if q_filter:
            opts['format'] = f'bestvideo{q_filter}+bestaudio/best{q_filter}'
        else:
            opts['format'] = 'bestvideo+bestaudio/best'
        opts['merge_output_format'] = 'mp4'
    else:  # 'auto'
        # Automatic optimal resolution with merged audio
        if q_filter:
            opts['format'] = f'bestvideo{q_filter}+bestaudio/best{q_filter}'
        else:
            opts['format'] = 'bestvideo*+bestaudio/best'
        opts['merge_output_format'] = 'mp4'

    return opts

def extract_info(url: str, extract_flat: bool = False) -> Dict[str, Any]:
    """Extracts metadata from a video or playlist URL."""
    if not sanitize_url(url):
        raise ValueError("Invalid URL: must start with http:// or https://")

    import yt_dlp
    ydl_opts = {
        'extract_flat': extract_flat,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

class DownloadTask:
    def __init__(
        self,
        task_id: str,
        urls: List[str],
        mode: str = "both",
        quality: str = "best",
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.task_id = task_id
        self.urls = [u.strip() for u in urls if sanitize_url(u)]
        self.mode = mode
        self.quality = quality
        self.output_dir = os.path.abspath(output_dir or get_default_download_dir())
        os.makedirs(self.output_dir, exist_ok=True)
        self.progress_callback = progress_callback
        self.is_cancelled = False
        self.current_title = ""
        self.current_percent = 0.0
        self.current_speed = ""
        self.current_eta = ""
        self.current_size = ""
        self.status = "queued"  # queued, downloading, processing, completed, cancelled, error
        self.error_message = ""
        self.results: List[Dict[str, Any]] = []

    def cancel(self):
        self.is_cancelled = True
        self.status = "cancelled"

    def _hook(self, d: Dict[str, Any]):
        if self.is_cancelled:
            raise Exception("Download cancelled by user")

        if d.get('status') == 'downloading':
            self.status = "downloading"
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes') or 0
            if total > 0:
                self.current_percent = round((downloaded / total) * 100, 1)
                self.current_size = f"{downloaded / (1024*1024):.1f}MB / {total / (1024*1024):.1f}MB"
            else:
                self.current_percent = 0.0
                self.current_size = f"{downloaded / (1024*1024):.1f}MB"

            speed = d.get('speed')
            self.current_speed = f"{speed / (1024*1024):.2f} MB/s" if speed else "--"

            eta = d.get('eta')
            self.current_eta = f"{int(eta)}s" if eta is not None else "--"

            if self.progress_callback:
                self.progress_callback({
                    'task_id': self.task_id,
                    'status': 'downloading',
                    'title': self.current_title,
                    'percent': self.current_percent,
                    'speed': self.current_speed,
                    'eta': self.current_eta,
                    'size': self.current_size,
                })

        elif d.get('status') == 'finished':
            self.status = "processing"
            if self.progress_callback:
                self.progress_callback({
                    'task_id': self.task_id,
                    'status': 'processing',
                    'title': self.current_title,
                    'percent': 100.0,
                    'speed': '--',
                    'eta': 'Processing / Merging...',
                    'size': self.current_size,
                })

    def run(self):
        import yt_dlp

        opts = build_format_string(self.mode, self.quality)
        outtmpl = os.path.join(self.output_dir, '%(title)s.%(ext)s')
        opts['outtmpl'] = outtmpl
        opts['progress_hooks'] = [self._hook]

        total_urls = len(self.urls)
        for index, url in enumerate(self.urls, 1):
            if self.is_cancelled:
                self.status = "cancelled"
                break

            try:
                self.status = "fetching_info"
                if self.progress_callback:
                    self.progress_callback({
                        'task_id': self.task_id,
                        'status': 'fetching_info',
                        'item_index': index,
                        'total_items': total_urls,
                        'url': url,
                        'title': f"Fetching metadata ({index}/{total_urls})...",
                        'percent': 0.0
                    })

                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get('title', 'Unknown Title') if info else 'Downloaded Video'
                    self.current_title = title
                    filename = ydl.prepare_filename(info) if info else ""
                    self.results.append({
                        'url': url,
                        'title': title,
                        'status': 'success',
                        'filename': filename,
                        'thumbnail': info.get('thumbnail') if info else None
                    })

            except Exception as e:
                err_str = str(e)
                if self.is_cancelled:
                    self.status = "cancelled"
                    break
                logger.error(f"Download failed for {url}: {err_str}")
                self.results.append({
                    'url': url,
                    'title': f"URL #{index}",
                    'status': 'error',
                    'error': err_str
                })

        if not self.is_cancelled:
            self.status = "completed"

        if self.progress_callback:
            self.progress_callback({
                'task_id': self.task_id,
                'status': self.status,
                'title': "Finished" if self.status == 'completed' else "Stopped",
                'percent': 100.0 if self.status == 'completed' else self.current_percent,
                'results': self.results
            })
