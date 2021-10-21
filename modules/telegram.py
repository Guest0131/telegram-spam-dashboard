from re import split
from telethon import TelegramClient, sync, functions, types, tl
import configparser as cp, subprocess, sys, asyncio, time, psutil, os, random
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
        
    def create_on_db(self, owner):
        """
        Register on db

        Args:
            owner ([string]): Owner login
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
        db = client['tg']['accounts']

        if db.find_one({'api_id' : self.api_id, 'api_hash' : self.api_hash}) == None:
            subprocess.Popen([sys.executable, 'modules/create_on_db_tg.py', str(self.api_id), self.api_hash, self.session_file, owner])
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
        
        # Update count
        db.update_one({
            'api_id' : self.api_id,
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
        client = MongoClient("mongodb://{login}:{password}@{host}:{port}".format(
            login=config['MONGO']['login'],
            password=config['MONGO']['password'],
            host=config['MONGO']['host'],
            port=config['MONGO']['port']
            ))
        db = client['tg']['accounts']

        return list(db.find({'owner_login' : login}))


    async def check_username(self, username):
        """
        Check username

        Args:
            username ([string]): username
        """ 

        client = await TelegramClient(self.session_file, self.api_id, self.api_hash)
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
    def create_tmp_session(api_id, api_hash, phone):
        subprocess.Popen(
                [
                    sys.executable, 'modules/create_session.py',
                    str(api_id), api_hash, phone
                ]
            )

    @staticmethod
    def send_code_request(api_id, api_hash, code):
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
       subprocess.Popen(
                [
                    sys.executable, 'modules/telegram_sign_in_chats.py',
                    str(self.api_id), self.api_hash, self.session_file, chats_file, start, end
                ]
            )
    def inc_group_count(self):
        # Create connection
        client = self.get_mongo_client()
        db = client['tg']['accounts']

        db.update(
            {'session_file' : self.session_file},
            {'$inc': { 'group_count' : 1 } }
        )
        
    def update_status(self, status):

        # Create connection
        client = self.get_mongo_client()
        db = client['tg']['accounts']

        db.update(
            {'session_file' : self.session_file},
            {'$set': { 'status' : status } }
        )

    @staticmethod
    def get_mongo_client():
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