import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


PSYCHOLOGIST_ID = 721614105

load_dotenv()
TOKEN = "7640887728:AAF4-NQ14ufDYPJRon-6VZaW_s9mqseemko"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Створюємо клавіатуру
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💙 Підтримка")],
        [KeyboardButton(text="🧘 Дихальна практика"), KeyboardButton(text="📖 Корисні матеріали")],
	    [KeyboardButton(text="Cтрес"), KeyboardButton(text="Тривога")],
	    [KeyboardButton(text="Депресія"), KeyboardButton(text="Самотність")]
    ],
    resize_keyboard=True
)
#keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#keyboard.add(KeyboardButton("💙 Підтримка"))
#keyboard.add(KeyboardButton("🧘 Дихальна практика"), KeyboardButton("📖 Корисні матеріали"))
#keyboard.add(KeyboardButton("Cтрес"), KeyboardButton("Тривога"))
#keyboard.add(KeyboardButton("Депресія"), KeyboardButton("Самотність"))

# Оновлений обробник команди /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Привіт! Я бот психологічної підтримки. Обери дію:",
        reply_markup=main_kb
    )


@dp.message(Command("myid"))
async def get_id(message: types.Message):
    await message.answer(f"🆔 Твій Telegram ID: <code>{message.from_user.id}</code>")

# Додаємо обробку кнопок
# Стан для FSM
class SupportState(StatesGroup):
    waiting_for_message = State()

# Кнопка "Підтримка"
@dp.message(F.text == "💙 Підтримка")
async def ask_for_message(message: types.Message, state: FSMContext):
    await message.answer("📝 Напиши своє повідомлення. Я передам його психологу.")
    await state.set_state(SupportState.waiting_for_message)

# Обробка наступного повідомлення
@dp.message(SupportState.waiting_for_message)
async def handle_user_message(message: types.Message, state: FSMContext):
    user = message.from_user
    text = f"<b>💌 Повідомлення від:</b> {user.full_name} (@{user.username or 'без юзернейму'})\n\n{message.text}"

    # Пересилаємо психологу, додаючи ID користувача в підпис
    sent_msg = await bot.send_message(chat_id=PSYCHOLOGIST_ID, text=text)

    # Зберігаємо user_id в caption message_id → user_id
    await state.clear()

    # Зберігаємо user_id в базу (спрощено: у dict)
    user_message_map[sent_msg.message_id] = user.id

    await message.answer("✅ Повідомлення надіслано психологу.")

# Словник message_id → user_id
user_message_map = {}

# Обробка відповіді психолога
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


@dp.message(F.text == "Cтрес")
async def stress_handler(message: types.Message):
    await message.answer("Спробуй зробити глибокий вдих і видих. Дихальні практики допомагають знизити рівень стресу.")
    

@dp.message(F.text == "Тривога")
async def alert_handler(message: types.Message):
    await message.answer("Тривога – це нормально. Спробуй зосередитися на теперішньому моменті.")

@dp.message(F.text == "Самотність")
async def depr_handler(message: types.Message):
    await message.answer("Ти не один. Якщо тобі дуже важко, можливо, варто звернутися до спеціаліста.")

@dp.message(F.text == "Депресія")
async def alon_handler(message: types.Message):
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
        "• Що таке стрес та як з ним боротися? — https://mgc-pd.kr.ua/shho-take-stres-ta-yak-z-nim-borotisya/?utm_source=chatgpt.com"
	"• Рекомендації з психологічної допомоги: - https://moz.gov.ua/uk/rekomendacii-z-psihologichnoi-dopomogi?utm_source=chatgpt.com"
	"• Як подолати тривогу й стрес. Дієві поради та вправи - https://phc.org.ua/news/yak-podolati-trivogu-y-stres-dievi-poradi-ta-vpravi?utm_source=chatgpt.com"
 	"• Як боротися зі стресом: - https://timeplus.ua/yak-borotysia-zi-stresom-efektyvni-sposoby-ta-tekhniky?utm_source=chatgpt.com"
    )



# Відповідь на будь-яке повідомлення
# @dp.message_handler()
# async def echo_handler(message: types.Message):
#     response = get_psychological_response(message.text)
#     await message.answer(response)

# def get_psychological_response(text):
#     """Проста логіка відповідей"""
#     keywords = {
#         "стрес": "Спробуй зробити глибокий вдих і видих. Дихальні практики допомагають знизити рівень стресу.",
#         "тривога": "Тривога – це нормально. Спробуй зосередитися на теперішньому моменті.",
#         "депресія": "Ти не один. Якщо тобі дуже важко, можливо, варто звернутися до спеціаліста.",
#         "самотність": "Ти важливий! Поговори з друзями чи сім’єю, це може допомогти."
#     }
    
#     for word, response in keywords.items():
#         if word in text.lower():
#             return response
#     return "Я тут, щоб підтримати тебе. Напиши, що тебе турбує 💙"



# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
