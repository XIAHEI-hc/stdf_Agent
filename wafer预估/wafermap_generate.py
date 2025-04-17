import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import pandas as pd
import math
from openpyxl import Workbook

# 输入参数
wafer_diameter = 300  # 12英寸对应300mm
edge_removal = 3.2
flat_height = 7

die_size_x = 5.4
die_size_y = 5.6
boarder_size = 0
seal_ring = 0.022
scribeline_x = 0.12
scribeline_y = 0.12

step_size_x = die_size_x + 2 * boarder_size + 2 * seal_ring + scribeline_x
step_size_y = die_size_y + 2 * boarder_size + 2 * seal_ring + scribeline_y

matrix_offset_x = -0.3
matrix_offset_y = -2.40506

effective_radius = (wafer_diameter / 2) - edge_removal  # 146.8 mm
y_threshold = - (effective_radius - flat_height)  # -139.8 mm


def is_in_circle(x, y):
    return 1 if x ** 2 + y ** 2 <= effective_radius ** 2 else -1


def is_outside_flat(y):
    return y >= y_threshold


def is_in_effective_area(x, y):
    return is_in_circle(x, y) == 1 and is_outside_flat(y)


def generate_spiral_points(start_x, start_y, step_x, step_y):
    """生成螺旋坐标点及对应的矩阵索引"""
    points = []
    indices = []  # 存储(row,col)索引
    x, y = start_x, start_y
    row, col = 0, 0
    points.append((x, y))
    indices.append((row, col))

    directions = [
        (step_x, 0, (0, 1)),  # 右，列+1
        (0, -step_y, (-1, 0)),  # 上，行-1
        (-step_x, 0, (0, -1)),  # 左，列-1
        (0, step_y, (1, 0)),  # 下，行+1
    ]
    current_dir = 0
    steps = 1

    while True:
        for _ in range(2):
            dx, dy, (drow, dcol) = directions[current_dir]
            for _ in range(steps):
                x += dx
                y += dy
                row += drow
                col += dcol
                points.append((x, y))
                indices.append((row, col))
                if x ** 2 + y ** 2 > 2*(wafer_diameter / 2) ** 2:
                    return points, indices
            current_dir = (current_dir + 1) % 4
        steps += 1


def evaluate_grid_points(points, step_x, step_y):
    grid_info = {}
    valid_count = 0
    validity_list = []

    for idx, (x, y) in enumerate(points):
        half_x = step_x / 2
        half_y = step_y / 2
        vertices = [
            (x - half_x, y - half_y),
            (x + half_x, y - half_y),
            (x + half_x, y + half_y),
            (x - half_x, y + half_y)
        ]
        in_effective = [is_in_effective_area(vx, vy) for vx, vy in vertices]
        count_effective = sum(in_effective)

        if count_effective == 4:
            grid_info[idx] = {'status': '内部', 'valid': 1}
            valid_count += 1
            validity_list.append(1)
        elif count_effective == 0:
            grid_info[idx] = {'status': '外部', 'valid': 0}
            validity_list.append(0)
        else:
            grid_info[idx] = {'status': '部分', 'valid': 1}
            valid_count += 1
            validity_list.append(1)

    return grid_info, valid_count, validity_list


def number_to_excel_column(n):
    """数字转Excel列字母"""
    letters = []
    while n >= 0:
        letters.append(chr(65 + n % 26))
        n = n // 26 - 1
    return ''.join(reversed(letters)) if letters else 'A'


def save_to_excel(points, validity_list, indices, filename="wafer_validity.xlsx"):
    """保存数据到Excel文件"""
    # 创建列表视图
    df_list = pd.DataFrame({
        "Index": range(len(points)),
        "X": [p[0] for p in points],
        "Y": [p[1] for p in points],
        "Valid": validity_list
    })

    # 创建Excel写入器
    writer = pd.ExcelWriter(filename, engine='openpyxl')
    df_list.to_excel(writer, sheet_name="列表视图", index=False)

    # 创建矩阵视图
    wb = writer.book
    ws_matrix = wb.create_sheet("矩阵视图")

    # 计算矩阵范围
    rows = [r for r, c in indices]
    cols = [c for r, c in indices]
    min_row, max_row = min(rows), max(rows)
    min_col, max_col = min(cols), max(cols)

    # 构建矩阵
    matrix = [[None] * (max_col - min_col + 1) for _ in range(max_row - min_row + 1)]
    for i in range(len(validity_list)):
        r, c = indices[i]
        adj_r = r - min_row
        adj_c = c - min_col
        matrix[adj_r][adj_c] = validity_list[i]

    # 从DS137开始写入（D=3, S=18 → 3*26 + 18 = 96 → 列号117）
    start_row = 137
    start_col = 118  # DS列的列号（从1开始计数）

    print(matrix)

    # 写入矩阵数据
    for r in range(len(matrix)):
        for c in range(len(matrix[0])):
            value = matrix[r][c]
            if value is not None:
                ws_matrix.cell(
                    row=start_row + r,
                    column=start_col + c,
                    value=value
                )

    # 保存文件
    writer.save()
    print(f"数据已保存到 {filename}，矩阵视图从DS137单元格开始")


def plot_grid(points, grid_info, step_x, step_y):
    fig, ax = plt.subplots(figsize=(10, 10))

    wafer_circle = Circle((0, 0), wafer_diameter / 2, color='gray', fill=False, linestyle='--')
    ax.add_patch(wafer_circle)

    effective_circle = Circle((0, 0), effective_radius, color='blue', fill=False)
    ax.add_patch(effective_circle)

    flat_width = 2 * ((effective_radius ** 2 - (effective_radius - flat_height) ** 2) ** 0.5)
    plt.plot([-flat_width / 2, flat_width / 2], [y_threshold, y_threshold], 'r-', linewidth=2)

    for idx, (x, y) in enumerate(points):
        info = grid_info.get(idx, {'fill': None})
        if info.get('valid'):
            color = 'black' if info['status'] == '内部' else 'pink'
            rect = Rectangle((x - step_x / 2, y - step_y / 2), step_x, step_y,
                             edgecolor=color, facecolor=color, alpha=0.3)
            ax.add_patch(rect)

    ax.set_aspect('equal')
    plt.xlim(-wafer_diameter / 2 - 5, wafer_diameter / 2 + 5)
    plt.ylim(-wafer_diameter / 2 - 5, wafer_diameter / 2 + 5)
    plt.title("晶圆有效区域覆盖情况")
    plt.xlabel("X (mm)")
    plt.ylabel("Y (mm)")
    plt.show()


if __name__ == "__main__":
    # 生成螺旋网点
    spiral_points, spiral_indices = generate_spiral_points(
        matrix_offset_x, matrix_offset_y,
        step_size_x, step_size_y
    )

    # 评估网点状态
    grid_status, valid_count, validity_list = evaluate_grid_points(
        spiral_points, step_size_x, step_size_y
    )

    # 输出统计
    print(f"总网点数: {len(spiral_points)}")
    print(f"有效网点数: {valid_count}")
    print(f"无效网点数: {len(spiral_points) - valid_count}")

    # 保存到Excel
    save_to_excel(spiral_points, validity_list, spiral_indices)

    # 可视化
    plot_grid(spiral_points, grid_status, step_size_x, step_size_y)