from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Отслеживать рынок", callback_data="menu_track")],
        [
            InlineKeyboardButton(text="💰 Купить (мейкер)", callback_data="menu_buy_maker"),
            InlineKeyboardButton(text="💸 Продать (мейкер)", callback_data="menu_sell_maker")
        ],
        [InlineKeyboardButton(text="📉 Актуальные курсы", callback_data="menu_courses")],
        [InlineKeyboardButton(text="🧠 Авто-спред", callback_data="menu_spread")],
        [InlineKeyboardButton(text="🔔 Арбитраж", callback_data="menu_arbitrage")],
        [InlineKeyboardButton(text="📈 История сигналов", callback_data="menu_history")]
    ])

def get_maker_action_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Закупаюсь", callback_data="maker_action_buy")],
        [InlineKeyboardButton(text="⏳ Ждать точно", callback_data="maker_action_wait_exact")],
        [InlineKeyboardButton(text="📡 Ждать приближение", callback_data="maker_action_wait_near")],
        [InlineKeyboardButton(text="🛑 Стоп", callback_data="maker_action_stop")]
    ])
