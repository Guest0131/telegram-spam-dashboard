from telethon.sync import TelegramClient
from telethon import functions
from pymongo import MongoClient

import sys, time, configparser as cp, random

api_id, api_hash, session_file, chats_file, output_file, start, end = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], int(sys.argv[6]), int(sys.argv[7])
log = {
    'ok' : [],
    'error' : []
}

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
db.update(
    {'session_file' : session_file},
    {'$set': { 'status' : 'group' } }
    )

with TelegramClient(session_file, api_id, api_hash) as client:
    with open(chats_file, 'r') as f:
        data = f.read().splitlines()

    for chat in data:
        try:
            result = client(functions.channels.JoinChannelRequest(
                channel=chat[1:]
            ))
            print(result)
            log['ok'].append(chat[1:])
                
            db.update_one(
                { 'api_id' : api_id, 'api_hash' : api_hash },
                {
                    '$inc' : { 'group_count' : 1 }
                }
            )
        except:
            log['error'].append(chat[1:])
        time.sleep(random.randint(start, end))

with open(output_file, 'w') as f:
    f.write(
        '==========Success==========\n'+'\n'.join(log['ok']) + 
        '\n==========Bad==========\n'+'\n'.join(log['error'])
        )

db.update(
    {'session_file' : session_file},
    {'$set': { 'status' : 'not_work' } }
    )