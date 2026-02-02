import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode
import os

from config import Config
from scanner import VulnerabilityScanner
from report_generator import ReportGenerator
from formatter import TelegramFormatter
from database import DatabaseManager
from gemini_ai import GeminiAI
from sangmata import SangmataFeature
from sudo_manager import SudoManager
from logger import TelegramLogger

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

active_scans = {}
db_manager = DatabaseManager()
gemini_ai = GeminiAI()
sangmata = SangmataFeature()
sudo_manager = SudoManager()
telegram_logger = None

async def track_user_update(update: Update):
    user = update.effective_user
    if user:
        sangmata.track_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)

    keyboard = [
        [
            InlineKeyboardButton("📖 Help & Commands", callback_data='help'),
            InlineKeyboardButton("💬 Chat with AI", callback_data='chat_info')
        ],
        [
            InlineKeyboardButton("🔍 Vulnerability Scan", callback_data='scan_info'),
            InlineKeyboardButton("📊 My History", callback_data='history')
        ],
        [
            InlineKeyboardButton("📢 Channel", url="https://t.me/dark_musictm"),
            InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/cyber_github")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        TelegramFormatter.format_start(),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

    if telegram_logger:
        await telegram_logger.log_command(update.effective_user.id, update.effective_user.username, "/start")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    await update.message.reply_text(
        TelegramFormatter.format_help(),
        parse_mode=ParseMode.HTML
    )

    if telegram_logger:
        await telegram_logger.log_command(update.effective_user.id, update.effective_user.username, "/help")

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    user_id = update.effective_user.id

    if len(context.args) == 0:
        message = """<blockquote expandable>💬 <b>GEMINI AI CHAT</b>

🤖 <b>How to use:</b>

Simply type /chat followed by your message!

📝 <b>Examples:</b>
  <code>/chat Hello! How are you?</code>
  <code>/chat Explain SQL injection</code>
  <code>/chat What is XSS?</code>

💡 <b>Tips:</b>
  • I remember our conversation context
  • Ask me anything about tech, security, or general topics
  • Use /clear to reset our conversation

🚀 <b>Try it now!</b></blockquote>"""

        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return

    user_message = ' '.join(context.args)

    status_msg = await update.message.reply_text(
        "🤖 <i>Thinking...</i>",
        parse_mode=ParseMode.HTML
    )

    try:
        response = gemini_ai.get_response(user_id, user_message)

        formatted_response = f"<blockquote expandable>💬 <b>GEMINI AI RESPONSE</b>\n\n{response}</blockquote>"

        await status_msg.edit_text(
            formatted_response,
            parse_mode=ParseMode.HTML
        )

        if telegram_logger:
            await telegram_logger.log_ai_chat(user_id, update.effective_user.username, user_message)

    except Exception as e:
        logger.error(f"Chat error: {e}")
        await status_msg.edit_text(
            f"<blockquote expandable>❌ <b>ERROR</b>\n\nFailed to get AI response. Please try again.</blockquote>",
            parse_mode=ParseMode.HTML
        )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    user_id = update.effective_user.id

    success = gemini_ai.clear_conversation(user_id)

    if success:
        message = "<blockquote expandable>🗑️ <b>CONVERSATION CLEARED</b>\n\n✅ Your chat history with AI has been reset!\n\n💬 Start a new conversation with /chat</blockquote>"
    else:
        message = "<blockquote expandable>❌ <b>ERROR</b>\n\nFailed to clear conversation. Please try again.</blockquote>"

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    user_id = update.effective_user.id

    if context.args and sudo_manager.check_owner_access(update.effective_user.id):
        try:
            target_id = int(context.args[0]) if context.args[0].isdigit() else None
            if target_id:
                user_id = target_id
        except:
            pass

    history_message = sangmata.get_user_info(user_id)
    await update.message.reply_text(history_message, parse_mode=ParseMode.HTML)

async def vulnerscan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    user_id = update.effective_user.id

    if not sudo_manager.check_sudo_access(user_id):
        message = """<blockquote expandable>🚫 <b>ACCESS DENIED</b>

❌ You don't have permission to use this command!

🔐 <b>This command is restricted to sudo users only.</b>

💡 <b>What you can do:</b>
  • Use /chat to talk with AI
  • Use /history to check your user history
  • Contact the bot owner for sudo access

👑 <b>Owner:</b> Only the bot owner can grant sudo access.</blockquote>"""

        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return

    if user_id in active_scans:
        await update.message.reply_text(
            "<blockquote expandable>⏳ <b>SCAN IN PROGRESS</b>\n\n⚠️ You already have an active scan running!\n\n⏱️ Please wait for it to complete before starting a new one.</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if len(context.args) == 0:
        await update.message.reply_text(
            "<blockquote expandable>❌ <b>INVALID USAGE</b>\n\n<b>Correct usage:</b>\n<code>/vulnerscan &lt;website&gt;</code>\n\n<b>Examples:</b>\n<code>/vulnerscan example.com</code>\n<code>/vulnerscan https://example.com</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if len(active_scans) >= Config.MAX_CONCURRENT_SCANS:
        await update.message.reply_text(
            "<blockquote expandable>⏳ <b>SERVER BUSY</b>\n\n⚠️ Maximum concurrent scans reached!\n\n🔄 Please try again in a few moments.</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    target = context.args[0]

    active_scans[user_id] = True

    status_message = await update.message.reply_text(
        f"<blockquote expandable>🔍 <b>VULNERABILITY SCAN INITIATED</b>\n\n"
        f"🎯 <b>Target:</b> <code>{target}</code>\n\n"
        f"⏳ <b>Status:</b> Scanning in progress...\n\n"
        f"📊 <b>Progress:</b>\n"
        f"  ▫️ Resolving DNS...\n"
        f"  ▫️ Scanning ports and services...\n"
        f"  ▫️ Analyzing security headers...\n"
        f"  ▫️ Checking SSL/TLS configuration...\n"
        f"  ▫️ Assessing vulnerabilities...\n\n"
        f"⏱️ <i>This may take 1-3 minutes. Please wait...</i></blockquote>",
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
            "<blockquote expandable>📄 <b>GENERATING REPORT</b>\n\n✨ Creating detailed PDF report...\n\n⏳ Almost done!</blockquote>",
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

        db_manager.log_scan(
            user_id=user_id,
            username=update.effective_user.username or f"User{user_id}",
            target=target,
            risk_score=scan_results['risk_score']
        )

        if telegram_logger:
            await telegram_logger.log_scan(
                user_id,
                update.effective_user.username,
                target,
                scan_results['risk_score'],
                True
            )

        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    except asyncio.TimeoutError:
        await status_message.edit_text(
            "<blockquote expandable>⏱️ <b>SCAN TIMEOUT</b>\n\n"
            "❌ The scan took too long to complete!\n\n"
            "🔍 <b>Possible reasons:</b>\n"
            "  • Target is unresponsive\n"
            "  • Target is blocking scan attempts\n"
            "  • Network connectivity issues\n\n"
            "💡 Please verify the target is accessible and try again.</blockquote>",
            parse_mode=ParseMode.HTML
        )

        if telegram_logger:
            await telegram_logger.log_scan(user_id, update.effective_user.username, target, 0, False)

    except Exception as e:
        logger.error(f"Scan error: {e}")
        await status_message.edit_text(
            f"<blockquote expandable>❌ <b>SCAN ERROR</b>\n\n"
            f"⚠️ An error occurred during the scan:\n\n"
            f"<code>{str(e)}</code>\n\n"
            f"🔄 Please verify the target URL and try again.</blockquote>",
            parse_mode=ParseMode.HTML
        )

        if telegram_logger:
            await telegram_logger.log_error(user_id, update.effective_user.username, str(e))

    finally:
        if user_id in active_scans:
            del active_scans[user_id]

async def addsudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    user_id = update.effective_user.id

    if not sudo_manager.check_owner_access(user_id):
        await update.message.reply_text(
            "<blockquote expandable>🚫 <b>ACCESS DENIED</b>\n\n❌ This command is restricted to the bot owner only!</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if len(context.args) == 0:
        await update.message.reply_text(
            "<blockquote expandable>❌ <b>INVALID USAGE</b>\n\n<b>Correct usage:</b>\n<code>/addsudo &lt;user_id or @username&gt;</code>\n\n<b>Examples:</b>\n<code>/addsudo 123456789</code>\n<code>/addsudo @username</code>\n\nYou can also reply to a user's message with /addsudo</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    target_user_id = None
    target_username = None
    target_first_name = "Unknown"

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
        target_username = target_user.username
        target_first_name = target_user.first_name
    else:
        user_input = context.args[0]
        if user_input.isdigit():
            target_user_id = int(user_input)
            target_username = f"User{target_user_id}"
        elif user_input.startswith('@'):
            target_username = user_input[1:]
        else:
            await update.message.reply_text(
                "<blockquote expandable>❌ <b>INVALID INPUT</b>\n\nPlease provide a valid user ID or username (starting with @)</blockquote>",
                parse_mode=ParseMode.HTML
            )
            return

    if target_user_id:
        success, message = sudo_manager.add_sudo(target_user_id, target_username, target_first_name, user_id)

        response = f"<blockquote expandable>{'✅' if success else '❌'} <b>SUDO MANAGEMENT</b>\n\n{message}</blockquote>"
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)

        if success and telegram_logger:
            await telegram_logger.log_sudo_change(
                user_id,
                update.effective_user.username,
                target_user_id,
                target_username,
                "ADDED TO SUDO"
            )
    else:
        await update.message.reply_text(
            "<blockquote expandable>❌ <b>ERROR</b>\n\nCould not resolve user ID. Please use user ID or reply to a message.</blockquote>",
            parse_mode=ParseMode.HTML
        )

async def delsudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    user_id = update.effective_user.id

    if not sudo_manager.check_owner_access(user_id):
        await update.message.reply_text(
            "<blockquote expandable>🚫 <b>ACCESS DENIED</b>\n\n❌ This command is restricted to the bot owner only!</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if len(context.args) == 0 and not update.message.reply_to_message:
        await update.message.reply_text(
            "<blockquote expandable>❌ <b>INVALID USAGE</b>\n\n<b>Correct usage:</b>\n<code>/delsudo &lt;user_id or @username&gt;</code>\n\n<b>Examples:</b>\n<code>/delsudo 123456789</code>\n<code>/delsudo @username</code>\n\nYou can also reply to a user's message with /delsudo</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    target_user_id = None
    target_username = None

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
        target_username = target_user.username
    else:
        user_input = context.args[0]
        if user_input.isdigit():
            target_user_id = int(user_input)
            target_username = f"User{target_user_id}"

    if target_user_id:
        success, message = sudo_manager.remove_sudo(target_user_id)

        response = f"<blockquote expandable>{'✅' if success else '❌'} <b>SUDO MANAGEMENT</b>\n\n{message}</blockquote>"
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)

        if success and telegram_logger:
            await telegram_logger.log_sudo_change(
                user_id,
                update.effective_user.username,
                target_user_id,
                target_username,
                "REMOVED FROM SUDO"
            )
    else:
        await update.message.reply_text(
            "<blockquote expandable>❌ <b>ERROR</b>\n\nCould not resolve user ID. Please use user ID or reply to a message.</blockquote>",
            parse_mode=ParseMode.HTML
        )

async def sudolist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)

    sudo_list = sudo_manager.get_sudo_list_formatted()
    await update.message.reply_text(sudo_list, parse_mode=ParseMode.HTML)

    if telegram_logger:
        await telegram_logger.log_command(update.effective_user.id, update.effective_user.username, "/sudolist")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        keyboard = [
            [InlineKeyboardButton("← Back", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=TelegramFormatter.format_help(),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

    elif query.data == 'chat_info':
        keyboard = [
            [InlineKeyboardButton("← Back", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = """<blockquote expandable>💬 <b>GEMINI AI CHATBOT</b>

🤖 <b>About:</b>
Powered by Google Gemini AI, I can help you with:
  • General conversations
  • Technical questions
  • Cybersecurity topics
  • Programming help
  • And much more!

🚀 <b>How to use:</b>
<code>/chat Your message here</code>

📝 <b>Examples:</b>
  <code>/chat What is SQL injection?</code>
  <code>/chat Explain XSS attacks</code>
  <code>/chat Hello! How are you?</code>

💡 <b>Features:</b>
  ✅ Context-aware conversations
  ✅ Remember chat history
  ✅ Intelligent responses
  ✅ Multi-topic knowledge

🗑️ <b>Clear history:</b>
Use <code>/clear</code> to reset our conversation

🌟 Start chatting now!</blockquote>"""

        await query.edit_message_text(
            text=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

    elif query.data == 'scan_info':
        keyboard = [
            [InlineKeyboardButton("← Back", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = """<blockquote expandable>🔍 <b>VULNERABILITY SCANNING</b>

🔐 <b>Access Level:</b> Sudo users only

🎯 <b>What gets scanned:</b>
  ✅ Port and service discovery
  ✅ Security header analysis
  ✅ SSL/TLS configuration
  ✅ Cookie security assessment
  ✅ Technology stack detection
  ✅ Vulnerability identification
  ✅ Risk scoring

🚀 <b>How to scan:</b>
<code>/vulnerscan &lt;website&gt;</code>

📝 <b>Examples:</b>
  <code>/vulnerscan example.com</code>
  <code>/vulnerscan https://example.com</code>

⏱️ <b>Scan duration:</b> 1-3 minutes

📄 <b>Output:</b> Detailed PDF report + summary

⚠️ <b>Important:</b>
You can scan any website with this bot!

🔐 <b>Need sudo access?</b>
Contact the bot owner.</blockquote>"""

        await query.edit_message_text(
            text=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

    elif query.data == 'history':
        user_id = query.from_user.id
        history_message = sangmata.get_user_info(user_id)

        keyboard = [
            [InlineKeyboardButton("← Back", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=history_message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

    elif query.data == 'back_to_start':
        keyboard = [
            [
                InlineKeyboardButton("📖 Help & Commands", callback_data='help'),
                InlineKeyboardButton("💬 Chat with AI", callback_data='chat_info')
            ],
            [
                InlineKeyboardButton("🔍 Vulnerability Scan", callback_data='scan_info'),
                InlineKeyboardButton("📊 My History", callback_data='history')
            ],
            [
                InlineKeyboardButton("📢 Channel", url="https://t.me/dark_musictm"),
                InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/cyber_github")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=TelegramFormatter.format_start(),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)

    if update.message and update.message.text and not update.message.text.startswith('/'):
        user_id = update.effective_user.id
        user_message = update.message.text

        status_msg = await update.message.reply_text(
            "🤖 <i>Thinking...</i>",
            parse_mode=ParseMode.HTML
        )

        try:
            response = gemini_ai.get_response(user_id, user_message)

            formatted_response = f"<blockquote expandable>💬 <b>GEMINI AI</b>\n\n{response}</blockquote>"

            await status_msg.edit_text(
                formatted_response,
                parse_mode=ParseMode.HTML
            )

            if telegram_logger:
                await telegram_logger.log_ai_chat(user_id, update.effective_user.username, user_message)

        except Exception as e:
            logger.error(f"Message handler error: {e}")
            await status_msg.edit_text(
                "<blockquote expandable>❌ <b>ERROR</b>\n\nFailed to process message. Use /chat &lt;message&gt; instead.</blockquote>",
                parse_mode=ParseMode.HTML
            )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "<blockquote expandable>❌ <b>UNEXPECTED ERROR</b>\n\n⚠️ An error occurred while processing your request.\n\n🔄 Please try again later.</blockquote>",
            parse_mode=ParseMode.HTML
        )

def main():
    global telegram_logger

    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}")
        print("Please ensure your .env file is properly configured.\n")
        return

    sudo_manager.initialize_owner()

    application = Application.builder().token(Config.BOT_TOKEN).build()

    telegram_logger = TelegramLogger(application.bot)

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("chat", chat_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("vulnerscan", vulnerscan_command))
    application.add_handler(CommandHandler("addsudo", addsudo_command))
    application.add_handler(CommandHandler("delsudo", delsudo_command))
    application.add_handler(CommandHandler("sudolist", sudolist_command))

    application.add_handler(CallbackQueryHandler(button_callback))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.add_error_handler(error_handler)

    logger.info("🤖 Advanced AI Bot started successfully!")
    print("\n" + "="*50)
    print("🤖 ADVANCED AI BOT IS RUNNING")
    print("="*50)
    print("✅ Gemini AI: Active")
    print("✅ Vulnerability Scanner: Active")
    print("✅ Sangmata Feature: Active")
    print("✅ Sudo System: Active")
    print("✅ Logging: Active")
    print("="*50)
    print("Press Ctrl+C to stop\n")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
