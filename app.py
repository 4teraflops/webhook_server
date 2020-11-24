from flask import Flask
from flask import request
from datetime import datetime
import sqlite3
import config
from loguru import logger
import requests
import json
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


@logger.catch  # Логировать исключения из функции
@app.route('/finmonstate', methods=['POST'])
def finmonstate():
    if request.method == 'POST':
        data = request.get_json()
        try:
            key = data['key']
        except AttributeError:
            return 'Incorrect key'

        if key == config.key:
            state = data['state']
            try:
                count = data['count']
            except KeyError:
                count = ''
            now = datetime.now()
            time = now.strftime('%Y-%m-%d %H:%M:%S')
            #logger.debug(f'data: {data}\nkey: {key}\nstate: {state}\ntime: {time}')
            table = 'finmon_states'
            record_data(table, state, time, count)
            return 'Data Recorded'
        else:
            return 'Incorrect key'


@logger.catch  # Логировать исключения из функции
@app.route('/fiscalization', methods=['POST'])
def fiscalization():
    if request.method == 'POST':
        data = request.get_json()
        try:
            key = data['key']
        except AttributeError:
            return 'Incorrect key'

        if key == config.fisc_key:
            state = data['state']
            try:
                count = data['count']
            except KeyError:
                count = ''
            now = datetime.now()
            time = now.strftime('%Y-%m-%d %H:%M:%S')
            #logger.debug(f'data: {data}\nkey: {key}\nstate: {state}\ntime: {time}')
            table = 'fiscalization_states'
            record_data(table, state, time, count)
            return 'Data Recorded'
        else:
            return 'Incorrect key'


@logger.catch
def record_data(table, state, time, count):
    conn = sqlite3.connect('src/db.sqlite')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table} VALUES (Null, '{state}', '{time}', '{count}')")
    conn.commit()


def do_alarm(t_alarmtext):
    headers = {"Content-type": "application/json"}
    payload = {"text": f"{t_alarmtext}", "chat_id": f"{config.admin_id}"}
    requests.post(url=config.webhook_url, data=json.dumps(payload), headers=headers)


if __name__ == '__main__':
    try:
        # Debug/Development
        # app.run(debug=True, host="0.0.0.0", port="5000")
        # Production
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()
    except Exception as e:
        t_alarmtext = f'Webhook server (app.py): {str(e)}'
        do_alarm(t_alarmtext)
        logger.error(f'Other except error Exception', exc_info=True)
