from supabase import create_client, Client
from config import Config
from typing import List, Dict, Any, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

    def is_sudo_user(self, user_id: int) -> bool:
        try:
            response = self.supabase.table('sudo_users').select('*').eq('user_id', user_id).maybeSingle().execute()
            return response.data is not None
        except Exception as e:
            print(f"Error checking sudo user: {e}")
            return False

    def is_owner(self, user_id: int) -> bool:
        try:
            response = self.supabase.table('sudo_users').select('*').eq('user_id', user_id).eq('is_owner', True).maybeSingle().execute()
            return response.data is not None
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
                'is_owner': is_owner
            }
            self.supabase.table('sudo_users').insert(data).execute()
            return True
        except Exception as e:
            print(f"Error adding sudo user: {e}")
            return False

    def remove_sudo_user(self, user_id: int) -> bool:
        try:
            self.supabase.table('sudo_users').delete().eq('user_id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error removing sudo user: {e}")
            return False

    def get_sudo_list(self) -> List[Dict[str, Any]]:
        try:
            response = self.supabase.table('sudo_users').select('*').order('added_at').execute()
            return response.data
        except Exception as e:
            print(f"Error getting sudo list: {e}")
            return []

    def record_user_history(self, user_id: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str]) -> bool:
        try:
            response = self.supabase.table('user_history').select('*').eq('user_id', user_id).order('recorded_at', desc=True).limit(1).maybeSingle().execute()

            if response.data:
                last_record = response.data
                if (last_record.get('username') == username and
                    last_record.get('first_name') == first_name and
                    last_record.get('last_name') == last_name):
                    return True

            data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name
            }
            self.supabase.table('user_history').insert(data).execute()
            return True
        except Exception as e:
            print(f"Error recording user history: {e}")
            return False

    def get_user_history(self, user_id: int) -> List[Dict[str, Any]]:
        try:
            response = self.supabase.table('user_history').select('*').eq('user_id', user_id).order('recorded_at').execute()
            return response.data
        except Exception as e:
            print(f"Error getting user history: {e}")
            return []

    def add_chat_message(self, user_id: int, message: str, role: str) -> bool:
        try:
            data = {
                'user_id': user_id,
                'message': message,
                'role': role
            }
            self.supabase.table('chat_sessions').insert(data).execute()
            return True
        except Exception as e:
            print(f"Error adding chat message: {e}")
            return False

    def get_chat_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            response = self.supabase.table('chat_sessions').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            return list(reversed(response.data))
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []

    def clear_chat_history(self, user_id: int) -> bool:
        try:
            self.supabase.table('chat_sessions').delete().eq('user_id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error clearing chat history: {e}")
            return False

    def log_scan(self, user_id: int, username: str, target: str, risk_score: int) -> bool:
        try:
            data = {
                'user_id': user_id,
                'username': username,
                'target': target,
                'risk_score': risk_score
            }
            self.supabase.table('scan_logs').insert(data).execute()
            return True
        except Exception as e:
            print(f"Error logging scan: {e}")
            return False
