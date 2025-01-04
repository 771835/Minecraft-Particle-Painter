from plugins.plugin_api import plugin
class Run(plugin.Plugin):
    def __init__(self):
        self.plugin_name= "PluginAPI"
        self.__type__ = "library"
        self.__version__ = "1.0.0"
        self.__description__ = "This is a plugin to provide some APIs for other plugins."
        self.__author__ = "771835"
        self.__website__ = None
    def run(self):
        print("This is a plugin to provide some APIs for other plugins.")