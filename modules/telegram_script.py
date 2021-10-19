from telethon import TelegramClient, sync, events, utils
from telethon.tl.types import Channel
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

    tg = Telegram(api_id, api_hash, session_file)
    tg.update_pid(os.getpid())
    tg.update_status('work')
    

    try:
        chat = await event.get_chat()
        
        username = chat.username
        if type(chat) != Channel:
            raise Exception("Not channel")

        time.sleep(random.randint(
            int(response['group']['start']),
            int(response['group']['end'])
        ))
        message_arr = response['group']['text'].split('\n')
        await client.send_message(entity=chat.username, message=message_arr[random.randint(0, len(message_arr) - 1)])
    except:
        sender = await event.get_input_sender()
        time.sleep(random.randint(
            int(response['single']['start']),
            int(response['single']['end'])
        ))

        message_arr = response['single']['text'].split('\n')
        await client.send_message(sender, message_arr[random.randint(0, len(message_arr) - 1)])

    tg.update_count()
        

client.start()
client.run_until_disconnected()