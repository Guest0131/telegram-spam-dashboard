from telethon import TelegramClient, sync, functions
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from telegram import Telegram
from pymongo import MongoClient
import sys, configparser as cp, socks

tg = Telegram( int(sys.argv[1]), sys.argv[2], sys.argv[3])

proxy = tg.get_socks()

if proxy['login'] != ''  and proxy['password'] != '':
    proxyArr=("socks5", proxy['ip'], proxy['port'], proxy['login'], proxy['password'])
else:
    proxyArr=("socks5", proxy['ip'], proxy['port'])

with sync.TelegramClient(sys.argv[3], int(sys.argv[1]), sys.argv[2], proxy=proxyArr) as client:
    try:
        # Update first_name, last_name, about
        client(UpdateProfileRequest(
            first_name=sys.argv[4],
            last_name=sys.argv[5],
            about=sys.argv[6]
        ))
    except:
        pass


    # Update username
    try:
        client(functions.account.UpdateUsernameRequest(
            username=sys.argv[7]
        ))
    except:
        pass

    if sys.argv[8] != 'None':
        try:
            client(functions.photos.UploadProfilePhotoRequest(
                file=client.upload_file(sys.argv[8])
            ))
        except:
            pass
    
    count_chats = 0
    for dialog in client.iter_dialogs():
        if dialog.is_channel:
            count_chats += 1


    client_info = client(GetFullUserRequest(id=client.get_me().id))

    # Load config 
    config = cp.ConfigParser()
    config.read('config.ini')

    # Create connection
    client = Telegram.get_mongo_client()
    db = client['tg']['accounts']

    db.update_one(
        { 'api_id' : int(sys.argv[1]), 'api_hash': sys.argv[2] }, 
        { "$set" : 
        {
            
            'first_name' : str(client_info.user.first_name) if client_info.user.first_name == None else client_info.user.first_name,
            'last_name' : str(client_info.user.last_name)   if client_info.user.last_name  == None else client_info.user.last_name,
            'username' : str(client_info.user.username      if client_info.user.username   == None else client_info.user.username),
            'about' : str(client_info.about)                if client_info.about           == None else client_info.about,
            'group_count' : count_chats
        }
    })