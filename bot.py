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
MAX_FILE_SIZE = 50 * 1024 * 1024 # 50MB (Telegram limiti)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
 await update.message.reply_text(
 " *Fayl Yükləyici Bot*\n\n"
 "İstənilən linkdən fayl yüklə:\n"
 "• PDF, Word, Excel\n"
 "• Video, Audio\n"
 "• Şəkil\n"
 "• ZIP, RAR\n"
 "• Və daha çox...\n\n"
 " *Necə istifadə et:*\n"
 "Sadəcə linki buraya göndər — bot avtomatik yükləyib sənə göndərəcək.\n\n"
 " Maksimum fayl ölçüsü: 50MB",
 parse_mode="Markdown"
 )
def get_filename_from_url(url, content_type="", content_disposition=""):
 # Content-Disposition başlığından fayl adı al
 if content_disposition:
 match = re.search(r'filename\*=UTF-8\'\'(.+?)(?:;|$)', content_disposition)
 if match:
 return unquote(match.group(1))
 match = re.search(r'filename=["\']?([^"\';\n]+)["\']?', content_disposition)
 if match:
 return match.group(1).strip()

 # URL-dən fayl adı al
 parsed = urlparse(url)
 path = unquote(parsed.path)
 filename = os.path.basename(path)

 if filename and '.' in filename:
 return filename

 # Content-Type-dan uzantı müəyyən et
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
 return f"file{ext}" if ext else "downloaded_file"
async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
 url = update.message.text.strip()

 # URL yoxlaması
 if not url.startswith(("http://", "https://")):
 await update.message.reply_text(" Düzgün link deyil. http:// və ya https:// ilə baş return

 status_msg = await update.message.reply_text(" Yüklənir... gözləyin")

 try:
 headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrom }

 async with aiohttp.ClientSession() as session:
 async with session.get(url, headers=headers, allow_redirects=True, timeout=aiohtt
 if response.status != 200:
 await status_msg.edit_text(f" Xəta: Server {response.status} cavabı ver return

 content_length = response.headers.get("Content-Length")
 content_type = response.headers.get("Content-Type", "")
 content_disposition = response.headers.get("Content-Disposition", "")

 # Fayl ölçüsü yoxlaması
 if content_length and int(content_length) > MAX_FILE_SIZE:
 size_mb = int(content_length) / (1024 * 1024)
 await status_msg.edit_text(
 f" Fayl çox böyükdür: {size_mb:.1f}MB\n"
 f"Maksimum icazə verilən: 50MB"
 )
 return

 filename = get_filename_from_url(url, content_type, content_disposition)
 filepath = f"/tmp/{filename}"

 await status_msg.edit_text(f" *{filename}* yüklənir...", parse_mode="Markdo
 # Faylı yüklə
 total_size = 0
 async with aiofiles.open(filepath, 'wb') as f:
 async for chunk in response.content.iter_chunked(8192):
 await f.write(chunk)
 total_size += len(chunk)
 if total_size > MAX_FILE_SIZE:
 await f.close()
 os.remove(filepath)
 await status_msg.edit_text(" Fayl 50MB limitini aşdı.")
 return

 size_mb = total_size / (1024 * 1024)
 await status_msg.edit_text(f" Göndərilir... ({size_mb:.1f}MB)")

 # Fayl tipinə görə göndər
 with open(filepath, 'rb') as f:
 if content_type.startswith("image/"):
 await update.message.reply_photo(
 photo=f,
 caption=f" {filename}\n {size_mb:.1f}MB"
 )
 elif content_type.startswith("video/"):
 await update.message.reply_video(
 video=f,
 caption=f" {filename}\n {size_mb:.1f}MB"
 )
 elif content_type.startswith("audio/"):
 await update.message.reply_audio(
 audio=f,
 caption=f" {filename}\n {size_mb:.1f}MB"
 )
 else:
 await update.message.reply_document(
 document=f,
 filename=filename,
 caption=f" {filename}\n {size_mb:.1f}MB"
 )

 os.remove(filepath)
 await status_msg.delete()

 except aiohttp.ClientConnectorError:
 await status_msg.edit_text(" Serverə qoşulmaq mümkün olmadı. Link düzgündür?")
 except aiohttp.ClientResponseError as e:
 await status_msg.edit_text(f" Server xətası: {e.status}")
 except Exception as e:
 logger.error(f"Xəta: {e}")
 await status_msg.edit_text(f" Xəta baş verdi: {str(e)[:100]}")
def main():
 token = os.environ.get("BOT_TOKEN")
 if not token:
 print("BOT_TOKEN tapılmadı!")
 return

 app = Application.builder().token(token).build()

 app.add_handler(CommandHandler("start", start))
 app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_file))

 print("Downloader Bot işə düşdü!")
 app.run_polling()
if __name__ == "__main__":
 main()
