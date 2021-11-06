from re import split
from telethon import TelegramClient, sync, functions, types, tl
import configparser as cp, subprocess, sys, asyncio, time, psutil, os, random, socks
from pymongo import MongoClient


class Telegram:

    def __init__(self,api_id, api_hash, session_file):
        """
        Init

        Args:
            api_id ([id]): API_ID
            api_hash ([string]): API_HASH
            session_file ([string]): Path to session's file
        """
        self.session_file = session_file
        self.api_id = int(api_id)
        self.api_hash = api_hash
        
    def create_on_db(self, owner, ip, port, login, password):
        """
        Register on db

        Args:
            owner ([string]): Owner login
        """

        # Create connection
        client = self.get_mongo_client()
        db = client['tg']['accounts']

        if db.find_one({'api_id' : self.api_id, 'api_hash' : self.api_hash}) == None:
            subprocess.Popen([
                sys.executable, 'modules/create_on_db_tg.py', 
                str(self.api_id), self.api_hash, self.session_file, owner, 
                ip, port, login, password
                ])
        client.close()

    def run(self, login):
        """
        Run spam script

        Args:
            text ([string]): Admin login
        """

        cmd = [sys.executable, 'modules/telegram_script.py', str(self.api_id), self.api_hash, self.session_file, login]
        self.stop(login)
        subprocess.Popen(cmd)

    def stop(self, login = None):
        """
        Stop spam script

        Args:
            text ([string]): Admin login
        """
        cmd = [str(self.api_id), self.api_hash, self.session_file]
        self.update_status('not_work')
        for process in psutil.process_iter():
            try:
                if ';'.join(cmd) in ';'.join(process.cmdline()):
                    print('Process found. Terminating it.')
                    process.terminate()
            except:
                pass

        time.sleep(2)

    def update_count(self):
        """
        Update count. Increment field `count_message` once
        """
        # Create connection
        client = Telegram.get_mongo_client()
        db = client['tg']['accounts']
        
        # Update count
        db.update_one({
            'api_id' : int(self.api_id),
            'api_hash': self.api_hash
        }, {
            '$inc' : {
                'count_message' : 1
            }
        }, upsert=False)

        client.close()
    
    def update_pid(self, pid):
        """
        Update Process ID (PID)

        Args:
            pid ([int]): New PID
        """
        # Create connection
        client = Telegram.get_mongo_client()
        db = client['tg']['accounts']
        
        # Update count
        db.update_one({
            'api_id' : self.api_id,
            'api_hash': self.api_hash
        }, {
            '$set' : {
                'pid' : pid
            }
        }, upsert=False)

        client.close()

    def get_pid(self):
        """
        Get PID process

        Returns:
            [`int` or `None`]: Return `int`, if pid is available else `None`
        """
        # Create connection
        client = Telegram.get_mongo_client()
        db = client['tg']['accounts']

        query_resp = db.find_one({
            'api_id' : self.api_id,
            'api_hash': self.api_hash
        })

        client.close()
        return int(query_resp['pid']) if query_resp is not None and 'pid' in query_resp else None
        
    @staticmethod
    def get_bots_data(login):
        #TODO: Нужно чекать на бан аккаунта
        """
        Get list data about bots

        Args:
            login ([string]): Owner login
        Returns:
            [type]: [description]
        """
        # Load config 
        config = cp.ConfigParser()
        config.read('config.ini')

        # Create connection
        client = Telegram.get_mongo_client()
        db = client['tg']['accounts']

        return list(db.find({'owner_login' : login}))


    async def check_username(self, username):
        """
        Check username

        Args:
            username ([string]): username
        """ 
        proxy = self.get_socks()
        
        if proxy['login'] != ''  and proxy['password'] != '':
            client = TelegramClient(self.session_file, self.api_id, self.api_hash, proxy={
            'proxy_type': 'socks5',
            'addr': proxy['ip'],
            'port': proxy['port'],
            'username': proxy['login'],
            'password': proxy['password'],
            'rdns': True   
        })
        else:
            client = TelegramClient(self.session_file, self.api_id, self.api_hash, proxy=("socks5", proxy['ip'], proxy['port']))

        result = client(await functions.account.CheckUsernameRequest(
            username=sys.argv[4]
        ))

        return 'true' if bool(result) else 'false'

    def update_info(self, info):
        """
        Update UserProfile info

        Args:
            info ([dict]):  Data needed update 
                            {
                                'first_name': [string],
                                'last_name': [string]
                                'about': [string]
                                'username': [string]
                                'photo': [string]
                            }
        """
        subprocess.run(
                [
                    sys.executable, 'modules/telegram_update_profile.py', str(self.api_id), self.api_hash, self.session_file, 
                    info['first_name'], info['last_name'], info['about'], info['username'], info['photo']
                ]
            )

    @staticmethod
    def create_tmp_session(api_id, api_hash, phone, ip, port, login, password):
        subprocess.Popen(
                [
                    sys.executable, 'modules/create_session.py',
                    str(api_id), api_hash, phone, ip, str(port), login, password
                ]
            )

    @staticmethod
    def send_code_request(api_id , api_hash, code):
        """
        Send code from `@Telegram`

        Args:
            api_id (int | string): api_id
            api_hash (string): api_has
            code (string): Code
        """

        # Load config 
     
        # Create connection
        client = Telegram.get_mongo_client()
        db = client['tg']['tmp']
        
        db.update_one(
            {'api_id' : int(api_id), 'api_hash': api_hash},
            {'$set' : {
                'code' : code
            }})

        client.close()


    def drop_me(self):
        """
        Drop user from db
        """

        self.stop()

        # Create connection
        client = self.get_mongo_client()
        db = client['tg']['accounts']

        db.delete_one({'api_id' : int(self.api_id), 'api_hash': self.api_hash})
        os.remove(self.session_file)
        
        client.close()
        

    def get_chats_list(self):
        """
        Get chats list path

        Returns:
            [string]: Path to data file
        """
        try:
            os.remove('statistics/chats_data_{}.txt'.format(self.api_id))
            print('Remove old chat list')
        except:
            pass

        subprocess.Popen(
                [
                    sys.executable, 'modules/telegram_get_chat_list.py',
                    str(self.api_id), self.api_hash, self.session_file
                ]
            )
        
        time.sleep(2)

        
        return 'statistics/chats_data_{}.txt'.format(self.api_id)


    def load_chat_list(self, chats_file, start, end):
        """
        Load chat list in accout

        Args:
            chats_file (string): Path to chat list file
            start (string): Random start time
            end (string): Random end time
        """
        subprocess.Popen(
                [
                    sys.executable, 'modules/telegram_sign_in_chats.py',
                    str(self.api_id), self.api_hash, self.session_file, chats_file, start, end
                ]
            )


    def update_group_count(self, new_count = 0):
        """
        Update count groups

        Args:
            new_count (int, optional): New count value for group_count. Defaults to 0.
        """
        # Create connection
        client = self.get_mongo_client()
        db = client['tg']['accounts']

        db.update(
            {'session_file' : self.session_file},
            {'$set': { 'group_count' : new_count } }
        )
        
    def update_status(self, status):
        """
        Update status account

        Args:
            status (string): new status
        """
        # Create connection
        client = self.get_mongo_client()
        db = client['tg']['accounts']

        db.update(
            {'session_file' : self.session_file},
            {'$set': { 'status' : status } }
        )

    @staticmethod
    def get_mongo_client():
        """
        Get mongo client instance

        Returns:
            [MongoClient]: client mongo instance
        """
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
        
        return client


    def get_socks(self):
        """
        Get poxy params

        Returns:
            [None | dict]: Proxy configuration
        """
        client = self.get_mongo_client()
        db = client['tg']['accounts']

        response = db.find_one({ 'session_file' : self.session_file })
        if response == None or 'proxy' not in response:
            return None

        return response['proxy']