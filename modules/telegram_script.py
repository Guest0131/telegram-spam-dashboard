from telethon import TelegramClient, sync, events
from pymongo import MongoClient

from telegram import Telegram
from user import User

import sys, os, time, random

api_id, api_hash, session_file, admin_login = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]


# Create bot
client = TelegramClient(session_file, api_id, api_hash)

@client.on(events.NewMessage())
async def normal_handler(event):

    response = User.get_response(admin_login)

    time.sleep(random.randint(
        int(response['start']),
        int(response['end'])
    ))

    tg = Telegram(api_id, api_hash, session_file)
    tg.update_pid(os.getpid())
    tg.update_count()

    sender = await event.get_input_sender()
    await client.send_message(sender, response['text'])
        

client.start()
client.run_until_disconnected()