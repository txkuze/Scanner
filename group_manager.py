from telegram import Update, ChatPermissions, ChatMember
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from mongodb_database import MongoDatabase
from datetime import datetime, timedelta
from typing import Optional

class GroupManager:
    def __init__(self):
        self.db = MongoDatabase()

    async def is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
        """Check if user is admin in the chat"""
        try:
            chat_member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
            return chat_member.status in ['creator', 'administrator']
        except:
            return False

    async def is_bot_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if bot is admin in the chat"""
        try:
            bot_member = await context.bot.get_chat_member(update.effective_chat.id, context.bot.id)
            return bot_member.status == 'administrator'
        except:
            return False

    async def welcome_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome new members to the group"""
        chat_id = update.effective_chat.id
        group = self.db.get_group(chat_id)

        if not group or not group.get('welcome_enabled', True):
            return

        for member in update.message.new_chat_members:
            if member.is_bot:
                continue

            welcome_text = group.get('welcome_message', 'Welcome {mention} to {chat}!')
            welcome_text = welcome_text.replace('{mention}', member.mention_html())
            welcome_text = welcome_text.replace('{chat}', update.effective_chat.title or 'the group')
            welcome_text = welcome_text.replace('{name}', member.first_name)

            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.HTML
            )

    async def warn_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, reason: str) -> tuple[bool, str]:
        """Warn a user and auto-action if threshold reached"""
        chat_id = update.effective_chat.id
        warned_by = update.effective_user.id

        if not await self.is_admin(update, context, warned_by):
            return False, "You need to be an admin to warn users"

        if await self.is_admin(update, context, user_id):
            return False, "Cannot warn admins"

        warn_count = self.db.add_warning(chat_id, user_id, warned_by, reason)

        user = await context.bot.get_chat_member(chat_id, user_id)
        user_mention = user.user.mention_html()

        if warn_count >= 3:
            try:
                await context.bot.ban_chat_member(chat_id, user_id)
                self.db.reset_warnings(chat_id, user_id)
                return True, f"{user_mention} has been banned after receiving 3 warnings"
            except:
                return True, f"{user_mention} has {warn_count} warnings but I couldn't ban them"

        return True, f"{user_mention} has been warned ({warn_count}/3)\nReason: {reason}"

    async def ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, reason: str = "No reason provided") -> tuple[bool, str]:
        """Ban a user from the group"""
        chat_id = update.effective_chat.id

        if not await self.is_admin(update, context, update.effective_user.id):
            return False, "You need to be an admin to ban users"

        if not await self.is_bot_admin(update, context):
            return False, "I need admin rights to ban users"

        if await self.is_admin(update, context, user_id):
            return False, "Cannot ban admins"

        try:
            user = await context.bot.get_chat_member(chat_id, user_id)
            await context.bot.ban_chat_member(chat_id, user_id)
            return True, f"{user.user.mention_html()} has been banned\nReason: {reason}"
        except Exception as e:
            return False, f"Failed to ban user: {str(e)}"

    async def kick_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, reason: str = "No reason provided") -> tuple[bool, str]:
        """Kick a user from the group (can rejoin)"""
        chat_id = update.effective_chat.id

        if not await self.is_admin(update, context, update.effective_user.id):
            return False, "You need to be an admin to kick users"

        if not await self.is_bot_admin(update, context):
            return False, "I need admin rights to kick users"

        if await self.is_admin(update, context, user_id):
            return False, "Cannot kick admins"

        try:
            user = await context.bot.get_chat_member(chat_id, user_id)
            await context.bot.ban_chat_member(chat_id, user_id)
            await context.bot.unban_chat_member(chat_id, user_id)
            return True, f"{user.user.mention_html()} has been kicked\nReason: {reason}"
        except Exception as e:
            return False, f"Failed to kick user: {str(e)}"

    async def mute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, duration_minutes: int = 0) -> tuple[bool, str]:
        """Mute a user (restrict from sending messages)"""
        chat_id = update.effective_chat.id

        if not await self.is_admin(update, context, update.effective_user.id):
            return False, "You need to be an admin to mute users"

        if not await self.is_bot_admin(update, context):
            return False, "I need admin rights to mute users"

        if await self.is_admin(update, context, user_id):
            return False, "Cannot mute admins"

        try:
            user = await context.bot.get_chat_member(chat_id, user_id)
            permissions = ChatPermissions(can_send_messages=False)

            if duration_minutes > 0:
                until_date = datetime.now() + timedelta(minutes=duration_minutes)
                await context.bot.restrict_chat_member(chat_id, user_id, permissions, until_date=until_date)
                return True, f"{user.user.mention_html()} has been muted for {duration_minutes} minutes"
            else:
                await context.bot.restrict_chat_member(chat_id, user_id, permissions)
                return True, f"{user.user.mention_html()} has been muted permanently"
        except Exception as e:
            return False, f"Failed to mute user: {str(e)}"

    async def unmute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> tuple[bool, str]:
        """Unmute a user"""
        chat_id = update.effective_chat.id

        if not await self.is_admin(update, context, update.effective_user.id):
            return False, "You need to be an admin to unmute users"

        if not await self.is_bot_admin(update, context):
            return False, "I need admin rights to unmute users"

        try:
            user = await context.bot.get_chat_member(chat_id, user_id)
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            await context.bot.restrict_chat_member(chat_id, user_id, permissions)
            return True, f"{user.user.mention_html()} has been unmuted"
        except Exception as e:
            return False, f"Failed to unmute user: {str(e)}"

    async def unban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> tuple[bool, str]:
        """Unban a user"""
        chat_id = update.effective_chat.id

        if not await self.is_admin(update, context, update.effective_user.id):
            return False, "You need to be an admin to unban users"

        if not await self.is_bot_admin(update, context):
            return False, "I need admin rights to unban users"

        try:
            await context.bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
            return True, f"User {user_id} has been unbanned"
        except Exception as e:
            return False, f"Failed to unban user: {str(e)}"

    async def pin_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple[bool, str]:
        """Pin a message"""
        if not await self.is_admin(update, context, update.effective_user.id):
            return False, "You need to be an admin to pin messages"

        if not await self.is_bot_admin(update, context):
            return False, "I need admin rights to pin messages"

        if not update.message.reply_to_message:
            return False, "Reply to a message to pin it"

        try:
            await context.bot.pin_chat_message(
                update.effective_chat.id,
                update.message.reply_to_message.message_id
            )
            return True, "Message pinned successfully"
        except Exception as e:
            return False, f"Failed to pin message: {str(e)}"

    async def unpin_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple[bool, str]:
        """Unpin a message"""
        if not await self.is_admin(update, context, update.effective_user.id):
            return False, "You need to be an admin to unpin messages"

        if not await self.is_bot_admin(update, context):
            return False, "I need admin rights to unpin messages"

        try:
            if update.message.reply_to_message:
                await context.bot.unpin_chat_message(
                    update.effective_chat.id,
                    update.message.reply_to_message.message_id
                )
            else:
                await context.bot.unpin_all_chat_messages(update.effective_chat.id)
            return True, "Message unpinned successfully"
        except Exception as e:
            return False, f"Failed to unpin message: {str(e)}"

    def check_flood(self, chat_id: int, user_id: int) -> bool:
        """Check if user is flooding"""
        group = self.db.get_group(chat_id)

        if not group or not group.get('antiflood_enabled', False):
            return False

        limit = group.get('antiflood_limit', 5)
        message_count = self.db.record_message(chat_id, user_id)

        return message_count >= limit

    def format_rules(self, chat_id: int) -> str:
        """Get formatted rules for the group"""
        group = self.db.get_group(chat_id)

        if not group or not group.get('rules'):
            return "No rules have been set for this group yet"

        return f"<b>Group Rules:</b>\n\n{group['rules']}"
