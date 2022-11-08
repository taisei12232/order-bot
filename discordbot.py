import discord
from discord import app_commands, Object
import re
import os
import random
import json
import shutil
import asyncio
import time
import datetime
from pydub import AudioSegment
from typing import List
import logging

with open('monsters.json', 'r') as f:
    monsters = json.load(f)
    
monsters["alldata"] = []
for gen in monsters["gens"]:
    monsters["alldata"].extend(monsters["gens"][gen])

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

@tree.command(description="ポケモンクイズを開始します")
async def pstart(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    if interaction.user.voice is None:
        await interaction.response.send_message(content="コマンドの実行者がボイスチャットに接続していません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    await interaction.response.send_message(content="お題を生成中...")
    try:
        await interaction.user.voice.channel.connect(self_deaf=True)
    except discord.ClientException as e:
        pass
    except Exception as e:
        print(e)
    monster = random.choice(monsters["alldata"])
    with open(str(interaction.user.guild.id)+"p.json","w")as f:
        json.dump(monster,f,ensure_ascii=False)
    path = "./voice/" + monster["no"] + ".wav"
    print("server-name:" + interaction.user.guild.name + " server-id:" + str(interaction.user.guild.id) + " command:p " + monster["name"])
    await interaction.edit_original_response(content="Start!")

@tree.command(description="イントロを再生します")
async def pplay(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    if interaction.user.voice is None:
        await interaction.response.send_message(content="コマンドの実行者がボイスチャットに接続していません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    try:
        await interaction.user.voice.channel.connect(self_deaf=True)
    except discord.ClientException as e:
        pass
    except Exception as e:
        print(e)
    if os.path.isfile(str(interaction.user.guild.id)+"p.json") == False:
        await interaction.response.send_message(content="お題が生成されていません。先に`/pstart`を実行してください。")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    with open(str(interaction.user.guild.id)+"p.json","r") as f:
        monster = json.load(f)
    try:
        interaction.user.guild.voice_client.play(discord.FFmpegPCMAudio("./voice/" + monster["no"] + ".wav", options = "-loglevel error"))
    except discord.ClientException as e:
        await interaction.response.send_message("すでに鳴き声が再生中です")
        await asyncio.sleep(1)
        await interaction.delete_original_response()
        return
    except Exception as e:
        print(e)
        await interaction.response.send_message("ｴﾗｰﾃﾞｽ!")
        await asyncio.sleep(1)
        await interaction.delete_original_response()
        return
    await interaction.response.send_message(content="再生中...")
    await asyncio.sleep(1)
    await interaction.edit_original_response(content="再生しました")
    await asyncio.sleep(10)
    await interaction.delete_original_response()

@tree.command(description="イントロクイズの答え合わせをします 何度でも挑戦できます")
async def pcheck(interaction: discord.Interaction,answer:str):
    if interaction.user.voice is None:
        await interaction.response.send_message(content="コマンドの実行者がボイスチャットに接続していません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    if os.path.isfile(str(interaction.user.guild.id)+"p.json") == False:
        await interaction.response.send_message(content="問題が生成されていません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    await asyncio.sleep(0.1)
    with open(str(interaction.user.guild.id)+"p.json","r") as f:
        answermons = json.load(f)
        if(answer == answermons["name"]):
            await interaction.response.send_message("正解！ " + answer)
            monster = random.choice(monsters["alldata"])
            with open(str(interaction.user.guild.id)+"p.json","w")as f:
                json.dump(monster,f,ensure_ascii=False)
            print("server-name:" + interaction.user.guild.name + " server-id:" + str(interaction.user.guild.id) + " command:p" + monster["name"])
        else:
            await interaction.response.send_message("不正解... " + answer)

@pcheck.autocomplete('answer')
async def answer_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    answers = monsters["answers"]
    return [
        app_commands.Choice(name=answer, value=answer)
        for answer in answers if current.lower() in answer.lower()
    ][:25]

@tree.command(description="イントロクイズの正解発表をします")
async def pans(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message(content="コマンドの実行者がボイスチャットに接続していません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    if os.path.isfile(str(interaction.user.guild.id)+"p.json") == False:
        await interaction.response.send_message(content="解答が存在しません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    await asyncio.sleep(0.1)
    with open(str(interaction.user.guild.id)+"p.json","r") as f:
        answer = json.load(f)
        await interaction.response.send_message(content=f'{answer["name"]}')
    monster = random.choice(monsters["alldata"])
    with open(str(interaction.user.guild.id)+"p.json","w")as f:
        json.dump(monster,f,ensure_ascii=False)
    print("server-name:" + interaction.user.guild.name + " server-id:" + str(interaction.user.guild.id) + " command:intro " + monster["name"])

class Parter(discord.ui.View):
    genoptions = [
        discord.SelectOption(label='第1世代(赤緑)', value="gen1",default=True),
        discord.SelectOption(label='第2世代(金銀)', value="gen2",default=True),
        discord.SelectOption(label='第3世代(RS)', value="gen3",default=True),
        discord.SelectOption(label='第4世代(DP)', value="gen4",default=True),
        discord.SelectOption(label='第5世代(BW)', value="gen5",default=True),
        discord.SelectOption(label='第6世代(XY)', value="gen6",default=True),
        discord.SelectOption(label='第7世代(SM)', value="gen7",default=True),
        discord.SelectOption(label='第8世代(剣盾)', value="gen8",default=True)
    ]
    @discord.ui.select(placeholder='出題する範囲を選択してください', min_values=1, max_values=8, options=genoptions)
    async def callbackgen(self, interaction: discord.Interaction,select: discord.ui.Select):
        with open(str(interaction.user.guild.id)+"pm.json","r")as f:
            data = json.load(f)
        text = interaction.message.content
        s_text = text.split(":")
        selectedmonsters = []
        for gen in select.values:
            selectedmonsters.extend(monsters["gens"][gen])
        text = s_text[0] + ":" + str(min(len(selectedmonsters),data["num"])) + "\n参加者:" + s_text[2]
        for i in range(len(select.options)):
            if select.options[i].value in select.values:
                select.options[i].default = True
            else:
                select.options[i].default = False
        await interaction.response.edit_message(content=text,view=self)
    @discord.ui.button(label='参加', style=discord.ButtonStyle.green)
    async def callbacksubmit(self, interaction: discord.Interaction, button: discord.ui.Button):
        text = interaction.message.content
        if "<@" + str(interaction.user.id) + ">" not in interaction.message.content:
            text += "<@" + str(interaction.user.id) + ">"
        else:
            text = text.replace("<@" + str(interaction.user.id) + ">","")
        for option in self.children[0].options:
            if(option.default and option.value not in self.children[0].values):
                self.children[0].values.append(option.value)
        await interaction.response.edit_message(content=text,view=self)
    @discord.ui.button(label='開始', style=discord.ButtonStyle.red)
    async def callbackstart(self, interaction: discord.Interaction, button: discord.ui.Button):
        players = re.findall(r'<@\d+>',interaction.message.content)
        selectedmonsters = []
        if(len(self.children[0].values) == 0):
            for gen in monsters["gens"]:
                selectedmonsters.extend(monsters["gens"][gen])
        for gen in self.children[0].values:
            selectedmonsters.extend(monsters["gens"][gen])
        if len(players) == 0:
            await interaction.channel.send(content="誰も参加していません",delete_after=2)
        elif len(selectedmonsters) == 0:
            await interaction.channel.send(content="出題できる鳴き声がありません",delete_after=2)
        else:
            self.children[0].disabled = True
            self.children[1].disabled = True
            self.children[2].disabled = True
            await interaction.response.edit_message(view=self)
            await pmready(interaction,players,selectedmonsters)

@tree.command(description="出題数,出題範囲を指定し、鳴き声クイズを行います 回答は一人一度のみです 終了後それぞれの正答数が表示されます")
@app_commands.describe(num="問題数(1以上)")
async def pmarathon(interaction: discord.Interaction,num: int):
    if interaction.user.bot:
        return
    if interaction.user.voice is None:
        await interaction.response.send_message(content="コマンドの実行者がボイスチャットに接続していません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    try:
        await interaction.user.voice.channel.connect(self_deaf=True)
    except discord.ClientException as e:
        pass
    except Exception as e:
        print(e)
    if num < 1:
        await interaction.response.send_message(content="問題数は1以上にしてください")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    if os.path.isfile(str(interaction.user.guild.id)+"pm.wav"):
        os.remove(str(interaction.user.guild.id)+"pm.wav")
    data = {
        "monsters": random.sample(monsters["alldata"],min(len(monsters["alldata"]),num)),
        "num": num,
        "now": 1,
        "finished": True,
        "players": {},
        "standing": ""
    }
    if os.path.isfile(str(interaction.user.guild.id)+"pm.json"):
        with open(str(interaction.user.guild.id)+"pm.json","r")as f:
            olddata = json.load(f)
            data["players"] = olddata["players"]
    with open(str(interaction.user.guild.id)+"pm.json","w")as f:
        json.dump(data,f,ensure_ascii=False)
    await interaction.response.send_message(content="問題数:" + str(min(len(monsters["alldata"]),num)) + "\n参加者:",view=Parter())

async def pmready(interaction: discord.Interaction,players,selectedmonsters):
    message = await interaction.channel.send(content="準備中...")
    try:
        await interaction.user.voice.channel.connect(self_deaf=True)
    except discord.ClientException as e:
        pass
    except Exception as e:
        print(e)
    with open(str(interaction.user.guild.id)+"pm.json","r")as f:
        data = json.load(f)
    if(len(selectedmonsters) == 0):
        await message.edit(content="出題できるポケモンががいません",delete_after=5)
        return
    data["monsters"] = random.sample(selectedmonsters,min(len(selectedmonsters),data["num"]))
    data["start"] = time.time()
    data["finished"] = False
    data["num"] = len(data["monsters"])
    data["players"] = {}
    for player in players:
        data["players"][player] = {
            "correct":0,
            "wrong":0,
            "wrongs":[],
            "isAnswer":False,
            "retired":False
        }
    path = "./voice/" + data["monsters"][0]["no"] + ".wav"
    if os.path.isfile(path):
        music = AudioSegment.from_wav(path)
        music += ((5000-music.rms)+200)/1000
        music.export(str(interaction.user.guild.id)+"pm.wav", format="wav")
    else:
        await message.edit(content="ｴﾗｰﾃﾞｽ!",delete_after=5)
    print("server-name:" + interaction.user.guild.name + " server-id:" + str(interaction.user.guild.id) + " command:pm " + data["monsters"][0]["name"])
    await message.edit(content="Start!")
    await interaction.channel.send("[1/" + str(data["num"]) + "]")
    standing = await interaction.channel.send("全員の解答を待っています...\n解答:\n(0/" + str(len(data["players"])) + ")")
    data["standing"] = standing.id
    try:
        interaction.user.guild.voice_client.play(discord.FFmpegPCMAudio(str(interaction.user.guild.id)+"pm.wav", options = "-loglevel error"))
    except discord.ClientException as e:
        pass
    except Exception as e:
        print(e)
    with open(str(interaction.user.guild.id)+"pm.json","w")as f:
        json.dump(data,f,ensure_ascii=False)


@tree.command(description="マラソンクイズの鳴き声を再生します")
async def pmplay(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    if interaction.user.voice is None:
        await interaction.response.send_message(content="コマンドの実行者がボイスチャットに接続していません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    try:
        await interaction.user.voice.channel.connect(self_deaf=True)
    except discord.ClientException as e:
        pass
    except Exception as e:
        print(e)
    if os.path.isfile(str(interaction.user.guild.id)+"pm.wav") == False:
        await interaction.response.send_message(content="お題が生成されていません。先に`/pmarathon`を実行してください。")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    try:
        interaction.user.guild.voice_client.play(discord.FFmpegPCMAudio(str(interaction.user.guild.id)+"pm.wav", options = "-loglevel error"))
    except discord.ClientException as e:
        await interaction.response.send_message("すでに鳴き声が再生中です")
        await asyncio.sleep(1)
        await interaction.delete_original_response()
        return
    except Exception as e:
        print(e)
        await interaction.response.send_message("ｴﾗｰﾃﾞｽ!")
        await asyncio.sleep(1)
        await interaction.delete_original_response()
        return
    await interaction.response.send_message(content="再生中...")
    await asyncio.sleep(1)
    await interaction.edit_original_response(content="再生しました")
    await asyncio.sleep(2)
    await interaction.delete_original_response()

@tree.command(description="マラソンクイズの答え合わせをします")
async def pmcheck(interaction: discord.Interaction,answer:str):
    if interaction.user.voice is None:
        await interaction.response.send_message(content="コマンドの実行者がボイスチャットに接続していません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    if os.path.isfile(str(interaction.user.guild.id)+"pm.json") == False:
        await interaction.response.send_message(content="問題が生成されていません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    with open(str(interaction.user.guild.id)+"pm.json","r") as f:
        data = json.load(f)
    if("<@" + str(interaction.user.id) + ">" not in data["players"]):
        await interaction.response.send_message(content="あなたは参加していません",ephemeral=True)
        return
    if data["players"]["<@" + str(interaction.user.id) + ">"]["isAnswer"]:
        await interaction.response.send_message(content="解答は一回のみです",ephemeral=True)
        return
    data["players"]["<@" + str(interaction.user.id) + ">"]["isAnswer"] = True
    if(answer == data["monsters"][data["now"]-1]["name"]):
        await interaction.response.send_message(content="正解！ " + answer,ephemeral=True)
        data["players"]["<@" + str(interaction.user.id) + ">"]["correct"] += 1
    else:
        await interaction.response.send_message("不正解... " + answer + "\n正解:" + data["monsters"][data["now"]-1]["name"],ephemeral=True)
        data["players"]["<@" + str(interaction.user.id) + ">"]["wrong"] += 1
        data["players"]["<@" + str(interaction.user.id) + ">"]["wrongs"].append(data["monsters"][data["now"]-1]["name"])
    counters = []
    retires = 0
    for player in data["players"]:
        if(data["players"][player]["isAnswer"]):
            counters.append(player)
        elif data["players"][player]["retired"]:
            retires += 1
    standing = await interaction.channel.fetch_message(data["standing"])
    if(len(counters) + retires >= len(data["players"])):
        await standing.delete()
        for player in data["players"]:
            data["players"][player]["isAnswer"] = False
        data["now"] += 1
        if(data["now"] > data["num"]):
            await interaction.channel.send(content="正解:" + data["monsters"][data["now"]-2]["name"])
            data["finished"] = True
            td = datetime.timedelta(seconds=time.time() - data["start"])
            m, s = divmod(td.seconds, 60)
            h, m = divmod(m, 60)
            elapse = ""
            if(h != 0):
                elapse = str(h) + "時間"
            elapse += str(m) + "分" + str(s) + "秒"
            text = "お疲れ様でした！\n【結果】\n"
            for player in data["players"]:
                text += player + "\n     正答数:" + str(data["players"][player]["correct"]) + "/" + str(data["num"]) + "\n     正答率:" + str(data["players"][player]["correct"]/data["num"]*100)[:5] + "％\n"
            text += "かかった時間:" + elapse + "(1問あたり" + str((td / data["num"]).seconds )+ "秒)"
            await interaction.channel.send(text)
        else:
            await interaction.channel.send(content="正解:" + data["monsters"][data["now"]-2]["name"])
            path = "./voice/" + data["monsters"][data["now"]-1]["no"] + ".wav"
            if os.path.isfile(path):
                music = AudioSegment.from_wav(path)
                music += ((5000-music.rms)+200)/1000
                music.export(str(interaction.user.guild.id)+"pm.wav", format="wav")
            else:
                await interaction.channel.send("ｴﾗｰﾃﾞｽ!")
            await interaction.channel.send("[" + str(data["now"]) + "/" + str(data["num"]) + "]")
            standing = await interaction.channel.send("全員の解答を待っています...(0/" + str(len(data["players"])) + ")")
            data["standing"] = standing.id
            try:
                interaction.user.guild.voice_client.play(discord.FFmpegPCMAudio(str(interaction.user.guild.id)+"pm.wav", options = "-loglevel error"))
            except discord.ClientException as e:
                pass
            except Exception as e:
                print(e)
            print("server-name:" + interaction.user.guild.name + " server-id:" + str(interaction.user.guild.id) + " command:pm " + data["monsters"][data["now"]-1]["name"])
    else:
        counterstext = ""
        for counter in counters:
                counterstext += counter
        await standing.edit(content="全員の解答を待っています...\n解答した人:" + counterstext + "\n(" + str(len(counters)) + "/" + str(len(data["players"])) + ")")
        with open(str(interaction.user.guild.id)+"pm.json","r") as f:
            newdata = json.load(f)
        if(data != newdata):
            newdata["players"]["<@" + str(interaction.user.id) + ">"] = data["players"]["<@" + str(interaction.user.id) + ">"]
            data = newdata
        with open(str(interaction.user.guild.id)+"pm.json","w")as f:
            json.dump(data,f,ensure_ascii=False)
        newcounters = []
        for player in data["players"]:
            if(data["players"][player]["isAnswer"]):
                newcounters.append(player)
        if(counters != newcounters):
            if len(newcounters) >= len(data["players"]):
                await standing.delete()
                for player in data["players"]:
                    data["players"][player]["isAnswer"] = False
                data["now"] += 1
                if(data["now"] > data["num"]):
                    await standing.delete()
                    await interaction.channel.send(content="正解:" + data["monsters"][data["now"]-2]["name"])
                    data["finished"] = True
                    td = datetime.timedelta(seconds=time.time() - data["start"])
                    m, s = divmod(td.seconds, 60)
                    h, m = divmod(m, 60)
                    elapse = ""
                    if(h != 0):
                        elapse = str(h) + "時間"
                    elapse += str(m) + "分" + str(s) + "秒"
                    text = "お疲れ様でした！\n【結果】\n"
                    for player in data["players"]:
                        text += player + "\n     正答数:" + str(data["players"][player]["correct"]) + "/" + str(data["num"]) + "\n     正答率:" + str(data["players"][player]["correct"]/data["num"]*100)[:5] + "％\n"
                    text += "かかった時間:" + elapse + "(1問あたり" + str((td / data["num"]).seconds )+ "秒)"
                    await interaction.channel.send(text)
                else:
                    await interaction.channel.send(content="正解:" + data["monsters"][data["now"]-2]["name"])
                    path = "./voice/" + data["monsters"][data["now"]-1]["no"] + ".wav"
                    if os.path.isfile(path):
                        music = AudioSegment.from_wav(path)
                        music += ((5000-music.rms)+200)/1000
                        music.export(str(interaction.user.guild.id)+"pm.wav", format="wav")
                    await interaction.channel.send("[" + str(data["now"]) + "/" + str(data["num"]) + "]")
                    standing = await interaction.channel.send("全員の解答を待っています...(0/" + str(len(data["players"])) + ")")
                    data["standing"] = standing.id
                    try:
                        interaction.user.guild.voice_client.play(discord.FFmpegPCMAudio(str(interaction.user.guild.id)+"pm.wav", options = "-loglevel error"))
                    except discord.ClientException as e:
                        pass
                    except Exception as e:
                        print(e)
                    print("server-name:" + interaction.user.guild.name + " server-id:" + str(interaction.user.guild.id) + " command:pm " + data["monsters"][data["now"]-1]["name"])
            else:
                counterstext = ""
                for counter in newcounters:
                        counterstext += counter
            await standing.edit(content="全員の解答を待っています...\n解答した人:" + counterstext + "\n(" + str(len(newcounters)) + "/" + str(len(data["players"])) + ")")
    with open(str(interaction.user.guild.id)+"pm.json","w")as f:
            json.dump(data,f,ensure_ascii=False)


@pmcheck.autocomplete('answer')
async def answer_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    answers = monsters["answers"]
    return [
        app_commands.Choice(name=answer, value=answer)
        for answer in answers if current.lower() in answer.lower()
    ][:25]

@tree.command(description="前回のマラソンイントロクイズで間違えた問題を表示します")
async def pmwrongs(interaction: discord.Interaction):
    if os.path.isfile(str(interaction.user.guild.id)+"pm.json") == False:
        await interaction.response.send_message(content="履歴が存在しません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    with open(str(interaction.user.guild.id)+"pm.json","r") as f:
        data = json.load(f)
        if(data["finished"] == False):
            await interaction.response.send_message(content="現在マラソン中です 終了後再度お試しください")
            await asyncio.sleep(2)
            await interaction.delete_original_response()
            return
        if("<@" + str(interaction.user.id) + ">" not in data["players"]):
            await interaction.response.send_message(content="あなたは前回参加していません")
            await asyncio.sleep(2)
            await interaction.delete_original_response()
            return
        wrongtext = "<@" + str(interaction.user.id) + ">の間違えた問題:\n"
        for wrong in data["players"]["<@" + str(interaction.user.id) + ">"]["wrongs"]:
            wrongtext += wrong + "\n"
        wrongtext += "計" + str(len(data["players"]["<@" + str(interaction.user.id) + ">"]["wrongs"])) + "問"
        if len(wrongtext) < 1900:
            await interaction.response.send_message(content=wrongtext)
        else:
            with open(str(interaction.user.guild.id) + ".txt","w") as t:
                t.write(wrongtext)
            await interaction.response.send_message(file=discord.File(str(interaction.user.guild.id) + ".txt"))

@tree.command(description="あなただけマラソンクイズをリタイアします。リザルトは現時点でのものが終了後に表示されます")
async def pmretire(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    if os.path.isfile(str(interaction.user.guild.id)+"pm.json") == False:
        await interaction.response.send_message(content="現在マラソンクイズは行われていません。")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    with open(str(interaction.user.guild.id)+"pm.json","r") as f:
        data = json.load(f)
        if(data["finished"]):
            await interaction.response.send_message(content="現在マラソンクイズは行われていません。")
            await asyncio.sleep(2)
            await interaction.delete_original_response()
            return
        if("<@" + str(interaction.user.id) + ">" not in data["players"]):
            await interaction.response.send_message(content="あなたは参加していないため、実行できません。")
            await asyncio.sleep(2)
            await interaction.delete_original_response()
            return
        if data["players"]["<@" + str(interaction.user.id) + ">"]["retired"]:
            await interaction.response.send_message(content="あなたはすでにリタイアしています。")
            await asyncio.sleep(2)
            await interaction.delete_original_response()
            return
        data["players"]["<@" + str(interaction.user.id) + ">"]["retired"] = True
        counters = []
        retires = 0
        for player in data["players"]:
            if(data["players"][player]["isAnswer"]):
                counters.append(player)
            elif data["players"][player]["retired"]:
                retires += 1
        if len(counters) + retires < len(data["players"]):
            with open(str(interaction.user.guild.id)+"pm.json","w")as f:
                json.dump(data,f,ensure_ascii=False)
            counterstext = ""
            for counter in counters:
                counterstext += counter
            standing = await interaction.channel.fetch_message(data["standing"])
            await standing.edit(content="全員の解答を待っています...\n解答した人:" + counterstext + "\n(" + str(len(counters)) + "/" + str(len(data["players"])-retires) + ")")
            await interaction.response.send_message("<@" + str(interaction.user.id) + ">がリタイアしました。")
            return
        td = datetime.timedelta(seconds=time.time() - data["start"])
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        elapse = ""
        if(h != 0):
            elapse = str(h) + "時間"
        elapse += str(m) + "分" + str(s) + "秒"
        text = "リタイアしました...\n【結果】\n"
        for player in data["players"]:
            text += player + "\n     正答数:" + str(data["players"][player]["correct"]) + "/" + str(data["now"]) + "\n     正答率:" + str(data["players"][player]["correct"]/(data["now"])*100)[:5] + "％\n"
        text += "かかった時間:" + elapse + "(1問あたり" + str((td / (data["now"])).seconds )+ "秒)"
        await interaction.response.send_message(text)
        if data["players"]["<@" + str(interaction.user.id) + ">"]["isAnswer"] == False:
            data["players"]["<@" + str(interaction.user.id) + ">"]["wrong"] += 1
            data["players"]["<@" + str(interaction.user.id) + ">"]["wrongs"].append(data["monsters"][data["now"]-1]["name"])
        data["finished"] = True
        with open(str(interaction.user.guild.id)+"pm.json","w")as f:
            json.dump(data,f,ensure_ascii=False)

@tree.command(description="全員のマラソンクイズをリタイアします。現時点でのリザルトが表示されます。")
async def pmretireall(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    if os.path.isfile(str(interaction.user.guild.id)+"pm.json") == False:
        await interaction.response.send_message(content="現在マラソンクイズは行われていません。")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    with open(str(interaction.user.guild.id)+"pm.json","r") as f:
        data = json.load(f)
        if(data["finished"]):
            await interaction.response.send_message(content="現在マラソンクイズは行われていません。")
            await asyncio.sleep(2)
            await interaction.delete_original_response()
            return
        if("<@" + str(interaction.user.id) + ">" not in data["players"]):
            await interaction.response.send_message(content="あなたは参加していないため、実行できません。")
            await asyncio.sleep(2)
            await interaction.delete_original_response()
            return
        data["finished"] = True
        td = datetime.timedelta(seconds=time.time() - data["start"])
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        elapse = ""
        if(h != 0):
            elapse = str(h) + "時間"
        elapse += str(m) + "分" + str(s) + "秒"
        text = "リタイアしました...\n【結果】\n"
        for player in data["players"]:
            text += player + "\n     正答数:" + str(data["players"][player]["correct"]) + "/" + str(data["now"]) + "\n     正答率:" + str(data["players"][player]["correct"]/(data["now"])*100)[:5] + "％\n"
        text += "かかった時間:" + elapse + "(1問あたり" + str((td / (data["now"])).seconds )+ "秒)"
        await interaction.response.send_message(text)
        for player in data["players"]:
            if data["players"][player]["isAnswer"] == False:
                data["players"][player]["wrong"] += 1
                data["players"][player]["wrongs"].append(data["monsters"][data["now"]-1]["name"])
        with open(str(interaction.user.guild.id)+"pm.json","w")as f:
            json.dump(data,f,ensure_ascii=False)

@tree.command(description="マラソンクイズに途中参加します。")
async def pmjoin(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    if os.path.isfile(str(interaction.user.guild.id)+"pm.json") == False:
        await interaction.response.send_message(content="現在マラソンクイズは行われていません。")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    with open(str(interaction.user.guild.id)+"pm.json","r") as f:
        data = json.load(f)
    if(data["finished"]):
        await interaction.response.send_message(content="現在マラソンクイズは行われていません。")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    if("<@" + str(interaction.user.id) + ">" in data["players"]):
        if data["players"]["<@" + str(interaction.user.id) + ">"]["retired"]:
            await interaction.response.send_message(content="あなたはすでにリタイアしています。")
            await asyncio.sleep(2)
            await interaction.delete_original_response()
            return
        await interaction.response.send_message(content="あなたはすでに参加しています。")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    data["players"]["<@" + str(interaction.user.id) + ">"] = {
        "correct":0,
        "wrong":0,
        "wrongs":[],
        "isAnswer":False,
        "retired":False
    }
    with open(str(interaction.user.guild.id)+"pm.json","w")as f:
        json.dump(data,f,ensure_ascii=False)
    counters = []
    retires = 0
    for player in data["players"]:
        if(data["players"][player]["isAnswer"]):
            counters.append(player)
        elif data["players"][player]["retired"]:
            retires += 1
    standing = await interaction.channel.fetch_message(data["standing"])
    counterstext = ""
    for counter in counters:
            counterstext += counter
    await interaction.response.send_message("<@" + str(interaction.user.id) + ">が途中参加しました。")
    await standing.edit(content="全員の解答を待っています...\n解答した人:" + counterstext + "\n(" + str(len(counters)) + "/" + str(len(data["players"])-retires) + ")")

@tree.command(description="鳴き声を試聴します")
async def ptrial(interaction: discord.Interaction,monster: str):
    if interaction.user.bot:
        return
    if interaction.user.voice is None:
        await interaction.response.send_message(content="コマンドの実行者がボイスチャットに接続していません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    try:
        await interaction.user.voice.channel.connect(self_deaf=True)
    except discord.ClientException as e:
        pass
    except Exception as e:
        print(e)
    path = None
    for mons in monsters["alldata"]:
        if(mons["name"] == monster):
            path = "./voice/" + mons["no"] + ".wav"
    if path == None:
        await interaction.response.send_message(content="この鳴き声は再生できません")
        await asyncio.sleep(2)
        await interaction.delete_original_response()
        return
    try:
        interaction.user.guild.voice_client.play(discord.FFmpegPCMAudio(path, options = "-loglevel error"))
    except discord.ClientException as e:
        await interaction.response.send_message("すでに他の鳴き声が再生中です")
        await asyncio.sleep(1)
        await interaction.delete_original_response()
        return
    except Exception as e:
        print(e)
        await interaction.response.send_message("ｴﾗｰﾃﾞｽ!")
        await asyncio.sleep(1)
        await interaction.delete_original_response()
        return
    await interaction.response.send_message(monster + " を再生しました")
    await asyncio.sleep(5)
    await interaction.delete_original_response()

@ptrial.autocomplete('monster')
async def monster_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    monsterslist = monsters["answers"]
    return [
        app_commands.Choice(name=monster, value=monster)
        for monster in monsterslist if current.lower() in monster.lower()
    ][:25]

@tree.command(description="収録ポケモンのリストを表示します")
async def monsterlist(interaction: discord.Interaction):
    text = ""
    for gen in monsters["gens"]:
        text += "第" + gen[-1] + "世代" + "(" + str(len(monsters["gens"][gen])) + "匹):\n"
        for monster in monsters["gens"][gen]:
            if monster["no"] + ".wav" in os.listdir("./voice"):
                text += "    " + monster["name"] + "\n"
            else:
                print(monster["name"])
    text += "全" + str(len(monsters["alldata"])) + "匹"
    with open("monsterlist.txt","w") as tf:
        tf.write(text)
    await interaction.response.send_message(file=discord.File("monsterlist.txt"))

@tree.command(description="このBotをボイスチャットから切断します")
async def dc(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    await interaction.user.guild.voice_client.disconnect()
    await interaction.response.send_message(content="また遊んでね！")

@tree.command(description="Botのヘルプを表示します")
async def phelp(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    await interaction.response.send_message(content= """`/pstart`:お題を生成
`/pplay`:
    ランダムな鳴き声を再生します。
`/pcheck 解答`:
    クイズの答え合わせをします。
    解答は選択肢の中から選んでください。
    正解するまで何回でも挑戦できます。
    正解するとお題がリセットされます。
`/pans`:
    クイズの答えを表示します。
    クイズのお題がリセットされます

`/pmarathon 問題数`:
    マラソンクイズを開始します。
    受付用のコメントが送信されます。
    出題範囲(世代)を選択することができます.
    参加する人全員が参加ボタンを押し、名前が表示されたことを確認したら、開始ボタンを押してください。
    すでに参加ボタンを押して着る人が再度ボタンを押すと、参加をキャンセルできます。
    一度開始ボタンを押すと、その後参加ボタンを押しても参加者は変更できません。
    すでにマラソンクイズをプレイしている場合、このコマンドを実行するとリセットされてしまうため、ご注意ください。
    また、3分経つと接続が切れますので，その際は再度実行をお願いします。
`/pmplay`:
    マラソンクイズの鳴き声を再生します。
    ボイスチャットにいれば誰でも実行することができます。
`/pmcheck 解答`:
    マラソンクイズに解答します。
    解答は必ず選択肢の中から選んでください。
    1問につき1人1回しか解答できません。
    正誤は回答者にのみ表示されます。
    参加者全員が解答すると、次の問題に進みます。
    全ての問題が終了すると、結果が発表されます。
`/pmretire`:
    自分だけマラソンクイズをリタイアします。
    実行できるのは参加者のみです。
`/pmretireall`:
    マラソンクイズを中断します。
    実行できるのは参加者のみです。
    その時点でのリザルトが表示されます。
`/pmjoin`:
    マラソンクイズに途中参加します。
    リタイアしていた場合、再度参加はできません。
`/pmwrongs`:
    このコマンドを実行した人が前回のマラソンクイズで間違えた問題を表示します。
    他人のリザルトは表示できません。
    このコマンドはマラソンクイズ終了後に実行できます。
    `/pmarathon`の開始ボタンをクリックすると、履歴がリセットされます。

`/ptrial ポケモン名`:鳴き声を試聴します。
`/dc`:ボイスチャットから切断(お題は保持されます)
※一日に一度お題がリセットされます。その際は、再度生成コマンドを実行して下さい。""")

@tree.command(description="再生を止めます")
async def stop(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    if interaction.user.voice is None:
        await interaction.response.send_message(content="コマンドの実行者がボイスチャットに接続していません",ephemeral=True)
        return
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("stop")
        await interaction.delete_original_response()
        return
    interaction.guild.voice_client.stop()
    await interaction.response.send_message("stop")
    await interaction.delete_original_response()

@client.event
async def on_voice_state_update(member, before, after):
    if(member.guild.voice_client != None):
        if after.channel is not member.guild.voice_client.channel: #ボイスチャンネル切断時
            if member.id != client.user.id: #botではないか判定
                if member.guild.voice_client.channel is before.channel: #ユーザーとbotが同じボイスチャンネルに居たかどうか判定
                    if len(member.guild.voice_client.channel.members) == 1: #ボイスチャンネルにbotだけが残っているか判定
                        await member.guild.voice_client.disconnect()

client.run(os.environ["TOKEN"],log_level=logging.ERROR)