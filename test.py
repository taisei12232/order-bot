import discord
from discord import app_commands, Object
import re
import os
import random as rand
import asyncio
from typing import List
import logging

intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(discord.__version__)
    print("ready")
    await tree.sync()
    print("go!")
    print(tree.get_commands())
    await client.close()


client.run("MTAzOTUxNDg0NTAxNzU0Njc4Mg.GYxWBX.HzgoOTKCtot8_HqsjBZV51AwkXCFb4cyHknw3E",log_level=logging.ERROR)