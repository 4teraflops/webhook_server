from flask import Flask
from flask import request
from datetime import datetime
import sqlite3
import config
from loguru import logger
import requests
import json

app = Flask(__name__)
logger.add(f'src/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


@logger.catch  # Логировать исключения из функции
@app.route('/finmonstate', methods=['POST'])
def finmonstate():
    if request.method == 'POST':
        data = request.get_json()
        key = data['key']

        if key == config.key:
            state = data['state']
            try:
                count = data['count']
            except KeyError:
                count = ''
            now = datetime.now()
            time = now.strftime('%d-%m-%Y %H:%M:%S')
            #logger.debug(f'data: {data}\nkey: {key}\nstate: {state}\ntime: {time}')
            record_data(time, state, count)
            return 'Data Recorded'


@logger.catch
def record_data(time, state, count):
    conn = sqlite3.connect('src/db.sqlite')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO finmon_states VALUES (Null, '{state}', '{time}', '{count}')")
    conn.commit()


def do_alarm(t_alarmtext):
    headers = {"Content-type": "application/json"}
    payload = {"text": f"{t_alarmtext}", "chat_id": f"{config.admin_id}"}
    requests.post(url=config.webhook_url, data=json.dumps(payload), headers=headers)


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        t_alarmtext = f'Webhook server (app.py): {str(e)}'
        do_alarm(t_alarmtext)
        logger.error(f'Other except error Exception', exc_info=True)
