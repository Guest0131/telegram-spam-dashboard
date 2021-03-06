from pymongo import MongoClient
import hashlib, configparser as cp, sys


class User:

    def __init__(self, login=None, password=None):
        """
        Init and auth user

        Args:
            login ([string], optional): Login. Defaults to None.
            password ([string], optional): Password. Defaults to None.
        """
        
        # Check empty values
        if login == None or password == None:
            self.authenticated = False
            return

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
        db = client['tg']['users']

        # Search user in db
        resp = db.find_one({
            'login': login,
            'password': hashlib.md5(password.encode()).hexdigest() # Hashed password
        })

        self.authenticated = resp != None

    @staticmethod
    def register(login, password):
        """
        Register new user

        Args:
            login ([string]): Login
            password ([string]): Password
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
        db = client['tg']['users']

        new_user_id = db.insert_one({
            'login': login,
            'password': hashlib.md5(password.encode()).hexdigest(), # Hashed password
            'response' : {
                    'group' : {
                        'text' : 'Тут текст для группы',
                        'start': 77,
                        'end'  : 777
                    },
                    'single' : {
                        'text' : 'Тут текст для чувака',
                        'start': 0,
                        'end'  : 10
                    }
                    
                }
        })

    @staticmethod
    def get_response(login):
        """
        Get response text

        Args:
            login ([string]): Admin login

        Returns:
            [string]
        """
        # Load config 
        config = cp.ConfigParser()
        config.read('config.ini')

        # Create connection
        client = client = MongoClient("mongodb://{login}:{password}@{host}:{port}".format(
            login=config['MONGO']['login'],
            password=config['MONGO']['password'],
            host=config['MONGO']['host'],
            port=config['MONGO']['port']
            ))
        db = client['tg']['users']

        data = db.find_one({'login':login})
        client.close()
        return data['response'] if data is not None and 'response' in data else {'text': 'Обновите текст', 'start' : 0, 'end' : 10}

    @staticmethod
    def update_response(login, group_text, group_start, group_end, single_text, single_start, single_end):
        """
        Update response text

        Args:
            login ([string]): Admin login
            start ([int]): Start random timeout
            end ([int]): End random timeout
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
        db = client['tg']['users']

        db.update_one(
            { 'login':login },
            { 
                '$set' : {
                'response' : {
                    'group' : {
                        'text' : group_text,
                        'start': int(group_start),
                        'end'  : int(group_end)
                    },
                    'single' : {
                        'text' : single_text,
                        'start': int(single_start),
                        'end'  : int(single_end)
                    }
                    
                }
                }
            })
        client.close()
        
        

if __name__ == '__main__':
    if len(sys.argv) == 3:
        User.register(
            login=sys.argv[1],
            password=sys.argv[2]
        )
