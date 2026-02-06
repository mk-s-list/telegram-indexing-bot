from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID


# 🔹 Main Menu Keyboard
def main_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📚 Index", callback_data="index")],
            [
                InlineKeyboardButton("ℹ️ About", callback_data="about"),
                InlineKeyboardButton("📝 Request", url="https://t.me/OTC_BEN_BOT")
            ],
            [InlineKeyboardButton("⚠️ Important", callback_data="important")]
        ]
    )


# 🔹 /start Command
@Client.on_message(filters.private & filters.command("start"))
async def start_cmd(client, message):
    text = (
        "👋 **Welcome!**\n\n"
        "📂 This bot helps you browse indexed movies & series easily.\n"
        "🎯 No searching, only buttons.\n\n"
        "👇 Use the buttons below to continue."
    )

    await message.reply_photo(
        photo="https://i.imgur.com/8wKQZgP.jpeg",  # you can change later
        caption=text,
        reply_markup=main_menu()
    )
