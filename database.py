import aiosqlite

DB_NAME = "p2p_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблиця сесій (хто авторизований)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER PRIMARY KEY
            )
        """)
        # Таблиця історії сигналів
        await db.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                buy_exchange TEXT,
                sell_exchange TEXT,
                profit_percent REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def is_authorized(user_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT 1 FROM sessions WHERE user_id = ?", (user_id,))
        return await cursor.fetchone() is not None

async def authorize_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO sessions (user_id) VALUES (?)", (user_id,))
        await db.commit()
