import os.path
import sys
from pathlib import Path
import functools
# 将项目的根目录添加到 sys.path 中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config_manager import YamlFileManager
import builtins
class Plugin:
    def __init__(self,safeMode:bool=True,plugin_root='./'):
        self.plugin_name= "name"
        self.__type__ = "plugin"
        self.__version__ = "1.0.0"
        self.__description__ = "This is a plugin template."
        self.__author__ = "Your name"
        self.__website__ = "https://www.example.com/website"
    def run(self):
        pass

    def initialize(self):
        pass
    
    def exit_plugin(self):
        pass
    
    def get_plugin_name(self):
        return self.__name__
    
    def get_plugin_type(self):
        return self.__type__
    
    def get_plugin_version(self):
        return self.__version__
    
    def get_plugin_description(self):
        return self.__description__
    
    def get_plugin_author(self):
        return self.__author__
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)  # 调用父类的 __init_subclass__
        ALLOWED_MODULES = {'plugin_api','config_manager'} # 允许导入的模块
        # 保存原始的 import
        original_import = builtins.__import__
        # 重写 import
        def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name in ALLOWED_MODULES:
                return original_import(name, globals, locals, fromlist, level)
            raise ImportError(f"Importing module '{name}' is not allowed.")
        builtins.__import__ = custom_import
# 获得根目录(已弃用,请使用 get_project_root)
def get_root_path() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
# 获取项目根目录
def get_project_root() -> str|None:
    current_dir = Path(__file__).resolve()
    while current_dir != current_dir.parent:  # 一直向上直到达到根目录
        if (current_dir / 'config.yaml').exists():
            return current_dir
        current_dir = current_dir.parent
    return None
# 获取安全模式
def get_safe_mode() -> bool :
    mode=YamlFileManager(os.path.join(get_project_root(),"config.yaml"))
    return mode.get("settings",True).get("safeMode",True)

class YamlManager(YamlFileManager):
    def __init__(self, file_path,yaml_data=None):
        super().__init__(file_path,encoding='utf-8',yaml_data=yaml_data)
        self.safeMode = get_safe_mode()
        return
    @property
    def _write_yaml(self):
        if self.safeMode:
            raise PermissionError("Do not have permission to write file, because the safe mode is enabled.")
        super()._write_yaml()
    @property
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.safeMode:
            raise PermissionError("Do not have permission to write file, because the safe mode is enabled.")
        self._write_yaml()
    @property
    def save(self):
        if self.safeMode:
            raise PermissionError("Do not have permission to write file, because the safe mode is enabled.")
        return super().save()
    @property
    def get_safeMode(self):
        return self.safeMode
    def __setattr__(self, name, value):
        # 定义可被修改的属性
        saft_name=['safeMode','yaml_data','file_path','encoding','is_closed']
        if name in saft_name:
            return super().__setattr__(name, value)
        if self.safeMode:
            raise PermissionError("Do not have permission to write file, because the safe mode is enabled.")
        raise AttributeError("can't set attribute")
def exit_plugin(code=0):
    sys.exit(code)