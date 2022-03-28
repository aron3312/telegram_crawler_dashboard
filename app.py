from flask import Flask, render_template
from flask import request
from flask import jsonify
from datetime import datetime, timedelta
import sqlite3 as sql
import requests
import json
import random
import re
import os
import math
import pickle
app = Flask(__name__)

@app.route('/')
def index():
    con = sql.connect('D:/telegram_crawler/record.db')
    cur = con.cursor()
    query = cur.execute("SELECT strftime('%Y-%m-%d', date), COUNT(strftime('%Y-%m-%d', date)) date_count FROM message GROUP BY strftime('%Y-%m-%d', date) ORDER BY strftime('%Y-%m-%d', date) DESC")
    result = query.fetchall()
    result = sorted(result, key=lambda x:x[0], reverse=True)[0:60]
    time_series = {'time': [p[0] for p in result], 'count': [p[1] for p in result]}
    hour_query = cur.execute("SELECT strftime('%H', date), COUNT(strftime('%H', date)) date_count FROM message GROUP BY strftime('%H', date) ORDER BY strftime('%H', date) DESC")
    h_result = query.fetchall()
    h_result = [list(p) for p in h_result]
    for h in h_result:
        h[0] = int(h[0]) + 8 if int(h[0]) < 16 else int(h[0]) - 16
    h_result = sorted(h_result, key=lambda x: x[0])
    hour_series = {'time': [p[0] for p in h_result], 'count': [p[1] for p in h_result]}
    channel_name = [p for p in cur.execute("SELECT channel_name, COUNT(message) from message GROUP BY channel_name").fetchall()]
    message_count = cur.execute("SELECT COUNT(*) FROM message").fetchone()[0]
    return render_template('index.html', time_series=json.dumps(time_series, ensure_ascii=False), hour_series=json.dumps(hour_series, ensure_ascii=False), message_count=message_count, channel_name=channel_name)

@app.route('/news')
def news():
    con = sql.connect('D:/telegram_crawler/record.db')
    cur = con.cursor()
    query = cur.execute("SELECT * FROM message ORDER BY date DESC LIMIT 100")
    messages = query.fetchall()
    messages = [list(p) for p in messages]
    for message in messages:
        message[2] = datetime.strptime(re.sub('(.+)\+.*', r'\1', message[2]), '%Y-%m-%d %H:%M:%S')
        message[2] = str(message[2] + timedelta(hours=8))
    return render_template('news.html', messages=messages)

@app.route('/map_network')
def map_network():
    return render_template('map_network.html')

@app.route('/road_heat')
def road_heat():
    return render_template('road_heat.html')

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host="0.0.0.0", port=5000)
