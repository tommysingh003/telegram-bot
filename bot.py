import os
import logging
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# Configuration
DOWNLOAD_WEBSITE = "https://theteradownloader.com"  # Or your preferred site
TOKEN = os.environ.get("TOKEN")  # Set this in Render environment variables

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== Telegram Bot Functions ==========
async def start(update: Update, context):
    await update.message.reply_text(
        "🚀 Welcome to Video Downloader Bot!\n"
        "Send me a video link (YouTube, Instagram, etc.) and I'll download it for you!"
    )

async def download_video(update: Update, context):
    url = update.message.text
    chat_id = update.message.chat_id

    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("❌ Please send a valid URL starting with http:// or https://")
        return

    try:
        await update.message.reply_text("⏳ Processing your request...")

        download_link = await asyncio.to_thread(get_download_link, url)

        if not download_link:
            await update.message.reply_text("❌ Could not find download link. Please try another URL.")
            return

        await update.message.reply_text("⬇️ Downloading and uploading video...")

        async with aiohttp.ClientSession() as session:
            async with session.get(download_link, stream=True) as response:
                if response.status == 200:
                    try:  # Inner try-except for send_video errors
                        await context.bot.send_video(
                            chat_id=chat_id,
                            video=response.content,
                            supports_streaming=True,
                            # Add a timeout to send_video to prevent indefinite hanging
                            timeout=600 # 10 minutes timeout
                        )
                    except Exception as e:
                        logger.exception(f"Error sending video: {e}")
                        await update.message.reply_text("❌ Error uploading video. Please try again later.")
                else:
                    await update.message.reply_text(f"❌ Failed to download video: {response.status}")

    except aiohttp.ClientError as e:
        logger.error(f"Download error: {e}")
        await update.message.reply_text("❌ An error occurred during download. Please try again later.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        await update.message.reply_text("❌ An unexpected error occurred. Please try again later.")


def get_download_link(video_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        payload = {"url": video_url}
        response = requests.post(DOWNLOAD_WEBSITE, data=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(response.text, "html.parser")
        download_button = soup.find("a", {"class": "download-btn"})  # Improve this selector!

        if download_button and "href" in download_button.attrs:
            return download_button["href"]

        return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None
    except Exception as e:
        logger.exception(f"Scraping error: {e}")
        return None


# ========== Flask Server (for Render compatibility) ==========
app = Flask(__name__)  # Flask app initialization (moved here)

@app.route('/')
def home():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 5000))  # Use a more common port
    app.run(host='0.0.0.0', port=port)

# ========== Main Execution ==========
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("Missing Telegram token! Set the 'TOKEN' environment variable.")

    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    logger.info("Bot is running...")
    application.run_polling() # or application.run_webhook()
