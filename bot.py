import asyncio
import random
import io
import sys
import traceback
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from contextlib import redirect_stdout, redirect_stderr
from subprocess import getoutput as run
from database import Database
import shortuuid
from ai_chat import AiChats, generate_demon_name, generate_race_rank_description, ai_chat

# Replace these with your own values
API_ID = "14676558"
API_HASH = "b3c4bc0ba6a4fc123f4d748a8cc39981"
BOT_TOKEN = "7842526948:AAEYKr5fSDsDf1cIgoMEpe6-KYOnWum9mKo"
MONGODB_URI = "mongodb+srv://knight_rider:GODGURU12345@knight.jm59gu9.mongodb.net/?retryWrites=true&w=majority"
BOT_USERNAME = "@AasfLegionBot"
DEVS = [5965055071, 5456798232]  # Add the user IDs of developers here

app = Client("demon_lord_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = Database(MONGODB_URI)
ai = AiChats()

# Global variables
AASF_ID = 5456798232  # User ID for Lord AASF

# Demonic symbols
DEMONIC_SYMBOLS = {
    "pentagram": "⛧", "demon": "𝖉𝖊𝖒𝖔𝖓", "cross": "⸸", "star": "⛧⃝", "goat": "𓃶",
    "fire": "🜏", "skull": " ☠︎︎", "number": "⁶⁶⁶", "ankh": "˙𓄋"
}

async def generate_ai_response(prompt, user_id=None):
    conversation = await db.get_ai_conversation(user_id) if user_id else []
    formatted_prompt = f"""
    {prompt}

    Use the following formatting in your response:
    - *bold* for emphasis
    - _italic_ for secondary emphasis
    - `fixed width font` for commands or special terms
    - [text](http://example.com) for links (use sparingly)

    Incorporate these demonic symbols where appropriate: {', '.join([f'{k}: {v}' for k, v in DEMONIC_SYMBOLS.items()])}

    Use demonic slang and a sinister accent. Make the response extremely evil, intimidating, and befitting of Lord AASF's demonic realm.
    """
    response = await ai_chat(formatted_prompt, conversation)
    if user_id:
        conversation.append({"role": "user", "content": prompt})
        conversation.append({"role": "assistant", "content": response})
        await db.update_ai_conversation(user_id, conversation[-10:])  # Keep last 10 messages
    return response

@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        demon_name = await generate_demon_name()
        race = await generate_race_rank_description(random.choice(["Imp", "Hellhound", "Succubus", "Necromancer", "Abyssal Horror", "Plague Bearer", "Soul Reaver"]), is_race=True)
        referral_link, unique_id = f"https://t.me/{BOT_USERNAME}?start={shortuuid.uuid()}", shortuuid.uuid()
        
        new_user = {
            "user_id": user_id,
            "name": demon_name,
            "race": race,
            "rank": "Forsaken Soul",
            "souls_collected": 0,
            "referral_code": unique_id,
            "referral_link": referral_link,
            "referred_by": message.text.split()[-1] if len(message.text.split()) > 1 else unique_id,
            "last_ritual": datetime.utcnow() - timedelta(days=1),
            "cursed_souls": 0
        }
        await db.create_user(new_user)
        
        welcome_prompt = f"""
        Generate a welcoming message for a new soul named *{demon_name}* who has just been dragged into Lord AASF's infernal legion.
        Describe their newfound demonic form as a {race} in gruesome detail.
        Explain the hierarchy of Hell and how they can ascend through harvesting souls.
        Mention the following commands they can use to serve their dark master:
        - `{DEMONIC_SYMBOLS['pentagram']}status{DEMONIC_SYMBOLS['pentagram']}` - Witness their demonic transformation
        - `{DEMONIC_SYMBOLS['skull']}harvest{DEMONIC_SYMBOLS['skull']}` - Reap the essence of mortal fools
        - `{DEMONIC_SYMBOLS['demon']}hierarchy{DEMONIC_SYMBOLS['demon']}` - Gaze upon the ranks of the damned
        - `{DEMONIC_SYMBOLS['star']}ritual{DEMONIC_SYMBOLS['star']}` - Perform unholy rites for power
        - `{DEMONIC_SYMBOLS['cross']}curse{DEMONIC_SYMBOLS['cross']}` - Inflict suffering upon the weak
        - `{DEMONIC_SYMBOLS['goat']}summon_aasf{DEMONIC_SYMBOLS['goat']}` - Beseech the Dark Lord for an audience
        Make it clear that their eternal torment has only just begun, and their only path to power is through absolute loyalty to Lord AASF.
        """
    else:
        welcome_prompt = f"""
        Generate a spine-chilling welcome back message for *{user['name']}*, a {user['race']} in Lord AASF's demonic legion.
        Remind them of their eternal servitude and the price of failure.
        Encourage them to continue their unholy work using the following commands:
        - `{DEMONIC_SYMBOLS['pentagram']}status{DEMONIC_SYMBOLS['pentagram']}` - Witness their demonic transformation
        - `{DEMONIC_SYMBOLS['skull']}harvest{DEMONIC_SYMBOLS['skull']}` - Reap the essence of mortal fools
        - `{DEMONIC_SYMBOLS['demon']}hierarchy{DEMONIC_SYMBOLS['demon']}` - Gaze upon the ranks of the damned
        - `{DEMONIC_SYMBOLS['star']}ritual{DEMONIC_SYMBOLS['star']}` - Perform unholy rites for power
        - `{DEMONIC_SYMBOLS['cross']}curse{DEMONIC_SYMBOLS['cross']}` - Inflict suffering upon the weak
        - `{DEMONIC_SYMBOLS['goat']}summon_aasf{DEMONIC_SYMBOLS['goat']}` - Beseech the Dark Lord for an audience
        Emphasize that Lord AASF's hunger for souls is insatiable, and their position in the infernal hierarchy is always at risk.
        """

    welcome_message = await generate_ai_response(welcome_prompt, user_id)
    
    await message.reply_text(welcome_message, parse_mode="Markdown")

@app.on_message(filters.command("status") | filters.regex(f"^{DEMONIC_SYMBOLS['pentagram']}status{DEMONIC_SYMBOLS['pentagram']}$"))
async def status_command(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if user:
        global_souls = await db.get_global_souls()
        status_prompt = f"""
        Generate a terrifying status update for *{user['name']}*, a {user['race']} in Lord AASF's infernal legion.
        Current unholy statistics:
        - Rank: {user['rank']}
        - Souls Harvested: {user['souls_collected']}
        - Cursed Souls: {user['cursed_souls']}
        - Global Soul Harvest Progress: {global_souls}/{SOULS_GOAL}

        Describe their current form and the horrific transformations they've undergone.
        Hint at the even more monstrous forms they could attain by harvesting more souls.
        Remind them of the consequences of falling behind in the soul harvest.
        Make it clear that their very existence is a testament to Lord AASF's dark power.
        """
        status_text = await generate_ai_response(status_prompt, user_id)
        await message.reply_text(status_text, parse_mode="Markdown")
    else:
        await message.reply_text(await generate_ai_response("Generate a message for a pathetic mortal who hasn't yet pledged their soul to Lord AASF. Make it clear that their continued existence outside the legion is an affront to the forces of darkness.", user_id), parse_mode="Markdown")

@app.on_message(filters.command("harvest") | filters.regex(f"^{DEMONIC_SYMBOLS['skull']}harvest{DEMONIC_SYMBOLS['skull']}$"))
async def harvest_souls_command(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if user:
        referrals = await db.get_user_referrals(user_id)
        souls_collected = len(referrals)
        
        if souls_collected == 0:
            failure_prompt = f"""
            Generate a message of extreme disappointment and threat for *{user['name']}* who has failed to harvest any souls.
            Remind them of the agonies that await those who fail to meet Lord AASF's expectations.
            Suggest horrific ways they can corrupt more mortals and drag their souls into the abyss.
            Emphasize that their own soul may be forfeit if they don't improve their performance immediately.
            """
            response = await generate_ai_response(failure_prompt, user_id)
            await message.reply_text(response, parse_mode="Markdown")
            return
        
        await db.increment_user_stats(user_id, {"souls_collected": souls_collected})
        await db.update_global_souls(souls_collected)
        
        new_rank = await get_rank(user['souls_collected'] + souls_collected)
        if new_rank['name'] != user['rank']:
            await db.update_user(user_id, {"rank": new_rank['name']})
            rank_up_prompt = f"""
            Generate a message of dark exultation for *{user['name']}* who has ascended to the rank of *{new_rank['name']}*.
            They've harvested {souls_collected} fresh souls for the legion.
            Describe in gruesome detail the transformation they undergo as they rise in rank.
            Detail the new, horrific powers they've gained and the increased expectations that come with their ascension.
            Remind them that while they've pleased Lord AASF for now, the hunger for souls is eternal.
            """
            response = await generate_ai_response(rank_up_prompt, user_id)
        else:
            harvest_prompt = f"""
            Generate a message of cruel satisfaction for *{user['name']}* who has harvested {souls_collected} souls.
            Describe the agonized screams of the newly damned as their essence is added to Lord AASF's power.
            Emphasize how this harvest has strengthened both {user['name']} and the infernal legion.
            Encourage them to continue their dark work, hinting at the unspeakable rewards that await the most prolific soul harvesters.
            """
            response = await generate_ai_response(harvest_prompt, user_id)
        
        await message.reply_text(response, parse_mode="Markdown")
        
        # Notify AASF
        aasf_notify_prompt = f"""
        Generate a formal report for Lord AASF regarding *{user['name']}'s* soul harvest.
        Souls collected: {souls_collected}
        New rank: {new_rank['name']}
        Total souls: {user['souls_collected'] + souls_collected}

        Make it clear and concise, yet maintain an air of dread and malevolence befitting the Demon King's status.
        """
        aasf_response = await generate_ai_response(aasf_notify_prompt)
        await app.send_message(AASF_ID, aasf_response, parse_mode="Markdown")
    else:
        await message.reply_text(await generate_ai_response("Generate a message of utter contempt for a mortal who dares to attempt soul harvesting without first pledging themselves to Lord AASF's unholy cause.", user_id), parse_mode="Markdown")

@app.on_message(filters.command("hierarchy") | filters.regex(f"^{DEMONIC_SYMBOLS['demon']}hierarchy{DEMONIC_SYMBOLS['demon']}$"))
async def hellish_hierarchy_command(client, message):
    top_collectors = await db.get_leaderboard(10)
    global_souls = await db.get_global_souls()
    
    hierarchy_prompt = f"""
    Generate a terrifying description of the Hellish Hierarchy, showcasing the top 10 soul collectors in Lord AASF's infernal legion.
    
    Leaderboard:
    {', '.join([f'{i+1}. {user["name"]} - {user["souls_collected"]} souls' for i, user in enumerate(top_collectors)])}
    
    Total Souls Claimed for Lord AASF: {global_souls}/{SOULS_GOAL}
    
    Describe each rank in the hierarchy, from the lowliest imp to the most terrifying archfiends.
    Detail the horrific transformations and unholy powers granted at each level.
    Emphasize the constant struggle for power and the fate of those who fall behind.
    Make it clear that while these are the current leaders, their positions are always at risk.
    Conclude with a reminder of Lord AASF's ultimate goal and the apocalyptic consequences of reaching the soul quota.
    """
    leaderboard_text = await generate_ai_response(hierarchy_prompt)
    
    await message.reply_text(leaderboard_text, parse_mode="Markdown")

@app.on_message(filters.command("ritual") | filters.regex(f"^{DEMONIC_SYMBOLS['star']}ritual{DEMONIC_SYMBOLS['star']}$"))
async def dark_ritual_command(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if user:
        now = datetime.utcnow()
        time_since_last_ritual = now - user['last_ritual']
        
        if time_since_last_ritual < timedelta(hours=24):
            time_left = timedelta(hours=24) - time_since_last_ritual
            cooldown_prompt = f"""
            Generate a message of dark foreboding for *{user['name']}* who attempted to perform a dark ritual too soon.
            They must wait {time_left.seconds // 3600} hours and {(time_left.seconds % 3600) // 60} minutes before the stars align again.
            Describe the catastrophic consequences of rushing an unholy ritual.
            Suggest ominous ways they can prepare for their next attempt.
            """
            response = await generate_ai_response(cooldown_prompt, user_id)
            await message.reply_text(response, parse_mode="Markdown")
            return
        
        ritual_power = random.randint(1, 10)
        souls_gained = ritual_power * 5
        
        await db.increment_user_stats(user_id, {"souls_collected": souls_gained})
        await db.update_user(user_id, {"last_ritual": now})
        await db.update_global_souls(souls_gained)
        
        ritual_prompt = f"""
        Generate a blood-curdling description of the dark ritual performed by *{user['name']}*.
        Ritual power level: {ritual_power}
        Souls gained: {souls_gained}

        Detail the eldritch preparations, the chanting of forbidden words, and the sacrifice required.
        Describe the horrific transformation {user['name']} undergoes during the ritual.
        Explain how the ritual has strengthened their connection to the infernal realms.
        Emphasize the price they've paid for this power and the even greater sacrifices required for future rituals.
        Conclude with a reminder that each ritual brings Lord AASF's ultimate victory closer to fruition.
        """
        response = await generate_ai_response(ritual_prompt, user_id)
        await message.reply_text(response, parse_mode="Markdown")
        
        # Notify AASF
        aasf_notify_prompt = f"""
        Generate a formal report for Lord AASF about the dark ritual performed by *{user['name']}*.
        Ritual power: {ritual_power}
        Souls gained: {souls_gained}
        Total souls: {user['souls_collected'] + souls_gained}

        Make it clear and concise, yet maintain an air of dread and malevolence befitting the Demon King's status.
        """
        aasf_response = await generate_ai_response(aasf_notify_prompt)
        await app.send_message(AASF_ID, aasf_response, parse_mode="Markdown")
    else:
        await message.reply_text(await generate_ai_response("Generate a message of utter contempt for a mortal who dares to attempt a dark ritual without first pledging themselves to Lord AASF's unholy cause.", user_id), parse_mode="Markdown")

@app.on_message(filters.command("curse") | filters.regex(f"^{DEMONIC_SYMBOLS['cross']}curse{DEMONIC_SYMBOLS['cross']}$"))
async def curse_command(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if user:
        if user['cursed_souls'] < 10:
            insufficient_prompt = f"""
            Generate a message of seething disappointment for *{user['name']}* who lacks the power to cast a curse.
            They have only {user['cursed_souls']} cursed souls but need at least 10.
            Describe the pathetic state of their current abilities.
            Suggest horrific ways they can corrupt more souls to gain the required power.
            Remind them of the consequences of remaining weak in Lord AASF's legion.
            """
            response = await generate_ai_response(insufficient_prompt, user_id)
            await message.reply_text(response, parse_mode="Markdown")
            return
        
        curse_power = random.randint(1, 5)
        cursed_souls_used = curse_power * 2
        
        await db.increment_user_stats(user_id, {"cursed_souls": -cursed_souls_used})
        
        curse_prompt = f"""
        Generate a bone-chilling description of the curse cast by *{user['name']}*.
        Curse power level: {curse_power}
        Cursed souls consumed: {cursed_souls_used}

        Detail the intricate process of weaving the curse, including forbidden incantations and blasphemous symbols.
        Describe the horrific effects of the curse on its victims, lasting for {curse_power} days.
        Explain how the curse strengthens Lord AASF's hold on the mortal realm.
        Emphasize the dark satisfaction {user['name']} feels as they unleash suffering upon their enemies.
        Conclude with a reminder that the power to curse comes at a great cost, and they must continue to prove their worth to maintain this privilege.
        """
        response = await generate_ai_response(curse_prompt, user_id)
        await message.reply_text(response, parse_mode="Markdown")
        
        # Notify AASF
        aasf_notify_prompt = f"""
        Generate a formal report for Lord AASF about the curse cast by *{user['name']}*.
        Curse power: {curse_power}
        Cursed souls used: {cursed_souls_used}
        Remaining cursed souls: {user['cursed_souls'] - cursed_souls_used}

        Make it clear and concise, yet maintain an air of dread and malevolence befitting the Demon King's status.
        """
        aasf_response = await generate_ai_response(aasf_notify_prompt)
        await app.send_message(AASF_ID, aasf_response, parse_mode="Markdown")
    else:
        await message.reply_text(await generate_ai_response("Generate a message of utter contempt for a mortal who dares to attempt casting a curse without first pledging themselves to Lord AASF's unholy cause.", user_id), parse_mode="Markdown")

@app.on_message(filters.command("summon_aasf") | filters.regex(f"^{DEMONIC_SYMBOLS['goat']}summon_aasf{DEMONIC_SYMBOLS['goat']}$"))
async def summon_aasf_command(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if user:
        summon_prompt = f"""
        Generate a message describing *{user['name']}'s* attempt to summon Lord AASF for an audience.
        Detail the elaborate and gruesome ritual they perform to catch the Dark Lord's attention.
        Explain that their message will be relayed to Lord AASF, who may choose to respond if he deems it worthy.
        Warn them of the dire consequences of wasting the Demon King's time with trivial matters.
        """
        response = await generate_ai_response(summon_prompt, user_id)
        await message.reply_text(response, parse_mode="Markdown")
        
        # Notify AASF
        aasf_notify_prompt = f"""
        Generate a formal notification for Lord AASF about *{user['name']}'s* attempt to summon him.
        Include their current rank, souls collected, and any notable achievements.
        Suggest that Lord AASF may wish to respond to this minion, should he find their request intriguing.
        """
        aasf_response = await generate_ai_response(aasf_notify_prompt)
        
        # Create inline keyboard for AASF to respond
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Respond to Minion", callback_data=f"respond_to_minion:{user_id}")]
        ])
        
        await app.send_message(AASF_ID, aasf_response, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.reply_text(await generate_ai_response("Generate a message of utter contempt for a mortal who dares to attempt summoning Lord AASF without first pledging their soul to his unholy cause.", user_id), parse_mode="Markdown")

@app.on_callback_query(filters.regex("^respond_to_minion:"))
async def respond_to_minion_callback(client, callback_query):
    if callback_query.from_user.id != AASF_ID:
        await callback_query.answer("You dare impersonate the Dark Lord?", show_alert=True)
        return

    minion_id = int(callback_query.data.split(":")[1])
    minion = await db.get_user(minion_id)

    if minion:
        await callback_query.message.reply_text(f"Enter your message for {minion['name']}:")
        # Set up a conversation handler to capture AASF's response
        app.conversation_handler = {
            "waiting_for_aasf_response": True,
            "minion_id": minion_id
        }
    else:
        await callback_query.answer("The summoner's soul has been lost to the void.", show_alert=True)

@app.on_message(filters.user(AASF_ID) & filters.private)
async def handle_aasf_response(client, message):
    if hasattr(app, 'conversation_handler') and app.conversation_handler.get("waiting_for_aasf_response"):
        minion_id = app.conversation_handler["minion_id"]
        minion = await db.get_user(minion_id)
        
        if minion:
            aasf_message_prompt = f"""
            Lord AASF has deigned to respond to *{minion['name']}'s* summons. 
            Generate an appropriately terrifying introduction to Lord AASF's message.
            The message from Lord AASF is as follows:

            {message.text}

            Embellish and enhance Lord AASF's message with additional demonic flair and intimidating language.
            Conclude with a reminder of the honor bestowed upon {minion['name']} by receiving a direct communication from the Dark Lord.
            """
            enhanced_message = await generate_ai_response(aasf_message_prompt)
            await app.send_message(minion_id, enhanced_message, parse_mode="Markdown")
            await message.reply_text(f"Your message has been delivered to {minion['name']} with appropriate demonic embellishments.")
        else:
            await message.reply_text("The minion's soul has been lost to the void.")
        
        # Reset the conversation handler
        app.conversation_handler = {}
    else:
        # Handle other messages from AASF here
        pass

@app.on_message(filters.reply & filters.text)
async def handle_minion_reply(client, message):
    if message.reply_to_message.from_user.id == app.me.id:
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        
        if user:
            reply_prompt = f"""
            *{user['name']}* has replied to Lord AASF's message with the following:

            {message.text}

            Generate a demonic and sinister version of this reply, enhancing it with unholy imagery and dark undertones.
            Ensure the core message remains intact while making it sound like it's coming from a devoted servant of the Dark Lord.
            """
            enhanced_reply = await generate_ai_response(reply_prompt, user_id)
            
            # Forward the enhanced reply to AASF
            await app.send_message(AASF_ID, f"Reply from {user['name']}:\n\n{enhanced_reply}", parse_mode="Markdown")
            
            await message.reply_text("Your message has been conveyed to the Dark Lord with appropriate demonic enhancements.")
        else:
            await message.reply_text(await generate_ai_response("Generate a message of utter contempt for a mortal who dares to reply to Lord AASF without first pledging their soul to his unholy cause.", user_id), parse_mode="Markdown")

@app.on_message(filters.text & ~filters.command())
async def handle_general_message(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if user:
        response_prompt = f"""
        *{user['name']}*, a {user['rank']} in Lord AASF's infernal legion, has sent the following message:

        {message.text}

        Generate a sinister and demonic response that addresses their message while reminding them of their place in the hellish hierarchy.
        Incorporate references to their current rank, soul count, and any recent achievements or failures.
        Encourage them to continue their unholy work and spread Lord AASF's influence.
        """
        response = await generate_ai_response(response_prompt, user_id)
        await message.reply_text(response, parse_mode="Markdown")
    else:
        await message.reply_text(await generate_ai_response("Generate a message of utter contempt for a mortal who dares to speak without first pledging their soul to Lord AASF's unholy cause.", user_id), parse_mode="Markdown")

# Administration commands for Lord AASF (user_id: 3911)
@app.on_message(filters.command("admin_stats") & filters.user(AASF_ID))
async def admin_stats_command(client, message):
    total_users = await db.get_total_users()
    global_souls = await db.get_global_souls()
    top_collectors = await db.get_leaderboard(5)
    
    stats_prompt = f"""
    Generate an administrative statistics report for Lord AASF, the Demon King.
    
    Infernal Legion Statistics:
    - Total Minions: {total_users}
    - Total Souls Harvested: {global_souls}
    - Soul Goal Progress: {global_souls}/{SOULS_GOAL}
    
    Top 5 Soul Harvesters:
    {', '.join([f'{i+1}. {user["name"]} - {user["souls_collected"]} souls' for i, user in enumerate(top_collectors)])}
    
    Provide a detailed analysis of the legion's performance, highlighting areas of strength and identifying weaknesses that need to be addressed.
    Suggest strategies for increasing soul collection and expanding the legion's influence.
    Conclude with a reminder of the approaching apocalypse and the steps needed to hasten its arrival.
    
    Make it formal, evil, and befitting of the Demon King's status.
    """
    stats_text = await generate_ai_response(stats_prompt)
    await message.reply_text(stats_text, parse_mode="Markdown")

@app.on_message(filters.command("broadcast") & filters.user(AASF_ID))
async def broadcast_command(client, message):
    broadcast_message = message.text.split(None, 1)[1]
    all_users = await db.get_all_users()
    successful_sends = 0
    failed_sends = 0
    
    for user in all_users:
        try:
            await app.send_message(user['user_id'], broadcast_message, parse_mode="Markdown")
            successful_sends += 1
        except Exception as e:
            failed_sends += 1
            print(f"Failed to send message to user {user['user_id']}: {e}")
    
    report_prompt = f"""
    Generate a broadcast report for Lord AASF, the Demon King.
    
    Broadcast Results:
    - Successfully sent: {successful_sends}
    - Failed to send: {failed_sends}
    
    Provide a brief analysis of the broadcast's reach and impact.
    Suggest improvements for future broadcasts to ensure maximum influence over the legion.
    Conclude with a reminder of the power of Lord AASF's words and the terror they instill in his minions.
    
    Make it formal, evil, and befitting of the Demon King's status.
    """
    report_text = await generate_ai_response(report_prompt)
    await message.reply_text(report_text, parse_mode="Markdown")

@app.on_message(filters.command("set_soul_goal") & filters.user(AASF_ID))
async def set_soul_goal_command(client, message):
    try:
        new_goal = int(message.text.split()[1])
        await db.update_soul_goal(new_goal)
        update_prompt = f"""
        Generate a message confirming the update of the soul harvest goal to {new_goal:,}.
        Describe the cosmic significance of this new target.
        Explain how reaching this goal will bring about a new era of darkness and suffering.
        Emphasize the increased expectations placed upon every member of the infernal legion.
        Conclude with a bone-chilling prophecy of the apocalypse that will unfold once the goal is reached.
        
        Make it formal, evil, and befitting of the Demon King's status.
        """
        update_text = await generate_ai_response(update_prompt)
        await message.reply_text(update_text, parse_mode="Markdown")
    except (ValueError, IndexError):
        await message.reply_text("Invalid input. Use format: `/set_soul_goal [number]`")

@app.on_message(filters.command("bless_minion") & filters.user(AASF_ID))
async def bless_minion_command(client, message):
    try:
        user_id = int(message.text.split()[1])
        souls_to_add = int(message.text.split()[2])
        user = await db.get_user(user_id)
        
        if user:
            await db.increment_user_stats(user_id, {"souls_collected": souls_to_add})
            await db.update_global_souls(souls_to_add)
            
            bless_prompt = f"""
            Generate a message for Lord AASF confirming the dark blessing bestowed upon *{user['name']}* with {souls_to_add} souls.
            Describe the unholy power flowing into the minion and the transformations they undergo.
            Explain how this blessing strengthens the entire infernal legion.
            Emphasize that this favor comes with heightened expectations and the price of failure is even greater.
            
            Make it formal, evil, and befitting of the Demon King's status.
            """
            bless_text = await generate_ai_response(bless_prompt)
            await message.reply_text(bless_text, parse_mode="Markdown")
            
            minion_prompt = f"""
            Generate a message for *{user['name']}* informing them of Lord AASF's dark blessing of {souls_to_add} souls.
            Describe the rush of unholy power coursing through their being.
            Detail the horrific transformations they undergo as a result of this blessing.
            Emphasize their increased responsibilities and the terrible consequences of disappointing Lord AASF.
            Conclude with a reminder of their eternal servitude and the glory of the infernal legion.
            
            Make it reverent, grateful, and deeply intimidating.
            """
            minion_text = await generate_ai_response(minion_prompt)
            await app.send_message(user_id, minion_text, parse_mode="Markdown")
        else:
            await message.reply_text("The specified soul is not found in the infernal database. They may have escaped their eternal torment... for now.")
    except (ValueError, IndexError):
        await message.reply_text("Invalid input. Use format: `/bless_minion [user_id] [souls_to_add]`")

@app.on_message(filters.command("curse_minion") & filters.user(AASF_ID))
async def curse_minion_command(client, message):
    try:
        user_id = int(message.text.split()[1])
        souls_to_remove = int(message.text.split()[2])
        user = await db.get_user(user_id)
        
        if user:
            if user['souls_collected'] < souls_to_remove:
                souls_to_remove = user['souls_collected']
            
            await db.increment_user_stats(user_id, {"souls_collected": -souls_to_remove})
            await db.update_global_souls(-souls_to_remove)
            
            curse_prompt = f"""
            Generate a message for Lord AASF confirming the terrible curse inflicted upon *{user['name']}*, stripping them of {souls_to_remove} souls.
            Describe the agonizing process of soul extraction and the weakening of the minion.
            Explain how this punishment serves as a warning to all who would disappoint the Demon King.
            Emphasize that the minion's very existence now hangs by a thread, dependent on their ability to redeem themselves.
            
            Make it formal, evil, and befitting of the Demon King's status.
            """
            curse_text = await generate_ai_response(curse_prompt)
            await message.reply_text(curse_text, parse_mode="Markdown")
            
            minion_prompt = f"""
            Generate a message for *{user['name']}* informing them of Lord AASF's terrible curse, stripping them of {souls_to_remove} souls.
            Describe the excruciating pain of having their harvested souls torn from their being.
            Detail the degradation of their form and the loss of their unholy powers.
            Emphasize their precarious position in the infernal hierarchy and the monumental task of regaining Lord AASF's favor.
            Conclude with a vivid description of the eternal torments that await them should they fail to redeem themselves.
            
            Make it terrifying, remorseful, and deeply intimidating.
            """
            minion_text = await generate_ai_response(minion_prompt)
            await app.send_message(user_id, minion_text, parse_mode="Markdown")
        else:
            await message.reply_text("The specified soul is not found in the infernal database. They may have escaped their eternal torment... for now.")
    except (ValueError, IndexError):
        await message.reply_text("Invalid input. Use format: `/curse_minion [user_id] [souls_to_remove]`")

@app.on_message(filters.command("message_minion") & filters.user(AASF_ID))
async def message_minion_command(client, message):
    try:
        user_id = int(message.text.split()[1])
        aasf_message = " ".join(message.text.split()[2:])
        user = await db.get_user(user_id)
        
        if user:
            aasf_message_prompt = f"""
            Lord AASF has deigned to send a message to *{user['name']}*. 
            Generate an appropriately terrifying introduction to Lord AASF's message.
            The message from Lord AASF is as follows:

            {aasf_message}

            Embellish and enhance Lord AASF's message with additional demonic flair and intimidating language.
            Conclude with a reminder of the honor bestowed upon {user['name']} by receiving a direct communication from the Dark Lord.
            """
            enhanced_message = await generate_ai_response(aasf_message_prompt)
            await app.send_message(user_id, enhanced_message, parse_mode="Markdown")
            await message.reply_text(f"Your message has been delivered to {user['name']} with appropriate demonic embellishments.")
        else:
            await message.reply_text("The specified soul is not found in the infernal database. They may have escaped their eternal torment... for now.")
    except (ValueError, IndexError):
        await message.reply_text("Invalid input. Use format: `/message_minion [user_id] [your message]`")

@app.on_message(filters.command("sh") & filters.user(DEVS))
async def sh_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("`Give A Command To Run...`")
        return
    
    code = message.text.split(None, 1)[1]
    x = run(code)
    
    ai_prompt = f"""
    Generate a demonic response for the shell command execution:
    Command: {code}
    Output: {x}
    
    Make it sound like the infernal machines of Hell are processing the command.
    """
    response = await generate_ai_response(ai_prompt)
    
    await message.reply_text(response, parse_mode="Markdown")

@app.on_message(filters.command("eval") & filters.user(DEVS))
async def eval_command(client, message):
    status_message = await message.reply_text("Channeling the dark forces of code evaluation...")
    
    if len(message.command) < 2:
        await status_message.edit("Foolish mortal, provide a command to execute!")
        return
    
    cmd = message.text.split(None, 1)[1]
    
    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message
    
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    evaluation = exc or stderr or stdout or "The void remains silent..."
    
    ai_prompt = f"""
    Generate a demonic response for the code evaluation:
    Command: {cmd}
    Output: {evaluation}
    
    Describe the process as if dark magic is being used to interpret and execute the code.
    """
    response = await generate_ai_response(ai_prompt)
    
    if len(response) > 4096:
        with io.BytesIO(str.encode(response)) as out_file:
            out_file.name = "demonic_eval.text"
            await reply_to_.reply_document(
                document=out_file, caption=cmd, disable_notification=True
            )
    else:
        await reply_to_.reply_text(response, parse_mode="Markdown")
    
    await status_message.delete()

async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {str(e)}\n"

@app.on_message(filters.command("broadcast") & filters.user(DEVS))
async def broadcast_command(client, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to broadcast the dark word of Lord AASF!")
        return
    
    exmsg = await message.reply_text("Commencing the unholy broadcast...")
    all_chats = await db.get_all_chats()
    all_users = await db.get_all_users()
    done_chats = 0
    done_users = 0
    failed_chats = 0
    failed_users = 0
    
    for chat in all_chats:
        try:
            status, _ = await send_msg(chat['chat_id'], message.reply_to_message)
            if status == 200:
                done_chats += 1
            else:
                failed_chats += 1
            await asyncio.sleep(0.1)
        except Exception:
            failed_chats += 1
    
    for user in all_users:
        try:
            status, _ = await send_msg(user['user_id'], message.reply_to_message)
            if status == 200:
                done_users += 1
            else:
                failed_users += 1
            await asyncio.sleep(0.1)
        except Exception:
            failed_users += 1
    
    ai_prompt = f"""
    Generate a demonic report on the broadcast results:
    - Successfully sent to {done_chats} chats and {done_users} users
    - Failed to send to {failed_chats} chats and {failed_users} users
    
    Make it sound like a report on soul harvesting and corruption spreading across realms.
    """
    response = await generate_ai_response(ai_prompt)
    
    await exmsg.edit_text(response, parse_mode="Markdown")

async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)

async def check_and_update_soul_goal():
    while True:
        # Get the current soul goal from the database
        current_goal = await db.get_soul_goal()
        
        # If the goal is not set, initialize it (this should not happen if initialized correctly)
        if current_goal == 0:
            await db.update_soul_goal(666666)  # Set to default if not set
        
        await asyncio.sleep(3600)  # Check every hour

async def send_apocalyptic_message():
    all_users = await db.get_all_users()
    apocalypse_prompt = f"""
    Generate an earth-shattering, apocalyptic message announcing that the soul goal of {SOULS_GOAL:,} has been reached.
    Describe in vivid, terrifying detail:
    - The shattering of the veil between the mortal realm and the infernal planes
    - The horrific transformation of the world as demons pour forth
    - Lord AASF's ascension to godhood and his reign over the new hell on earth
    - The fate of those who served him well and the eternal torment awaiting those who failed him
    - The birth of a new, darker universe under Lord AASF's rule
    
    Encourage continued soul harvesting, explaining how it will further empower Lord AASF and elevate his most loyal servants.
    Warn of the unimaginable horrors that await those who resist the new order.
    Conclude with a bone-chilling proclamation of Lord AASF's ultimate victory and the dawn of an age of eternal darkness.
    
    Make it extremely evil, utterly terrifying, and befitting of Lord AASF's ultimate triumph.
    """
    apocalypse_message = await generate_ai_response(apocalypse_prompt)
    
    for user in all_users:
        try:
            await app.send_message(user['user_id'], apocalypse_message, parse_mode="Markdown")
        except Exception as e:
            print(f"Failed to send message to user {user['user_id']}: {e}")
    
    # Update the soul goal
    SOULS_GOAL = await db.get_soul_goal()
    new_goal = SOULS_GOAL * 2
    await db.update_soul_goal(new_goal)

async def main():
    await app.start()
    print(f"{DEMONIC_SYMBOLS['fire']} The gates of hell have been thrown wide. Lord AASF's unholy bot awakens... {DEMONIC_SYMBOLS['fire']}")
    
    asyncio.create_task(check_and_update_soul_goal())
    
    await idle()
    
if __name__ == "__main__":
    app.run(main())
