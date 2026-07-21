import asyncio
from p2p_parser import P2PDataFetcher
from keyboards import get_maker_action_menu

# Зберігаємо активні завдання мейкерів у пам'яті (у продакшені краще Redis)
active_maker_tasks = {}

async def maker_monitoring_task(bot, chat_id: int, trade_type: str, target_price: float):
    try:
        while True:
            # Для мейкера-покупця дивимось на тих, хто продає (щоб стати поруч)
            opposite_type = "SELL" if trade_type == "BUY" else "BUY"
            top_orders = await P2PDataFetcher.get_filtered_top_10("Bybit", opposite_type)

            if top_orders:
                best_price = top_orders[0]["price"]
                diff = abs(best_price - target_price)

                if 0.36 <= diff <= 0.50:
                    await bot.send_message(
                        chat_id,
                        f"🔔 Внимание! Цена близка к вашей.\n"
                        f"Ваша цель: {target_price}\n"
                        f"Лучшая цена: {best_price}\n"
                        f"Разница: {round(diff, 2)}",
                        reply_markup=get_maker_action_menu()
                    )

            await asyncio.sleep(10) # Оновлення кожні 10 секунд
    except asyncio.CancelledError:
        pass

def start_maker_task(bot, chat_id: int, trade_type: str, target_price: float):
    if chat_id in active_maker_tasks:
        active_maker_tasks[chat_id].cancel()

    task = asyncio.create_task(maker_monitoring_task(bot, chat_id, trade_type, target_price))
    active_maker_tasks[chat_id] = task

def stop_maker_task(chat_id: int):
    if chat_id in active_maker_tasks:
        active_maker_tasks[chat_id].cancel()
        del active_maker_tasks[chat_id]
