from  flask import Flask, render_template, request, flash, redirect, url_for, session
from modules.user import User
from modules.telegram import Telegram

import configparser as cp, time, os, signal


app = Flask(__name__)
app.secret_key = 'super secret'

@app.route('/')
def main():
    if 'auth' not in session or session.get('auth') == False:
        return redirect(url_for('login'))
    else:
        bots_data = Telegram.get_bots_data()

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
            tg.create_on_db()
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
            photo_path = 'tmp_data/photo_{}.{}'.format(
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


    return redirect(url_for('main'))


@app.route('/api', methods=['POST'])
def api_manager():
    if request.method == 'POST' and 'action' in request.form:
        action = request.form['action']

        # Switch action
        if action == 'change_responce_text':
            User.update_response(session['auth'], request.form['text'])
            return 'true'

        # (Re-)start bot
        if action == 'start_bot':
            api_id, api_hash, session_file = request.form['api_id'], request.form['api_hash'], request.form['session_file']
            tg = Telegram(api_id, api_hash, session_file)            
            tg.run(session.get('auth'))

            
            return 'true'

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


    return 'false'

            


if __name__ == '__main__':
    app.run(port=80)