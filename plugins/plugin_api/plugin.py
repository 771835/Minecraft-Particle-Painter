from .lib import *
class Plugin:
    def __init__(self):
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
        pass