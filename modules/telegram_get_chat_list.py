from telethon import TelegramClient
from telegram import Telegram

import sys, socks

api_id, api_hash, session_file = int(sys.argv[1]), sys.argv[2], sys.argv[3]


# Create bot
tg = Telegram(api_id, api_hash, session_file)
proxy = tg.get_socks()


if proxy['login'] != ''  and proxy['password'] != '':
    client = TelegramClient(session_file, api_id, api_hash, proxy=(socks.SOCKS5, proxy['ip'], proxy['port'], proxy['login'], proxy['password']))
else:
    client = TelegramClient(session_file, api_id, api_hash, proxy=(socks.SOCKS5, proxy['ip'], proxy['port']))

client.start()

chats = ['Link\tID\tTitle']
for dialog in client.iter_dialogs():
    if dialog.is_channel:
        chats.append('tg.me/' + str(dialog.entity.username) + '\t' + str(dialog.entity.id) + '\t' + str(dialog.entity.title))


with open('statistics/chats_data_{}.txt'.format(api_id), 'w', encoding='cp1251') as f:
    f.write(('\n'.join(chats)).encode('ascii', errors='ignore').decode())