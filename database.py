from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta

class Database:
    def __init__(self, uri):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client.demon_lord_bot
        self.default_soul_goal = 666666  # Default soul goal
        self.initialize_soul_goal()

    async def initialize_soul_goal(self):
        existing_goal = await self.get_soul_goal()
        if existing_goal == 0:
            await self.update_soul_goal(self.default_soul_goal)

    async def get_user(self, user_id):
        return await self.db.users.find_one({"user_id": user_id})

    async def get_user_by_referral_code(self, referral_code):
        return await self.db.users.find_one({"referral_code": referral_code})

    async def create_user(self, user_data):
        user_data['created_at'] = datetime.utcnow()
        user_data['last_ritual'] = datetime.utcnow() - timedelta(days=1)  # Set to yesterday to allow immediate ritual
        return await self.db.users.insert_one(user_data)

    async def update_user(self, user_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        return await self.db.users.update_one({"user_id": user_id}, {"$set": update_data})

    async def increment_user_stats(self, user_id, stats):
        return await self.db.users.update_one(
            {"user_id": user_id},
            {
                "$inc": stats,
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    async def get_leaderboard(self, limit=10):
        return await self.db.users.find().sort("souls_collected", -1).limit(limit).to_list(length=limit)

    async def update_global_souls(self, souls_collected):
        return await self.db.global_stats.update_one(
            {"_id": "soul_counter"},
            {
                "$inc": {"total_souls": souls_collected},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )

    async def get_global_souls(self):
        stats = await self.db.global_stats.find_one({"_id": "soul_counter"})
        return stats['total_souls'] if stats else 0

    async def get_all_users(self):
        return await self.db.users.find().to_list(length=None)

    async def update_soul_goal(self, new_goal):
        return await self.db.global_stats.update_one(
            {"_id": "soul_goal"},
            {"$set": {"goal": new_goal, "updated_at": datetime.utcnow()}},
            upsert=True
        )

    async def get_soul_goal(self):
        stats = await self.db.global_stats.find_one({"_id": "soul_goal"})
        return stats['goal'] if stats else 0

    async def get_user_referrals(self, user_id):
        user = await self.get_user(user_id)
        if user:
            return await self.db.users.find({"referred_by": user['referral_code']}).to_list(length=None)
        return []

    async def get_total_users(self):
        return await self.db.users.count_documents({})

    async def get_ai_conversation(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id})
        return user.get('ai_conversation', []) if user else []

    async def update_ai_conversation(self, user_id, conversation):
        await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"ai_conversation": conversation}}
        )

    async def get_all_chats(self):
        return await self.db.chats.find().to_list(length=None)

    async def add_chat(self, chat_id, chat_type):
        return await self.db.chats.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_type": chat_type, "updated_at": datetime.utcnow()}},
            upsert=True
        )

    async def remove_chat(self, chat_id):
        return await self.db.chats.delete_one({"chat_id": chat_id})
