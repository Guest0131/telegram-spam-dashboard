from telethon.sync import TelegramClient
from telethon import functions
from pymongo import MongoClient

import sys, time, configparser as cp

api_id, api_hash, session_file, chats_file, output_file = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
log = {
    'ok' : [],
    'error' : []
}

with TelegramClient(session_file, api_id, api_hash) as client:
    with open(chats_file, 'r') as f:
        data = f.read().splitlines()

    for chat in data:
        try:
            result = client(functions.channels.JoinChannelRequest(
                channel=chat[1:]
            ))
            log['ok'].append(chat[1:])
        except:
            log['error'].append(chat[1:])
        time.sleep(1)

with open(output_file, 'w') as f:

    # Load config 
    config = cp.ConfigParser()
    config.read('config.ini')

    # Create connection
    client = MongoClient("mongodb://{login}:{password}@{host}:{port}".format(
                login=config['MONGO']['login'],
                password=config['MONGO']['password'],
                host=config['MONGO']['host'],
                port=config['MONGO']['port']
                ))
    db = client['tg']['accounts']
    db.update_one(
        { 'api_id' : api_id, 'api_hash' : api_hash },
        {
            '$inc' : { 'group_count' : len(log['ok']) }
        }
    )
    f.write(
        '==========Success==========\n'+'\n'.join(log['ok']) + 
        '\n==========Bad==========\n'+'\n'.join(log['error'])
        )