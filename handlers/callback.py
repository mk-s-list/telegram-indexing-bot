from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import files
from config import ADMIN_ID


# 🔹 Helper: Back Button
def back_btn(to):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data=to)]]
    )


# 🔹 HOME
@Client.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    data = query.data

    # ---------------- HOME ----------------
    if data == "home":
        from handlers.start import main_menu

        await query.message.edit_caption(
            caption=(
                "👋 **Welcome!**\n\n"
                "📂 Browse movies & series using buttons only.\n"
                "👇 Choose an option below."
            ),
            reply_markup=main_menu()
        )

    # ---------------- ABOUT ----------------
    elif data == "about":
        kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("👤 About Owner", callback_data="about_owner"),
                    InlineKeyboardButton("🤖 About Bot", callback_data="about_bot")
                ],
                [InlineKeyboardButton("⬅️ Back", callback_data="home")]
            ]
        )

        await query.message.edit_caption(
            caption="ℹ️ **About Section**\n\nChoose an option:",
            reply_markup=kb
        )

    elif data == "about_bot":
        await query.message.edit_caption(
            caption="🤖 **About Bot**\n\nThis is an open-source indexing bot.",
            reply_markup=back_btn("about")
        )

    elif data == "about_owner":
        await query.message.edit_caption(
            caption="👤 **About Owner**\n\n(You can edit this later)",
            reply_markup=back_btn("about")
        )

    # ---------------- IMPORTANT ----------------
    elif data == "important":
        await query.message.edit_caption(
            caption=(
                "⚠️ **DISCLAIMER**\n\n"
                "• This is an open-source indexing bot\n"
                "• We do NOT host any files\n"
                "• Files are uploaded by users\n"
                "• Owner is not responsible for content\n\n"
                f"📩 Admin ID: `{ADMIN_ID}`"
            ),
            reply_markup=back_btn("home")
        )

    # ---------------- INDEX (A–Z) ----------------
    elif data == "index":
        buttons = []
        row = []

        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            row.append(InlineKeyboardButton(c, callback_data=f"letter_{c}"))
            if len(row) == 6:
                buttons.append(row)
                row = []

        buttons.append([InlineKeyboardButton("#", callback_data="letter_#")])
        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="home")])

        await query.message.edit_caption(
            caption="📚 **Browse by Letter**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ---------------- LETTER CLICK ----------------
    elif data.startswith("letter_"):
        letter = data.split("_")[1]

        query_filter = {"letter": letter} if letter != "#" else {"letter": {"$regex": "^[^A-Z]"}}
        titles = files.distinct("title", query_filter)

        if not titles:
            await query.message.edit_caption(
                caption="❌ No content available.",
                reply_markup=back_btn("index")
            )
            return

        buttons = [
            [InlineKeyboardButton(t, callback_data=f"title_{t}")]
            for t in sorted(titles)
        ]
        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="index")])

        await query.message.edit_caption(
            caption=f"📂 **Titles starting with {letter}**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ---------------- TITLE CLICK ----------------
    elif data.startswith("title_"):
        title = data.replace("title_", "", 1)

        content = files.find_one({"title": title})
        if not content:
            await query.message.edit_caption(
                caption="❌ File not available.\n\n📩 Contact admin.",
                reply_markup=back_btn("index")
            )
            return

        if content["type"] == "movie":
            qualities = files.distinct("quality", {"title": title})
            buttons = [
                [InlineKeyboardButton(q, callback_data=f"movie_{title}_{q}")]
                for q in qualities
            ]
        else:
            seasons = files.distinct("season", {"title": title})
            buttons = [
                [InlineKeyboardButton(f"Season {s}", callback_data=f"season_{title}_{s}")]
                for s in seasons
            ]

        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"letter_{title[0]}")])

        await query.message.edit_caption(
            caption=f"🎬 **{title}**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ---------------- SEASON ----------------
    elif data.startswith("season_"):
        _, title, season = data.split("_")
        season = int(season)

        episodes = files.distinct(
            "episode", {"title": title, "season": season}
        )

        buttons = [
            [InlineKeyboardButton(f"Episode {e}", callback_data=f"episode_{title}_{season}_{e}")]
            for e in episodes
        ]
        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"title_{title}")])

        await query.message.edit_caption(
            caption=f"📺 **{title} – Season {season}**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ---------------- EPISODE ----------------
    elif data.startswith("episode_"):
        _, title, season, episode = data.split("_")
        season, episode = int(season), int(episode)

        qualities = files.distinct(
            "quality",
            {"title": title, "season": season, "episode": episode}
        )

        buttons = [
            [InlineKeyboardButton(q, callback_data=f"send_{title}_{season}_{episode}_{q}")]
            for q in qualities
        ]
        buttons.append(
            [InlineKeyboardButton("⬅️ Back", callback_data=f"season_{title}_{season}")]
        )

        await query.message.edit_caption(
            caption=f"🎞 **Episode {episode}**\nChoose quality:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ---------------- SEND FILE ----------------
    elif data.startswith("send_"):
        _, title, season, episode, quality = data.split("_")
        season, episode = int(season), int(episode)

        file = files.find_one({
            "title": title,
            "season": season,
            "episode": episode,
            "quality": quality
        })

        if not file:
            await query.answer("File not available", show_alert=True)
            return

        await client.send_cached_media(
            chat_id=query.message.chat.id,
            file_id=file["file_id"]
        )

        await query.answer("📤 File sent!")
