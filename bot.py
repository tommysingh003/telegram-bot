import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token (set via environment variable)
TOKEN = os.environ.get('TOKEN')

# /start command handler
async def start(update: Update, context):
    await update.message.reply_text("Hi! Send me a video link, and I'll download it for you.")

# Video link handler
async def download_video(update: Update, context):
    url = update.message.text
    await update.message.reply_text(f"Received link: {url}. Processing...")

# Main function
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.run_polling()

if __name__ == "__main__":
    main()
    # Add Flask to keep the app alive (required for Render)
    from flask import Flask
    app = Flask(__name__)
    @app.route('/')
    def home():
        return "Bot is running!"
    if __name__ == "__main__":
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# Set webhook URL (replace with your Render URL)
await application.bot.set_webhook(url="https://your-bot.onrender.com/webhook")
