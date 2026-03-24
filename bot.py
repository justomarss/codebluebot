import logging
import os
import re
import aiohttp
import aiofiles
from urllib.parse import urlparse, unquote
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MAX_FILE_SIZE = 50 * 1024 * 1024
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
 await update.message.reply_text(
 "Fayl Yukleyici Bot\n\n"
 "Istediyin linkden fayl yukle:\n"
 "- PDF, Word, Excel\n"
 "- Video, Audio\n"
 "- Sekil (JPG, PNG)\n"
 "- ZIP, RAR\n"
 "- Ve diger her sey\n\n"
 "Nece istifade et:\n"
 "Sadece linki gonder - bot yukleyib sene gonderecek.\n\n"
 "Maksimum: 50MB"
 )
def get_filename_from_url(url, content_type="", content_disposition=""):
 if content_disposition:
 match = re.search(r"filename\*=UTF-8''(.+?)(?:;|$)", content_disposition)
 if match:
 return unquote(match.group(1))
 match = re.search(r'filename=["\']?([^"\';\n]+)["\']?', content_disposition)
 if match:
 return match.group(1).strip()
 parsed = urlparse(url)
 path = unquote(parsed.path)
 filename = os.path.basename(path)
 if filename and "." in filename:
 return filename
 extensions = {
 "application/pdf": ".pdf",
 "application/zip": ".zip",
 "application/x-rar-compressed": ".rar",
 "video/mp4": ".mp4",
 "video/mpeg": ".mpeg",
 "audio/mpeg": ".mp3",
 "audio/wav": ".wav",
 "image/jpeg": ".jpg",
 "image/png": ".png",
 "image/gif": ".gif",
 "application/msword": ".doc",
 "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
 "application/vnd.ms-excel": ".xls",
 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
 "text/plain": ".txt",
 }
 ext = extensions.get(content_type.split(";")[0].strip(), "")
 return "file" + ext if ext else "downloaded_file"
async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
 url = update.message.text.strip()
 if not url.startswith(("http://", "https://")):
 await update.message.reply_text("h" \
"Xeta: Zehmet olmasa, duzgun bir URL gonderin.")
 status_msg = await update.message.reply_text("Yuklenir... gozleyin")
 try:
 headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrom }
 async with aiohttp.ClientSession() as session:
 async with session.get(url, headers=headers, allow_redirects=True, timeout=aiohtt if response.status != 200:
 await status_msg.edit_text("Xeta: Server " + str(response.status) + " cav return
 content_length = response.headers.get("Content-Length")
 content_type = response.headers.get("Content-Type", "")
 content_disposition = response.headers.get("Content-Disposition", "")
 if content_length and int(content_length) > MAX_FILE_SIZE:
 size_mb = int(content_length) / (1024 * 1024)
 await status_msg.edit_text("Xeta: Fayl cox boyukdur: " + str(round(size_m return
 filename = get_filename_from_url(url, content_type, content_disposition)
 filepath = "/tmp/" + filename
 await status_msg.edit_text("Yuklenir: " + filename)
 total_size = 0
 async with aiofiles.open(filepath, "wb") as f:
 async for chunk in response.content.iter_chunked(8192):
 await f.write(chunk)
 total_size += len(chunk)
 if total_size > MAX_FILE_SIZE:
 os.remove(filepath)
 await status_msg.edit_text("Xeta: Fayl 50MB limitini asdi.")
 return
 size_mb = round(total_size / (1024 * 1024), 1)
 await status_msg.edit_text("Gonderilir... " + str(size_mb) + "MB")
 with open(filepath, "rb") as f:
 if content_type.startswith("image/"):
 await update.message.reply_photo(photo=f, caption=filename + " - " +  elif content_type.startswith("video/"):
 await update.message.reply_video(video=f, caption=filename + " - " +  elif content_type.startswith("audio/"):
 await update.message.reply_audio(audio=f, caption=filename + " - " +  else:
 await update.message.reply_document(document=f, filename=filename, ca os.remove(filepath)
 await status_msg.delete()
 except aiohttp.ClientConnectorError:
 await status_msg.edit_text("Xeta: Servere qosulmaq mumkun olmadi.")
 except aiohttp.ClientResponseError as e:
 await status_msg.edit_text("Xeta: Server " + str(e.status))
 except Exception as e:
 logger.error("Xeta: " + str(e))
 await status_msg.edit_text("Xeta: " + str(e)[:100])
def main():
 token = os.environ.get("BOT_TOKEN")
 if not token:
 print("BOT_TOKEN tapilmadi!")
 return
 app = Application.builder().token(token).build()
 app.add_handler(CommandHandler("start", start))
 app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_file))
 print("Downloader Bot ise dusdu!")
 app.run_polling()
if __name__ == "__main__":
 main()