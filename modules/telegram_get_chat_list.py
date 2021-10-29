from telethon import TelegramClient
from telegram import Telegram

import sys, python_socks

api_id, api_hash, session_file = int(sys.argv[1]), sys.argv[2], sys.argv[3]


# Create bot
tg = Telegram(api_id, api_hash, session_file)
proxy = tg.get_socks()


if proxy['login'] != ''  and proxy['password'] != '':
    client = TelegramClient(session_file, api_id, api_hash, proxy={
            'proxy_type': 'socks5',
            'addr': proxy['ip'],
            'port': proxy['port'],
            'username': proxy['login'],
            'password': proxy['password'],
            'rdns': True   
        })
else:
    client = TelegramClient(session_file, api_id, api_hash, proxy=("socks5", proxy['ip'], proxy['port']))

client.start()

chats = ['Link\tID\tTitle']
for dialog in client.iter_dialogs():
    if dialog.is_channel:
        chats.append('tg.me/' + str(dialog.entity.username) + '\t' + str(dialog.entity.id) + '\t' + str(dialog.entity.title))


with open('statistics/chats_data_{}.txt'.format(api_id), 'w', encoding='cp1251') as f:
    f.write(('\n'.join(chats)).encode('ascii', errors='ignore').decode())