from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import Config

class MongoDatabase:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client[Config.MONGODB_NAME]

        # Collections
        self.sudo_users = self.db.sudo_users
        self.user_history = self.db.user_history
        self.chat_sessions = self.db.chat_sessions
        self.scan_logs = self.db.scan_logs
        self.groups = self.db.groups
        self.warnings = self.db.warnings
        self.notes = self.db.notes
        self.filters = self.db.filters
        self.welcome_settings = self.db.welcome_settings
        self.user_flood = self.db.user_flood

        self._create_indexes()

    def _create_indexes(self):
        """Create indexes for better query performance"""
        self.sudo_users.create_index("user_id", unique=True)
        self.user_history.create_index([("user_id", 1), ("recorded_at", -1)])
        self.chat_sessions.create_index([("user_id", 1), ("created_at", -1)])
        self.groups.create_index("chat_id", unique=True)
        self.warnings.create_index([("chat_id", 1), ("user_id", 1)])
        self.notes.create_index([("chat_id", 1), ("note_name", 1)], unique=True)
        self.filters.create_index([("chat_id", 1), ("keyword", 1)], unique=True)
        self.user_flood.create_index([("chat_id", 1), ("user_id", 1)])

    # Sudo Users Management
    def is_sudo_user(self, user_id: int) -> bool:
        try:
            return self.sudo_users.find_one({"user_id": user_id}) is not None
        except Exception as e:
            print(f"Error checking sudo user: {e}")
            return False

    def is_owner(self, user_id: int) -> bool:
        try:
            return self.sudo_users.find_one({"user_id": user_id, "is_owner": True}) is not None
        except Exception as e:
            print(f"Error checking owner: {e}")
            return False

    def add_sudo_user(self, user_id: int, username: str, first_name: str, added_by: int, is_owner: bool = False) -> bool:
        try:
            data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'added_by': added_by,
                'is_owner': is_owner,
                'added_at': datetime.utcnow()
            }
            self.sudo_users.insert_one(data)
            return True
        except DuplicateKeyError:
            return False
        except Exception as e:
            print(f"Error adding sudo user: {e}")
            return False

    def remove_sudo_user(self, user_id: int) -> bool:
        try:
            result = self.sudo_users.delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error removing sudo user: {e}")
            return False

    def get_sudo_list(self) -> List[Dict[str, Any]]:
        try:
            return list(self.sudo_users.find().sort("added_at", 1))
        except Exception as e:
            print(f"Error getting sudo list: {e}")
            return []

    # User History (Sangmata)
    def record_user_history(self, user_id: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str]) -> bool:
        try:
            last_record = self.user_history.find_one(
                {"user_id": user_id},
                sort=[("recorded_at", -1)]
            )

            if last_record:
                if (last_record.get('username') == username and
                    last_record.get('first_name') == first_name and
                    last_record.get('last_name') == last_name):
                    return True

            data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'recorded_at': datetime.utcnow()
            }
            self.user_history.insert_one(data)
            return True
        except Exception as e:
            print(f"Error recording user history: {e}")
            return False

    def get_user_history(self, user_id: int) -> List[Dict[str, Any]]:
        try:
            return list(self.user_history.find({"user_id": user_id}).sort("recorded_at", 1))
        except Exception as e:
            print(f"Error getting user history: {e}")
            return []

    # Chat Sessions (AI)
    def add_chat_message(self, user_id: int, message: str, role: str) -> bool:
        try:
            data = {
                'user_id': user_id,
                'message': message,
                'role': role,
                'created_at': datetime.utcnow()
            }
            self.chat_sessions.insert_one(data)
            return True
        except Exception as e:
            print(f"Error adding chat message: {e}")
            return False

    def get_chat_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            return list(self.chat_sessions.find({"user_id": user_id}).sort("created_at", -1).limit(limit))[::-1]
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []

    def clear_chat_history(self, user_id: int) -> bool:
        try:
            self.chat_sessions.delete_many({"user_id": user_id})
            return True
        except Exception as e:
            print(f"Error clearing chat history: {e}")
            return False

    # Scan Logs
    def log_scan(self, user_id: int, username: str, target: str, risk_score: int) -> bool:
        try:
            data = {
                'user_id': user_id,
                'username': username,
                'target': target,
                'risk_score': risk_score,
                'scanned_at': datetime.utcnow()
            }
            self.scan_logs.insert_one(data)
            return True
        except Exception as e:
            print(f"Error logging scan: {e}")
            return False

    # Group Management
    def register_group(self, chat_id: int, chat_title: str) -> bool:
        try:
            data = {
                'chat_id': chat_id,
                'chat_title': chat_title,
                'registered_at': datetime.utcnow(),
                'rules': None,
                'welcome_enabled': True,
                'welcome_message': "Welcome {mention} to {chat}!",
                'antiflood_enabled': False,
                'antiflood_limit': 5
            }
            self.groups.update_one(
                {"chat_id": chat_id},
                {"$setOnInsert": data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error registering group: {e}")
            return False

    def get_group(self, chat_id: int) -> Optional[Dict[str, Any]]:
        try:
            return self.groups.find_one({"chat_id": chat_id})
        except Exception as e:
            print(f"Error getting group: {e}")
            return None

    def update_group_settings(self, chat_id: int, settings: Dict[str, Any]) -> bool:
        try:
            self.groups.update_one(
                {"chat_id": chat_id},
                {"$set": settings}
            )
            return True
        except Exception as e:
            print(f"Error updating group settings: {e}")
            return False

    # Warnings System
    def add_warning(self, chat_id: int, user_id: int, warned_by: int, reason: str) -> int:
        try:
            data = {
                'chat_id': chat_id,
                'user_id': user_id,
                'warned_by': warned_by,
                'reason': reason,
                'warned_at': datetime.utcnow()
            }
            self.warnings.insert_one(data)

            count = self.warnings.count_documents({"chat_id": chat_id, "user_id": user_id})
            return count
        except Exception as e:
            print(f"Error adding warning: {e}")
            return 0

    def get_warnings(self, chat_id: int, user_id: int) -> List[Dict[str, Any]]:
        try:
            return list(self.warnings.find({"chat_id": chat_id, "user_id": user_id}).sort("warned_at", -1))
        except Exception as e:
            print(f"Error getting warnings: {e}")
            return []

    def reset_warnings(self, chat_id: int, user_id: int) -> bool:
        try:
            self.warnings.delete_many({"chat_id": chat_id, "user_id": user_id})
            return True
        except Exception as e:
            print(f"Error resetting warnings: {e}")
            return False

    # Notes System
    def save_note(self, chat_id: int, note_name: str, note_content: str, created_by: int) -> bool:
        try:
            data = {
                'chat_id': chat_id,
                'note_name': note_name.lower(),
                'note_content': note_content,
                'created_by': created_by,
                'created_at': datetime.utcnow()
            }
            self.notes.update_one(
                {"chat_id": chat_id, "note_name": note_name.lower()},
                {"$set": data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving note: {e}")
            return False

    def get_note(self, chat_id: int, note_name: str) -> Optional[Dict[str, Any]]:
        try:
            return self.notes.find_one({"chat_id": chat_id, "note_name": note_name.lower()})
        except Exception as e:
            print(f"Error getting note: {e}")
            return None

    def delete_note(self, chat_id: int, note_name: str) -> bool:
        try:
            result = self.notes.delete_one({"chat_id": chat_id, "note_name": note_name.lower()})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting note: {e}")
            return False

    def get_all_notes(self, chat_id: int) -> List[str]:
        try:
            notes = self.notes.find({"chat_id": chat_id}, {"note_name": 1})
            return [note['note_name'] for note in notes]
        except Exception as e:
            print(f"Error getting all notes: {e}")
            return []

    # Filters System
    def save_filter(self, chat_id: int, keyword: str, reply_text: str, created_by: int) -> bool:
        try:
            data = {
                'chat_id': chat_id,
                'keyword': keyword.lower(),
                'reply_text': reply_text,
                'created_by': created_by,
                'created_at': datetime.utcnow()
            }
            self.filters.update_one(
                {"chat_id": chat_id, "keyword": keyword.lower()},
                {"$set": data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving filter: {e}")
            return False

    def get_filter(self, chat_id: int, keyword: str) -> Optional[Dict[str, Any]]:
        try:
            return self.filters.find_one({"chat_id": chat_id, "keyword": keyword.lower()})
        except Exception as e:
            print(f"Error getting filter: {e}")
            return None

    def delete_filter(self, chat_id: int, keyword: str) -> bool:
        try:
            result = self.filters.delete_one({"chat_id": chat_id, "keyword": keyword.lower()})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting filter: {e}")
            return False

    def get_all_filters(self, chat_id: int) -> List[str]:
        try:
            filters = self.filters.find({"chat_id": chat_id}, {"keyword": 1})
            return [f['keyword'] for f in filters]
        except Exception as e:
            print(f"Error getting all filters: {e}")
            return []

    # Antiflood System
    def record_message(self, chat_id: int, user_id: int) -> int:
        try:
            current_time = datetime.utcnow()

            self.user_flood.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {
                    "$push": {
                        "messages": {
                            "$each": [current_time],
                            "$slice": -10
                        }
                    }
                },
                upsert=True
            )

            user_data = self.user_flood.find_one({"chat_id": chat_id, "user_id": user_id})

            if user_data and 'messages' in user_data:
                recent_messages = [
                    msg for msg in user_data['messages']
                    if (current_time - msg).total_seconds() <= 5
                ]
                return len(recent_messages)

            return 0
        except Exception as e:
            print(f"Error recording message: {e}")
            return 0
