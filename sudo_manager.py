from database import DatabaseManager
from config import Config
from typing import Optional

class SudoManager:
    def __init__(self):
        self.db = DatabaseManager()

    def initialize_owner(self) -> bool:
        if Config.OWNER_ID and not self.db.is_sudo_user(Config.OWNER_ID):
            return self.db.add_sudo_user(
                user_id=Config.OWNER_ID,
                username="Owner",
                first_name="Owner",
                added_by=Config.OWNER_ID,
                is_owner=True
            )
        return True

    def check_sudo_access(self, user_id: int) -> bool:
        return self.db.is_sudo_user(user_id)

    def check_owner_access(self, user_id: int) -> bool:
        return self.db.is_owner(user_id)

    def add_sudo(self, user_id: int, username: str, first_name: str, added_by: int) -> tuple[bool, str]:
        if self.db.is_sudo_user(user_id):
            return False, f"❌ User {username or user_id} is already a sudo user!"

        success = self.db.add_sudo_user(user_id, username, first_name, added_by, is_owner=False)

        if success:
            return True, f"✅ Successfully added {username or user_id} to sudo users!"
        else:
            return False, "❌ Failed to add user to sudo list. Please try again."

    def remove_sudo(self, user_id: int) -> tuple[bool, str]:
        if self.db.is_owner(user_id):
            return False, "❌ Cannot remove the bot owner from sudo list!"

        if not self.db.is_sudo_user(user_id):
            return False, "❌ User is not in sudo list!"

        success = self.db.remove_sudo_user(user_id)

        if success:
            return True, f"✅ Successfully removed user {user_id} from sudo list!"
        else:
            return False, "❌ Failed to remove user from sudo list. Please try again."

    def get_sudo_list_formatted(self) -> str:
        sudo_users = self.db.get_sudo_list()

        if not sudo_users:
            return "<blockquote expandable>👥 <b>SUDO USERS LIST</b>\n\n❌ No sudo users found.</blockquote>"

        message = "<blockquote expandable>👥 <b>SUDO USERS LIST</b>\n\n"
        message += f"📊 <b>Total Sudo Users:</b> {len(sudo_users)}\n\n"
        message += "━━━━━━━━━━━━━━━━\n\n"

        owner_count = 0
        sudo_count = 0

        for idx, user in enumerate(sudo_users, 1):
            is_owner = user.get('is_owner', False)
            if is_owner:
                owner_count += 1
                badge = "👑 OWNER"
            else:
                sudo_count += 1
                badge = "🔑 SUDO"

            message += f"<b>{idx}.</b> {badge}\n"
            message += f"   🆔 <b>User ID:</b> <code>{user['user_id']}</code>\n"
            message += f"   👤 <b>Name:</b> {user.get('first_name', 'N/A')}\n"

            if user.get('username'):
                message += f"   🔖 <b>Username:</b> @{user['username']}\n"

            added_at = user.get('added_at', 'Unknown')
            if added_at != 'Unknown':
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(added_at.replace('Z', '+00:00'))
                    added_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass

            message += f"   📅 <b>Added:</b> {added_at}\n\n"

        message += "━━━━━━━━━━━━━━━━\n"
        message += f"👑 <b>Owners:</b> {owner_count}\n"
        message += f"🔑 <b>Sudo Users:</b> {sudo_count}\n"
        message += "</blockquote>"

        return message
