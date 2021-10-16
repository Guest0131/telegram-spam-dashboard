from telethon import TelegramClient, sync, functions
from telethon.tl.functions.users import GetFullUserRequest

import configparser as cp, sys, time,random
from pymongo import MongoClient
from pprint import pprint


api_id, api_hash, session_file, owner = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]

# Load config 
config = cp.ConfigParser()
config.read('config.ini')

# Create connection
client = client = MongoClient(config['MONGO']['connection'])
db = client['tg']['accounts']

clientTg = TelegramClient(session_file, api_id, api_hash)
clientTg.start()


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
    'owner_login' : owner
})