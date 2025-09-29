## File Backups

---
### 运行环境
建议 Python 3.12

---
### 使用
##### 命令行
需要先配置./file-backups/app/settings.py中的 `NEED_BACKUPS_DIR` 和 `SAVE_DIR`，然后执行下方命令
```shell
python ./file-backups/app/main.py
```
##### 视窗
```shell
python ./file-backups/app/main_ui.py
```
---
### 说明
#### 备份目录
文件备份时，会按文件的最后一次修改日期生成目录，例如 2025/2025-09/xxx-0-xxxx.jpg

#### 备份文件命名
文件名会被重命名，格式为 MD5-VersionCode-FileName
- MD5 : 文件的MD5值
- VersionCode : 版本号，不出意外的话，VersionCode 一直是 0, 当 MD5-VersionCode-FileName 已经存在时，采用保守的备份方式，将VersionCode 自加 1
- FileName : 原始的文件名，包括扩展名