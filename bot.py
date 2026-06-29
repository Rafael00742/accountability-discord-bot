import json
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

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
    username = username.lower()  # fix the Rafael vs rafael problem

    try:
        with open("data.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    data[username] = {
        "goals": goals,
        "strikes": 0
    }

    with open("data.json", "w") as file:
        json.dump(data, file, indent=2)


# --- Discord bot setup ---

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready!")



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith("1."):
        goals = parse_daily_goals(message.content)
        save_goals(message.author.name, goals)
        await message.channel.send("Got your goals! ✅")
    else:
        await message.channel.send("Submission must start with 1.")
    
    await bot.process_commands(message)
bot.run(TOKEN)


