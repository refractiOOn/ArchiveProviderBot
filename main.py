import os, shutil
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup

from credentials import API_ID, API_HASH, BOT_TOKEN
from buffer import ARCHIVE_STORAGE_DIRECTORY


BUFFER_DIRECTORY = f'{ARCHIVE_STORAGE_DIRECTORY}/tmp'
GET_FILE_CALLBACK_DATA = 'get_file_callback'

app = Client(name='SampleBot',
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN
)


def create_buffer() -> None:
    buffer_dir = Path(BUFFER_DIRECTORY)
    if buffer_dir.exists():
        return

    buffer_dir.mkdir(parents=True, exist_ok=True)
    print(f'Buffer directory created at: {BUFFER_DIRECTORY}')


def list_files() -> list[str]:
    entries = os.listdir(ARCHIVE_STORAGE_DIRECTORY)
    archive_files = [
        file for file in entries
        if os.path.isfile(os.path.join(ARCHIVE_STORAGE_DIRECTORY, file)) and file.lower().endswith(('.zip', '.rar'))
    ]
    return archive_files


def get_account() -> str:
    file_name = list_files().pop()
    shutil.move(f'{ARCHIVE_STORAGE_DIRECTORY}/{file_name}', BUFFER_DIRECTORY)
    return f'{BUFFER_DIRECTORY}/{file_name}'


@app.on_message(filters.command("start"))
async def start_handler(client, message) -> None:
    reply_markup = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text='/get_file')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.reply_text(
        'Click the button below to get the file',
        reply_markup=reply_markup
    )


@app.on_message(filters.command('get_file'))
async def get_file_handler(user, message) -> None:
    try:
        file = get_account()
        print(f'Selected file: {file}')
        await app.send_document(
            chat_id=message.chat.id,
            document=file
        )
        os.remove(file)
    except IndexError:
        await message.reply('No accounts available')


@app.on_callback_query(filters.regex(GET_FILE_CALLBACK_DATA))
async def get_file_callback(user, callback_query):
    await get_file_handler(user, callback_query.message)


def main() -> None:
    create_buffer()
    app.run()


if __name__ == '__main__':
    main()