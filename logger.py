from telegram import Bot
from config import Config
from datetime import datetime
from typing import Optional

class TelegramLogger:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.log_group_id = Config.LOG_GROUP_ID

    async def log_event(self, event_type: str, user_id: int, username: Optional[str], details: str):
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            message = f"<blockquote expandable>📊 <b>BOT EVENT LOG</b>\n\n"
            message += f"⏰ <b>Time:</b> {timestamp}\n"
            message += f"📌 <b>Event:</b> {event_type}\n"
            message += f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"

            if username:
                message += f"👤 <b>Username:</b> @{username}\n"

            message += f"\n📝 <b>Details:</b>\n{details}\n"
            message += "</blockquote>"

            await self.bot.send_message(
                chat_id=self.log_group_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Logging error: {e}")

    async def log_scan(self, user_id: int, username: Optional[str], target: str, risk_score: int, success: bool):
        status = "✅ SUCCESS" if success else "❌ FAILED"
        details = f"Target: {target}\nRisk Score: {risk_score}/100\nStatus: {status}"
        await self.log_event("VULNERABILITY SCAN", user_id, username, details)

    async def log_sudo_change(self, admin_id: int, admin_username: Optional[str], target_id: int, target_username: Optional[str], action: str):
        details = f"Admin: @{admin_username or admin_id}\n"
        details += f"Target: @{target_username or target_id} (ID: {target_id})\n"
        details += f"Action: {action}"
        await self.log_event("SUDO MANAGEMENT", admin_id, admin_username, details)

    async def log_command(self, user_id: int, username: Optional[str], command: str):
        details = f"Command: {command}"
        await self.log_event("COMMAND USED", user_id, username, details)

    async def log_error(self, user_id: int, username: Optional[str], error: str):
        details = f"Error: {error}"
        await self.log_event("ERROR", user_id, username, details)

    async def log_ai_chat(self, user_id: int, username: Optional[str], message_preview: str):
        if len(message_preview) > 100:
            message_preview = message_preview[:100] + "..."
        details = f"Message: {message_preview}"
        await self.log_event("AI CHAT", user_id, username, details)
