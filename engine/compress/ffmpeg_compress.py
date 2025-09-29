import os
import re
import traceback

import exifread
import ffmpeg
from filetype import filetype

from app.settings import RemoteSettings
from engine.compress.base_compress import Compress
from engine.parse import image_parser, video_parser
from utils import file_utils


class FFmpegCompress(Compress):
    def compress(self, input_path, output_path=None, res_parse_result=None):
        try:
            kind = filetype.guess(input_path)
            if kind:
                # print(kind.extension)
                print(kind.mime)
                limit_dimension = 0
                input_file_, input_suffix = os.path.splitext(input_path)
                input_file_ += '_compressed'
                options = {}
                if kind.mime.startswith('image/'):
                    print('input file type is image')
                    # options['c:v'] = 'libwebp'
                    limit_dimension = RemoteSettings.COMPRESS_IMAGE_LIMIT_DIMENSION
                    if output_path is None:
                        # if input_suffix.lower() == '.gif':
                        #     output_path = input_file_ + '.gif'
                        # else:
                        #     output_path = input_file_ + '.jpg'
                        output_path = input_file_ + '.webp'  # 可以解决 jpg 没有透明通道和gif动图效果的问题，并且webp压缩效果更好
                    if res_parse_result is None:
                        res_parse_result = image_parser.read_image(input_path)
                elif kind.mime.startswith('video/'):
                    print('input file type is video')
                    limit_dimension = RemoteSettings.COMPRESS_VIDEO_LIMIT_DIMENSION
                    if output_path is None:
                        output_path = input_file_ + '.mp4'
                    if res_parse_result is None:
                        res_parse_result = video_parser.read_video(input_path)
                if res_parse_result:
                    width = res_parse_result.width
                    height = res_parse_result.height
                    bit_rate = res_parse_result.bitrate
                    frame_rate = res_parse_result.framerate

                    dimension_min = min(width, height)
                    if dimension_min > limit_dimension:
                        # 进行缩放
                        d = int(max(width, height) * limit_dimension / dimension_min)
                        if dimension_min == width:
                            width = limit_dimension
                            height = d
                        else:
                            width = d
                            height = limit_dimension
                        options['s'] = str(width) + 'x' + str(height)

                    if kind.mime.startswith('video/'):
                        new_frame_rate = min(frame_rate, RemoteSettings.FRAME_RATE_LIMIT)  # 帧率不能超过上限
                        bitrate = int(0.25 * (width * height * new_frame_rate) ** 0.56 * 1000)
                        if dimension_min > limit_dimension or bit_rate > bitrate + 2000:
                            options['b:v'] = bitrate
                        if new_frame_rate != frame_rate:
                            options['r'] = new_frame_rate
                    print('压缩参数:')
                    for k, v in options.items():
                        print(k, '>', v)
                    _, output_suffix = os.path.splitext(output_path)
                    if options or input_suffix.lower() != output_suffix.lower():
                        if os.path.exists(output_path):
                            os.remove(output_path)
                        ffmpeg.input(input_path).output(output_path, **options).run()
                    else:
                        output_path = input_path
        except Exception as e:
            print(e)
            traceback.print_exc()
        return output_path