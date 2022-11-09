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

@client.event
async def on_guild_join(guild):
    print("new-server-join:" + guild.name + "," + str(guild.id))

@client.event
async def on_app_command_completion(interaction: discord.Interaction,command):
    if interaction.user.bot:
        return
    print(command.name + "が" + interaction.guild.name + "(" + str(interaction.guild.id) + ")で" + interaction.user.name + "(" + str(interaction.user.id) + ")により実行")

@tree.command(description="1〜100のランダムな整数を1つ出します")
async def random(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    await interaction.response.send_message(rand.randrange(100)+1)

@tree.command(description="任意の数ダイスを振ります。?D?の形でオプションを入力してください")
async def randdice(interaction: discord.Interaction,roll:str = "1D6"):
    if interaction.user.bot:
        return
    dice = re.fullmatch("\d+(d|D)\d+",roll)
    if(dice == None):
        await interaction.response.send_message("?D?の形式で入力してください")
        return
    else:
        digits = re.findall("\d+",roll)
        result = 0
        if 0 < int(digits[0]) <= 100 and 0 < int(digits[1]) <= 1000:
            for i in range(int(digits[0])):
                result += rand.randrange(int(digits[1])) + 1
        else:
            await interaction.response.send_message("ダイスの数は100以下、出目は1000以下に設定してください。")
            return
        await interaction.response.send_message(result)


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
            rand.shuffle(users)
            text = ""
            for i,user in enumerate(users):
                text += str(i+1) + " :" + user + "\n"
            self.children[0].disabled = True
            self.children[1].disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.channel.send(content=text)

@tree.command(description="ランダムに順番を決めます")
async def randorder(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    await interaction.response.send_message(content="対象者:",view=Parter())

client.run(os.environ["TOKEN"],log_level=logging.ERROR)