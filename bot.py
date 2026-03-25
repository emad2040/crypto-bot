import os
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8707402017:AAFli5Hl3mmsxVGOHd812AwGCSOqdcHd6rA"

# رسالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 CryptoMindX جاهز")

# تحليل بسيط
def analyze_market():
    url = "https://api.coingecko.com/api/v3/global"
    data = requests.get(url).json()

    btc_dom = data['data']['market_cap_percentage']['btc']

    if btc_dom > 52:
        return "⚠️ السوق خطر - سيطرة BTC عالية"
    elif btc_dom < 48:
        return "🚀 فرصة Altcoins قوية"
    else:
        return None

# إرسال إشارات تلقائي
async def auto_signals(app):
    while True:
        signal = analyze_market()

        if signal:
            await app.bot.send_message(
                chat_id="PUT_YOUR_CHAT_ID",
                text=signal
            )

        await asyncio.sleep(300)  # كل 5 دقايق

# تشغيل البوت
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # تشغيل الإشارات
    asyncio.create_task(auto_signals(app))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
