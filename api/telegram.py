import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import asyncio

# --- Основні дані ---
PSYCHOLOGIST_ID = 721614105
TOKEN = os.getenv("7640887728:AAF4-NQ14ufDYPJRon-6VZaW_s9mqseemko")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Клавіатура ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💙 Підтримка")],
        [KeyboardButton(text="🧘 Дихальна практика"), KeyboardButton(text="📖 Корисні матеріали")],
        [KeyboardButton(text="Cтрес"), KeyboardButton(text="Тривога")],
        [KeyboardButton(text="Депресія"), KeyboardButton(text="Самотність")]
    ],
    resize_keyboard=True
)

# --- Команди ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Привіт! Я бот психологічної підтримки. Обери дію:",
        reply_markup=main_kb
    )

@dp.message(Command("myid"))
async def get_id(message: types.Message):
    await message.answer(f"🆔 Твій Telegram ID: <code>{message.from_user.id}</code>", parse_mode=ParseMode.HTML)

# --- FSM стан ---
class SupportState(StatesGroup):
    waiting_for_message = State()

user_message_map = {}

# --- Підтримка ---
@dp.message(F.text == "💙 Підтримка")
async def ask_for_message(message: types.Message, state: FSMContext):
    await message.answer("📝 Напиши своє повідомлення. Я передам його психологу.")
    await state.set_state(SupportState.waiting_for_message)

@dp.message(SupportState.waiting_for_message)
async def handle_user_message(message: types.Message, state: FSMContext):
    user = message.from_user
    text = f"<b>💌 Повідомлення від:</b> {user.full_name} (@{user.username or 'без юзернейму'})\n\n{message.text}"

    sent_msg = await bot.send_message(chat_id=PSYCHOLOGIST_ID, text=text, parse_mode=ParseMode.HTML)
    user_message_map[sent_msg.message_id] = user.id
    await state.clear()
    await message.answer("✅ Повідомлення надіслано психологу.")

@dp.message(F.chat.id == PSYCHOLOGIST_ID)
async def psychologist_reply(message: types.Message):
    if message.reply_to_message:
        original_id = message.reply_to_message.message_id
        if original_id in user_message_map:
            user_id = user_message_map[original_id]
            await bot.send_message(chat_id=user_id, text=f"📩 Відповідь психолога:\n\n{message.text}")
            await message.answer("✅ Відповідь надіслано користувачу.")
        else:
            await message.answer("⚠️ Не знайдено, кому надіслати відповідь.")
    else:
        await message.answer("❗ Щоб відповісти користувачу, використай 'Reply' на його повідомлення.")

# --- Тематичні кнопки ---
@dp.message(F.text == "Cтрес")
async def stress_handler(message: types.Message):
    await message.answer("Спробуй зробити глибокий вдих і видих. Дихальні практики допомагають знизити рівень стресу.")

@dp.message(F.text == "Тривога")
async def alert_handler(message: types.Message):
    await message.answer("Тривога – це нормально. Спробуй зосередитися на теперішньому моменті.")

@dp.message(F.text == "Самотність")
async def alon_handler(message: types.Message):
    await message.answer("Ти не один. Якщо тобі дуже важко, можливо, варто звернутися до спеціаліста.")

@dp.message(F.text == "Депресія")
async def depr_handler(message: types.Message):
    await message.answer("Ти важливий! Поговори з друзями чи сім’єю, це може допомогти.")

@dp.message(F.text == "🧘 Дихальна практика")
async def breathing(message: types.Message):
    await message.answer(
        "🫁 Спробуй цю техніку:\n\n"
        "1️⃣ Вдихай на 4 секунди\n"
        "2️⃣ Затримай дихання на 4 секунди\n"
        "3️⃣ Видихай на 4 секунди\n"
        "4️⃣ Повтори 5 разів"
    )

@dp.message(F.text == "📖 Корисні матеріали")
async def materials(message: types.Message):
    await message.answer(
        "📚 Корисні посилання:\n"
        "• Корисні звички, що допоможуть знизити стрес: — https://phc.org.ua/news/korisni-zvichki-scho-dopomozhut-zniziti-stres\n"
        "• Що таке стрес та як з ним боротися? — https://mgc-pd.kr.ua/shho-take-stres-ta-yak-z-nim-borotisya\n"
        "• Рекомендації з психологічної допомоги: - https://moz.gov.ua/uk/rekomendacii-z-psihologichnoi-dopomogi\n"
        "• Як подолати тривогу й стрес. Дієві поради та вправи - https://phc.org.ua/news/yak-podolati-trivogu-y-stres-dievi-poradi-ta-vpravi\n"
        "• Як боротися зі стресом: - https://timeplus.ua/yak-borotysia-zi-stresom-efektyvni-sposoby-ta-tekhniky"
    )

# --- Webhook ---
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

app = asyncio.get_event_loop().run_until_complete(create_app())
