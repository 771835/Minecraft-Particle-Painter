# 警告：该沙盒环境并不安全，仅仅用于防御简单的恶意代码，请尽量不要安装不信任的插件
import plugins.load_plugin.sandbox
from pathlib import Path
class PluginLoader:
    def __init__(self):
        print("警告：该沙盒环境并不安全，仅仅用于防御简单的恶意代码，请尽量不要安装不信任的插件")
        print("Warning: This sandbox environment is not secure, only used to defend simple malicious code, please try not to install untrusted plugins")
        for plugin_path in Path('plugins').iterdir():
            if plugin_path.is_dir() and (plugin_path / 'main.py').exists() and plugin_path.name != "load_plugin":
                print(f"加载插件 {plugin_path.name}")
                self.load(plugin_path)
    def load(self,plugin_path):
        with open(plugin_path/'main.py', 'r', encoding='utf-8') as f:
            code = f.read()
            plugins.load_plugin.sandbox.execute_code(code)
if __name__ == "__main__":
    PluginLoader()