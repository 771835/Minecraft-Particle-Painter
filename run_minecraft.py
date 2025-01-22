import minecraft_launcher_lib
import subprocess
import sys
import os
import mcpartlib.mcdataformat as mcformat
# -----待办----- 重写 minecraft_launcher_lib | 优先级低
class RunMinecraft:
    def __init__(self,minecraft_version:mcformat.MinecraftVersion=mcformat.MinecraftVersion('1.21.4'),
                 minecraft_directory = "./.minecraft",
                 output_processing=lambda line,process : None,argv:list=[]):
        self.minecraft_version=minecraft_version
        self.minecraft_directory=minecraft_directory
        self.output_processing=output_processing
        self.argv=argv
    def install_minecraft(self):
        minecraft_launcher_lib.install.install_minecraft_version(self.minecraft_version(),self.minecraft_directory)
    def get_version_path(self):
        installed_versions_list=minecraft_launcher_lib.utils.get_installed_versions(self.minecraft_directory)
        for i in installed_versions_list:
            if i['id']==self.minecraft_version():
                return os.path.abspath(os.path.join(self.minecraft_directory,"versions",self.minecraft_version()))
        return None
    def get_run_argv(self):
        options = minecraft_launcher_lib.utils.generate_test_options()
        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(self.minecraft_version(), self.minecraft_directory, options)
        print(minecraft_command)
        return minecraft_command
    def run_minecraft(self):
        # 使用 Popen 执行命令并实时输出
        process = subprocess.Popen(
            self.get_run_argv()+self.argv,  # 替换为实际的命令和参数
            stdout=subprocess.PIPE,  # 捕获标准输出
            stderr=subprocess.PIPE,  # 捕获标准错误
            text=True,  # 将输出解码为字符串而不是字节
            encoding='utf-8'  # 强制使用 UTF-8 编码
        )

        # 实时读取输出
        for line in process.stdout:
            self.output_processing(line,process)  # 打印标准输出内容
        for line in process.stderr:
            print(line, end='', file=sys.stderr)  # 打印标准错误内容

        # 等待命令执行完毕
        process.wait()
# -----待办结束----- 
if __name__ == '__main__':
    #quit()
    mc=RunMinecraft()
    mc.run_minecraft()