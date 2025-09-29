# coding=utf-8
"""
同步保存的数据
长时间存储可会有删除文件的情况
或都不小心把本地数据库删除的情况
用于同步更新本地备份的数据
"""
import datetime
import os
import sqlite3

from app.settings import LocalSettings
from utils import file_utils, bus_msg

TAG = "SYNC"

def work():
    bus_msg.task_progress_updated.send(tag=TAG, value=0)
    md5_dict = {}
    file_utils.find_file_by_md5(LocalSettings.SAVE_DIR, md5_dict)
    print('find file count: ', len(md5_dict))
    conn = sqlite3.connect(os.path.join(LocalSettings.SAVE_DIR, LocalSettings.DB_NAME))
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS ' + LocalSettings.DB_TABLE + ' ('
                   'md5 CHAR(32) PRIMARY KEY NOT NULL,'
                   'name CHAR(255) NOT NULL,'
                   'path TEXT NOT NULL,'
                   'create_time DATETIME'
                   ')')
    conn.commit()
    print('db is ready')
    total = len(md5_dict)
    if total == 1 and os.path.basename(md5_dict.values()[0][0]) == LocalSettings.DB_NAME:
        cursor.execute('DELETE FROM ' + LocalSettings.DB_TABLE)
        conn.commit()
        print('db clear all')
    elif total:
        cursor.execute('SELECT * FROM ' + LocalSettings.DB_TABLE)
        result = cursor.fetchall()
        for row in result:
            print('db select ->', row)
            md5 = row[0]
            item = md5_dict.pop(md5, None)
            if item and len(item):
                relative_path = item[0][len(LocalSettings.SAVE_DIR):]
                if row[2] != relative_path:
                    cursor.execute('UPDATE ' + LocalSettings.DB_TABLE + ' SET path = "' + relative_path + '" WHERE md5 = "' + md5 + '"')
                    print('db update ->', md5)
            else:
                cursor.execute('DELETE FROM ' + LocalSettings.DB_TABLE + ' WHERE md5 = "' + md5 + '"')
                print('db delete ->', md5)
        conn.commit()
        total = len(md5_dict)
        for index, (k, v) in enumerate(md5_dict.items()):
            bus_msg.task_progress_updated.send(tag=TAG, value=(index + 1)/total * 100)
            print('sync -> dict', index + 1, '/', total, k, ':', v)
            cursor.execute('SELECT * FROM ' + LocalSettings.DB_TABLE + ' WHERE md5 = "' + k + '"')
            result = cursor.fetchone()
            print('sql select', k, '->', result)
            if result is None:
                path = v[0]
                filename = os.path.basename(path)
                if filename == LocalSettings.DB_NAME:
                    continue
                creation_time = os.path.getmtime(path)  # 最后一次修改时间绝大概率是文件的真正创建时间
                creation_date_time = datetime.datetime.fromtimestamp(creation_time)
                formatted_time = creation_date_time.strftime('%Y-%m-%d %H:%M:%S')
                relative_path = path[len(LocalSettings.SAVE_DIR):]
                cursor.execute('INSERT INTO ' + LocalSettings.DB_TABLE + ' '
                               '(md5, name, path, create_time)'
                               'VALUES '
                               '("' + k + '", "' + filename + '", "' + relative_path + '", "' + formatted_time + '")')
                conn.commit()
                print('sql insert', k, '->', filename)
        bus_msg.task_progress_updated.send(tag=TAG, value=100)
    else:
        cursor.execute('DELETE FROM ' + LocalSettings.DB_TABLE)
        conn.commit()
        print('db clear all')
    cursor.close()
    conn.close()
    print('db is close')
    bus_msg.task_finished.send(tag=TAG, result=None)


if __name__ == '__main__':
    work()


__all__ = ['work']

