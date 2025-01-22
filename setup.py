import sys
import os
import platform
import subprocess
import locale
import zipfile

install=False

default_language='zh_cn'

# 获取当前系统的语言和区域设置
print(platform.python_version())
language, encoding = locale.getdefaultlocale()
encoding = locale.getencoding()
language=os.getenv('LANG', 'zh_cn').split('.')[0].lower()
print(f"当前系统语言: {language}")
print(f"当前系统编码: {encoding}")


def check_requirements(requirements_file='requirements.txt'):
    # 读取 requirements.txt 文件中的内容
    with open(requirements_file, 'r') as f:
        required_libraries = f.readlines()

    # 去掉多余的空白符和注释
    required_libraries = [lib.strip() for lib in required_libraries if lib.strip() and not lib.strip().startswith('#')]

    missing_libraries = []

    for lib in required_libraries:
        # 去除前后空格并拆分库名和版本（如果有的话）
        lib = lib.strip()
        if '==' in lib:
            package_name, version = lib.split('==')
        else:
            package_name, version = lib, None
        package_name=package_name.strip()
        # 尝试通过 pip 查询是否已安装
        try:
            # 执行 pip show 命令，查询库是否已安装
            result = subprocess.run(['pip', 'show', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:  # 如果 returncode 不为0，说明未找到该包
                missing_libraries.append(lib)
            else:
                # 如果有版本限制，检查版本是否匹配
                if version:
                    # 获取已安装的版本
                    installed_version = next(line for line in result.stdout.decode(encoding).splitlines() if line.startswith('Version:')).split(' ')[1]
                    if installed_version != version.strip():
                        missing_libraries.append(lib)
        except Exception as e:
            missing_libraries.append(lib)
            raise

    if missing_libraries:
        print("The following libraries are not installed or have mismatched versions:")
        for lib in missing_libraries:
            print(f"- {lib}")
    else:
        print("All libraries are installed and the versions are matched.")
    return missing_libraries

def is_virtualenv():
    return (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def is_docker():
    """ 检测是否在 Docker 容器中 """
    current_platform = platform.system()
    if current_platform == "Linux":
        try:
            with open('/proc/1/cgroup', 'rt') as f:
                if 'docker' in f.read():
                    return True
        except FileNotFoundError:
            return False
    elif current_platform == "Darwin":
        # macOS 使用命令行工具 docker info 进行检测
        try:
            result = subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                return "Docker" in result.stdout.decode("utf-8")
        except FileNotFoundError:
            return False
    elif current_platform == "Windows":
        # 在 Windows 上通过 Docker API 检测
        try:
            result = subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                return "Docker" in result.stdout.decode("utf-8")
        except FileNotFoundError:
            return False
    return False

def is_conda_env():
    """ 检测是否在 Conda 虚拟环境中 """
    return 'CONDA_PREFIX' in os.environ

def is_pipenv_env():
    """ 检测是否在 Pipenv 虚拟环境中 """
    return os.path.exists('Pipfile')

def extract_jar_folder(jar_path, target_folder, folder_name="META-INF"):
    """
    提取 JAR 文件中的特定文件夹资源到指定文件夹

    :param jar_path: JAR 文件路径
    :param target_folder: 提取到的目标文件夹
    :param folder_name: 需要提取的文件夹名称（默认为 "META-INF"）
    :return: None
    """
    # 检查目标文件夹是否存在，如果不存在则创建
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 打开 JAR 文件
    with zipfile.ZipFile(jar_path, 'r') as jar:
        # 获取 JAR 文件中所有文件的列表
        file_list = jar.namelist()

        # 遍历所有文件
        for file in file_list:
            # 判断是否是特定文件夹内的文件
            if file.startswith(folder_name):
                # 提取文件
                output_path = os.path.join(target_folder, file)
                output_dir = os.path.dirname(output_path)

                # 如果文件夹路径不存在，则创建它
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                # 提取文件内容
                with open(output_path, 'wb') as f:
                    f.write(jar.read(file))

                print(f"已提取文件: {file} 到 {output_path}")
def extract_folder_from_jar(jar_path, target_folder, folder_name="META-INF"):
    """
    提取 JAR 文件中指定文件夹下的文件，不包含文件夹结构

    :param jar_path: JAR 文件路径
    :param target_folder: 提取到的目标文件夹
    :param folder_name: 需要提取的文件夹名称（默认为 "META-INF"）
    :return: None
    """
    # 检查目标文件夹是否存在，如果不存在则创建
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 打开 JAR 文件
    with zipfile.ZipFile(jar_path, 'r') as jar:
        # 获取 JAR 文件中所有文件的列表
        file_list = jar.namelist()

        # 过滤出指定文件夹内的文件
        folder_prefix = folder_name + '/'
        filtered_files = [f for f in file_list if f.startswith(folder_prefix) and not f.endswith('/')]

        # 遍历所有文件
        for file in filtered_files:
            # 获取文件名，忽略文件夹结构
            output_path = os.path.join(target_folder, os.path.basename(file))

            # 提取文件内容
            with open(output_path, 'wb') as f:
                f.write(jar.read(file))

            print(f"已提取文件: {file} 到 {output_path}")

def exit_(exit_code=1):
    
    if config.get_data()['settings']['installMinecraft'] == False:
        config['settings']['installMinecraft']=install
    else:
        if not isinstance(config.get_data()['settings']['installMinecraft'],bool):
            config['settings']['installMinecraft']=install
            
    if config['settings']['language']!=language:
        if os.path.exists(os.path.join(config['paths']['languageDirectory'],config['settings']['language']+'json')):
            config['settings']['language']=language
        else:
            config['settings']['language']=default_language
    print("language",config['settings']['language'])
    config.close()
    sys.exit(exit_code)
if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        print("This is a Nuitka-compiled program")
    else:
        print("This is not a Nuitka-compiled program")
    if not (is_virtualenv() or is_conda_env() or is_pipenv_env()):
        print("It is recommended to install the program in a virtual environment.")# 推荐在虚拟环境下安装该程序
        install=input("Continue with the installation (Yes/No)").lower()# 继续安装(是/否)
        if install == 'yes' or install == 'y' or install == '是' or install == '好' or install == '是的' or install == '好的' :
            install=True
        else:
            install=False
            exit_()
    else:
        install=True
    if check_requirements():
        print("To install the dependency library, please run: python -m pip install -r requirements.txt")
        install=False
        sys.exit(1)
    import run_minecraft
    mc=run_minecraft.RunMinecraft()
    minecraft_path=mc.get_version_path()
    if not minecraft_path:
        print("A Java version of Minecraft is required, otherwise the software cannot be used. Do you want to install it? (Yes/No)")
        install=input().lower()
        if install == 'yes' or install == 'y':
            install=True
            import threading,time
            print_thread=threading.Thread(target=lambda:[[print('.',end=''),time.sleep(20)] for i in range(14)])
            print_thread.start()
            a=time.time()
            mc.install_minecraft()
            print('.\n',time.time()-a)
        else:
            install=False
    import config_manager
    config=config_manager.YamlFileManager("config.yaml")
    extract_folder_from_jar(os.path.abspath(os.path.join(mc.get_version_path(),mc.minecraft_version()+".jar")),
                            config['paths']["particlesTexturesDirectory"],'assets/minecraft/textures/particle')
    extract_folder_from_jar(os.path.abspath(os.path.join(mc.get_version_path(),mc.minecraft_version()+".jar")),
                            config['paths']["particlesJsonDirectory"],'assets/minecraft/particles')

    exit_(0)