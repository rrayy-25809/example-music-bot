import discord
from discord.ext import commands
import discord.ext.commands.bot
from discord.ui import Button, View
from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio
import json
import os
import sys


with open('bot.json', 'r', encoding='utf-8') as f:
    bot_data = json.load(f)

prefix = bot_data["prefix"]
bot = commands.Bot(command_prefix = prefix, intents=discord.Intents.all()) #명령어 접두사 설정
token = bot_data["token"]
if token=="":
    print("토큰 값을 찾을 수 없습니다")
    sys.exit("다시 시도해 주세요")

user_list = []
music_list = []
music_now:int = 0
msg = None

@bot.event
async def on_ready():
    print(bot.user.name + "가 현재 온라인 입니다!")
    activity = prefix + "명령어" #~하는 중 ex)<명령어 하는 중
    if bot_data["status"] =="online":
        status = discord.Status.online
    elif  bot_data["status"] == "offline":
        status = discord.Status.offline
    elif bot_data["status"] == "dnd":
        status=discord.Status.dnd
    elif bot_data["status"] =="idle":
        status=discord.Status.idle
    else:
        print("prefix 값을 다시 설정해 주세요")
        sys.exit("다시 시도해 주세요")
    await bot.change_presence(status=status, activity=discord.Game(activity))


@bot.command()
async def 들어와(ctx):#들어와 명령어를 입력했을 때
    global vc
    vc = await ctx.message.author.voice.channel.connect() #명령어 친 사람이 있는 채널 들어가기
    print(vc)#디버그용 프린트 함수



@bot.command()
async def 나가(ctx):#나가 명령어를 입력했을 때
    await vc.disconnect() #채널 나가기

@bot.command()
async def 재생(ctx, *, url):
    global music_now
    global msg
    YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True', 'writesubtitles':'writesubtitles','writethumbnail':'writethumbnail'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not vc.is_playing():
        music_now = music_now+1
        user_list.append(ctx.message.author)
        music_list.append(url)
    else:
        await ctx.send("노래를 대기열에 추가하였습니다! (다음 곡) 버튼으로 들으실 수 있어요!")
        user_list.append(ctx.message.author)
        music_list.append(url)

@bot.command()
async def 리스트재생(ctx, *, url):
    global music_now
    global msg
    YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'False', 'writesubtitles':'writesubtitles','writethumbnail':'writethumbnail'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not vc.is_playing():
        music_now = music_now+1
        user_list.append(ctx.message.author)
        music_list.append(url)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)    
        global jemok
        global yeongsang
        global subtitle
        global thumnail
        global msg
        yeongsang = url
        jemok = info["title"]
        URL = info['formats'][0]['url']
        #subtitle = info['subtitles']
        thumnail =info["thumbnail"]
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: print('done', e))
        embed = discord.Embed(title="노래 재생", description="현재 " + jemok + "을(를) 재생하고 있습니다.", color=0x24d0ff)
        embed.add_field(name="노래의 URL", value=url, inline=True)
        embed.add_field(name="사용자", value=ctx.message.author, inline=True)
        embed.set_thumbnail(url=thumnail)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("❤")
        await msg.add_reaction("💔")
        await msg.add_reaction("⏮")
        await msg.add_reaction("⏹")
        await msg.add_reaction("▶")
        await msg.add_reaction("⏭")
    else:
        await ctx.send("노래를 대기열에 추가하였습니다! (다음 곡) 버튼으로 들으실 수 있어요!")
        user_list.append(ctx.message.author)
        music_list.append(url)

@bot.command()
async def 플레이어(ctx):
    global msg
    embed = discord.Embed(title="노래 플레이어", description="현재 " + jemok + "을(를) 재생하고 있습니다.", color=0x24d0ff)
    embed.add_field(name="노래의 URL", value=music_list[music_now], inline=True)
    embed.add_field(name="사용자", value=user_list[music_now], inline=True)
    msg = await ctx.send(embed=embed)
 
    await msg.add_reaction("❤")
    await msg.add_reaction("💔")
    await msg.add_reaction("⏮")
    await msg.add_reaction("⏹")
    await msg.add_reaction("▶")
    await msg.add_reaction("⏭")

@bot.command()
async def 목록재생(ctx,*,what):
    global music_now
    global music_now
    vc.pause()
    YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True', 'writesubtitles':'writesubtitles'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(music_list[what], download=False)
    yeongsang = music_list[what]
    jemok = info["title"]
    URL = info['formats'][0]['url']
    #subtitle = info['subtitles']
    thumnail =info["thumbnail"]
    vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: print('done', e))
    embed = discord.Embed(title="노래 재생", description="현재 " + jemok + "을(를) 재생하고 있습니다.", color=0x24d0ff)
    embed.add_field(name="노래의 URL", value=yeongsang, inline=True)
    embed.add_field(name="사용자", value=user_list[what], inline=True)
    embed.set_thumbnail(url=thumnail)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("❤")
    await msg.add_reaction("💔")
    await msg.add_reaction("⏮")
    await msg.add_reaction("⏹")
    await msg.add_reaction("▶")
    await msg.add_reaction("⏭")

