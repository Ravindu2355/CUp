import math
from time import time
from config import CHAT_ID

last_t={
    text:"",
};

async def upload_with_progress(client, filename, thumb, duration, progress_msg, file_id):
    start_time = time()

    async def progress(current, total):
        percent = current * 100 / total if total else 0
        speed = current / (time() - start_time + 1)
        eta = (total - current) / speed if speed > 0 else 0
        if int(time() - start_time) % 5 == 0:  # update every 5s
            try:
                tt = (
                     f"⬆️ **Uploading** `{filename}`\n"
                     f"Progress: {percent:.2f}%\n"
                     f"Uploaded: {current/1024/1024:.2f}MB / {total/1024/1024:.2f}MB\n"
                     f"Speed: {speed/1024/1024:.2f} MB/s\n"
                     f"ETA: {math.ceil(eta)}s"
                )
                if tt != last_t["text"]:
                    await progress_msg.edit_text(tt)
                    last_t["text"] = tt
            except:
                pass

    await client.send_video(
        CHAT_ID,
        video=filename,
        thumb=thumb,
        duration=duration,
        supports_streaming=True,
        caption=f"✅ Uploaded ID: {file_id}",
        progress=progress
    )
    await progress_msg.delete()
