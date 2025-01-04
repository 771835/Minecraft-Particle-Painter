import numpy as np
import matplotlib.pyplot as plt
from ..mcpartmath import calculate_ellipse_points

# 示例：计算中心在原点，长半轴为6，短半轴为4，精度为1000的椭圆
a = 6  # 长半轴
b = 4  # 短半轴
center = (0, 0)
precision = 1000  # 精度越高，点越多

# 计算椭圆上所有点的坐标
x_points, y_points = calculate_ellipse_points(a, b, center, precision)

# 输出前几个点坐标
print("前几个椭圆上的点坐标：")
for i in range(5):
    print(f"({x_points[i]:.2f}, {y_points[i]:.2f})")

# 可视化椭圆
plt.figure(figsize=(6, 6))
plt.plot(x_points, y_points, label="Ellipse")
plt.scatter(x_points, y_points, color='red', s=1)
plt.gca().set_aspect('equal', adjustable='box')
plt.title(f"Ellipse with semi-major axis {a} and semi-minor axis {b}")
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True)
plt.show()
