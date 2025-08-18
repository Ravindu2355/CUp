import os
import math
import requests
import subprocess
import shutil
from time import time
from config import CHAT_ID, MAX_SIZE

def get_file_size(url):
    try:
        r = requests.head(url, timeout=10)
        return int(r.headers.get("content-length", 0))
    except:
        return 0

async def download_file(url, filename, client):
    """Download with progress updates every 5s"""
    r = requests.get(url, stream=True)
    total = int(r.headers.get("content-length", 0))
    downloaded = 0
    start_time = time()

    progress_msg = await client.send_message(CHAT_ID, f"⬇️ Downloading `{filename}`...")
    last_update = time()

    with open(filename, "wb") as f:
        for chunk in r.iter_content(1024 * 1024):  # 1MB chunks
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)

            if time() - last_update >= 5:
                percent = downloaded * 100 / total if total else 0
                speed = downloaded / (time() - start_time + 1)
                eta = (total - downloaded) / speed if speed > 0 else 0
                await progress_msg.edit_text(
                    f"⬇️ **Downloading** `{filename}`\n"
                    f"Progress: {percent:.2f}%\n"
                    f"Size: {downloaded/1024/1024:.2f}MB / {total/1024/1024:.2f}MB\n"
                    f"Speed: {speed/1024/1024:.2f} MB/s\n"
                    f"ETA: {math.ceil(eta)}s"
                )
                last_update = time()
    return progress_msg

def generate_thumb_and_duration(filename):
    thumb = f"{filename}.jpg"
    # Duration
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename],
        capture_output=True, text=True
    )
    duration = int(float(result.stdout.strip()))
    # Thumbnail
    subprocess.run(["ffmpeg", "-y", "-i", filename, "-ss", "3", "-vframes", "1", thumb])
    return thumb, duration

def split_file_ffmpeg(filename):
    """Split large file into 1.9GB chunks without re-encoding"""
    out_dir = f"{filename}_parts"
    os.makedirs(out_dir, exist_ok=True)
    cmd = [
        "ffmpeg", "-i", filename, "-c", "copy", "-map", "0",
        "-f", "segment", "-reset_timestamps", "1",
        "-segment_time_metadata", "1",
        "-fs", str(MAX_SIZE),
        os.path.join(out_dir, "part_%03d.mp4")
    ]
    subprocess.run(cmd, check=True)
    return [os.path.join(out_dir, f) for f in sorted(os.listdir(out_dir))]

def cleanup(filename):
    try: os.remove(filename)
    except: pass
    try: os.remove(f"{filename}.jpg")
    except: pass
    try: shutil.rmtree(f"{filename}_parts", ignore_errors=True)
    except: pass
