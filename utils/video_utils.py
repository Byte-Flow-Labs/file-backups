import subprocess

def capture_frame(video_path, output_path, timestamp):
    """
    从视频中捕获一帧并保存为图片。
    :param video_path: 视频文件的路径。
    :param output_path: 截图文件的保存路径。
    :param timestamp: 要截取的帧的时间戳（秒）。
    """
    command = [
        'ffmpeg',
        '-ss', str(timestamp),  # 指定从视频的哪个时间点开始截取
        '-i', video_path,  # 指定输入视频文件
        '-vframes', '1',  # 只截取一帧
        '-q:v', '50',  # 输出图片的质量
        output_path  # 指定输出图片文件
    ]

    # 使用subprocess执行命令
    subprocess.run(command, check=True)