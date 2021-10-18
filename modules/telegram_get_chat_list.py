from telethon import TelegramClient
import sys

api_id, api_hash, session_file = int(sys.argv[1]), sys.argv[2], sys.argv[3]


# Create bot
client = TelegramClient(session_file, api_id, api_hash)
client.start()

chats = ['Link\tID\tTitle']
for dialog in client.iter_dialogs():
    if dialog.is_channel:
        chats.append('tg.me/' + dialog.entity.username + '\t' + str(dialog.entity.id) + '\t' + dialog.entity.title)


with open('statistics/chats_data_{}.txt'.format(api_id), 'w', encoding='cp1251') as f:
    f.write(('\n'.join(chats)).encode('ascii', errors='ignore').decode())