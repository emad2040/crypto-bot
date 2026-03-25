import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8707402017:AAFli5Hl3mmsxVGOHd812AwGCSOqdcHd6rA"
CHAT_ID = "PUT_YOUR_CHAT_ID"

# رسالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 CryptoMindX شغال 24/7")

# تحليل السوق
def analyze_market():
    url = "https://api.coingecko.com/api/v3/global"
    data = requests.get(url).json()

    btc_dom = data['data']['market_cap_percentage']['btc']

    if btc_dom > 52:
        return "⚠️ السوق خطر - سيطرة BTC عالية"
    elif btc_dom < 48:
        return "🚀 فرصة Altcoins قوية"
    return None

# إرسال إشارات
async def send_signal(context: ContextTypes.DEFAULT_TYPE):
    signal = analyze_market()

    if signal:
        await context.bot.send_message(chat_id=CHAT_ID, text=signal)

# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

# كل 5 دقايق
app.job_queue.run_repeating(send_signal, interval=300, first=10)

app.run_polling()