from blinker import Signal

# 1. 定义信号（相当于“消息类型”）
task_progress_updated = Signal()  # 信号可携带 progress 和 status 参数
task_finished = Signal()
