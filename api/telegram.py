import os
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Приклад простої відповіді
@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Привіт 👋 Ти написав: {message.text}")

async def on_startup(app):
    webhook_url = f"https://{os.getenv('VERCEL_URL')}/api/telegram"
    await bot.set_webhook(webhook_url)

async def on_shutdown(app):
    await bot.session.close()

async def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/api/telegram")
    setup_application(app, dp, on_startup, on_shutdown)
    return app

app = asyncio.run(main())
