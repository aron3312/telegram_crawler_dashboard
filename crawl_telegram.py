from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import sqlite3 as sql
import time
import os
import pickle


def get_channel_data(client, channel_username, update):
    con = sql.connect('record.db')
    cur = con.cursor()
    if not os.path.exists('entity/{}.pkl'.format(channel_username[1])):
        channel_entity = client.get_entity(channel_username[1])
        pickle.dump(channel_entity, open('entity/{}.pkl'.format(channel_username[1]), 'wb'))
    else:
        channel_entity = pickle.load(open('entity/{}.pkl'.format(channel_username[1]), 'rb'))
    if update:
        newest = cur.execute("SELECT MAX(date), id FROM message WHERE channel_name = '{}'".format(channel_username[0]))
        newest_data = newest.fetchall()
        newest_id = int(newest_data[0][1].split('_')[-1])
    else:
        newest_id = 0
    print(newest_id)
    posts = client(GetHistoryRequest(
        peer=channel_entity,
        limit=100,
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=newest_id,
        add_offset=0,
        hash=0))
    d = posts.messages
    if not d:
        return 'No New Message!'
    temp = [p for p in d]
    for t in temp:
        if not t.message:
            t.message = ''
        if not t.views:
            t.views = ''

    t = temp[0]
    temp_result = {'id': channel_username[1] + '_' + str(t.id), 'channel_name': channel_username[0],
                   'date': str(t.date), 'message': t.message, 'views': t.views}
    upload_result = [(channel_username[1] + '_' + str(p.id), channel_username[0], str(p.date), p.message, p.views) for p
                     in temp]
    cur.executemany("INSERT or REPLACE into message ({}) VALUES ({})".format(','.join(temp_result.keys()),
                                                                             ','.join(['?'] * len(temp_result.keys()))),
                    upload_result)
    con.commit()
    last = d[-1].id

    if int(last) > newest_id:
        while True:
            conti = client.iter_messages(
                channel_entity,
                            limit=100,
                            min_id=last-100,
                            reverse=True
                        )
            temp = [p for p in conti]
            prev = last
            last = temp[0].id
            if prev == last:
                break
            temp.reverse()
            for t in temp:
                if not t.message:
                    t.message = ''
                if not t.views:
                    t.views = ''
            t = temp[0]
            temp_result = {'id': channel_username[1] + '_' + str(t.id), 'channel_name': channel_username[0], 'date': str(t.date), 'message': t.message, 'views': t.views}
            upload_result = [(channel_username[1] + '_' + str(p.id), channel_username[0], str(p.date), p.message, p.views) for p in temp]
            cur.executemany("INSERT or REPLACE into message ({}) VALUES ({})".format(','.join(temp_result.keys()),
                                                                            ','.join(['?'] * len(temp_result.keys()))),
                               upload_result)
            con.commit()
            if last < newest_id:
                break
    return 'Success'


if __name__ == '__main__':
    with open('channel_lst.txt', 'r', encoding='utf-8') as f:
        channel_lst = [tuple(p.split('\t')) for p in f.read().split('\n')]
    api_id = 1191168
    api_hash = ''
    phone = ''
    client = TelegramClient(phone, api_id, api_hash)
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input('Enter the code: '))
    for channel in channel_lst:
        result = get_channel_data(client, channel, True)
        print(channel[1] + ' ' + result)