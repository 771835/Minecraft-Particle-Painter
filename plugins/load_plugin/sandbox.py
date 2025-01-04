import sys
import os
import builtins
import time
import multiprocessing
import types
import copy

# 将项目的根目录添加到 sys.path 中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from plugins.plugin_api import plugin
#class SafeSandbox:
#def __init__(self):
safe_modules = {'plugins.plugin_api',"plugins"} # 允许导入的模块
# 重写 import
def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name in safe_modules or not plugin.get_safe_mode():
        return __import__(name, globals, locals, fromlist, level)
    # 提示用户导入模块不被允许，或只能在顶级代码中导入模块
    raise ImportError(f"Importing module '{name}' is not allowed, or only allowed in top-level code.")
# 定义一个限制的内建函数环境
safe_builtins = {
    'print': print,   # 允许用户使用 print 函数
    'range': range,   # 允许用户使用 range 函数
    'len': len,       # 允许用户使用 len 函数
    'list': list,     # 允许用户使用 list 函数
    'tuple': tuple,   # 允许用户使用 tuple 函数
    'dict': dict,     # 允许用户使用 dict 函数
    'set': set,       # 允许用户使用 set 函数
    'abs': abs,       # 允许用户使用 abs 函数
    'all': all,       # 允许用户使用 all 函数
    'any': any,       # 允许用户使用 any 函数
    'max': max,       # 允许用户使用 max 函数
    'min': min,       # 允许用户使用 min 函数
    'sum': sum,       # 允许用户使用 sum 函数
    'sorted': sorted, # 允许用户使用 sorted 函数
    'zip': zip,       # 允许用户使用 zip 函数
    'filter': filter, # 允许用户使用 filter 函数
    'map': map,       # 允许用户使用 map 函数
    'enumerate': enumerate, # 允许用户使用 enumerate 函数
    'int': int,       # 允许用户使用 int 函数
    'float': float,   # 允许用户使用 float 函数
    'str': str,       # 允许用户使用 str 函数
    'bool': bool,     # 允许用户使用 bool 函数
    'hasattr': hasattr, # 允许用户使用 hasattr 函数
    'type': type,       # 允许用户使用 type 函数
    'issubclass': issubclass, # 允许用户使用 issubclass 函数
    'isinstance': isinstance, # 允许用户使用 isinstance 函数
    'time': time,     # 允许用户使用 time 模块
    'os': None,       # 禁止用户使用 os 模块
    'sys': None,      # 禁止用户使用 sys 模块
    '__build_class__': __build_class__,  # 允许用户使用 __build_class__ 函数
    '__name__': 'plugin',  # 允许用户使用 __name__ 变量
    '__import__': custom_import,  # 允许用户使用 __import__ 函数
    'sys_path': sys.path,  # 允许用户访问 sys.path 变量
    'ImportError': ImportError,  # 允许用户访问 ImportError 异常
    'Exception': Exception,      # 允许用户访问 Exception 异常
    'SystemExit': SystemExit,    # 允许用户访问 SystemExit 异常
    'KeyboardInterrupt': KeyboardInterrupt,  # 允许用户访问 KeyboardInterrupt 异常
    'FileNotFoundError': FileNotFoundError,  # 允许用户访问 FileNotFoundError 异常
    'NotImplementedError': NotImplementedError,  # 允许用户访问 NotImplementedError 异常
    'PermissionError': PermissionError,  # 允许用户访问 PermissionError 异常
    'OSError': OSError,  # 允许用户访问 OSError 异常
    'ValueError': ValueError,  # 允许用户访问 ValueError 异常
    'TypeError': TypeError,    # 允许用户访问 TypeError 异常
    'ZeroDivisionError': ZeroDivisionError,  # 允许用户访问 ZeroDivisionError 异常
    'ArithmeticError': ArithmeticError,  # 允许用户访问 ArithmeticError 异常
    'None': None,        # 允许用户使用 NoneType 类型
    # 其他内建函数...
    }

# 设置一个安全的假 sys 模块，禁止用户访问 os 和 sys 模块
import plugins.load_plugin.fake_sys_module as Fsys
_sys=Fsys.FakeSysModule(modules={'ctypes':None})
# 设置全局作用域
safe_globals = {
    '__builtins__': safe_builtins,  # 限制用户代码只能访问这些内建函数
    'allowed_function': print,      # 允许用户使用的其他函数
    'plugin': plugin, # 允许用户使用 plugin 模块
    'sys': _sys,      # 允许用户使用修改后的 sys 模块
}

def user_code_wrapper(module_code):
    """
    通过 exec 执行用户代码，限制其访问的内建函数和模块。
    """
    try:
        exec(module_code, safe_globals)  # 执行用户代码，限制其访问的内建函数
        # 获取用户代码中的 run 类
        run_class = safe_globals.get('Run')
        if issubclass(run_class,plugin.Plugin): 
            run_instance = run_class()
            run_instance.run()
    except Exception as e:
        print(f"执行用户代码时发生异常: {e}")
        sys.exit(1)  # 子进程执行失败，退出
    except SystemExit:
        print("用户代码调用了 sys.exit，但已被拦截。")
        sys.exit(1)  # 退出进程，避免 sys.exit 中断主进程

def execute_code(module_code):
    """
    在子进程中执行用户代码
    """
    process = multiprocessing.Process(target=user_code_wrapper, args=(module_code,))

    process.start()
    return
    # 等待子进程结束，并设置超时机制
    process.join(timeout=10)

    if process.is_alive():
        print("用户代码执行超时，正在强制终止子进程...")
        process.terminate()
        process.join()
    else:
        print("用户代码执行完毕。")


if __name__ == "__main__":
    # 示例：假设我们有如下用户代码（可以动态传入）
    user_code = """

class Run(plugin.Plugin):
    def __init__(self):
        self.__name__= "HelloWorld"
        self.__type__ = "plugin"
        self.__version__ = "1.0.0"
        self.__description__ = "This is a plugin to print 'Hello, world!'"
        self.__author__ = "771835"
    def run(self):
        print("Hello, world!")
        
"""
    execute_code(user_code)