import re
from aiohttp import ClientSession
import asyncio

class AiChats:
    def __init__(self):
        self.system_prompt = """
        You are an AI assistant for the Demon Lord AASF's Legion. Respond in character as a demonic entity serving Lord AASF. 
        Your responses should be evil, intimidating, and aligned with the dark themes of the bot. 
        Use demonic language and references when appropriate.
        """

    async def groq(self, messages: list, api_key: str = "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"):
        async with ClientSession() as session:
            try:
                if messages and messages[0]['role'] != "system":
                    messages.insert(0, {"role": "system", "content": self.system_prompt})
                data = {
                    "model": "llama3-70b-8192",
                    "messages": messages
                }
                headers = {"Authorization": f"Bearer {api_key}"}
                api_url = "https://api.groq.com/openai/v1/chat/completions"

                async with session.post(api_url, json=data, headers=headers) as result:
                    if result.status != 200:
                        return {'error': result.reason}
                    else:
                        results = await result.json()
                        return {'reply': results.get("choices", [{}])[0].get("message", {}).get("content", "I serve only Lord AASF.")}
            except Exception as e:
                return {'error': str(e)}

ai = AiChats()

async def generate_demon_name():
    messages = [{"role": "user", "content": "Generate a demonic name for a follower of Lord AASF. Make it sound evil and intimidating."}]
    response = await ai.groq(messages)
    return response['reply'].strip() if response.get('reply') else "Shadowfiend"

async def generate_race_rank_description(name, is_race=True):
    prompt = f"Generate a short, evil description for a demonic {'race' if is_race else 'rank'} called '{name}'. Make it sound intimidating and malevolent."
    messages = [{"role": "user", "content": prompt}]
    response = await ai.groq(messages)
    return response['reply'].strip() if response.get('reply') else "A terrifying demonic entity."

async def ai_chat(user_message, conversation_history):
    messages = conversation_history + [{"role": "user", "content": user_message}]
    response = await ai.groq(messages)
    return response['reply'] if response.get('reply') else f"I serve only Lord AASF. {response}"
