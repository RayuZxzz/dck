import asyncio
import logging
import random
import aiofiles
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

API_TOKEN = "8161722746:AAHrqSCHAHB0UbWDn5VAl0PBs3tJqX3tBmk"
ADMIN_ID = 5744286333
CHANNEL_ID = "@legendbrother786"
PHOTO_FILE = "photos.txt"
CAPTION_FILE = "caption.txt"

bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def load_photos():
    try:
        async with aiofiles.open(PHOTO_FILE, "r") as f:
            photos = await f.readlines()
        return [p.strip() for p in photos if p.strip()]
    except FileNotFoundError:
        return []


async def load_caption():
    try:
        async with aiofiles.open(CAPTION_FILE, "r", encoding="utf-8") as f:
            return await f.read()
    except FileNotFoundError:
        return "❌ <b>Caption file not found!</b>"


async def send_photo_to_channel(photo_url, caption):
    buttons = [
        [InlineKeyboardButton(text="🌩 Mᴏʀᴇ Fᴇᴇᴅʜᴀᴄᴋ's", callback_data="change_photo")],
        [InlineKeyboardButton(text="🥷 Bᴜʏ Hᴀᴄᴋ 🔥", url="https://telegram.dog/ishowchhetri")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    message = await bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=photo_url,
        caption=caption,
        parse_mode="MarkdownV2",
        reply_markup=markup
    )
    return message.message_id


@dp.message_handler(Command("start"))
async def start(msg: types.Message):
    welcome_message = (
        "🤖 <b>Welcome to the Auto Photo Poster Bot!</b>\n"
        "🛠️ Manage your photos and captions easily with this bot.\n\n"
        "➕ Use /add to add photos\n"
        "📷 Use /send to post a photo with caption\n"
        "📝 Send a new <code>caption.txt</code> file anytime to update caption (MarkdownV2 ready).\n"
        "❌ Use /delete_caption to remove caption file.\n"
    )
    await msg.answer(welcome_message)


@dp.message_handler(Command("add"))
async def add_photo(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    urls = msg.text.split("\n")[1:]
    if not urls:
        await msg.answer("⚠️ <b>Provide photo URLs after /add</b>")
        return
    async with aiofiles.open(PHOTO_FILE, "a") as f:
        await f.writelines([url.strip() + "\n" for url in urls if url.strip()])
    await msg.answer(f"✅ <b>{len(urls)} photos added successfully!</b>")


@dp.message_handler(Command("remove"))
async def remove_photos(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    async with aiofiles.open(PHOTO_FILE, "w") as f:
        await f.write("")
    await msg.answer("🗑️ <b>All photos removed successfully!</b>")


@dp.message_handler(Command("delete_caption"))
async def delete_caption(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    if os.path.exists(CAPTION_FILE):
        os.remove(CAPTION_FILE)
        await msg.answer("🗑️ <b>Caption file deleted successfully!</b>")
    else:
        await msg.answer("❌ <b>No caption file found!</b>")


@dp.message_handler(Command("send"))
async def send(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    photos = await load_photos()
    if not photos:
        await msg.answer("❌ <b>No photos available!</b>")
        return

    photo_url = random.choice(photos)
    caption = await load_caption()

    print(f"\n========== FINAL CAPTION TO BE SENT ==========\n{caption}\n==========================================\n")

    await send_photo_to_channel(photo_url, caption)


@dp.callback_query_handler(lambda c: c.data == "change_photo")
async def change_photo(callback: types.CallbackQuery):
    photos = await load_photos()
    if not photos:
        await callback.answer("No photos available!")
        return

    photo_url = random.choice(photos)
    caption = await load_caption()

    print(f"\n========== FINAL CAPTION TO BE SENT (CHANGE PHOTO) ==========\n{caption}\n==========================================\n")

    buttons = [
        [InlineKeyboardButton(text="🌩 Mᴏʀᴇ Fᴇᴇᴅʜᴀᴄᴋ's", callback_data="change_photo")],
        [InlineKeyboardButton(text="🥷 Bᴜʏ Hᴀᴄᴋ 🔥", url="https://telegram.dog/ishowchhetri")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.edit_message_media(
        media=types.InputMediaPhoto(
            media=photo_url,
            caption=caption,
            parse_mode="MarkdownV2"
        ),
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=markup
    )


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def receive_caption_file(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    if msg.document.file_name != "caption.txt":
        await msg.answer("❌ <b>File name must be</b> <code>caption.txt</code>")
        return

    file_info = await bot.get_file(msg.document.file_id)
    file_path = file_info.file_path
    file = await bot.download_file(file_path)

    content = file.read().decode('utf-8')

    async with aiofiles.open(CAPTION_FILE, 'w', encoding='utf-8') as f:
        await f.write(content)

    await msg.answer("✅ <b>Caption file uploaded successfully!</b>")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
