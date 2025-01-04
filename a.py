import asyncio

# 定义一个异步任务
async def async_task(name, delay):
    print(f"Task {name} starting...")
    await asyncio.sleep(delay)  # 模拟 I/O 操作（如网络请求、文件读取等）
    print(f"Task {name} completed after {delay} seconds.")

# 创建一个事件循环并运行任务
async def main():
    # 使用 asyncio.gather 来并发执行多个任务
    await asyncio.gather(
        async_task("A", 2),
        async_task("B", 1),
        async_task("C", 3)
    )

# 执行主函数
if __name__ == "__main__":
    asyncio.run(main())
