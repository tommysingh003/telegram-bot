import os
import logging
import asyncio
import aiohttp
import requests  # FIXED: Added missing import
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# Configuration
DOWNLOAD_WEBSITE = "https://theteradownloader.com"  # Change if needed
TOKEN = os.environ.get("TOKEN")  # Ensure this is set in Render

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

async def download_video(update: Up
