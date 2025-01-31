from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
import subprocess

# Install ChromeDriver on Render
subprocess.run(["apt-get", "update"])
subprocess.run(["apt-get", "install", "-y", "chromium-chromedriver"])
os.environ["CHROMEDRIVER_PATH"] = "/usr/bin/chromedriver"

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Telegram Bot Token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize the bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Send me a video link to download.")

def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    update.message.reply_text(f"Processing your link: {user_message}")

    # Set up Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Visit the website
        driver.get("https://theteradownloader.com/")

        # Find the input field and enter the link
        input_field = driver.find_element(By.NAME, "url")
        input_field.send_keys(user_message)

        # Find and click the submit button
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Download')]")
        submit_button.click()

        # Wait for the download link to appear
        time.sleep(10)  # Adjust based on website response time

        # Find the download link
        download_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Download")
        video_url = download_link.get_attribute("href")

        # Send the download link to the user
        update.message.reply_text(f"Here's your download link: {video_url}")

    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")
    finally:
        driver.quit()

def main() -> None:
    # Set up the Telegram bot
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
