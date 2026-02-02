import asyncio
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ChatMemberHandler
from telegram.constants import ParseMode
import os

from config import Config
from scanner import VulnerabilityScanner
from report_generator import ReportGenerator
from formatter import TelegramFormatter
from mongodb_database import MongoDatabase
from gemini_ai import GeminiAI
from sangmata import SangmataFeature
from sudo_manager import SudoManager
from logger import TelegramLogger
from group_manager import GroupManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

active_scans = {}
db_manager = MongoDatabase()
gemini_ai = GeminiAI()
sangmata = SangmataFeature()
sudo_manager = SudoManager()
group_manager = GroupManager()
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

def should_trigger_ai(text: str) -> bool:
    """Check if message should trigger AI response"""
    if not text:
        return False

    text_lower = text.lower().strip()

    for trigger in Config.CHAT_TRIGGERS:
        if trigger in text_lower:
            return True

    return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        keyboard = [
            [
                InlineKeyboardButton("Help & Commands", callback_data='help'),
                InlineKeyboardButton("Chat with AI", callback_data='chat_info')
            ],
            [
                InlineKeyboardButton("Vulnerability Scan", callback_data='scan_info'),
                InlineKeyboardButton("My History", callback_data='history')
            ],
            [
                InlineKeyboardButton("Channel", url="https://t.me/dark_musictm"),
                InlineKeyboardButton("Developer", url="https://t.me/cyber_github")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            TelegramFormatter.format_start(),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Hello! I'm an advanced AI and group management bot. Use /help to see available commands.",
            parse_mode=ParseMode.HTML
        )

        db_manager.register_group(update.effective_chat.id, update.effective_chat.title)

    if telegram_logger:
        await telegram_logger.log_command(update.effective_user.id, update.effective_user.username, "/start")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text(
            TelegramFormatter.format_help(),
            parse_mode=ParseMode.HTML
        )
    else:
        help_text = """<b>Bot Commands</b>

<b>AI & Chat:</b>
Just say hi, hello, or chat naturally - I'll respond!
/clear - Clear AI chat history

<b>Admin Commands:</b>
/ban - Ban user (reply or use ID)
/kick - Kick user (reply or use ID)
/mute - Mute user (reply or use ID)
/unmute - Unmute user (reply or use ID)
/unban - Unban user (use ID)
/warn - Warn user (reply or use ID)
/warnings - Check user warnings (reply)
/resetwarns - Reset user warnings (reply)
/pin - Pin replied message
/unpin - Unpin replied message

<b>Group Settings:</b>
/setrules - Set group rules
/rules - View group rules
/setwelcome - Set welcome message
/welcome - Toggle welcome on/off

<b>Notes & Filters:</b>
/save - Save a note
/get - Get a note
/notes - List all notes
/clear - Delete a note
/filter - Add filter (trigger word)
/filters - List all filters
/stop - Remove filter

<b>Info:</b>
/history - View user history
/adminlist - List group admins
/info - Group information

<b>Security:</b>
/vulnerscan - Scan website (sudo only)"""

        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

    if telegram_logger:
        await telegram_logger.log_command(update.effective_user.id, update.effective_user.username, "/help")

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    user_id = update.effective_user.id

    if len(context.args) == 0:
        message = """<b>Gemini AI Chat</b>

Just chat naturally! No commands needed.
Say hi, hello, or anything and I'll respond.

Or use: /chat Your message here

Use /clear to reset conversation."""

        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return

    user_message = ' '.join(context.args)

    status_msg = await update.message.reply_text("Thinking...")

    try:
        response = gemini_ai.get_response(user_id, user_message)
        await status_msg.edit_text(response, parse_mode=ParseMode.HTML)

        if telegram_logger:
            await telegram_logger.log_ai_chat(user_id, update.effective_user.username, user_message)

    except Exception as e:
        logger.error(f"Chat error: {e}")
        await status_msg.edit_text("Failed to get AI response. Please try again.")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    user_id = update.effective_user.id

    success = gemini_ai.clear_conversation(user_id)

    if success:
        await update.message.reply_text("Your chat history has been cleared!")
    else:
        await update.message.reply_text("Failed to clear chat history.")

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
        await update.message.reply_text(
            "This command requires sudo access. Contact the bot owner.",
            parse_mode=ParseMode.HTML
        )
        return

    if user_id in active_scans:
        await update.message.reply_text("You already have an active scan running!")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Usage: /vulnerscan <website>")
        return

    if len(active_scans) >= Config.MAX_CONCURRENT_SCANS:
        await update.message.reply_text("Server busy. Try again later.")
        return

    target = context.args[0]
    active_scans[user_id] = True

    status_message = await update.message.reply_text(
        f"<b>⚕️ Scanning the web :</b> {target}\n\nThis may take 1-3 minutes let me generate scanned reports,since i am not that featurepacked so i can give you minimal vulnerabilities...",
        parse_mode=ParseMode.HTML
    )

    try:
        scanner = VulnerabilityScanner()
        report_gen = ReportGenerator(Config.REPORT_DIR)

        scan_results = await asyncio.wait_for(
            asyncio.to_thread(scanner.scan_website, target),
            timeout=Config.SCAN_TIMEOUT
        )

        await status_message.edit_text("Generating PDF report...")

        pdf_path = await asyncio.to_thread(report_gen.generate_pdf, scan_results)

        formatted_message = TelegramFormatter.format_scan_results(scan_results)

        await update.message.reply_document(
            document=open(pdf_path, 'rb'),
            caption="📄 Full vulnerability report (see document)",
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
        await status_message.edit_text("Scan timeout. Target may be unresponsive.")
    except Exception as e:
        logger.error(f"Scan error: {e}")
        await status_message.edit_text(f"Scan error: {str(e)}")
    finally:
        if user_id in active_scans:
            del active_scans[user_id]

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user from the group"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    user_id = None
    reason = "No reason provided"

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        reason = ' '.join(context.args) if context.args else reason
    elif context.args:
        try:
            user_id = int(context.args[0])
            reason = ' '.join(context.args[1:]) if len(context.args) > 1 else reason
        except:
            await update.message.reply_text("Usage: /ban <user_id> [reason] or reply to a user's message")
            return

    if not user_id:
        await update.message.reply_text("Reply to a user or provide user ID")
        return

    success, message = await group_manager.ban_user(update, context, user_id, reason)
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kick a user from the group"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    user_id = None
    reason = "No reason provided"

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        reason = ' '.join(context.args) if context.args else reason
    elif context.args:
        try:
            user_id = int(context.args[0])
            reason = ' '.join(context.args[1:]) if len(context.args) > 1 else reason
        except:
            await update.message.reply_text("Usage: /kick <user_id> [reason] or reply to a user's message")
            return

    if not user_id:
        await update.message.reply_text("Reply to a user or provide user ID")
        return

    success, message = await group_manager.kick_user(update, context, user_id, reason)
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mute a user"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    user_id = None
    duration = 0

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        if context.args:
            try:
                duration = int(context.args[0])
            except:
                pass
    elif context.args:
        try:
            user_id = int(context.args[0])
            if len(context.args) > 1:
                duration = int(context.args[1])
        except:
            await update.message.reply_text("Usage: /mute <user_id> [minutes] or reply to a user's message")
            return

    if not user_id:
        await update.message.reply_text("Reply to a user or provide user ID")
        return

    success, message = await group_manager.mute_user(update, context, user_id, duration)
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unmute a user"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    user_id = None

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            user_id = int(context.args[0])
        except:
            await update.message.reply_text("Usage: /unmute <user_id> or reply to a user's message")
            return

    if not user_id:
        await update.message.reply_text("Reply to a user or provide user ID")
        return

    success, message = await group_manager.unmute_user(update, context, user_id)
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a user"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return

    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("Invalid user ID")
        return

    success, message = await group_manager.unban_user(update, context, user_id)
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Warn a user"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    user_id = None
    reason = "No reason provided"

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        reason = ' '.join(context.args) if context.args else reason
    elif context.args:
        try:
            user_id = int(context.args[0])
            reason = ' '.join(context.args[1:]) if len(context.args) > 1 else reason
        except:
            await update.message.reply_text("Usage: /warn <user_id> [reason] or reply to a user's message")
            return

    if not user_id:
        await update.message.reply_text("Reply to a user or provide user ID")
        return

    success, message = await group_manager.warn_user(update, context, user_id, reason)
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def warnings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check warnings for a user"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    user_id = None

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            user_id = int(context.args[0])
        except:
            pass

    if not user_id:
        await update.message.reply_text("Reply to a user or provide user ID")
        return

    warnings = db_manager.get_warnings(update.effective_chat.id, user_id)

    if not warnings:
        await update.message.reply_text("User has no warnings.")
        return

    message = f"<b>Warnings for user {user_id}:</b>\n\n"
    for idx, warn in enumerate(warnings, 1):
        message += f"{idx}. {warn.get('reason', 'No reason')}\n"

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def resetwarns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset warnings for a user"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    if not await group_manager.is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("You need to be an admin.")
        return

    user_id = None

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            user_id = int(context.args[0])
        except:
            pass

    if not user_id:
        await update.message.reply_text("Reply to a user or provide user ID")
        return

    db_manager.reset_warnings(update.effective_chat.id, user_id)
    await update.message.reply_text(f"Warnings reset for user {user_id}")

async def pin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pin a message"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    success, message = await group_manager.pin_message(update, context)
    await update.message.reply_text(message)

async def unpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unpin a message"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    success, message = await group_manager.unpin_message(update, context)
    await update.message.reply_text(message)

async def setrules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set group rules"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    if not await group_manager.is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("You need to be an admin.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /setrules Your rules here")
        return

    rules = ' '.join(context.args)
    db_manager.update_group_settings(update.effective_chat.id, {"rules": rules})
    await update.message.reply_text("Rules have been set!")

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View group rules"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    rules = group_manager.format_rules(update.effective_chat.id)
    await update.message.reply_text(rules, parse_mode=ParseMode.HTML)

async def setwelcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set welcome message"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    if not await group_manager.is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("You need to be an admin.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /setwelcome Your message\n\nVariables:\n{mention} - mention user\n{name} - user name\n{chat} - group name"
        )
        return

    welcome_msg = ' '.join(context.args)
    db_manager.update_group_settings(update.effective_chat.id, {"welcome_message": welcome_msg})
    await update.message.reply_text("Welcome message has been set!")

async def welcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle welcome on/off"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    if not await group_manager.is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("You need to be an admin.")
        return

    group = db_manager.get_group(update.effective_chat.id)
    current = group.get('welcome_enabled', True) if group else True
    new_state = not current

    db_manager.update_group_settings(update.effective_chat.id, {"welcome_enabled": new_state})
    await update.message.reply_text(f"Welcome messages: {'enabled' if new_state else 'disabled'}")

async def save_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save a note"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    if not await group_manager.is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("You need to be an admin.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /save <note_name> <note_content>")
        return

    note_name = context.args[0]
    note_content = ' '.join(context.args[1:])

    db_manager.save_note(update.effective_chat.id, note_name, note_content, update.effective_user.id)
    await update.message.reply_text(f"Note '{note_name}' saved!")

async def get_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a note"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /get <note_name>")
        return

    note_name = context.args[0]
    note = db_manager.get_note(update.effective_chat.id, note_name)

    if note:
        await update.message.reply_text(note['note_content'])
    else:
        await update.message.reply_text("Note not found.")

