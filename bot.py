import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# Configuration
DOWNLOAD_WEBSITE = "https://theteradownloader.com"
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
    """Handle /start command"""
    await update.message.reply_text(
        "🚀 Welcome to Video Downloader Bot!\n"
        "Send me a video link (YouTube, Instagram, etc.) and I'll download it for you!"
    )

async def download_video(update: Update, context):
    """Handle video download requests"""
    url = update.message.text
    chat_id = update.message.chat_id
    
    # Validate URL format
    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("❌ Please send a valid URL starting with http:// or https://")
        return

    try:
        # Show processing message
        await update.message.reply_text("⏳ Processing your request...")
        
        # Get download link from website
        download_link = get_download_link(url)
        
        if not download_link:
            await update.message.reply_text("❌ Could not find download link. Please try another URL.")
            return

        # Download the video
        await update.message.reply_text("⬇️ Downloading video...")
        video_response = requests.get(download_link, stream=True)
        
        if video_response.status_code == 200:
            # Save video temporarily
            with open("video.mp4", "wb") as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Send video to user
            await update.message.reply_text("📤 Uploading video...")
            with open("video.mp4", "rb") as f:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=f,
                    supports_streaming=True
                )
            
            # Clean up
            os.remove("video.mp4")
        else:
            await update.message.reply_text("❌ Failed to download video from the website.")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ An error occurred. Please try again later.")

def get_download_link(video_url):
    """Scrape download link from theteradownload
