import aiohttp
import asyncio
import logging
import schedule
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, BotCommand
from config import token

bot = Bot(token=token)
dp = Dispatcher()

logging.basicConfig(filename='crypto_monitoring.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
        
monitoring = False
chat_id = None
selected_crypto = None


async def get_crypto_price(symbol):
    url = f'https://api.binance.com/api/v3/avgPrice?symbol={symbol}USDT'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                json_response = await response.json()
                price = json_response.get('price')
                if price:
                    return f'Стоимость {symbol} на {time.ctime()}, {price}'
                else:
                    return f'Не удалось получить цену {symbol}'
    except Exception as e:
        logging.error(f'Ошибка при запросе {symbol}: {e}')
        return 'Ошибка запроса к Binance API'


async def monitor_crypto_price(symbol):
    global monitoring
    logging.info(f'Начат мониторинг {symbol}')
    while monitoring:
        try:
            message = await get_crypto_price(symbol)
            logging.info(f'Изменение цены {symbol}: {message}')
            await bot.send_message(chat_id, message)
        except Exception as e:
            logging.error(f'Ошибка мониторинга {symbol}: {e}')
        await asyncio.sleep(10)
    logging.info(f'Мониторинг {symbol} остановлен')


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.full_name}')


@dp.message(Command('btc'))
async def btc(message: Message):
    global chat_id, monitoring, selected_crypto
    chat_id = message.chat.id
    selected_crypto = 'BTC'
    if not monitoring:
        monitoring = True
        await message.answer("Начало мониторинга Bitcoin")
        asyncio.create_task(monitor_crypto_price(selected_crypto))
    else:
        await message.answer("Мониторинг уже запущен!")


@dp.message(Command('eth'))
async def eth(message: Message):
    global chat_id, monitoring, selected_crypto
    chat_id = message.chat.id
    selected_crypto = 'ETH'
    if not monitoring:
        monitoring = True
        await message.answer("Начало мониторинга Ethereum")
        asyncio.create_task(monitor_crypto_price(selected_crypto))
    else:
        await message.answer("Мониторинг уже запущен!")


@dp.message(Command('ltc'))
async def ltc(message: Message):
    global chat_id, monitoring, selected_crypto
    chat_id = message.chat.id
    selected_crypto = 'LTC'
    if not monitoring:
        monitoring = True
        await message.answer("Начало мониторинга Litecoin")
        asyncio.create_task(monitor_crypto_price(selected_crypto))
    else:
        await message.answer("Мониторинг уже запущен!")


@dp.message(Command('stop'))
async def stop(message: Message):
    global monitoring
    if monitoring:
        monitoring = False
        await message.answer("Мониторинг остановлен")
    else:
        await message.answer("Мониторинг уже остановлен")


def periodic_report():
    loop = asyncio.get_event_loop()
    if selected_crypto:
        message = loop.run_until_complete(get_crypto_price(selected_crypto))
        loop.run_until_complete(bot.send_message(chat_id, f'Периодический отчет: {message}'))


def scheduler():
    schedule.every(10).minutes.do(periodic_report)
    while True:
        schedule.run_pending()
        time.sleep(1)
