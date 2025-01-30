import os
import logging
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# ... (Configuration and logging remain mostly the same)

async def download_video(update: Update, context):
    # ... (URL validation remains the same)

    try:
        await update.message.reply_text("⏳ Processing your request...")

        download_link = await asyncio.to_thread(get_download_link, url) # Run in a separate thread

        if not download_link:
            await update.message.reply_text("❌ Could not find download link. Please try another URL.")
            return

        await update.message.reply_text("⬇️ Downloading and uploading video...")

        async with aiohttp.ClientSession() as session:
            async with session.get(download_link, stream=True) as response:
                if response.status == 200:
                    await context.bot.send_video(
                        chat_id=update.message.chat_id,
                        video=response.content,  # Stream directly
                        supports_streaming=True
                    )
                else:
                    await update.message.reply_text(f"❌ Failed to download video: {response.status}")

    except aiohttp.ClientError as e:
        logger.error(f"Download error: {e}")
        await update.message.reply_text("❌ An error occurred during download. Please try again later.")
    except Exception as e:  # Keep a general exception for unexpected errors
        logger.exception(f"An unexpected error occurred: {e}") # Log the full stack trace
        await update.message.reply_text("❌ An unexpected error occurred. Please try again later.")

# ... (get_download_link function - maintain and improve scraping logic)

# ... (Flask app remains, but the / route can be simplified)
@app.route('/')
def home():
    return "Bot is running"

# ... (Main execution remains mostly the same)
