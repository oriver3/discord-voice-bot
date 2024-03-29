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

def text_to_speech(text:str, is_bot:bool=False) -> str:
    try:
        now = datetime.datetime.now()
        now_str = now.strftime('%Y%m%d-%H%M%S')
        if is_bot:
            voice_name = 'ja-JP-Standard-A'
            postfix_list = ['']
            fname_text = './' + work_dir + '/bot-text-' + now_str + '.txt'
            fname_voice = './' + work_dir + '/bot-speech-' + now_str + '.mp3'
        else:
            voice_name = 'ja-JP-Standard-B'
            postfix_list = ['にゃ', 'でござる', 'どすぇ', 'ずら', 'だす', 'でげす', 'そす']
            fname_text = './' + work_dir + '/text-' + now_str + '.txt'
            fname_voice = './' + work_dir + '/speech-' + now_str + '.mp3'
        text_mod = url_patter.sub(r'\1 ', text)
        text_mod = text_mod + random.choice(postfix_list)
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text_mod)
        voice = texttospeech.VoiceSelectionParams(
            # language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            language_code="ja-JP",
            # ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, # NEUTRAL
            name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.25
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        with open(fname_text, 'w') as out:
            out.write(text)
        with open(fname_voice, 'wb') as out:
            out.write(response.audio_content)
        return fname_voice
    except Exception as e:
        print(datetime.datetime.now())
        print(e)
        return None

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました ' + str(datetime.datetime.now()))

# メッセージ受信時に動作する処理
@client.event
async def on_message(message: discord.message.Message):
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
    elif message.content.startswith('オリバー'): # == 'ボット応答始め':
        response = requests.post('https://api-mebo.dev/api', json={
            'api_key': secret['miibo']['api_key'],
            'agent_id': secret['miibo']['agent'],
            'utterance': message.content[5:],
            'uid': str(message.guild.id)
        })
        if response.ok:
            res_json = response.json()
            if res_json and res_json["bestResponse"] and res_json["bestResponse"]["utterance"]:
                await message.channel.send(res_json["bestResponse"]["utterance"])
                # if message.guild.voice_client:
                #     fname = text_to_speech(res_json["bestResponse"]["utterance"], is_bot=True)
                #     if fname != None:
                #         message.guild.voice_client.play(discord.FFmpegPCMAudio(fname))
            else:
                await message.channel.send('...')
        else:
            print(f'miibo respond error with code {response.status_code}.')
            await message.channel.send('応答がない。ただの屍のようだ。')
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
