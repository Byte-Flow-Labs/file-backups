import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time

from app.settings import LocalSettings
from local import sync, backups, check
from utils import bus_msg


class PopupProgressBar:
    def __init__(self, parent, title="处理中", max_value=100):
        # 创建独立的顶级窗口
        self.parent = parent
        self.top = tk.Toplevel()
        self.top.title(title)
        # self.top.geometry("500x150")

        self.top.transient(parent)
        # 防止用户关闭窗口
        self.top.protocol("WM_DELETE_WINDOW", self._disable_close)

        # 进度条变量
        self.progress_var = tk.DoubleVar()
        self.max_value = max_value
        self.stage_var = tk.StringVar(value="阶段")
        self.stage_label = ttk.Label(self.top, textvariable=self.stage_var)
        self.stage_label.pack(side="top", padx=10)
        # 创建进度条
        self.progress_bar = ttk.Progressbar(
            self.top,
            variable=self.progress_var,
            maximum=max_value,
            length=450
        )
        self.progress_bar.pack(pady=10, padx=10)

        # 状态标签
        self.status_label = ttk.Label(self.top, text="准备开始...")
        self.status_label.pack(pady=5)
        self.action_button = ttk.Button(self.top, text="取消", command=self.close)
        self.action_button.pack(side="right", pady=10, padx=10)

        # 任务完成标志
        self.task_complete = False

        # 绑定信号与槽函数
        bus_msg.task_progress_updated.connect(self.update_progress)
        bus_msg.task_finished.connect(self.finished)

    def _disable_close(self):
        """禁用窗口关闭按钮"""
        pass

    def update_stage(self, text):
        self.stage_var.set(text)

    def update_progress(self, sender, **kwargs):
        """更新进度条和状态文本"""
        tag = kwargs.get("tag")
        value = kwargs.get("value")
        status_text = kwargs.get("status_text")
        self.progress_var.set(value)
        if status_text:
            self.status_label.config(text=status_text)
        else:
            percentage = int((value / self.max_value) * 100)
            self.status_label.config(text=f"处理中: {percentage}%")
        self.top.update_idletasks()

    def finished(self, sender, **kwargs):
        self.task_complete = True

    def close(self):
        """关闭进度条窗口"""
        self.task_complete = True
        self.top.destroy()

    def wait_for_completion(self):
        """等待任务完成"""
        while not self.task_complete:
            self.top.update()
            time.sleep(0.1)
        self.close()


def select_folder(selected_folder):
    """打开文件夹选择对话框并获取路径"""
    # 弹出文件夹选择对话框
    folder_path = filedialog.askdirectory(
        title="选择文件夹",  # 对话框标题
        initialdir="/"  # 初始目录（可以改为当前目录".")
    )

    # 如果用户选择了文件夹（不是点击取消）
    if folder_path:
        selected_folder.set(folder_path)


def frame_select_folder(root, label="选择文件夹", default_folder=None):
    selected_folder = tk.StringVar(value=default_folder)
    frame = ttk.Frame(root)
    ttk.Label(frame, text=label + ":", font=("", 10)).grid(
        row=0, column=0, sticky="w"
    )

    ttk.Entry(
        frame,
        textvariable=selected_folder,
        width=40,
        font=("", 10)
    ).grid(row=0, column=1, padx=5)

    # 选择文件夹按钮
    ttk.Button(
        frame,
        text="浏览",
        command=lambda: select_folder(selected_folder),
    ).grid(row=0, column=2)
    return frame, selected_folder


def frame_action(root, title, description=None, default_selected=False):
    frame = ttk.Frame(root)
    frame.pack(side="top", fill="x")

    ttk.Label(frame, text=title, font=("", 12)).grid(
        row=0, column=0, sticky="w")
    ttk.Label(frame, text=description, font=("", 9)).grid(
        row=1, column=0, sticky="w"
    )
    selected = tk.BooleanVar(value=default_selected)
    ttk.Checkbutton(frame, variable=selected).grid(
        row=0, column=1, sticky="e", rowspan=2
    )
    # 设置列权重，让column=1可扩展
    frame.columnconfigure(1, weight=1)

    result = tk.StringVar()
    result_label = tk.Label(root, textvariable=result, fg="blue")
    result_label.pack(side="top", fill="x")

    return frame, selected, result


