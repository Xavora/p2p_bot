import aiohttp
from config import MIN_AMOUNT, MIN_COMPLETION_RATE, MIN_ORDERS

class P2PDataFetcher:
    @staticmethod
    async def fetch_order_book(exchange: str, trade_type: str) -> list:
        if exchange.lower() != "bybit":
            return [] # Поки що реалізуємо тільки Bybit

        # Bybit API URL для P2P
        url = "https://api2.bybit.com/fiat/otc/item/online"

        # trade_type: якщо користувач хоче КУПИТИ (BUY), ми шукаємо оголошення продавців (1)
        # якщо ПРОДАТИ (SELL), ми шукаємо оголошення покупців (0)
        side = "1" if trade_type == "BUY" else "0"

        # Тіло запиту (POST payload)
        payload = {
            "userId": "",
            "tokenId": "USDT",
            "currencyId": "UAH", # Зміни на потрібний фіат (наприклад, KZT, PLN)
            "payment": [],
            "side": side,
            "size": "20",        # Кількість оголошень для парсингу
            "page": "1",
            "amount": "",
            "authMaker": False,
            "canTrade": False
        }

        # Заголовки, щоб біржа думала, що ми звичайний браузер
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        orders = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Парсимо JSON відповідь від Bybit
                        items = data.get("result", {}).get("items", [])

                        for item in items:
                            orders.append({
                                "price": float(item["price"]),
                                "advertiser": item["nickName"],
                                "orders_count": int(item["recentOrderNum"]),
                                "completion_rate": float(item["recentExecuteRate"]),
                                "min_amount": float(item["minQuoteInToken"]) # Мінімальна сума в крипті або фіаті
                            })

        except Exception as e:
            print(f"Помилка парсингу Bybit: {e}")

        return orders

    @staticmethod
    async def get_filtered_top_10(exchange: str, trade_type: str) -> list:
        """Топ-10 оголошень після анти-скам фільтрів, відсортовані за вигідністю ціни."""
        orders = await P2PDataFetcher.fetch_order_book(exchange, trade_type)

        filtered = [
            o for o in orders
            if o["completion_rate"] >= MIN_COMPLETION_RATE
            and o["orders_count"] >= MIN_ORDERS
            and o["min_amount"] <= MIN_AMOUNT
        ]

        # Купуємо — шукаємо найдешевших продавців; продаємо — найдорожчих покупців
        filtered.sort(key=lambda o: o["price"], reverse=(trade_type == "SELL"))
        return filtered[:10]

    @staticmethod
    async def get_average_course(exchange: str, trade_type: str) -> float:
        """Середня ціна по топ-10 відфільтрованих оголошень (0.0, якщо даних немає)."""
        top_orders = await P2PDataFetcher.get_filtered_top_10(exchange, trade_type)
        if not top_orders:
            return 0.0
        return sum(o["price"] for o in top_orders) / len(top_orders)