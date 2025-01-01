import unittest

# 使用 discover 方法自动发现并运行测试
suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')

# 创建一个测试运行器并执行
runner = unittest.TextTestRunner()
runner.run(suite)