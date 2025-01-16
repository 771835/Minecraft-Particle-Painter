import numpy as np
import matplotlib.pyplot as plt
from mcpartmath  import calculate_circle_points
# 示例：计算圆心在原点，半径为5，精度为1000的圆的坐标
radius = 5
center = (0, 0)
precision = 1000  # 精度越高，点越多

# 计算圆上所有点的坐标
x_points, y_points = calculate_circle_points(radius, center, precision)

# 输出前几个点坐标
print("前几个圆上点的坐标：")
for i in range(5):
    print(f"({x_points[i]:.2f}, {y_points[i]:.2f})")

# 可视化圆
plt.figure(figsize=(6, 6))
plt.plot(x_points, y_points, label="Circle")
plt.scatter(x_points, y_points, color='red', s=1)
plt.gca().set_aspect('equal', adjustable='box')
plt.title(f"Circle with radius {radius} and center {center}")
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True)
plt.show()
