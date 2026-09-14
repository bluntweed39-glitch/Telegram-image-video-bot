import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from moviepy import ImageClip

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        image_path = f"temp_{photo.file_id}.jpg"
        video_path = f"temp_{photo.file_id}.mp4"

        await file.download_to_drive(image_path)

        # Create 10-second video with slow zoom
        clip = ImageClip(image_path).with_duration(10)

        def zoom(t):
            return 1 + 0.12 * (t / 10)

        clip = clip.resized(zoom)
        clip = clip.with_position("center")

        final = clip.resized(height=1280)
        final.write_videofile(
            video_path,
            fps=24,
            codec="libx264",
            audio=False,
            preset="ultrafast",
            threads=2,
            logger=None
        )

        await update.message.reply_video(
            video=open(video_path, "rb"),
            supports_streaming=True,
            caption="Here's your 10-second video"
        )

        os.remove(image_path)
        os.remove(video_path)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Sorry, something went wrong. Please try again.")

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
