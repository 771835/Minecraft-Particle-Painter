import copy
import types

class FakeSysModule:
    def __init__(self,argv=[],byteorder='little',dont_write_bytecode=False,executable='/usr/bin/python',flags=None,platform='win32',version='3.10.0',version_info=(3, 10, 0, 'final', 0),warnoptions=None,modules={}):
        self.argv = argv
        self.byteorder = byteorder
        self.dont_write_bytecode = dont_write_bytecode
        self.executable = executable
        self.flags = flags
        self.platform = platform
        self.version = version
        self.version_info = version_info
        self.warnoptions = warnoptions
        self.__stderr__ = None
        self.__stdin__ = None
        self.__stdout__ = None
        self.modules = {"sys": self, "os": None}.update(modules)
        
    def exit(self, code=0):
        raise SystemExit(code)

    def setrecursionlimit(self, limit):
        raise NotImplementedError("setrecursionlimit is not allowed in the sandbox")

    def getrecursionlimit(self):
        return 1000
    getdefaultencoding = lambda self: 'utf-8'
    
