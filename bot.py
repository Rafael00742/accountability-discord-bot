import json
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext import commands, tasks


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Your existing logic (cleaned up) ---

def parse_daily_goals(message):
    lines = message.splitlines()
    expected_number = 1
    goals = []

    for line in lines:
        line = line.strip()
        if len(line) > 1 and line[0] == str(expected_number) and line[1] == ".":
            parts = line.split(".", 1)
            goal = parts[1].strip()
            goals.append(goal)
            expected_number += 1
        else:
            print("Invalid format on line:", line)
            return []

    return goals


def save_goals(username, goals):
    username = username.lower()

    try:
        with open("data.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    # 1. Grab today's date and format it as a string (e.g., "2026-06-29")
    date_string = datetime.date.today().isoformat()

    # 2. Add it to the dictionary!
    data[username] = {
        "goals": goals,
        "last_submitted": date_string,  # New line added here
        "strikes": 0
    }

    with open("data.json", "w") as file:
        json.dump(data, file, indent=2) 



# --- Discord bot setup ---

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# Create a specific time target: Midnight UTC
MIDNIGHT_UTC = datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc)

@tasks.loop(time=MIDNIGHT_UTC)
async def daily_strike_check():
    print("Running the daily midnight check...")
    # This is where our strike logic will go!

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready!")

    # Start the loop if it isn't already running
    if not daily_strike_check.is_running():
        daily_strike_check.start()



@bot.event
async def on_message(message):
    # 1. Ignore the bot's own messages
    if message.author == bot.user:
        return
    
    # 2. Check if the message is in the correct channel
    if message.channel.name == "general":  # Replace with "daily-journaling" later!
        
        # 3. NOW we check if it starts with 1.
        if message.content.startswith("1."):
            goals = parse_daily_goals(message.content)
            save_goals(message.author.name, goals)
            await message.channel.send("Got your goals! ✅")
        else:
            await message.channel.send("Submission must start with 1.")
    
    # 4. Required for discord.py to keep processing other commands
    await bot.process_commands(message)
bot.run(TOKEN) 



@tasks.loop(time=MIDNIGHT_UTC)
async def daily_strike_check():
    print("Running the daily midnight check...")
    
    # 1. Get yesterday's date as a string
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    
    # 2. Open the data file
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        return

    # 3. Fetch your channel using the ID you just copied!
    # REPLACE THE ZEROES BELOW WITH YOUR ACTUAL COPIED CHANNEL ID
    TARGET_CHANNEL_ID = 1519104632163668100  #channel ID change it to brotherhood daily-journalind channel id
    channel = bot.get_channel(TARGET_CHANNEL_ID)  

    # 4. Loop through every user
    for username, user_info in data.items():
        last_date = user_info.get("last_submitted")
        current_strikes = user_info.get("strikes", 0)
        
        # 5. Check if they missed yesterday's deadline
        if last_date != yesterday:
            new_strikes = current_strikes + 1
            user_info["strikes"] = new_strikes
            
            print(f"Oh no! {username} got a strike. Total strikes: {new_strikes}")
            
            # 6. Send the warning message to the server!
            if channel:
                await channel.send(
                    f"⚠️ Hey {username}, quick reminder: you just missed your daily journaling and got 1 strike! "
                    f"You are currently at **{new_strikes}/3 strikes**. "
                    f"If you reach 3 strikes, you will lose access to the main server channels until you fix your situation!"
                )

    # 7. Save the updated data back to the JSON file
    with open("data.json", "w") as file:
        json.dump(data, file, indent=2)   