import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

# 输入参数
wafer_diameter = 300  # 12英寸对应300mm
edge_removal = 3.2  # 边缘去除量
flat_height = 17 # Flat区域高度

die_size_x = 5.4  # 芯片X尺寸
die_size_y = 5.6  # 芯片Y尺寸
boarder_size = 0  # 边界尺寸
seal_ring = 0.022  # 密封环宽度
scribeline_x = 0.12  # X方向切割道宽度
scribeline_y = 0.12  # Y方向切割道宽度

# 计算步长
step_size_x = die_size_x + 2 * boarder_size + 2 * seal_ring + scribeline_x
step_size_y = die_size_y + 2 * boarder_size + 2 * seal_ring + scribeline_y

# 起始偏移量
matrix_offset_x = -0.3
matrix_offset_y = -2.40506

# 计算有效半径和Flat区域的阈值
effective_radius = (wafer_diameter / 2) - edge_removal  # 146.8 mm
y_threshold = - (effective_radius - flat_height)  # -139.8 mm (Flat区域的上边界)


def is_in_circle(x, y):
    """判断点是否在有效圆内"""
    distance_squared = x ** 2 + y ** 2
    return 1 if distance_squared <= effective_radius ** 2 else -1


def is_outside_flat(y):
    """判断点的y坐标是否在Flat区域外（y >= -139.8mm）"""
    return y >= y_threshold  # y_threshold = -139.8


def is_in_effective_area(x, y):
    """综合判断点是否在有效区域"""
    return is_in_circle(x, y) == 1 and is_outside_flat(y)


def generate_spiral_points(start_x, start_y, step_x, step_y):
    """生成逆时针螺旋网点坐标"""
    points = []
    x, y = start_x, start_y
    points.append((x, y))

    # 定义方向和初始参数
    directions = [
        (step_x, 0),  # 右
        (0, -step_y),  # 上
        (-step_x, 0),  # 左
        (0, step_y)  # 下
    ]
    current_dir = 0
    steps = 1

    while True:
        for _ in range(2):  # 每两个方向后增加步长
            dx, dy = directions[current_dir]
            for _ in range(steps):
                x += dx
                y += dy
                points.append((x, y))
                # 检查是否超出晶圆直径
                if (x ** 2 + y ** 2) > 2*(wafer_diameter / 2) ** 2:
                    return points
            current_dir = (current_dir + 1) % 4
        steps += 1


def evaluate_grid_points(points, step_x, step_y):
    """评估每个网点的覆盖区域状态"""
    grid_info = {}
    for idx, (x, y) in enumerate(points):
        # 计算方形的四个顶点
        half_x = step_x / 2
        half_y = step_y / 2
        vertices = [
            (x - half_x, y - half_y),
            (x + half_x, y - half_y),
            (x + half_x, y + half_y),
            (x - half_x, y + half_y)
        ]
        # 判断顶点是否在有效区域
        in_effective = [is_in_effective_area(vx, vy) for vx, vy in vertices]
        count_effective = sum(in_effective)

        if count_effective == 4:
            grid_info[idx] = {'status': '内部', 'fill': 'black'}
        elif count_effective == 0:
            grid_info[idx] = {'status': '外部', 'fill': None}
        else:
            grid_info[idx] = {'status': '部分', 'fill': 'pink'}
    return grid_info


def plot_grid(points, grid_info, step_x, step_y):
    """可视化网点和覆盖区域"""
    fig, ax = plt.subplots(figsize=(10, 10))

    # 绘制晶圆边界
    wafer_circle = Circle((0, 0), wafer_diameter / 2, color='gray', fill=False, linestyle='--', label='晶圆边界')
    ax.add_patch(wafer_circle)

    # 绘制有效区域边界
    effective_circle = Circle((0, 0), effective_radius, color='blue', fill=False, label='有效区域边界')
    ax.add_patch(effective_circle)

    # 绘制Flat区域标记线（修正位置）
    flat_width = 2 * ((effective_radius ** 2 - (effective_radius - flat_height) ** 2) ** 0.5)
    plt.plot([-flat_width / 2, flat_width / 2], [y_threshold, y_threshold], 'r-', linewidth=2, label='Flat区域边界')

    # 绘制网点
    for idx, (x, y) in enumerate(points):
        info = grid_info.get(idx, {'fill': None})
        if info['fill']:
            rect = Rectangle((x - step_x / 2, y - step_y / 2), step_x, step_y,
                             fill=info['status'] == '部分',
                             edgecolor=info['fill'],
                             facecolor=info['fill'] if info['status'] == '部分' else None,
                             alpha=0.5)
            ax.add_patch(rect)

    ax.set_aspect('equal')
    plt.xlim(-wafer_diameter / 2 - 5, wafer_diameter / 2 + 5)
    plt.ylim(-wafer_diameter / 2 - 5, wafer_diameter / 2 + 5)
    plt.title("晶圆有效区域覆盖情况\n(黑色:完全覆盖, 粉色:部分覆盖)")
    plt.xlabel("X (mm)")
    plt.ylabel("Y (mm)")
    plt.legend()
    plt.grid(True)
    plt.show()


# 主程序
if __name__ == "__main__":
    # 生成螺旋网点
    spiral_points = generate_spiral_points(matrix_offset_x, matrix_offset_y, step_size_x, step_size_y)

    # 评估网点状态
    grid_status = evaluate_grid_points(spiral_points, step_size_x, step_size_y)

    # 输出结果
    print(f"生成的网点总数: {len(spiral_points)}")
    print("\n前5个网点坐标和状态:")
    for i in range(5):
        print(f"网点{i}: 坐标({spiral_points[i][0]:.2f}, {spiral_points[i][1]:.2f}) - {grid_status[i]['status']}")

    # 可视化
    plot_grid(spiral_points, grid_status, step_size_x, step_size_y)