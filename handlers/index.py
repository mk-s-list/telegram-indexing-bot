import re
from pyrogram import Client, filters
from database import files
from config import FILE_CHANNEL


# 🔹 CAPTION PARSER (supports both formats)
def parse_caption(caption: str):
    caption_low = caption.lower()

    # TITLE (first word(s) before SxxExx if exists)
    title_match = re.split(r"s\d+e\d+", caption, flags=re.I)
    title = title_match[0].strip().title()

    # SEASON & EPISODE
    season = episode = None
    s = re.search(r"s(\d+)", caption_low)
    e = re.search(r"e(\d+)", caption_low)

    if s:
        season = int(s.group(1))
    if e:
        episode = int(e.group(1))

    # QUALITY
    quality = "Unknown"
    for q in ["360p", "480p", "720p", "1080p"]:
        if q in caption_low:
            quality = q
            break

    content_type = "movie" if not season else "series"

    return {
        "title": title,
        "type": content_type,
        "season": season,
        "episode": episode,
        "quality": quality,
        "letter": title[0].upper()
    }


# 🔹 AUTO INDEX FILES FROM CHANNEL
@Client.on_message(
    filters.channel & filters.chat(FILE_CHANNEL) &
    (filters.document | filters.video)
)
async def auto_index(client, message):

    if not message.caption:
        return

    data = parse_caption(message.caption)

    file_id = None
    if message.document:
        file_id = message.document.file_id
    elif message.video:
        file_id = message.video.file_id

    if not file_id:
        return

    # prevent duplicate indexing
    exists = files.find_one({
        "title": data["title"],
        "season": data["season"],
        "episode": data["episode"],
        "quality": data["quality"]
    })

    if exists:
        return

    data["file_id"] = file_id
    files.insert_one(data)

    print(f"Indexed: {data['title']} | {data['season']} | {data['episode']} | {data['quality']}")
