import os
import re
import traceback

import exifread
from PIL import Image
from filetype import filetype

from engine.parse.model import ResParseResult
from utils import file_utils, date_utils, common_utils


def parse_gps(tude, tude_ref):
    """
    解析经纬度
    :param tude: 经纬度格式 [39, 19, 29163/2500]  [116, 1877/100, 0]  [40, 0, 0]
    :param tude_ref: N W E S
    :return:
    """
    num = None
    if tude and tude_ref:
        # 度分秒
        pattern = re.compile(r'[\d\/]+')
        match_result = pattern.findall(str(tude).strip())
        if match_result:
            num = 0
            for i in range(len(match_result)):
                arr = match_result[i].split('/')
                n = int(arr[0])
                if len(arr) > 1 and int(arr[1]) != 0:
                    n = n / int(arr[1])
                num += n / pow(60, i)
            s_tude_ref = str(tude_ref)
            if s_tude_ref == 'W' or s_tude_ref == 'S':
                num *= -1
    return num


def read_image(path):
    """
    读取图片信息
    :param path: 图片文件路径
    :return:
    """
    try:
        if not file_utils.is_image(path):
            return None
        size = os.path.getsize(path)
        mine_type = None
        kind = filetype.guess(path)
        if kind:
            mine_type = kind.mime
        md5 = file_utils.get_md5(path)
        result = ResParseResult(md5, path, mine_type, None, None, size, None, None, None)

        f = open(path, 'rb')
        tags = exifread.process_file(f)
        f.close()
        if tags:
            # print(tags)
            # for key, value in tags.items():
            #     print(key, ':', value)
            # Dimension
            width = tags.get('Image ImageWidth')
            height = tags.get('Image ImageLength')
            if width is None:
                width = tags.get('EXIF ExifImageWidth')
            if height is None:
                height = tags.get('EXIF ExifImageLength')
            # Orientation
            orientation = tags.get('Image Orientation')
            search = re.search(r'\d+', str(orientation))
            if search:
                if 90 == abs(int(search.group())):
                    temp = width
                    width = height
                    height = temp
            if width:
                width = int(str(width))
            if height:
                height = int(str(height))

            # GPS
            gps_latitude = tags.get('GPS GPSLatitude')
            gps_latitude_ref = tags.get('GPS GPSLatitudeRef')
            gps_longitude = tags.get('GPS GPSLongitude')
            gps_longitude_ref = tags.get('GPS GPSLongitudeRef')
            latitude = parse_gps(gps_latitude, gps_latitude_ref)
            longitude = parse_gps(gps_longitude, gps_longitude_ref)

            # DateTime
            date_time = tags.get('Image DateTime')
            date_time2 = tags.get('EXIF DateTimeOriginal')
            timestamp = 0
            if date_time:
                timestamp = date_utils.parse_format_time(str(date_time).strip())
            timestamp2 = 0
            if date_time2:
                timestamp2 = date_utils.parse_format_time(str(date_time2).strip())
            if timestamp < 1 or timestamp2 < 1:
                timestamp = max(timestamp, timestamp2)
            else:
                timestamp = min(timestamp, timestamp2)
            if timestamp == 0:
                timestamp = None
            # print('width:{} , height:{} , latitude:{} , longitude:{}, creation_time:{}'
            #       .format(width, height, latitude, longitude, timestamp))
            result.width = width
            result.height = height
            result.latitude = latitude
            result.longitude = longitude
            result.create_time = timestamp
        if not result.width or not result.height:
            # 上面使用 exifread 获取 webp 格式时，查不到信息 ，Webp file does not have exif data.
            # 使用以下方法取的图片宽高信息，可能有差错，因为图片可能有旋转角度 90的情况
            # 但是 没有得到 exif 信息的话，应该就不存在图片角度问题
            img = Image.open(path)
            if img:
                result.width = img.width
                result.height = img.height
        if result.width and result.height:
            # width 和 height 是必要条件
            return result
        else:
            return None
    except Exception as e:
        print(e)
        traceback.print_exc()
    return None

