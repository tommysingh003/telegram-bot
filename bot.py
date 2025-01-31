from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re, requests, math, random

# Terabox classes
headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'}

class TeraboxFile:
    def __init__(self) -> None:
        self.r = requests.Session()
        self.headers = headers
        self.result = {'status': 'failed', 'js_token': '', 'browser_id': '', 'cookie': '', 'sign': '', 'timestamp': '', 'shareid': '', 'uk': '', 'list': []}

    def search(self, url: str) -> None:
        req = self.r.get(url, allow_redirects=True)
        self.short_url = re.search(r'surl=([^ &]+)', str(req.url)).group(1)
        self.getAuthorization()
        self.getMainFile()

    def getAuthorization(self) -> None:
        url = f'https://www.terabox.app/wap/share/filelist?surl={self.short_url}'
        req = self.r.get(url, headers=self.headers, allow_redirects=True)
        js_token = re.search(r'%28%22(.*?)%22%29', str(req.text.replace('\\', ''))).group(1)
        browser_id = req.cookies.get_dict().get('browserid')
        cookie = 'lang=id;' + ';'.join(['{}={}'.format(a, b) for a, b in self.r.cookies.get_dict().items()])
        self.result['js_token'] = js_token
        self.result['browser_id'] = browser_id
        self.result['cookie'] = cookie

    def getMainFile(self) -> None:
        url = f'https://www.terabox.com/api/shorturlinfo?app_id=250528&shorturl=1{self.short_url}&root=1'
        req = self.r.get(url, headers=self.headers, cookies={'cookie': ''}).json()
        all_file = self.packData(req, self.short_url)
        if len(all_file):
            self.result['sign'] = req['sign']
            self.result['timestamp'] = req['timestamp']
            self.result['shareid'] = req['shareid']
            self.result['uk'] = req['uk']
            self.result['list'] = all_file
            self.result['status'] = 'success'

    def getChildFile(self, short_url, path: str = '', root: str = '0') -> list[dict[str, any]]:
        params = {'app_id': '250528', 'shorturl': short_url, 'root': root, 'dir': path}
        url = 'https://www.terabox.com/share/list?' + '&'.join([f'{a}={b}' for a, b in params.items()])
        req = self.r.get(url, headers=self.headers, cookies={'cookie': ''}).json()
        return self.packData(req, short_url)

    def packData(self, req: dict, short_url: str) -> list[dict[str, any]]:
        all_file = [{
            'is_dir': item['isdir'],
            'path': item['path'],
            'fs_id': item['fs_id'],
            'name': item['server_filename'],
            'type': self.checkFileType(item['server_filename']) if not bool(int(item.get('isdir'))) else 'other',
            'size': item.get('size') if not bool(int(item.get('isdir'))) else '',
            'image': item.get('thumbs', {}).get('url3', '') if not bool(int(item.get('isdir'))) else '',
            'list': self.getChildFile(short_url, item['path'], '0') if item.get('isdir') else [],
        } for item in req.get('list', [])]
        return all_file

    def checkFileType(self, name: str) -> str:
        name = name.lower()
        if any(ext in name for ext in ['.mp4', '.mov', '.m4v', '.mkv', '.asf', '.avi', '.wmv', '.m2ts', '.3g2']):
            typefile = 'video'
        elif any(ext in name for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
            typefile = 'image'
        elif any(ext in name for ext in ['.pdf', '.docx', '.zip', '.rar', '.7z']):
            typefile = 'file'
        else:
            typefile = 'other'
        return typefile

class TeraboxLink:
    def __init__(self, fs_id: str, uk: str, shareid: str, timestamp: str, sign: str, js_token: str, cookie: str) -> None:
        self.r = requests.Session()
        self.headers = headers
        self.result = {'status': 'failed', 'download_link': {}}
        self.cookie = cookie
        self.dynamic_params = {
            'uk': str(uk),
            'sign': str(sign),
            'shareid': str(shareid),
            'primaryid': str(shareid),
            'timestamp': str(timestamp),
            'jsToken': str(js_token),
            'fid_list': str(f'[{fs_id}]')
        }
        self.static_param = {
            'app_id': '250528',
            'channel': 'dubox',
            'product': 'share',
            'clienttype': '0',
            'dp-logid': '',
            'nozip': '0',
            'web': '1'
        }

    def generate(self) -> None:
        params = {**self.dynamic_params, **self.static_param}
        url = 'https://www.terabox.com/share/download?' + '&'.join([f'{a}={b}' for a, b in params.items()])
        req = self.r.get(url, cookies={'cookie': self.cookie}).json()
        if not req['errno']:
            slow_url = req['dlink']
            self.result['download_link'].update({'url_1': slow_url})
            self.result['status'] = 'success'
            self.generateFastURL()
        self.r.close()

    def generateFastURL(self) -> None:
        r = requests.Session()
        try:
            old_url = r.head(self.result['download_link']['url_1'], allow_redirects=True).url
            old_domain = re.search(r'://(.*?)\.', str(old_url)).group(1)
            medium_url = old_url.replace('by=themis', 'by=dapunta')
            fast_url = old_url.replace(old_domain, 'd3').replace('by=themis', 'by=dapunta')
            self.result['download_link'].update({'url_2': medium_url, 'url_3': fast_url})
        except:
            pass
        r.close()

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Terabox Downloader Bot! 🚀\n\n"
        "Send me a Terabox file link, and I'll fetch the download links for you."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "terabox.com" not in url and "terabox.app" not in url:
        await update.message.reply_text("Please send a valid Terabox link.")
        return

    await update.message.reply_text("Processing your link... ⏳")

    try:
        tf = TeraboxFile()
        tf.search(url)

        if tf.result['status'] == 'success':
            file_info = f"📂 *File Name:* {tf.result['list'][0]['name']}\n"
            file_info += f"📦 *File Size:* {tf.result['list'][0]['size']}\n"
            file_info += f"📄 *File Type:* {tf.result['list'][0]['type']}\n"

            tl = TeraboxLink(
                fs_id=tf.result['list'][0]['fs_id'],
                uk=tf.result['uk'],
                shareid=tf.result['shareid'],
                timestamp=tf.result['timestamp'],
                sign=tf.result['sign'],
                js_token=tf.result['js_token'],
                cookie=tf.result['cookie']
            )
            tl.generate()

            await update.message.reply_text(file_info, parse_mode="Markdown")
            await update.message.reply_text("🔗 *Download Links:*", parse_mode="Markdown")
            for key, value in tl.result['download_link'].items():
                await update.message.reply_text(f"{key}: {value}")

        else:
            await update.message.reply_text("Failed to fetch file information. Please check the link and try again.")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

# Main function to run the bot
def main():
    application = Application.builder().token("YOUR_BOT_TOKEN").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
