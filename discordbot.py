import discord
from discord import app_commands, Object
import re
import os
import random
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

@client.event
async def on_guild_join(guild):
    print("new-server-join:" + guild.name + "," + str(guild.id))

@client.event
async def on_app_command_completion(interaction: discord.Interaction,command):
    if interaction.user.bot:
        return
    print(command.name + "が" + interaction.guild.name + "(" + str(interaction.guild.id) + ")で" + interaction.user.name + "(" + str(interaction.user.id) + ")により実行")

class Parter(discord.ui.View):
    @discord.ui.button(label='参加', style=discord.ButtonStyle.green)
    async def callbacksubmit(self, interaction: discord.Interaction, button: discord.ui.Button):
        text = interaction.message.content
        if "<@" + str(interaction.user.id) + ">" not in interaction.message.content:
            text += "<@" + str(interaction.user.id) + ">"
        else:
            text = text.replace("<@" + str(interaction.user.id) + ">","")
        await interaction.response.edit_message(content=text,view=self)
    @discord.ui.button(label='GO!', style=discord.ButtonStyle.red)
    async def callbackstart(self, interaction: discord.Interaction, button: discord.ui.Button):
        users = re.findall(r'<@\d+>',interaction.message.content)
        if len(users) == 0:
            await interaction.channel.send(content="対象者がいません",delete_after=2)
        else:
            text = ""
            for i,user in enumerate(users):
                text += str(i+1) + " :" + user + "\n"
            self.children[0].disabled = True
            self.children[1].disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.channel.send(content=text)

@tree.command(description="順番を決めます")
async def order(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    await interaction.response.send_message(content="対象者:",view=Parter())

client.run(os.environ["TOKEN"],log_level=logging.ERROR)