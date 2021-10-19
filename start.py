import sys
from  flask import Flask, render_template, request, flash, redirect, url_for, session, send_from_directory
from modules.user import User
from modules.telegram import Telegram

import configparser as cp, time, os, signal, subprocess


app = Flask(__name__)
app.secret_key = 'super secret'

@app.route('/')
def main():
    if 'auth' not in session or session.get('auth') == False:
        return redirect(url_for('login'))
    else:
        bots_data = Telegram.get_bots_data(session.get('auth'))

        config = cp.ConfigParser()
        config.read('config.ini')

        return render_template(
            'index.html', 
            username=session.get('auth'), 
            data=bots_data,
            bots_count = len(bots_data),
            message_count = sum([bot['count_message'] for bot in bots_data]),
            response=User.get_response(session.get('auth')))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if ('login' and 'password' in request.form) or session.get('auth') not in [False, None]:
        user = User(request.form['login'], request.form['password'])
        session['auth'] = request.form['login'] if user.authenticated else False
        
        return redirect(url_for('main'))

    session.clear()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))

@app.route('/create_bot')
def create_bot():
    return render_template('session.html')

@app.route('/add_bot', methods=['POST'])
def addbot():
    if request.method == 'POST':
        api_id, api_hash, tg_code = request.form['api_id'], request.form['api_hash'], request.form['tg_code']
        Telegram.send_code_request(api_id, api_hash, tg_code)
        time.sleep(3)

        session_file = 'sessions/{}_{}.session'.format(api_id, api_hash)
        try:
            tg = Telegram(api_id, api_hash, session_file)
            tg.create_on_db(session.get('auth'))
            time.sleep(2)
            tg.run(session.get('auth'))
        except:
            pass


    return redirect(url_for('main'))


@app.route('/update_settings', methods=['POST'])
def update_settings():
    if request.method == 'POST':
        try:
            firstName, lastName, about, username = request.form['firstName'], request.form['lastName'],request.form['about'],request.form['username']
            api_id, api_hash, session_file = request.form['api_id'], request.form['api_hash'], request.form['session_file']
        except:
            return redirect(url_for('main'))

        tg = Telegram(api_id, api_hash, session_file)
        if username != '' and tg.check_username(username):
            return redirect(url_for('main'))

        if 'photoProfile' in request.files and request.files['photoProfile'].filename != '':
            file = request.files['photoProfile']
            photo_path = 'photo_data/photo_{}.{}'.format(
                api_id, file.filename.split('.')[-1]
            )
            file.save(photo_path)

        else:
            photo_path = 'None'

        tg.stop(session.get('auth'))
        tg.update_info({
            'first_name': firstName,
            'last_name': lastName,
            'about' : about,
            'username' : username,
            'photo' : photo_path
        })

        tg.run(session.get('auth'))

    time.sleep(2)
    return redirect(url_for('main'))


@app.route('/api', methods=['POST'])
def api_manager():
    print(request.form)
    if request.method == 'POST' and 'action' in request.form:
        action = request.form['action']
        

        # Switch action
        if action == 'update_response':
            User.update_response(
                session['auth'],
                request.form['group_text'], request.form['group_start'], request.form['group_end'], 
                request.form['single_text'], request.form['single_start'], request.form['single_end']
                )
            return 'Настройки обновлены'

        # (Re-)start bot
        if action == 'restart_bot':
            api_id, api_hash, session_file = request.form['api_id'], request.form['api_hash'], request.form['session_file']
            tg = Telegram(api_id, api_hash, session_file)            
            tg.run(session.get('auth'))

            return 'Бот перезапущен'

        # Stop bot
        if action == 'stop_bot':
            api_id, api_hash, session_file = request.form['api_id'], request.form['api_hash'], request.form['session_file']
            tg = Telegram(api_id, api_hash, session_file)            
            tg.stop(session.get('auth'))

            return 'Бот остановлен'

        # Drop bot
        if action == 'drop_bot':
            api_id, api_hash, session_file = request.form['api_id'], request.form['api_hash'], request.form['session_file']
            tg = Telegram(api_id, api_hash, session_file)
            tg.stop(session.get('auth'))            
            tg.drop_me()

            return 'Бот удалён'

        # Check username
        if action == 'check_username':
            api_id, api_hash, session_file, username = request.form['api_id'], request.form['api_hash'], request.form['session_file'], request.form['username']
            tg = Telegram(api_id, api_hash, session_file)
            tg.stop(session.get('auth'))

            result = tg.check_username(username)
            tg.run(session.get('auth'))
            return 'true' if result else 'false'

        # Create session (tmp record on db)
        if action == 'create_session':
            api_id, api_hash, phone = request.form['api_id'], request.form['api_hash'], request.form['phone']
            Telegram.create_tmp_session(api_id, api_hash, phone)

        # Download list chats
        if action == 'get_list_chats':
            api_id, api_hash, session_file = request.form['api_id'], request.form['api_hash'], request.form['session_file']
            tg = Telegram(api_id, api_hash, session_file)
            return tg.get_chats_list()

        # Upload chat lists
        if action == 'load_chats':
            
            api_id, api_hash, session_file, start, end = request.form['api_id'], request.form['api_hash'], request.form['session_file'], request.form['start'], request.form['end']
            
            file = request.files['file']
            file.save('chat_lists_data/chats_{}.txt'.format(api_id))

            tg = Telegram(api_id, api_hash, session_file)
            tg.stop(session.get('auth'))
            tg.load_chat_list('chat_lists_data/chats_{}.txt'.format(api_id), start, end)
            return 'Подписка началась'


    return 'false'

@app.route('/statistics/<path:filename>', methods=['GET', 'POST'])
def download_statistic(filename):
    return send_from_directory(directory='./statistics', path=filename)
            


if __name__ == '__main__':
    app.run(host=sys.argv[1], port=int(sys.argv[2]))