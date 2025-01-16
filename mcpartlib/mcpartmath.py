import numpy as np

def calculate_circle_points(radius, center=(0, 0), precision=100):
    """
    计算圆上所有点的坐标。
    
    :param radius: 圆的半径
    :param center: 圆心坐标 (h, k)，默认为原点 (0, 0)
    :param precision: 精度，步长越小，点越多，默认100
    :return: 圆上所有点的坐标 (x, y)
    """
    # 生成从 0 到 2π 的角度，步长根据精度控制
    angles = np.linspace(0, 2 * np.pi, precision)
    
    # 计算圆上所有点的坐标
    x_coords = center[0] + radius * np.cos(angles)
    y_coords = center[1] + radius * np.sin(angles)
    
    # 返回计算出来的坐标列表
    return x_coords, y_coords

def calculate_ellipse_points(a, b, center=(0, 0), precision=100):
    """
    计算椭圆上所有点的坐标。

    :param a: 椭圆的长半轴（水平轴半径）
    :param b: 椭圆的短半轴（垂直轴半径）
    :param center: 椭圆的中心坐标 (h, k)，默认为原点 (0, 0)
    :param precision: 精度，步长越小，点越多，默认100
    :return: 椭圆上所有点的坐标 (x, y)
    """
    # 生成从 0 到 2π 的角度，步长根据精度控制
    angles = np.linspace(0, 2 * np.pi, precision)
    
    # 计算椭圆上所有点的坐标
    x_coords = center[0] + a * np.cos(angles)
    y_coords = center[1] + b * np.sin(angles)
    
    return x_coords, y_coords

def line_intersection(p1, p2, p3, p4):
    """
    计算两条线段 (p1, p2) 和 (p3, p4) 的交点。
    
    :param p1: 线段1的起点
    :param p2: 线段1的终点
    :param p3: 线段2的起点
    :param p4: 线段2的终点
    :return: 交点坐标（x, y），如果没有交点则返回None
    """
    # 解线段交点公式
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # 平行或重合，无法求交点

    intersect_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    intersect_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

    return (intersect_x, intersect_y)
def calculate_hexagram_points(radius, precision=100):
    """
    计算六芒星上所有点的位置，精度控制步长，步长越小，点越多。
    
    :param radius: 六芒星的半径
    :param precision: 精度，步长越小，点越多，默认100
    :return: 六芒星上所有点的坐标 (x, y)
    """
    # 计算六个顶点的位置
    angles = np.linspace(0, 2 * np.pi, 7)  # 六个顶点的角度
    hexagon_points = [(radius * np.cos(angle), radius * np.sin(angle)) for angle in angles]

    # 计算六芒星内的所有点
    hexagram_points = []

    # 计算第一组三角形的点
    for i in range(3):
        # 顶点间插值生成多个点
        p1 = hexagon_points[i]
        p2 = hexagon_points[(i + 1) % 6]
        for t in np.linspace(0, 1, precision):
            x = (1 - t) * p1[0] + t * p2[0]
            y = (1 - t) * p1[1] + t * p2[1]
            hexagram_points.append((x, y))

    # 计算第二组三角形的点
    for i in range(3, 6):
        # 顶点间插值生成多个点
        p1 = hexagon_points[i]
        p2 = hexagon_points[(i + 1) % 6]
        for t in np.linspace(0, 1, precision):
            x = (1 - t) * p1[0] + t * p2[0]
            y = (1 - t) * p1[1] + t * p2[1]
            hexagram_points.append((x, y))

    # 返回六芒星的所有点
    return hexagram_points

def find_closest_point_np(points, x_target, y_target):
    """通过欧几里得距离寻找最近的x,y点，使用NumPy实现。
    :param points: 点列表
    :param x_target: 目标点的x坐标
    :param y_target: 目标点的y坐标
    :return: 最近的点的坐标 (x, y)
    """
    # 将点列表转换为 NumPy 数组
    points = np.array(points)
    
    # 计算每个点与目标点的欧几里得距离
    distances = np.sqrt((points[:, 0] - x_target) ** 2 + (points[:, 1] - y_target) ** 2)
    
    # 找到距离最小的点的索引
    closest_index = np.argmin(distances)
    
    # 返回最近的点
    return tuple(points[closest_index])

def generate_line_points(p1, p2, precision):
    """
    在两点之间插值，生成一条线段上的多个点
    
    :param p1: 线段的起始点 (x1, y1)
    :param p2: 线段的结束点 (x2, y2)
    :param precision: 插值精度，控制每条边上的点数
    :return: 插值后的点列表 [(x, y), ...]
    """
    t_values = np.linspace(0, 1, precision)
    return [( (1 - t) * p1[0] + t * p2[0], (1 - t) * p1[1] + t * p2[1]) for t in t_values]

def calculate_hexagram_points(radius, precision=100):
    """
    计算六芒星的所有点，由两个交错的三角形组成
    
    :param radius: 六芒星的半径
    :param precision: 插值精度，控制每条边上的点数
    :return: 六芒星的所有点的坐标 [(x, y), ...]
    """
    # 计算六个顶点的位置，按 60° 间隔
    angles = np.linspace(0, 2 * np.pi, 7)  # 六个顶点的角度，最后一个点与第一个点重合
    hexagon_points = [(radius * np.cos(angle), radius * np.sin(angle)) for angle in angles]

    # 六芒星的两个交错三角形的点集
    hexagram_points = []
    
    # 交错的三角形1（使用顶点0, 2, 4）
    hexagram_points.extend(generate_line_points(hexagon_points[0], hexagon_points[2], precision))
    hexagram_points.extend(generate_line_points(hexagon_points[2], hexagon_points[4], precision))
    hexagram_points.extend(generate_line_points(hexagon_points[4], hexagon_points[0], precision))
    
    # 交错的三角形2（使用顶点1, 3, 5）
    hexagram_points.extend(generate_line_points(hexagon_points[1], hexagon_points[3], precision))
    hexagram_points.extend(generate_line_points(hexagon_points[3], hexagon_points[5], precision))
    hexagram_points.extend(generate_line_points(hexagon_points[5], hexagon_points[1], precision))

    return hexagram_points
