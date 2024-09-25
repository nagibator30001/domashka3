
import sqlite3
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import asyncio
from config import token

bot = Bot(token=token)
dp = Dispatcher()

stop_parsing = asyncio.Event()

def init_db():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_news_to_db(news):
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO news (news) VALUES (?)', (news,))
    conn.commit()
    conn.close()

# Клавиатура с кнопкой "Stop"
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Stop")]
    ],
    resize_keyboard=True
)

@dp.message(Command('start'))
async def start(message: Message):
    await message.answer("Привет! Я бот новостей. Чтобы получить новости, введите команду /news.", reply_markup=keyboard)

@dp.message(Command('news'))
async def news(message: Message):
    stop_parsing.clear()  
    await message.answer("Начинаю парсинг новостей...", reply_markup=keyboard)

    for page in range(1, 11):
        if stop_parsing.is_set():
            await message.answer("Парсинг новостей остановлен.", reply_markup=keyboard)
            break

        url = f'https://24.kg/page_{page}'
        try:
            response = requests.get(url=url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            all_news = soup.find_all('div', class_='one')

            for news_item in all_news:
                if stop_parsing.is_set():
                    await message.answer("Парсинг новостей остановлен.", reply_markup=keyboard)
                    break

                news_title_div = news_item.find('div', class_='title')
                news_link = news_item.find('a')
                if news_title_div and news_link:
                    news_title = news_title_div.text.strip()
                    news_url = f"https://24.kg{news_link['href']}"
                    news_text = f"{news_title}\n{news_url}"
                    add_news_to_db(news_text)

                    # Разбиваем текст новости на части длиной не более 4096 символов
                    while len(news_text) > 0:
                        await message.answer(news_text[:4096])
                        news_text = news_text[4096:]

        except Exception as e:
            await message.answer(f"Произошла ошибка при получении новостей: {e}", reply_markup=keyboard)

@dp.message(lambda message: message.text == "Stop")
async def stop(message: Message):
    stop_parsing.set()
    await message.answer("Парсинг новостей будет остановлен.", reply_markup=keyboard)

init_db()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
