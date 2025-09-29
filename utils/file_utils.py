# coding=utf-8
import hashlib
import os

import piexif
from PIL import Image
from filetype import filetype


def format_file_size(size):
    """
    格式化文件大小的表示 -h
    :param size:
    :return:
    """
    if size < 1024:
        return f"{size} bytes"
    elif size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 ** 3:
        return f"{size / (1024 ** 2):.2f} MB"
    elif size < 1024 ** 4:
        return f"{size / (1024 ** 3):.2f} GB"
    else:
        return f"{size / (1024 ** 4):.2f} TB"


def is_image(path):
    """
    判断是否是图片文件
    :param path:
    :return:
    """
    b = False
    kind = filetype.guess(path)
    if kind:
        print(kind.extension)
        print(kind.mime)
        b = kind.mime.startswith('image/')
    return b


def is_video(path):
    """
    判断是否是视频文件
    :param path:
    :return:
    """
    b = False
    kind = filetype.guess(path)
    if kind:
        # print(kind.extension)
        # print(kind.mime)
        b = kind.mime.startswith('video/')
    return b


def get_md5(path):
    """
    获取文件的MD5
    大文件可能会报报 MemoryError
    请使用 get_md5_of_large_file方法
    :param path:
    :return:
    """
    # m = hashlib.md5()
    # f = open(path, 'rb')
    # m.update(f.read())
    # f.close()
    # md5value = m.hexdigest()
    # return md5value
    return get_md5_of_large_file(path)


def get_md5_of_large_file(path):
    """
    获取文件的MD5
    为大文件准备
    :param path:
    :return:
    """
    md5 = hashlib.md5()
    chunk_size = 4096  # 例如，每次读取4KB
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            md5.update(chunk)
    return md5.hexdigest()


def find_file(path, file_list, filename=None):
    """
    遍历目录下所有的文件
    :param filename: 需要查找的文件名
    :param path:
    :param file_list:
    :return:
    """
    for name in os.listdir(path):
        f = os.path.join(path, name)
        if os.path.isfile(f):
            print(f)
            if filename is None or name == filename:
                file_list.append(f)
        else:
            find_file(f, file_list, filename)


def find_file_by_md5(path, md5_dict):
    """
    递归遍历文件，并以md5为key，文件路径为value 列表，存储在字典中
    :param path:
    :param md5_dict:
    :return:
    """
    file_list = []
    find_file(path, file_list)
    for f in file_list:
        print(f)
        md5 = get_md5(f)
        if md5 in md5_dict:
            paths = md5_dict[md5]
            paths.append(f)
        else:
            md5_dict[md5] = [f]


def find_file_by_name(path, name_dict):
    """
    递归遍历文件，并以name为key，文件路径为value 列表，存储在字典中
    :param path:
    :param name_dict:
    :return:
    """
    file_list = []
    find_file(path, file_list)
    for f in file_list:
        print(f)
        name = os.path.basename(f)
        if name in name_dict:
            paths = name_dict[name]
            paths.append(f)
        else:
            name_dict[name] = [f]


def remove_duplicate_file(path):
    """
    删除重复文件
    通过md5的方式
    :param path: 目录路径
    :return:
    """
    names = {}
    find_file_by_md5(path, names)

    duplicate_total = 0
    delete_total = 0
    duplicate_size_total = 0
    for k, v in names.items():
        if len(v) > 1:
            duplicate_total += 1
            print('name:{} count:{} '.format(k, len(v)))
            for i in range(len(v)):
                f = v[i]
                size = os.path.getsize(f)
                print('---{}  size:{}'.format(f, size))
                if i > 0:
                    os.remove(f)
                    delete_total += 1
    print('total:{}  duplicate total:{}  delete total:{}'.format(len(names), duplicate_total, delete_total))


def remove_empty_dir(path):
    """
    清空目录
    :param path:
    :return:
    """
    empty_dir_list = []
    for dir_path, sub_dir, files in os.walk(path):
        # for d in sub_dir:
        #     print('dir', os.path.join(dir_path, d))
        # for f in files:
        #     print('file', os.path.join(dir_path, f))
        for d in sub_dir:
            new_dir = os.path.join(dir_path, d)
            file_list = os.listdir(new_dir)
            if not file_list or len(file_list) == 0:
                print(new_dir)
                empty_dir_list.append(new_dir)
    for f in empty_dir_list:
        os.rmdir(f)