import os
import requests
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN
from downloader import (
    get_file_size, download_file, generate_thumb_and_duration,
    split_file_ffmpeg, cleanup
)
from uploader import upload_with_progress

# Bot state
url_pattern = None
start_id = None
end_id = None
current_id = None
is_running = False

app = Client("bulk_uploader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def file_exists(url):
    try:
        r = requests.head(url, timeout=10)
        return r.status_code == 200
    except:
        return False

async def process_file(client, url, file_id):
    filename = f"{file_id}.mp4"
    file_size = get_file_size(url)
    progress_msg = await download_file(url, filename, client)

    if file_size > 1900 * 1024 * 1024:
        await progress_msg.edit_text("⚡ Splitting file into 1.9GB parts...")
        parts = split_file_ffmpeg(filename)
        os.remove(filename)
        part_no = 1
        for part in parts:
            thumb, duration = generate_thumb_and_duration(part)
            await upload_with_progress(client, part, thumb, duration, progress_msg, f"{file_id}-part{part_no}")
            cleanup(part)
            part_no += 1
    else:
        thumb, duration = generate_thumb_and_duration(filename)
        await upload_with_progress(client, filename, thumb, duration, progress_msg, file_id)
        cleanup(filename)

async def process_files(client, message):
    global current_id, is_running
    while is_running and current_id <= end_id:
        url = url_pattern.format(id=current_id)
        if file_exists(url):
            try:
                await process_file(client, url, current_id)
            except Exception as e:
                await message.reply(f"❌ Error {current_id}: {e}")
        current_id += 1
    if current_id > end_id:
        await message.reply("✅ Finished all files.")

# -------- Commands --------
@app.on_message(filters.command("url") & filters.private)
async def set_url(client, message):
    global url_pattern, start_id, end_id, current_id
    try:
        _, pattern, start, end = message.text.split()
        url_pattern = pattern
        start_id = int(start)
        end_id = int(end)
        current_id = start_id
        await message.reply(f"🔗 URL pattern set!\nFrom **{start_id}** to **{end_id}**\nPattern: `{pattern}`")
    except:
        await message.reply("❌ Usage: /url <url_pattern_with_{id}> <start_id> <end_id>")

@app.on_message(filters.command("run") & filters.private)
async def run_process(client, message):
    global is_running
    if not url_pattern:
        return await message.reply("❌ First set URL with /url command.")
    if is_running:
        return await message.reply("⚡ Already running.")
    is_running = True
    await message.reply("▶️ Started processing...")
    await process_files(client, message)

@app.on_message(filters.command("stop") & filters.private)
async def stop_process(client, message):
    global is_running
    is_running = False
    await message.reply("⏸️ Stopped. Use /continue to resume.")

@app.on_message(filters.command("continue") & filters.private)
async def continue_process(client, message):
    global is_running
    if not url_pattern:
        return await message.reply("❌ First set URL with /url command.")
    if is_running:
        return await message.reply("⚡ Already running.")
    is_running = True
    await message.reply(f"▶️ Resuming from ID {current_id}...")
    await process_files(client, message)

@app.on_message(filters.command("reset") & filters.private)
async def reset_process(client, message):
    global is_running, url_pattern, start_id, end_id, current_id
    url_pattern = None
    start_id = None
    end_id = None
    current_id = None
    is_running = False
    await message.reply("Reseted ✅️")


app.run()
