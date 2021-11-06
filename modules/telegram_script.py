from telethon import TelegramClient, sync, events, utils
from telethon.tl.types import Channel, User as tUser
from pymongo import MongoClient
from threading import Thread
from telegram import Telegram
from user import User

import sys, os, time, random, asyncio, python_socks, configparser as cp

api_id, api_hash, session_file, admin_login = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]


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



async def send_user_message(response, sender, text):
    time.sleep(random.randint(
        int(response['single']['start']),
        int(response['single']['end'])
    ))
    
    count_chats = 0
    for dialog in client.iter_dialogs():
        if dialog.is_channel:
            count_chats += 1
    tg.update_group_count(count_chats)
    
    await client.send_message(
        sender, 
        text
    )
    
async def send_chat_message(response, sender, text):
    time.sleep(random.randint(
            int(response['group']['start']),
            int(response['group']['end'])
        ))

    count_chats = 0
    for dialog in client.iter_dialogs():
        if dialog.is_channel:
            count_chats += 1
    tg.update_group_count(count_chats)

    await client.send_message(
        entity=sender, 
        message=text
    )
    

def beetwen_callback(type, response, sender, text, api_id, api_hash, session_file):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if type == 'group':
        loop.run_until_complete(send_chat_message(response,sender, text))
    else:
        loop.run_until_complete(send_user_message(response,sender, text))
    
    loop.close()

    
    

@client.on(events.NewMessage())
async def normal_handler(event):

    response = User.get_response(admin_login)

    
    tg.update_pid(os.getpid())
    tg.update_status('work')
    
    chat = await event.get_chat()
    
    if type(chat) == tUser:
        print(chat.username)
        sender = await event.get_input_sender()
        message_arr = response['single']['text'].split('\n')

        _thread = Thread(target=beetwen_callback, args=(
            'user', 
            response, sender, message_arr[random.randint(0, len(message_arr) - 1)], 
            api_id, api_hash, session_file))
        
        
    elif type(chat) == Channel:
        chat = await event.get_chat()
        print(chat.username)

        message_arr = response['group']['text'].split('\n')

        _thread = Thread(target=beetwen_callback, args=(
            'group', 
            response, chat.username, message_arr[random.randint(0, len(message_arr) - 1)], 
            api_id, api_hash, session_file))
    
    _thread.start()
        

client.start()
client.run_until_disconnected()