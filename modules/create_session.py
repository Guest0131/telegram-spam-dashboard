from telethon import TelegramClient
from pymongo import MongoClient

import sys, configparser as cp, time


api_id, api_hash, phone = int(sys.argv[1]), sys.argv[2], sys.argv[3]
session_file = f'sessions/{api_id}_{api_hash}.session'
clientTg = TelegramClient(session_file, api_id, api_hash)

async def main():
    await clientTg.connect()
    await clientTg.send_code_request(phone)

    # Load config 
    config = cp.ConfigParser()
    config.read('config.ini')

    # Create connection
    client = client = MongoClient(config['MONGO']['connection'])
    db = client['tg']['tmp']

    if db.find_one({'api_id': api_id, 'api_hash': api_hash}) is None:
        db.insert_one({'api_id': api_id, 'api_hash': api_hash})
    
    while 'code' not in db.find_one({'api_id': api_id, 'api_hash': api_hash}):
        time.sleep(1)
    
    await clientTg.sign_in(phone, db.find_one({'api_id': api_id, 'api_hash': api_hash})['code'])
    print(f'Create session for {phone}')
    db.delete_one({'api_id': api_id, 'api_hash': api_hash})
    client.close()


# Create session
clientTg.loop.run_until_complete(main())
