import requests
import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8707402017:AAFli5Hl3mmsxVGOHd812AwGCSOqdcHd6rA"

coins = ["bitcoin", "ethereum", "solana", "chainlink"]

user_chat_id = None
last_market_status = None
sent_signals = set()

# 📊 Global Data
def get_global():
    data = requests.get("https://api.coingecko.com/api/v3/global").json()["data"]
    btc_dom = data["market_cap_percentage"]["btc"]
    total_cap = data["total_market_cap"]["usd"]
    return btc_dom, total_cap

# 📊 USDT Dominance
def get_usdt_dom():
    usdt = requests.get("https://api.coingecko.com/api/v3/coins/tether").json()
    usdt_mc = usdt["market_data"]["market_cap"]["usd"]

    total_cap = requests.get("https://api.coingecko.com/api/v3/global").json()["data"]["total_market_cap"]["usd"]

    return round((usdt_mc / total_cap) * 100, 2)

# 📊 الأسعار
def get_data(coin):
    data = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=1").json()
    prices = [p[1] for p in data["prices"]]
    volumes = [v[1] for v in data["total_volumes"]]
    return prices, volumes

# 📊 RSI
def rsi(prices, period=14):
    gains, losses = [], []

    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

# 📊 دعم ومقاومة
def levels(prices):
    return min(prices[-30:]), max(prices[-30:])

# 🧠 Market Filter
def market_filter():
    btc_dom, _ = get_global()
    usdt_dom = get_usdt_dom()

    if btc_dom < 55 and usdt_dom < 6:
        return "RISK ON"
    else:
        return "RISK OFF"

# 🧠 تحليل العملة
def analyze(coin):
    prices, volumes = get_data(coin)

    price = prices[-1]
    r = rsi(prices)
    sup, res = levels(prices)

    cond = [
        price <= sup * 1.01,
        volumes[-1] > max(volumes[-10:]),
        price > prices[-20],
        r < 35
    ]

    if sum(cond) >= 3:
        return {
            "coin": coin.upper(),
            "entry": round(price, 2),
            "target": round(res, 2),
            "stop": round(sup * 0.98, 2),
            "rsi": r,
            "score": sum(cond)
        }

    return None

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_chat_id
    user_chat_id = update.effective_chat.id

    await update.message.reply_text("🔥 PRO SYSTEM RUNNING")

# 🚨 Engine
async def engine(app):
    global user_chat_id, last_market_status, sent_signals

    while True:
        if user_chat_id:

            market = market_filter()

            # 🔁 منع التكرار
            if market == "RISK OFF":
                if last_market_status != "RISK OFF":
                    await app.bot.send_message(chat_id=user_chat_id, text="⚠️ السوق خطر - لا دخول")
                    last_market_status = "RISK OFF"

            else:
                if last_market_status != "RISK ON":
                    await app.bot.send_message(chat_id=user_chat_id, text="🟢 السوق مناسب للدخول")
                    last_market_status = "RISK ON"

                best = None

                for coin in coins:
                    try:
                        result = analyze(coin)

                        if result:
                            if not best or result["score"] > best["score"]:
                                best = result

                    except:
                        pass

                # 💰 إرسال صفقة واحدة فقط
                if best:
                    if best["coin"] not in sent_signals:

                        msg = f"""
💣 صفقة قوية

{best['coin']}

📥 Entry: {best['entry']}$
🎯 Target: {best['target']}$
🛑 Stop: {best['stop']}$

📊 RSI: {best['rsi']}
⭐ Score: {best['score']}/4
"""

                        await app.bot.send_message(chat_id=user_chat_id, text=msg)
                        sent_signals.add(best["coin"])

        await asyncio.sleep(180)

# ⚙️ تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

async def on_startup(app):
    asyncio.create_task(engine(app))

app.post_init = on_startup

app.run_polling()