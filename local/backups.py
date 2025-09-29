# coding=utf-8
"""
本地备份工具
主要作用：避免重复文件
只做文件复制，不追加属性，保持文件创建时间不变
在保存的根目录放一个sqlite数据文件，记录该目录下所有文件的md5
"""
import datetime
import os.path
import shutil
import sqlite3
import re

from app.settings import LocalSettings
from utils import file_utils, bus_msg

TAG = "BACKUPS"

def get_path(dir, k, filename):
    version = 0
    # 正则表达式
    pattern = r'([\da-f]{32})-(\d+)-(.+)'
    # 使用 re.search 查找匹配项
    match = re.search(pattern, filename)
    # 检查是否找到匹配项
    if match:
        # 打印匹配到的组
        # md5 = match.group(1)
        # version = match.group(2)
        # filename = match.group(3)
        name = filename
    else:
        name = k + '-' + str(version) + '-' + filename
        while True:
            path = os.path.join(dir, name)
            if os.path.exists(path):
                md5 = file_utils.get_md5(path)
                if md5 != k:
                    version += 1
                    name = k + '-' + str(version) + '-' + filename
                else:
                    name = None
                    break
            else:
                break
    if name is None:
        return None
    else:
        return os.path.join(dir, name)


def work():
    bus_msg.task_progress_updated.send(tag=TAG, value=0)
    md5_dict = {}
    file_utils.find_file_by_md5(LocalSettings.NEED_BACKUPS_DIR, md5_dict)
    total = len(md5_dict)
    print('find file total: ', total)
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
            bus_msg.task_progress_updated.send(tag=TAG, value=(index + 1)/total * 100)
            print('backups -> dict', index + 1, '/', total, k, ':', v)
            cursor.execute('SELECT * FROM ' + LocalSettings.DB_TABLE + ' WHERE md5 = "' + k + '"')
            result = cursor.fetchone()
            print('sql select', k, '->', result)
            if result is None:
                src = v[0]
                filename = os.path.basename(src)
                if filename == LocalSettings.DB_NAME:
                    continue
                creation_time = os.path.getmtime(src)  # 最后一次修改时间绝大概率是文件的真正创建时间
                creation_date_time = datetime.datetime.fromtimestamp(creation_time)
                formatted_time_y = creation_date_time.strftime('%Y')
                formatted_time_ym = creation_date_time.strftime('%Y-%m')
                formatted_time = creation_date_time.strftime('%Y-%m-%d %H:%M:%S')
                dst_dir = os.path.join(LocalSettings.SAVE_DIR, formatted_time_y, formatted_time_ym)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                dst = get_path(dst_dir, k, filename)
                if dst:
                    print('copy', src, '->', dst)
                    shutil.copy2(src, dst)
                    relative_path = dst[len(LocalSettings.SAVE_DIR):]
                    cursor.execute('INSERT INTO ' + LocalSettings.DB_TABLE + ' '
                                   '(md5, name, path, create_time)'
                                   'VALUES '
                                   '("' + k + '", "' + filename + '", "' + relative_path + '", "' + formatted_time + '")')
                    conn.commit()
                    print('sql insert', k, '->', filename)
                else:
                    print('no copy')
        bus_msg.task_progress_updated.send(tag=TAG, value=100)
        cursor.close()
        conn.close()
        print('db is close')
        bus_msg.task_finished.send(tag=TAG, result=None)


if __name__ == '__main__':
    work()


__all__ = ['work']

