# coding=utf-8
import os
import sqlite3

from app.settings import LocalSettings
from utils import file_utils, bus_msg

TAG = "CHECK"

def check_duplicate_file():
    """
    检查文件重复
    :return:
    """
    md5_dict = {}
    file_list = []
    file_utils.find_file(LocalSettings.SAVE_ROOT_DIR, file_list, LocalSettings.DB_NAME)
    for db_file in file_list:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ' + LocalSettings.DB_TABLE)
        row = cursor.fetchone()
        while row is not None:
            md5 = row[0]
            path = os.path.join(os.path.dirname(db_file), row[2])
            if md5 in md5_dict:
                paths = md5_dict[md5]
                paths.append(path)
            else:
                md5_dict[md5] = [path]
            row = cursor.fetchone()
        cursor.close()
        conn.close()
    print('Duplicate File List :')
    for k, v in md5_dict.items():
        if len(v) > 1:
            file_size = os.path.getsize(v[0])
            print(k, ':', file_utils.format_file_size(file_size), 'x', len(v), '=', file_utils.format_file_size(file_size * len(v)))
            for path in v:
                print('  -->', path)


def check_backups():
    """
    验证文件是否全部备份
    :return:
    """
    bus_msg.task_progress_updated.send(tag=TAG, value=0)
    no_backup_list = []
    md5_dict = {}
    file_utils.find_file_by_md5(LocalSettings.NEED_BACKUPS_DIR, md5_dict)
    total = len(md5_dict)
    if total:
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

        for index, (k, v) in enumerate(md5_dict.items()):
            bus_msg.task_progress_updated.send(tag=TAG, value=(index + 1) / total * 100)
            print('check -> dict', index + 1, '/', total, k, ':', v)
            cursor.execute('SELECT * FROM ' + LocalSettings.DB_TABLE + ' WHERE md5 = "' + k + '"')
            result = cursor.fetchone()
            if result is None:
                no_backup_list.append((k, v))
        bus_msg.task_progress_updated.send(tag=TAG, value=100)
        cursor.close()
        conn.close()
        print('db is close')
    print('No Backup File List:')
    if no_backup_list:
        msg = f"存在{len(no_backup_list)}项未备份"
        for item in no_backup_list:
            print('--->', item)
    else:
        msg = None
        print('---> EMPTY')
    print('Total:', total, ',Backup:', total - len(no_backup_list), ',No Backup:', len(no_backup_list))
    bus_msg.task_finished.send(tag=TAG, result=msg)


if __name__ == '__main__':
    check_duplicate_file()

