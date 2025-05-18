import discord
import os
from dotenv import load_dotenv

load_dotenv()

discord_bot_token = os.getenv('discord_bot_token')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    # if the message has the playlist command
    # we can query the database and get current songs
    # on the chosen playlist
    # if message.content.startswith('$get_playlist'):
    #     await message.channel.send()

client.run(discord_bot_token)
