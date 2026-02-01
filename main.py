import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
import os

from config import Config
from scanner import VulnerabilityScanner
from report_generator import ReportGenerator
from formatter import TelegramFormatter

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

active_scans = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        TelegramFormatter.format_start(),
        parse_mode=ParseMode.HTML
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        TelegramFormatter.format_help(),
        parse_mode=ParseMode.HTML
    )

async def vulnerscan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in active_scans:
        await update.message.reply_text(
            "⏳ You already have an active scan. Please wait for it to complete.",
            parse_mode=ParseMode.HTML
        )
        return

    if len(context.args) == 0:
        await update.message.reply_text(
            "❌ <b>Usage:</b> /vulnerscan &lt;website&gt;\n\n"
            "<b>Example:</b> <code>/vulnerscan example.com</code>",
            parse_mode=ParseMode.HTML
        )
        return

    if len(active_scans) >= Config.MAX_CONCURRENT_SCANS:
        await update.message.reply_text(
            "⏳ Maximum concurrent scans reached. Please try again in a few moments.",
            parse_mode=ParseMode.HTML
        )
        return

    target = context.args[0]

    active_scans[user_id] = True

    status_message = await update.message.reply_text(
        f"🔍 <b>Initiating Security Scan</b>\n\n"
        f"🎯 Target: <code>{target}</code>\n\n"
        f"⏳ This may take 1-3 minutes...\n"
        f"📊 Scanning ports and services\n"
        f"🔒 Analyzing security headers\n"
        f"🛡️ Checking SSL/TLS configuration\n\n"
        f"<i>Please wait...</i>",
        parse_mode=ParseMode.HTML
    )

    try:
        scanner = VulnerabilityScanner()
        report_gen = ReportGenerator(Config.REPORT_DIR)

        scan_results = await asyncio.wait_for(
            asyncio.to_thread(scanner.scan_website, target),
            timeout=Config.SCAN_TIMEOUT
        )

        await status_message.edit_text(
            f"📄 Generating detailed report...",
            parse_mode=ParseMode.HTML
        )

        pdf_path = await asyncio.to_thread(report_gen.generate_pdf, scan_results)

        formatted_message = TelegramFormatter.format_scan_results(scan_results)

        await update.message.reply_document(
            document=open(pdf_path, 'rb'),
            caption=formatted_message,
            parse_mode=ParseMode.HTML,
            filename=f"security_report_{scan_results['host']}.pdf"
        )

        await status_message.delete()

        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    except asyncio.TimeoutError:
        await status_message.edit_text(
            "⏱️ <b>Scan Timeout</b>\n\n"
            "The scan took too long to complete. The target may be unresponsive or blocking scan attempts.\n\n"
            "Please verify the target is accessible and try again.",
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logger.error(f"Scan error: {e}")
        await status_message.edit_text(
            f"❌ <b>Scan Error</b>\n\n"
            f"An error occurred during the scan:\n"
            f"<code>{str(e)}</code>\n\n"
            f"Please verify the target URL and try again.",
            parse_mode=ParseMode.HTML
        )

    finally:
        if user_id in active_scans:
            del active_scans[user_id]

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An unexpected error occurred. Please try again later.",
            parse_mode=ParseMode.HTML
        )

def main():
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}")
        print("Please ensure your .env file is properly configured.\n")
        return

    application = Application.builder().token(Config.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("vulnerscan", vulnerscan_command))

    application.add_error_handler(error_handler)

    logger.info("Bot started successfully!")
    print("\n🤖 Vulnerability Scanner Bot is running...")
    print("Press Ctrl+C to stop\n")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
