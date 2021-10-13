from telethon import TelegramClient
import sys

api_id, api_hash = int(sys.argv[1]), sys.argv[2]
client = TelegramClient('session', api_id, api_hash)
client.start()