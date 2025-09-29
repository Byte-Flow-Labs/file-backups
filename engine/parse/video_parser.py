import re
import traceback

import ffmpeg
from filetype import filetype

from engine.parse.model import ResParseResult
from utils import common_utils, date_utils, file_utils


def parse_gps(tude):
    """
    解析经纬度
    :param tude: +39.9393+116.3407/
    :return:
    """
    t = (None, None)
    if tude:
        pattern = re.compile(r'[\+\-][\w\.]+')
        match_result = pattern.findall(tude)
        if match_result and len(match_result) == 2:
            t = float(match_result[0]), float(match_result[1])
    return t


def read_video(path):
    """
    获取视频信息
    :param path:
    :return:
    """
    try:
        if not file_utils.is_video(path):
            return None
        probe = ffmpeg.probe(path)
        print(probe)
        if probe:
            # width = probe['streams'][0]['width']
            # height = probe['streams'][0]['height']
            # size = probe['format']['size']
            # duration = probe['format']['duration']
            # bit_rate = probe['format']['bit_rate']
            # display_aspect_ratio = probe['streams'][0]['display_aspect_ratio']
            # r_frame_rate = probe['streams'][0]['r_frame_rate']
            # creation_time = probe['streams'][0]['tags']['creation_time']
            # location = probe['format']['tags']['location']
            creation_time_list = []
            width = common_utils.deep_find_dict_by_key(probe, 'width')
            height = common_utils.deep_find_dict_by_key(probe, 'height')
            size = common_utils.deep_find_dict_by_key(probe, 'size')
            duration = common_utils.deep_find_dict_by_key(probe, 'duration')
            bit_rate = common_utils.deep_find_dict_by_key(probe, 'bit_rate')
            display_aspect_ratio = common_utils.deep_find_dict_by_key(probe, 'display_aspect_ratio')
            r_frame_rate = common_utils.deep_find_dict_by_key(probe, 'r_frame_rate')
            common_utils.deep_find_dict_by_key(probe, 'creation_time', creation_time_list)
            location = common_utils.deep_find_dict_by_key(probe, 'location')
            rotation = common_utils.deep_find_dict_by_key(probe, 'rotation')

            if size:
                size = int(size)
            if duration:
                duration = float(duration)
            if bit_rate:
                bit_rate = int(bit_rate)

            if rotation:
                # 修正转换
                if 90 == abs(rotation):
                    temp = width
                    width = height
                    height = temp

            t = parse_gps(location)
            latitude = t[0]
            longitude = t[1]

            timestamp = None
            if len(creation_time_list):
                for creation_time in creation_time_list:
                    # print(creation_time)
                    if creation_time:
                        # timestamp = time.mktime(time.strptime(creation_time, '%Y-%m-%dT%H:%M:%S.%fZ'))
                        timestamp2 = date_utils.parse_format_time(str(creation_time).strip())
                        if timestamp2:
                            if timestamp is None:
                                timestamp = timestamp2
                            else:
                                timestamp = min(timestamp, timestamp2)

            if timestamp:
                if longitude:
                    timestamp += 3600 * date_utils.get_timezone(longitude)
                else:
                    timestamp += 3600 * date_utils.get_local_timezone()
            else:
                timestamp = None
            frame_rate = None
            if r_frame_rate:
                frame_rate = int(r_frame_rate.split('/')[0])

            mine_type = None
            kind = filetype.guess(path)
            if kind:
                mine_type = kind.mime
            md5 = file_utils.get_md5(path)
            result = ResParseResult(md5, path, mine_type, width, height, size, latitude, longitude,
                                    timestamp, duration, bit_rate, frame_rate)

            # print(result)
            return result
        else:
            return None
    except Exception as e:
        print(e)
        traceback.print_exc()
    return None

