from local import sync, backups, check

if __name__ == '__main__':
    # 本地备份
    # 复件并去重文件，并维护一个sqlite数据库
    # 运行之前请先设置 settings.py

    # 先同步存储文件夹(排除存储文件的变动)，更新数据库，可不调用
    sync.work()
    # 再从其他文件开始备份到存储文件夹中
    backups.work()
    # 检查备份结果，可不调用
    check.check_backups()