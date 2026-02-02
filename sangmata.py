from mongodb_database import MongoDatabase
from typing import List, Dict, Any
from datetime import datetime

class SangmataFeature:
    def __init__(self):
        self.db = MongoDatabase()

    def track_user(self, user_id: int, username: str, first_name: str, last_name: str) -> None:
        self.db.record_user_history(user_id, username, first_name, last_name)

    def get_user_info(self, user_id: int) -> str:
        history = self.db.get_user_history(user_id)

        if not history:
            return "<blockquote expandable>📊 <b>User History</b>\n\n❌ No history found for this user.</blockquote>"

        current = history[-1] if history else None
        changes = len(history)

        message = "<blockquote expandable>📊 <b>SANGMATA - USER HISTORY TRACKER</b>\n\n"
        message += f"🆔 <b>User ID:</b> <code>{user_id}</code>\n\n"

        if current:
            message += "📝 <b>CURRENT INFORMATION</b>\n"
            message += f"👤 <b>First Name:</b> {current.get('first_name', 'N/A')}\n"
            message += f"👥 <b>Last Name:</b> {current.get('last_name', 'N/A')}\n"
            message += f"🔖 <b>Username:</b> @{current.get('username', 'None')}\n\n"

        message += f"🔄 <b>TOTAL CHANGES:</b> {changes}\n\n"

        message += "📜 <b>HISTORY LOG</b>\n"
        message += "━━━━━━━━━━━━━━━━\n\n"

        for idx, record in enumerate(history, 1):
            recorded_at = record.get('recorded_at', 'Unknown')
            if recorded_at != 'Unknown':
                try:
                    dt = datetime.fromisoformat(recorded_at.replace('Z', '+00:00'))
                    recorded_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass

            message += f"<b>#{idx}</b> - 📅 {recorded_at}\n"
            message += f"   👤 Name: {record.get('first_name', 'N/A')} {record.get('last_name', 'N/A')}\n"
            message += f"   🔖 Username: @{record.get('username', 'None')}\n\n"

        message += "━━━━━━━━━━━━━━━━\n"
        message += "ℹ️ <i>This feature tracks username and name changes over time</i>\n"
        message += "</blockquote>"

        return message

    def format_quick_info(self, user_id: int) -> str:
        history = self.db.get_user_history(user_id)

        if not history:
            return "📊 No history available"

        current = history[-1]
        changes = len(history) - 1

        info = f"👤 {current.get('first_name', 'N/A')}"
        if current.get('username'):
            info += f" (@{current.get('username')})"
        if changes > 0:
            info += f"\n🔄 {changes} change(s) detected"

        return info
