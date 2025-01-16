from pathlib import Path

class SafeOpen:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir).resolve()  # 确保 base_dir 是绝对路径

    def check_path(self, filename):
        abs_path = Path(filename).resolve()  # 获取真实路径，解析符号链接
        
        # 使用 pathlib 的 in 判断文件是否位于 base_dir 的范围内
        if self.base_dir not in abs_path.parents:
            raise PermissionError(f"文件路径 {filename} 不在允许的范围内！")
        
        return abs_path

    def open(self, filename, mode='r', *args, **kwargs):
        abs_path = self.check_path(filename)
        try:
            file = open(abs_path, mode, *args, **kwargs)
            return file
        except Exception as e:
            print(f"打开文件 {filename} 时发生错误: {e}")
            return None
if __name__ == '__main__':
    # 使用示例
    base_directory = '/allowed/directory'
    safe_open = SafeOpen(base_directory)

    file = safe_open.open('/allowed/directory/test.txt', 'r')
    if file:
        print(file.read())
    else:
        print("文件打开失败。")
