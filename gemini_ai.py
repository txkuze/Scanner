import google.generativeai as genai
from config import Config
from mongodb_database import MongoDatabase
from typing import List, Dict

class GeminiAI:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.db = MongoDatabase()

        self.system_prompt = """You are an advanced AI assistant integrated into a Telegram bot with multiple capabilities:

1. You can have natural conversations with users
2. You can help with vulnerability scanning (though that requires special permissions)
3. You provide helpful, friendly, and informative responses
4. You use emojis appropriately to make conversations engaging
5. You're knowledgeable about cybersecurity, programming, and technology

Always be helpful, respectful, and provide accurate information. When users ask about scanning websites, remind them that only authorized sudo users can perform scans, and they should only scan websites they own or have permission to test.

Respond in a friendly, conversational manner while being informative and helpful."""

    def get_response(self, user_id: int, user_message: str) -> str:
        try:
            chat_history = self.db.get_chat_history(user_id, limit=10)

            history_context = ""
            if chat_history:
                for msg in chat_history:
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    history_context += f"{role}: {msg['message']}\n"

            full_prompt = f"{self.system_prompt}\n\nConversation History:\n{history_context}\n\nUser: {user_message}\n\nAssistant:"

            response = self.model.generate_content(full_prompt)

            assistant_reply = response.text

            self.db.add_chat_message(user_id, user_message, 'user')
            self.db.add_chat_message(user_id, assistant_reply, 'assistant')

            return assistant_reply

        except Exception as e:
            print(f"Gemini AI error: {e}")
            return "I apologize, but I encountered an error processing your message. Please try again."

    def clear_conversation(self, user_id: int) -> bool:
        return self.db.clear_chat_history(user_id)
