import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логіни та паролі задаються в .env у форматі: AUTHORIZED_USERS=login1:pass1,login2:pass2
AUTHORIZED_USERS = dict(
    pair.split(":", 1)
    for pair in os.getenv("AUTHORIZED_USERS", "").split(",")
    if ":" in pair
)

# Налаштування P2P
MIN_AMOUNT = 1000
MIN_COMPLETION_RATE = 90.0 # Анти-скам: мінімальний % успішних угод
MIN_ORDERS = 50            # Анти-скам: мінімальна кількість ордерів
