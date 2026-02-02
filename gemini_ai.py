from openai import OpenAI
from config import Config
from mongodb_database import MongoDatabase
from typing import List, Dict


class DeepSeekAI:
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL
        )

        self.model = "deepseek-chat"
        self.db = MongoDatabase()

        self.system_prompt = (
            "You are an advanced AI assistant integrated into a Telegram bot with multiple capabilities:\n\n"
            "1. You can have natural conversations with users\n"
            "2. You can help with vulnerability scanning (only conceptually unless user is authorized)\n"
            "3. You provide helpful, friendly, and informative responses\n"
            "4. You use emojis appropriately to make conversations engaging\n"
            "5. You're knowledgeable about cybersecurity, programming, and technology\n\n"
            "Rules:\n"
            "- Be polite, friendly, and accurate\n"
            "- Never encourage illegal hacking\n"
            "- When users ask about scanning websites, remind them that only authorized sudo users can perform scans\n"
            "- Scans should only be done on websites they own or have permission to test\n\n"
            "Respond in a friendly, conversational tone."
        )

    def get_response(self, user_id: int, user_message: str) -> str:
        try:
            chat_history = self.db.get_chat_history(user_id, limit=10)

            messages = [
                {"role": "system", "content": self.system_prompt}
            ]

            if chat_history:
                for msg in chat_history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["message"]
                    })

            messages.append({
                "role": "user",
                "content": user_message
            })

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )

            assistant_reply = response.choices[0].message.content.strip()

            self.db.add_chat_message(user_id, user_message, "user")
            self.db.add_chat_message(user_id, assistant_reply, "assistant")

            return assistant_reply

        except Exception as e:
            print(f"DeepSeek AI error: {e}")
            return (
                "⚠️ Oops! I ran into a technical issue while processing your message.\n"
                "Please try again in a moment."
            )

    def clear_conversation(self, user_id: int) -> bool:
        return self.db.clear_chat_history(user_id)
