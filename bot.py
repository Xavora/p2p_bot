import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import config
from database import init_db, is_authorized, authorize_user
from keyboards import get_main_menu
from p2p_parser import P2PDataFetcher
from maker_service import start_maker_task, stop_maker_task

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

class AuthStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

class MakerStates(StatesGroup):
    waiting_for_buy_price = State()
    waiting_for_sell_price = State()

# --- АВТОРИЗАЦІЯ ---

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    if await is_authorized(message.from_user.id):
        await message.answer("Главное меню", reply_markup=get_main_menu())
        return

    await message.answer("🔐 Введите логин:")
    await state.set_state(AuthStates.waiting_for_login)

@dp.message(AuthStates.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("🔑 Введите пароль:")
    await state.set_state(AuthStates.waiting_for_password)

@dp.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get("login")
    password = message.text

    # Видалення повідомлення з паролем для безпеки
    try:
        await message.delete()
    except Exception as e:
        logging.error(f"Не вдалося видалити повідомлення: {e}")

    if config.AUTHORIZED_USERS.get(login) == password:
        await authorize_user(message.from_user.id)
        await message.answer("✅ Доступ разрешен!", reply_markup=get_main_menu())
        await state.clear()
    else:
        await message.answer("❌ Неверный логин или пароль. Доступ закрыт. Нажмите /start для повторной попытки.")
        await state.clear()

# --- МІДЛВАР (Перевірка доступу для колбеків) ---

@dp.callback_query()
async def check_auth_callback(callback: CallbackQuery, state: FSMContext):
    if not await is_authorized(callback.from_user.id):
        await callback.answer("У вас нет доступа. Введите /start", show_alert=True)
        return
    # Передача керування далі
    await dp.propagate_event("callback_query", callback)


# --- ОСНОВНЕ МЕНЮ ТА ЛОГІКА ---

@dp.callback_query(F.data == "menu_courses")
async def show_courses(callback: CallbackQuery):
    await callback.message.edit_text("⏳ Анализирую актуальные курсы (ТОП-10)...")

    buy_orders = await P2PDataFetcher.get_filtered_top_10("Bybit", "BUY")
    sell_orders = await P2PDataFetcher.get_filtered_top_10("Bybit", "SELL")

    avg_buy = await P2PDataFetcher.get_average_course("Bybit", "BUY")
    avg_sell = await P2PDataFetcher.get_average_course("Bybit", "SELL")

    text = "📉 **Актуальные курсы (Bybit)**\n\n"
    text += f"🟢 Средний курс ПОКУПКИ (ТОП-10): {avg_buy:.2f}\n"
    text += f"🔴 Средний курс ПРОДАЖИ (ТОП-10): {avg_sell:.2f}\n\n"

    await callback.message.edit_text(text, reply_markup=get_main_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "menu_spread")
async def show_spread(callback: CallbackQuery):
    avg_buy = await P2PDataFetcher.get_average_course("Bybit", "BUY")
    avg_sell = await P2PDataFetcher.get_average_course("Bybit", "SELL")

    spread_abs = avg_sell - avg_buy
    spread_pct = (spread_abs / avg_buy) * 100 if avg_buy else 0

    text = (
        "🧠 **Авто-спред Анализ**\n\n"
        f"Текущий чистый спред: {spread_abs:.2f} ({spread_pct:.2f}%)\n"
        f"Рекомендованный спред для мейкера: {spread_pct - 0.2:.2f}% (с учетом комиссий)\n"
    )
    await callback.message.edit_text(text, reply_markup=get_main_menu(), parse_mode="Markdown")

# --- ЛОГІКА МЕЙКЕРА ---

@dp.callback_query(F.data == "menu_buy_maker")
async def start_buy_maker(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("💰 Введите желаемый курс для ПОКУПКИ:")
    await state.set_state(MakerStates.waiting_for_buy_price)

@dp.message(MakerStates.waiting_for_buy_price)
async def process_buy_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
        start_maker_task(bot, message.from_user.id, "BUY", price)
        await message.answer(f"✅ Трекер запущен. Ожидание приближения цены к {price}...", reply_markup=get_main_menu())
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите корректное число (например, 39.50)")

@dp.callback_query(F.data.startswith("maker_action_"))
async def handle_maker_actions(callback: CallbackQuery):
    action = callback.data.split("_")[2]

    if action == "stop" or action == "buy":
        stop_maker_task(callback.from_user.id)
        msg = "🛑 Мониторинг остановлен." if action == "stop" else "✅ Вы закупаетесь. Мониторинг остановлен."
        await callback.message.edit_text(msg)
    elif action == "wait_exact":
        await callback.answer("Продолжаю отслеживание (точное ожидание 0.01-0.10)...")
    elif action == "wait_near":
        await callback.answer("Продолжаю отслеживание (приближение 0.11-0.35)...")

async def main():
    await init_db()
    logging.info("Бот запущен. База данных инициализирована.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