async def notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all notes"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    notes = db_manager.get_all_notes(update.effective_chat.id)

    if not notes:
        await update.message.reply_text("No notes saved.")
        return

    message = "<b>Saved notes:</b>\n\n"
    for note in notes:
        message += f"• {note}\n"

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def clear_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a note"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    if not await group_manager.is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("You need to be an admin.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /clear <note_name>")
        return

    note_name = context.args[0]
    success = db_manager.delete_note(update.effective_chat.id, note_name)

    if success:
        await update.message.reply_text(f"Note '{note_name}' deleted!")
    else:
        await update.message.reply_text("Note not found.")

async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a filter"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    if not await group_manager.is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("You need to be an admin.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /filter <keyword> <reply_text>")
        return

    keyword = context.args[0]
    reply_text = ' '.join(context.args[1:])

    db_manager.save_filter(update.effective_chat.id, keyword, reply_text, update.effective_user.id)
    await update.message.reply_text(f"Filter for '{keyword}' added!")

async def filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all filters"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    filters_list = db_manager.get_all_filters(update.effective_chat.id)

    if not filters_list:
        await update.message.reply_text("No filters set.")
        return

    message = "<b>Active filters:</b>\n\n"
    for f in filters_list:
        message += f"• {f}\n"

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def stop_filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a filter"""
    await track_user_update(update)

    if update.effective_chat.type == 'private':
        await update.message.reply_text("This command only works in groups.")
        return

    if not await group_manager.is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("You need to be an admin.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /stop <keyword>")
        return

    keyword = context.args[0]
    success = db_manager.delete_filter(update.effective_chat.id, keyword)

    if success:
        await update.message.reply_text(f"Filter '{keyword}' removed!")
    else:
        await update.message.reply_text("Filter not found.")

async def addsudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    user_id = update.effective_user.id

    if not sudo_manager.check_owner_access(user_id):
        await update.message.reply_text("This command is restricted to the bot owner only!")
        return

    if len(context.args) == 0 and not update.message.reply_to_message:
        await update.message.reply_text("Usage: /addsudo <user_id or @username> or reply to a message")
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
            await update.message.reply_text("Please provide a valid user ID or username.")
            return

    if target_user_id:
        success, message = sudo_manager.add_sudo(target_user_id, target_username, target_first_name, user_id)
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

        if success and telegram_logger:
            await telegram_logger.log_sudo_change(
                user_id,
                update.effective_user.username,
                target_user_id,
                target_username,
                "ADDED TO SUDO"
            )

async def delsudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    user_id = update.effective_user.id

    if not sudo_manager.check_owner_access(user_id):
        await update.message.reply_text("This command is restricted to the bot owner only!")
        return

    if len(context.args) == 0 and not update.message.reply_to_message:
        await update.message.reply_text("Usage: /delsudo <user_id or @username> or reply to a message")
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
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

        if success and telegram_logger:
            await telegram_logger.log_sudo_change(
                user_id,
                update.effective_user.username,
                target_user_id,
                target_username,
                "REMOVED FROM SUDO"
            )

async def sudolist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_user_update(update)
    sudo_list = sudo_manager.get_sudo_list_formatted()
    await update.message.reply_text(sudo_list, parse_mode=ParseMode.HTML)

async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new members joining"""
    if update.message.new_chat_members:
        await group_manager.welcome_new_member(update, context)
        db_manager.register_group(update.effective_chat.id, update.effective_chat.title)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    await track_user_update(update)

    if not update.message or not update.message.text:
        return

    text = update.message.text

    if update.effective_chat.type != 'private':
        if group_manager.check_flood(update.effective_chat.id, update.effective_user.id):
            if await group_manager.is_bot_admin(update, context):
                await update.message.delete()
                await context.bot.send_message(
                    update.effective_chat.id,
                    f"{update.effective_user.mention_html()} stop flooding!",
                    parse_mode=ParseMode.HTML
                )
            return

        text_lower = text.lower()
        filter_result = db_manager.get_filter(update.effective_chat.id, text_lower)
        if filter_result:
            await update.message.reply_text(filter_result['reply_text'])
            return

    if should_trigger_ai(text) or update.effective_chat.type == 'private':
        status_msg = await update.message.reply_text("Thinking...")

        try:
            response = gemini_ai.get_response(update.effective_user.id, text)
            await status_msg.edit_text(response, parse_mode=ParseMode.HTML)

            if telegram_logger:
                await telegram_logger.log_ai_chat(
                    update.effective_user.id,
                    update.effective_user.username,
                    text[:50]
                )
        except Exception as e:
            logger.error(f"Message handler error: {e}")
            await status_msg.edit_text("Failed to process message.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        keyboard = [[InlineKeyboardButton("Back", callback_data='back_to_start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=TelegramFormatter.format_help(),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

    elif query.data == 'chat_info':
        keyboard = [[InlineKeyboardButton("Back", callback_data='back_to_start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = """<b>Gemini AI Chatbot</b>

Powered by Google Gemini AI!

Just chat naturally - I'll respond to greetings and messages.

Trigger words: hi, hello, hey, sup, yo, greetings

Features:
- Context-aware conversations
- Chat history memory
- Multi-topic knowledge

Use /clear to reset conversation"""
        await query.edit_message_text(text=message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    elif query.data == 'scan_info':
        keyboard = [[InlineKeyboardButton("Back", callback_data='back_to_start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = """<b>Vulnerability Scanning</b>

Access: Sudo users only

Features:
- Port scanning
- Security headers analysis
- SSL/TLS check
- Cookie security
- Vulnerability detection
- PDF reports

Usage: /vulnerscan <website>

Contact bot owner for sudo access."""
        await query.edit_message_text(text=message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    elif query.data == 'history':
        user_id = query.from_user.id
        history_message = sangmata.get_user_info(user_id)
        keyboard = [[InlineKeyboardButton("Back", callback_data='back_to_start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=history_message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    elif query.data == 'back_to_start':
        keyboard = [
            [
                InlineKeyboardButton("Help & Commands", callback_data='help'),
                InlineKeyboardButton("Chat with AI", callback_data='chat_info')
            ],
            [
                InlineKeyboardButton("Vulnerability Scan", callback_data='scan_info'),
                InlineKeyboardButton("My History", callback_data='history')
            ],
            [
                InlineKeyboardButton("Channel", url="https://t.me/dark_musictm"),
                InlineKeyboardButton("Developer", url="https://t.me/cyber_github")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=TelegramFormatter.format_start(),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    global telegram_logger

    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nConfiguration Error: {e}")
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

    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("kick", kick_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("unmute", unmute_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("warn", warn_command))
    application.add_handler(CommandHandler("warnings", warnings_command))
    application.add_handler(CommandHandler("resetwarns", resetwarns_command))
    application.add_handler(CommandHandler("pin", pin_command))
    application.add_handler(CommandHandler("unpin", unpin_command))

    application.add_handler(CommandHandler("setrules", setrules_command))
    application.add_handler(CommandHandler("rules", rules_command))
    application.add_handler(CommandHandler("setwelcome", setwelcome_command))
    application.add_handler(CommandHandler("welcome", welcome_command))

    application.add_handler(CommandHandler("save", save_note_command))
    application.add_handler(CommandHandler("get", get_note_command))
    application.add_handler(CommandHandler("notes", notes_command))
    application.add_handler(CommandHandler("clear", clear_note_command))

    application.add_handler(CommandHandler("filter", filter_command))
    application.add_handler(CommandHandler("filters", filters_command))
    application.add_handler(CommandHandler("stop", stop_filter_command))

    application.add_handler(CommandHandler("addsudo", addsudo_command))
    application.add_handler(CommandHandler("delsudo", delsudo_command))
    application.add_handler(CommandHandler("sudolist", sudolist_command))

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.add_error_handler(error_handler)

    logger.info("Advanced AI & Group Management Bot started!")
    print("\n" + "="*50)
    print("ADVANCED AI & GROUP MANAGEMENT BOT")
    print("="*50)
    print("Gemini AI: Active")
    print("MongoDB Database: Active")
    print("Vulnerability Scanner: Active")
    print("Group Management: Active")
    print("Sangmata Feature: Active")
    print("Sudo System: Active")
    print("="*50)
    print("Press Ctrl+C to stop\n")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
