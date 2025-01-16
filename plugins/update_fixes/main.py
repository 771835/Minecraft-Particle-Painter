import plugins.plugin_api as api
import plugins.plugin_api.lib as lib

__plugindir__=lib.get_plugin_path()
class Run(api.Plugin):
    def __init__(self):
        self.plugin_name= "UpdateFixes"
        self.__type__ = "plugin"
        self.__version__ = "1.0.0"
        self.__description__ = "This is an update patch installer."
        self.__author__ = "7718358"
    def run(self):
        if lib.get_safe_mode():
            return
        else:
            print("安全模式为关闭")