from telethon import TelegramClient, sync, functions
from telethon.tl.functions.users import GetFullUserRequest
from pymongo import MongoClient

from  telegram import Telegram

import configparser as cp, sys, time, socks



api_id, api_hash, session_file, owner = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
ip, port, login, password = sys.argv[5], int(sys.argv[6]), sys.argv[7], sys.argv[8]

# Load config 
config = cp.ConfigParser()
config.read('config.ini')

# Create connection
client = Telegram.get_mongo_client()
db = client['tg']['accounts']

if login != ''  and password != '':
    clientTg = TelegramClient(session_file, api_id, api_hash, proxy=socks.set_proxy(socks.SOCKS5, ip, port, username=login, password=password))
else:
    clientTg = TelegramClient(session_file, api_id, api_hash, proxy=(socks.SOCKS5, ip, port))

clientTg.start()

count_chats = 0
for dialog in clientTg.iter_dialogs():
    if dialog.is_channel:
        count_chats += 1

client_info = clientTg(GetFullUserRequest(id=clientTg.get_me().id))
db.insert_one({
    'api_id': api_id,
    'api_hash': api_hash,
    'session_file': session_file,
    'count_message': 0,
    'user_id' : str(client_info.user.id),
    'first_name' : str(client_info.user.first_name) if client_info.user.first_name != None else "",
    'last_name' : str(client_info.user.last_name)   if client_info.user.last_name  != None else "",
    'username' : str(client_info.user.username)     if client_info.user.username   != None else "",
    'phone' : str(client_info.user.phone)           if client_info.user.phone      != None else "",
    'about' : str(client_info.about)                if client_info.about           != None else "",
    'owner_login' : owner,
    'group_count' : count_chats,
    'proxy' : {
        'ip' : ip,
        'port' : port,
        'login' : login,
        'password' : password
    }
})