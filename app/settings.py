

class Settings:
    NEED_BACKUPS_DIR = ''
    IS_REMOVE_ORIGINAL_RES = False  # 上传资源成功后，是否删除原始资源
    IS_SAVE_CREATE_TIME_EMPTY_RES = False  # 是否保存创建时间为空的资源并记录

    # 压缩上限
    NEED_COMPRESS = False  # 上传资源是否开启压缩
    COMPRESS_IMAGE_LIMIT_DIMENSION = 1440  # 图片压缩后的最大分辨率，不超过
    COMPRESS_VIDEO_LIMIT_DIMENSION = 1080  # 视频压缩后的最大分辨率
    FRAME_RATE_LIMIT = 30  # 视频压缩的最大码率


class LocalSettings(Settings):
    # local settings
    # NEED_BACKUPS_DIR = r'\\192.168.123.200\mnt\Backups\Photos\xxx'  # 需要备份的文件夹
    NEED_BACKUPS_DIR = r'/home/dean/Pictures/xxx'  # 需要备份的文件夹
    IS_SAVE_CREATE_TIME_EMPTY_RES = True
    # SAVE_DIR = r'\\192.168.123.200\mnt\Storage1\Photos\xxx'  # 存储文件夹
    SAVE_DIR = r'/media/dean/Storage1/Photos/xxx'  # 存储文件夹
    DB_NAME = '.backups.db'  # 数据库文件名，不需要改动
    DB_TABLE = 'backups_file'

    # SAVE_ROOT_DIR = r'\\192.168.123.200\mnt\Storage1\Photos'  # 存储文件的总目录，用于检查重复文件
    SAVE_ROOT_DIR = r'/media/dean/Storage1/Photos'  # 存储文件的总目录，用于检查重复文件


class RemoteSettings(Settings):
    # remote settings
    # OSS
    OSS_ACCESS_KEY_ID = 'xxxxx'
    OSS_ACCESS_KEY_SECRET = 'xxxxx'
    OSS_ENDPOINT = 'oss-cn-beijing.aliyuncs.com'
    OSS_BUCKET_NAME = 'dean-xxx'

    NEED_BACKUPS_DIR = r'/home/dean/Pictures/xxx'
    IS_REMOVE_ORIGINAL_RES = True
    NEED_COMPRESS = True



