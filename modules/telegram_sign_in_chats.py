from telethon.sync import TelegramClient
from telegram import Telegram
from telethon import functions
from pymongo import MongoClient

import sys, time, configparser as cp, random, socks

api_id, api_hash, session_file, chats_file, start, end = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6])

tg = Telegram(api_id, api_hash, session_file)
tg.update_status('group')
proxy = tg.get_socks()


if proxy['login'] != ''  and proxy['password'] != '':
    client = TelegramClient(session_file, api_id, api_hash, proxy=("socks5", proxy['ip'], proxy['port'], proxy['login'], proxy['password']))
else:
    client = TelegramClient(session_file, api_id, api_hash, proxy=("socks5", proxy['ip'], proxy['port']))

client.connect()

with open(chats_file, 'r') as f:
    data = f.read().splitlines()
    random.shuffle(data)
    
for chat in data:
    try:
        channelInfo = client.get_entity(chat[1:])
        result = client(functions.channels.JoinChannelRequest(
            channelInfo
        ))
        print(channelInfo.username)
        
        tg.inc_group_count()
    except:
        pass
    time.sleep(random.randint(start, end))



tg.update_status('not_work')