class MainWindow:
    def __init__(self):
        self.sync_result = None
        self.backup_result = None
        self.check_result = None
        bus_msg.task_finished.connect(self.execute_result)

    def execute_result(self, sender, **kwargs):
        tag = kwargs.get("tag")
        result = kwargs.get("result")
        if result is None:
            result_msg = "--- 任务完成 ---"
        else:
            result_msg = "--- 任务结果 ---\n" + result
        if tag == sync.TAG:
            self.sync_result.set(result_msg)
        elif tag == backups.TAG:
            self.backup_result.set(result_msg)
        elif tag == check.TAG:
            self.check_result.set(result_msg)


    def execute(self, root, from_folder, to_folder, sync_selected, backup_selected, check_selected):
        """确认选择并显示结果"""
        from_path = from_folder.get()
        to_path = to_folder.get()
        sync_action = sync_selected.get()
        backup_action = backup_selected.get()
        check_action = check_selected.get()

        LocalSettings.NEED_BACKUPS_DIR = from_path
        LocalSettings.SAVE_DIR = to_path

        if sync_action and not backup_action and not check_action:
            if not to_path:
                messagebox.showwarning("提示", "请先选择存储目录")
            else:
                response = messagebox.askyesno(
                    "提示", f"是否维护目录[{to_path}]数据，更新索引"
                )
                if response:
                    print("执行 sync")
                    progress_bar = PopupProgressBar(root, "文件处理进度")
                    progress_bar.update_stage(f"维护数据")
                    sync.work()
                    progress_bar.wait_for_completion()
                else:
                    print("用户选择了取消 sync")
        else:
            if not from_path:
                messagebox.showwarning("提示", "请先选择备份目录")
            elif not to_path:
                messagebox.showwarning("提示", "请先选择存储目录")
            if from_path and to_path:
                if from_path == to_path:
                    messagebox.showwarning("提示", "备份目录和存储目录不可是同一个")
                else:
                    msg = "请选择操作"
                    if backup_action:
                        msg = f"是否要将目录[{from_path}]备份到[{to_path}]"
                    elif sync_action:
                        msg = f"是否维护目录[{to_path}]数据，更新索引"
                    elif check_action:
                        msg = f"是否检查目录[{from_path}]备份情况"
                    response = messagebox.askyesno(
                        "提示", msg
                    )
                    if response:
                        print("执行 sync " + str(sync_action) + ", backup " + str(backup_action) + ", check " + str(
                            check_action))
                        action_count = len(list(filter(lambda b: b, [sync_action, backup_action, check_action])))
                        index = 0
                        progress_bar = PopupProgressBar(root, "文件处理进度")
                        if sync_action:
                            index += 1
                            progress_bar.update_stage(f"{index}/{action_count} 维护数据")
                            sync.work()
                        if backup_action:
                            index += 1
                            progress_bar.update_stage(f"{index}/{action_count} 备份数据")
                            backups.work()
                        if check_action:
                            index += 1
                            progress_bar.update_stage(f"{index}/{action_count} 检查数据")
                            check.check_backups()
                        progress_bar.wait_for_completion()
                    else:
                        print("用户选择了取消")

    def ui(self):
        root = tk.Tk()
        root.title("文件备份")
        # root.geometry("300x300")
        frame_container = ttk.Frame(root)
        frame_container.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        frame_settings = ttk.Frame(frame_container)
        frame_settings.grid(row=0, column=0, padx=10)
        frame_actions = ttk.Frame(frame_container)
        frame_actions.grid(row=0, column=1, padx=10)

        frame_from_folder, from_folder = frame_select_folder(frame_settings, label="备份目录")
        frame_to_folder, to_folder = frame_select_folder(frame_settings, label="存储目录")
        frame_from_folder.pack(side="top", fill="x")
        from_to_flag = tk.Label(frame_settings, text="↓")
        from_to_flag.pack(side="top", fill="x")
        frame_to_folder.pack(side="top", fill="x")

        frame_sync_action, sync_selected, self.sync_result = frame_action(frame_actions, "维护数据",
                                                        description="维护存储目录数据，更新索引\n优化备份速度")
        frame_sync_action.pack(side="top", fill="x")

        frame_backup_action, backup_selected, self.backup_result = frame_action(frame_actions, "备份数据",
                                                            description="从备份目录复制数据到存储目录",
                                                            default_selected=True)
        frame_backup_action.pack(side="top", fill="x", pady=5)

        frame_check_action, check_selected, self.check_result = frame_action(frame_actions, "检查数据",
                                                          description="检查备份数据操作的结果")
        frame_check_action.pack(side="top", fill="x", pady=5)

        ttk.Button(frame_actions, text="执行", width=10,
                   command=lambda: self.execute(root, from_folder, to_folder, sync_selected, backup_selected,
                                           check_selected)).pack(side="right", fill="x")
        root.mainloop()


if __name__ == '__main__':
    MainWindow().ui()
