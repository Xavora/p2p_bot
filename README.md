# P2P Trading Assistant Bot

A Telegram bot for monitoring the Bybit P2P market (USDT/UAH). It tracks live order books, calculates average rates and spreads, and alerts market makers when the price approaches their target.

## Features

- **Login/password access control** — only whitelisted users can use the bot; authorized sessions persist in SQLite; password messages are auto-deleted from the chat
- **Live P2P rates** — fetches the Bybit P2P order book (buy and sell sides) and shows average top-10 rates
- **Anti-scam filtering** — advertisers are filtered by minimum order amount, completion rate and completed-order count (configurable in `config.py`)
- **Auto-spread analysis** — computes the current clean spread and a recommended maker spread with fees taken into account
- **Maker price tracker** — set a target buy/sell price; a background task polls the market every 10 seconds and sends an alert with quick-action buttons when the best price gets close to your target
- **Inline-keyboard UX** — full menu-driven flow built on aiogram FSM states

## Tech Stack

- Python 3, asyncio
- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot API framework (FSM, inline keyboards)
- [aiohttp](https://docs.aiohttp.org/) — async requests to the Bybit P2P API
- [aiosqlite](https://github.com/omnilib/aiosqlite) — SQLite storage for sessions and signal history
- python-dotenv — configuration via `.env`

## Getting Started

1. Clone the repo and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your bot token (get one from [@BotFather](https://t.me/BotFather)):

   ```
   BOT_TOKEN=your_telegram_bot_token
   ```

3. Set your user credentials and market filters in `config.py` (`AUTHORIZED_USERS`, `MIN_AMOUNT`, `MIN_COMPLETION_RATE`, `MIN_ORDERS`).

4. Run the bot:

   ```bash
   python bot.py
   ```

The SQLite database (`p2p_bot.db`) is created automatically on first run.

## Project Structure

```
├── bot.py           # Entry point: handlers, auth flow, menus
├── config.py        # Token loading, user whitelist, anti-scam filters
├── p2p_parser.py    # Bybit P2P order book fetcher and filters
├── maker_service.py # Background price-tracking tasks with alerts
├── database.py      # SQLite: sessions and signal history
├── keyboards.py     # Inline keyboard layouts
└── requirements.txt
```