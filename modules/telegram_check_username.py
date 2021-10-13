from telethon import TelegramClient, sync, functions, types
import sys

with sync.TelegramClient(sys.argv[3], int(sys.argv[1]), sys.argv[2]) as client:
    result = client(functions.account.CheckUsernameRequest(
        username=sys.argv[4]
    ))

    print('true' if bool(result) else 'false')