"""对函数库的再次封装"""
from .config_manager import *
import functools
# 获得根目录(已弃用,请使用 get_project_root)
def get_root_path() -> str:
    import os.path
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
# 获取项目根目录
def get_project_root() -> str|None:
    from pathlib import Path
    current_dir = Path(__file__).resolve()
    while current_dir != current_dir.parent:  # 一直向上直到达到根目录
        if (current_dir / 'config.yaml').exists():
            return current_dir
        current_dir = current_dir.parent
    return None
# 获取安全模式
def get_safe_mode() -> bool :
    import os.path
    mode=YamlFileManager(os.path.join(get_project_root(),"config.yaml"))
    return mode.get("settings",True).get("safeMode",True)

def exit_plugin(code=0):
    import sys as _sys
    _sys.exit(code)
def get_globals():
    if not is_check_process():
        return None
    import inspect
    # 获取当前调用堆栈信息
    frame = inspect.currentframe().f_back  # 获取调用者的帧
    caller_locals = frame.f_locals  # 获取调用者的局部变量
    caller_globals = frame.f_globals  # 获取调用者的全局变量

    # 获取调用者作用域中的 __builtins__
    caller_builtins = caller_globals.get('__builtins__', None)
    return caller_builtins
def get_plugin_path():
    if not is_check_process():
        return None
    import inspect
    # 获取当前调用堆栈信息
    frame = inspect.currentframe().f_back  # 获取调用者的帧
    caller_locals = frame.f_locals  # 获取调用者的局部变量
    caller_globals = frame.f_globals  # 获取调用者的全局变量

    # 获取调用者作用域中的 __builtins__
    caller_builtins = caller_globals.get('__builtins__', None)
    if '__plugindir__' in caller_builtins:
        return caller_builtins["__plugindir__"]
    else:
        return None
def is_check_process(callback=lambda name,pid:name or pid) -> bool:
    return callback(is_check_process_name,is_check_process_pid)
def is_check_process_name():
    import multiprocessing
    current_process = multiprocessing.current_process()
    if current_process.name == 'MainProcess':
        return False,current_process.name
    else:
        return True,current_process.name
def is_check_process_pid():
    import os
    pid = os.getpid()
    ppid = os.getppid()
    if pid==ppid:
        return False,pid
    else:
        return True,pid