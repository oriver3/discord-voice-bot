# インストールした discord.py を読み込む
import discord
import time
import datetime
import json
# import subprocess
from google.cloud import texttospeech
# import ffmpeg
import re
import random

work_dir = 'log'

# 接続に必要なオブジェクトを生成
client = discord.Client()

url_patter = re.compile(r'(http[s]?://[^/]+/)(\S+)')

def text_to_speech(text):
    try:
        text_mod = url_patter.sub(r'\1 ', text)
        postfix_list = ['にゃ', 'でござる', 'どすぇ', 'ずら', 'だす', 'でげす', 'そす']
        text_mod = text_mod + random.choice(postfix_list)
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text_mod)
        voice = texttospeech.VoiceSelectionParams(
            # language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            language_code="ja-JP",
            # ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, # NEUTRAL
            name='ja-JP-Standard-B'
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.25
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        now = datetime.datetime.now()
        now_str = now.strftime('%Y%m%d-%H%M%S')
        fname = './' + work_dir + '/text-' + now_str + '.txt'
        with open(fname, 'w') as out:
            out.write(text)
        fname = './' + work_dir + '/speech-' + now_str + '.mp3'
        with open(fname, 'wb') as out:
            out.write(response.audio_content)
        return fname
    except Exception as e:
        print(datetime.datetime.now())
        print(e)
        return None

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/neko':
        await message.channel.send('にゃーん')
        if message.author.voice is not None:
            await message.author.voice.channel.connect()
            message.guild.voice_client.play(discord.FFmpegPCMAudio('./neko.mp3'))
            time.sleep(3)
            await message.guild.voice_client.disconnect()
        return
    
    if message.content == 'ノヴァブラ最強':
        if message.author.voice is None:
            await message.channel.send('通話開始してから言って')
        else:
            await message.author.voice.channel.connect() # speech-20211003-143844.mp3
            message.guild.voice_client.play(discord.FFmpegPCMAudio('./start.mp3'))
    elif message.content == 'ノヴァブラ最弱':
        if message.guild.voice_client:
            await message.guild.voice_client.disconnect()
    # elif message.author.voice is None:
    #     print('ボイスチャンネルに接続していません。')
    elif message.guild.voice_client:
        # print('ボイスチャンネルに接続します。', message.author.voice.channel)
        # await message.author.voice.channel.connect()
        fname = text_to_speech(message.content)
        if fname != None:
            message.guild.voice_client.play(discord.FFmpegPCMAudio(fname))
        # message.guild.voice_client.play(discord.FFmpegPCMAudio('speech.mp3'))
        # time.sleep(5)
        # await message.guild.voice_client.disconnect()
        # print('ボイスチャンネルから切断しました。')

# Botの起動とDiscordサーバーへの接続
with open('./secret.json') as f:
    secret = json.load(f)

client.run(secret['discord_token'])