@bot.event
async def on_reaction_add(reaction, user):
    global music_now
    global jemok
    global yeongsang
    global subtitle
    global thumnail
    global msg
    if user.bot == 1: #봇이면 패스
        return None
    if reaction.message != msg:
        return None
    if str(reaction.emoji) == "❤":#미완
        await reaction.message.channel.send(user.name + "님이 노래에 좋아요를 표시하였습니다! 감사해요!")
        bot.get_guild(816942882078326796).get_channel(836065501943169024).send(user.name + "님이 노래를 추천하셨어요!" + yeongsang +"입니다!")
    if str(reaction.emoji) == "💔":#미완
        await reaction.message.channel.send(user.name + "님이 노래에 싫어요를 표시했습니다")
    if str(reaction.emoji) == "⏮":
        await reaction.message.channel.send(user.name + "님이 이전 곡을 재생하였습니다.")
        vc.pause()
        YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True', 'writesubtitles':'writesubtitles'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        music_now = music_now - 1
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(music_list[music_now], download=False)
        yeongsang = music_list[music_now]
        jemok = info["title"]
        URL = info['formats'][0]['url']
        #subtitle = info['subtitles']
        thumnail =info["thumbnail"]
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: print('done', e))
        embed = discord.Embed(title="노래 재생", description="현재 " + jemok + "을(를) 재생하고 있습니다.", color=0x24d0ff)
        embed.add_field(name="노래의 URL", value=music_list[music_now], inline=True)
        embed.add_field(name="사용자", value=user_list[music_now], inline=True)
        embed.set_thumbnail(url=thumnail)
        msg = await reaction.message.channel.send(embed=embed)
        await msg.add_reaction("❤")
        await msg.add_reaction("💔")
        await msg.add_reaction("⏮")
        await msg.add_reaction("⏹")
        await msg.add_reaction("▶")
        await msg.add_reaction("⏭")

    if str(reaction.emoji) == "⏹":
        await reaction.message.channel.send(user.name + "님이 노래를 일시정지 하셨습니다.")
        vc.pause()
    if str(reaction.emoji) == "⏭":
        await reaction.message.channel.send(user.name + "님이 다음 곡을 재생하셨습니다.")
        vc.pause()
        YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True', 'writesubtitles':'writesubtitles'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        music_now = music_now + 1
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(music_list[music_now], download=False)
        yeongsang = music_list[music_now]
        jemok = info["title"]
        URL = info['formats'][0]['url']
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: print('done', e))
        embed = discord.Embed(title="노래 재생", description="현재 " + jemok + "을(를) 재생하고 있습니다.", color=0x24d0ff)
        embed.add_field(name="노래의 URL", value=music_list[music_now], inline=True)
        embed.add_field(name="사용자", value=user_list[music_now], inline=True)
        msg = await reaction.message.channel.send(embed=embed)
        await msg.add_reaction("❤")
        await msg.add_reaction("💔")
        await msg.add_reaction("⏮")
        await msg.add_reaction("⏹")
        await msg.add_reaction("▶")
        await msg.add_reaction("⏭")

    if str(reaction.emoji) == "🖕":
        await reaction.message.channel.send("🖕" + user.name + "님이 노래에 중지를 날렸네요🖕")
    if str(reaction.emoji) == "▶":
        await reaction.message.channel.send(user.name + "님이 노래를 다시재생 하셨습니다")
        vc.resume()



@bot.command()
async def 일시정지(ctx):
    if vc.is_playing():
        vc.pause()
        await ctx.send(embed=discord.Embed(title="일시정지", description= jemok + "가 일시정지 되었습니다", color=0x24d0ff))
    else:
        await ctx.send("이미 노래가 재생되지 않았습니다")


@bot.command()
async def 다시재생(ctx):
    try:
        vc.resume()
    except:
        await ctx.send("이미 노래가 재생되지 않았습니다")
    else:
        await ctx.send(embed=discord.Embed(title="다시재생", description= jemok + "을(를) 다시 재생했습니다", color=0x24d0ff))


@bot.command()
async def 음악도움말(ctx):
    embed = discord.Embed(title="도움말", description="주제: 음악", color=0x24d0ff)
    embed.add_field(name="들어와", value="바이트가 음성채팅방에 들어옵니다!", inline=True)
    embed.add_field(name="나가", value="바이트가 음성채팅방에서 나갑니다!", inline=True)
    embed.add_field(name="재생", value="재생 뒤에 유튜브 주소를 넣으면 음악을 재생합니다!", inline=True)
    embed.add_field(name="일시정지", value="노래를 일시정지 합니다!", inline=True)
    embed.add_field(name="다시재생", value="일시정지 상태인 노래를 다시 재생합니다!", inline=True)
    embed.add_field(name="플레이어", value="음악 플레이어를 생성합니다!", inline=True)
    embed.add_field(name="목록", value="대기열 목록을 불러옵니다!", inline=True)
    embed.add_field(name="목록초기화", value="대기열 목록을 초기화 합니다!", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def 목록(ctx):
    global music_Text
    global user_Text
    music_Text = ""
    user_Text = ""
    for u in range(len(user_list)):
        user_Text = user_Text + "\n" + str(u + 1) + ". " + str(user_list[u])
    for l in range(len(music_list)):
        music_Text = music_Text + "\n" + str(l + 1) + ". " + str(music_list[l])
    embed = discord.Embed(title="현재목록",  color=0x24d0ff)
    embed.add_field(name="노래의 URL들", value=music_Text, inline=True)
    embed.add_field(name="사용자들", value=user_Text, inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def 목록초기화(ctx):
    user_list.clear()
    music_list.clear()
    await ctx.send(embed = discord.Embed(title="목록초기화", description="목록 리스트를 초기화 하였습니다.", color=0x24d0ff))

bot.run(token)