import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from bs4 import BeautifulSoup   
from datetime import datetime


bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

async def send_currency_rates(message: Message):
    url = 'https://www.nbkr.kg/index.jsp?lang=RUS'
    response = requests.get(url=url)
    soup = BeautifulSoup(response.text, 'lxml')
    currencies = soup.find_all('td', class_='exrate')

    chat_id = message.chat.id
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    await bot.send_message(chat_id=chat_id, text=f"Приветствую! Я бот, который поможет вам узнать текущие курсы валют.\n"
                                                 f"Вот актуальные курсы на {current_time}:\n"
                                                 f"Курс USD: {currencies[0].text}\n"
                                                 f"Курс EUR: {currencies[2].text}\n"
                                                 f"Курс RUB: {currencies[4].text}\n"
                                                 f"Курс KZT: {currencies[6].text}")

async def send_currency_rates_periodically(message: Message):
    while True:
        await send_currency_rates(message)
        await asyncio.sleep(60)

@dp.message(Command("start"))
async def start(message: Message):
    await send_currency_rates(message)
    asyncio.create_task(send_currency_rates_periodically(message))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
