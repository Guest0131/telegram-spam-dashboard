from telethon import TelegramClient
from pymongo import MongoClient

import sys, configparser as cp, time, socks


api_id, api_hash, phone = int(sys.argv[1]), sys.argv[2], sys.argv[3]
ip, port, login, password =  sys.argv[4], int(sys.argv[5]), sys.argv[6], sys.argv[7]

session_file = f'sessions/{api_id}_{api_hash}.session'

if login != ''  and password != '':
    clientTg = TelegramClient(session_file, api_id, api_hash, proxy=socks.set_proxy(socks.SOCKS5, ip, port, username=login, password=password))
else:
    clientTg = TelegramClient(session_file, api_id, api_hash, proxy=(socks.SOCKS5, ip, port))

async def main():
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
    db = client['tg']['tmp']

    

    if db.find_one({'api_id': api_id, 'api_hash': api_hash}) is None:
        db.insert_one({'api_id': api_id, 'api_hash': api_hash})
    else:
        db.delete_one({'api_id': api_id, 'api_hash': api_hash})
        time.sleep(2)
        db.insert_one({'api_id': api_id, 'api_hash': api_hash})


    await clientTg.connect()
    await clientTg.send_code_request(phone)
    
    while 'code' not in db.find_one({'api_id': api_id, 'api_hash': api_hash}):
        time.sleep(1)
    if db.find_one({'api_id': api_id, 'api_hash': api_hash})['code'] != '-1':
        await clientTg.sign_in(phone, db.find_one({'api_id': api_id, 'api_hash': api_hash})['code'])
        print(f'Create session for {phone}')
    db.delete_one({'api_id': api_id, 'api_hash': api_hash})
    client.close()


# Create session
clientTg.loop.run_until_complete(main())
