from telethon import TelegramClient, connection
from pymongo import MongoClient

import sys, configparser as cp, time, python_socks as ps


api_id, api_hash, phone = int(sys.argv[1]), sys.argv[2], sys.argv[3]
ip, port, login, password =  sys.argv[4], int(sys.argv[5]), sys.argv[6], sys.argv[7]

session_file = f'sessions/{api_id}_{api_hash}.session'

if login != ''  and password != '':
    clientTg = TelegramClient(
        session_file, api_id, api_hash,
        proxy={
            'proxy_type': 'socks5', # (mandatory) protocol to use (see above)
            'addr': ip,      # (mandatory) proxy IP address
            'port': port,           # (mandatory) proxy port number
            'username': login,      # (optional) username if the proxy requires auth
            'password': password,      # (optional) password if the proxy requires auth
            'rdns': True            # (optional) whether to use remote or local resolve, default remote
        })
else:
    clientTg = TelegramClient(
        session_file, api_id, api_hash, 
        proxy=(ps.ProxyType.SOCKS5, ip, port))

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
