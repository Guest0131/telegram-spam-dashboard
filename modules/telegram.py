from re import split
from telethon import TelegramClient, sync, functions, types
import configparser as cp, subprocess, sys, tempfile, time, psutil
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
        
    def create_on_db(self):
        """
        Register on db
        """
        # Load config 
        config = cp.ConfigParser()
        config.read('config.ini')

        # Create connection
        client = MongoClient(config['MONGO']['host'], int(config['MONGO']['port']))
        db = client['tg']['accounts']

        if db.find_one({'api_id' : self.api_id, 'api_hash' : self.api_hash}) == None:
            subprocess.Popen([sys.executable, 'modules/create_on_db_tg.py', str(self.api_id), self.api_hash, self.session_file])
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

    def stop(self, login):
        """
        Stop spam script

        Args:
            text ([string]): Admin login
        """
        cmd = [sys.executable, 'modules/telegram_script.py', str(self.api_id), self.api_hash, self.session_file, login]
        for process in psutil.process_iter():
            try:
                if process.cmdline() == cmd:
                    print('Process found. Terminating it.')
                    process.terminate()
                    break
            except:
                pass

    def update_count(self):
        """
        Update count. Increment field `count_message` once
        """
        # Load config 
        config = cp.ConfigParser()
        config.read('config.ini')

        # Create connection
        client = MongoClient(config['MONGO']['host'], int(config['MONGO']['port']))
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
        client = MongoClient(config['MONGO']['host'], int(config['MONGO']['port']))
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
        client = MongoClient(config['MONGO']['host'], int(config['MONGO']['port']))
        db = client['tg']['accounts']

        query_resp = db.find_one({
            'api_id' : self.api_id,
            'api_hash': self.api_hash
        })

        client.close()
        return int(query_resp['pid']) if query_resp is not None and 'pid' in query_resp else None
        
    @staticmethod
    def get_bots_data():
        #TODO: Нужно чекать на бан аккаунта
        """
        Get list data about bots

        Returns:
            [type]: [description]
        """
        # Load config 
        config = cp.ConfigParser()
        config.read('config.ini')

        # Create connection
        client = MongoClient(config['MONGO']['host'], int(config['MONGO']['port']))
        db = client['tg']['accounts']

        return list(db.find({}))


    def check_username(self, username):
        """
        Check username

        Args:
            username ([string]): username
        """

        process = subprocess.Popen(
            [sys.executable, 'modules/telegram_check_username.py', str(self.api_id), self.api_hash, self.session_file, username],
            stdout=subprocess.PIPE
            )

        last_line = ""
        while True:
            time.sleep(1)
            line = process.stdout.readline()
            if not line:
                break
            try:
                last_line += line.decode()
            except:
                pass
        return last_line.split()[0] == 'true' if len(last_line.split()) > 0 else False

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
        subprocess.Popen(
                [
                    sys.executable, 'modules/telegram_update_profile.py', str(self.api_id), self.api_hash, self.session_file, 
                    info['first_name'], info['last_name'], info['about'], info['username'], info['photo']
                ]
            )

        