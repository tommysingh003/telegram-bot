# Constants
DOWNLOAD_WEBSITE = "https://theteradownloader.com"  # Replace with your websiteimport os
from telegram.ext import ApplicationBuilder
import os

TOKEN = os.environ.get("7828188600:AAEoqP_VhVpFKInLEAnPS3F_t-o4peM9hV4")  # Token set in Render/Heroku
application = ApplicationBuilder().token(TOKEN).build()
from bs4 import BeautifulSoup
import requests

def get_download_link(video_url):
    try:
        # Send the video URL to the website
        payload = {"url": video_url}  # Adjust based on the website's form field
        response = requests.post(DOWNLOAD_WEBSITE, data=payload)
        
        # Parse the HTML response
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract the download link (customize this selector)
        download_link = soup.find("a", class_="download-btn")["href"]
        return download_link
    except Exception as e:
        print(f"Error: {e}")
        return None
        from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    # Start Flask server in a thread
    import threading
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": port}).start()
    
    # Start the Telegram bot
    application.run_polling()
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
from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    # Start Flask server in a thread
    import threading
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": port}).start()
    
    # Start the Telegram bot
    application.run_polling()
