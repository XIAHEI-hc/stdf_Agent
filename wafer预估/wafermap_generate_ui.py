import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle, Circle
import pandas as pd
import math
from openpyxl import Workbook
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
import numpy as np


class WaferPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 输入参数
        self.input_params = {
            'wafer_diameter': 300,
            'edge_removal': 3.2,
            'flat_height': 7,
            'die_size_x': 5.4,
            'die_size_y': 5.6,
            'boarder_size': 0,
            'seal_ring': 0.022,
            'scribeline_x': 0.12,
            'scribeline_y': 0.12,
            'matrix_offset_x': -0.3,
            'matrix_offset_y': -2.40506
        }

        # 创建输入框和标签
        self.input_widgets = {}
        input_layout = QHBoxLayout()
        for param, value in self.input_params.items():
            label = QLabel(param)
            line_edit = QLineEdit(str(value))
            self.input_widgets[param] = line_edit
            input_layout.addWidget(label)
            input_layout.addWidget(line_edit)

        # 创建按钮
        self.start_button = QPushButton('开始绘制')
        self.start_button.clicked.connect(self.start_plotting)
        self.save_button = QPushButton('保存到 Excel')
        self.save_button.clicked.connect(self.save_to_excel)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.save_button)

        # 创建绘图区域
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.canvas = FigureCanvas(self.fig)

        # 布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)
        self.setWindowTitle('晶圆绘图')
        self.show()

    def get_input_params(self):
        for param, widget in self.input_widgets.items():
            try:
                self.input_params[param] = float(widget.text())
            except ValueError:
                pass
        return self.input_params

    def start_plotting(self):
        params = self.get_input_params()
        wafer_diameter = params['wafer_diameter']
        edge_removal = params['edge_removal']
        flat_height = params['flat_height']
        die_size_x = params['die_size_x']
        die_size_y = params['die_size_y']
        boarder_size = params['boarder_size']
        seal_ring = params['seal_ring']
        scribeline_x = params['scribeline_x']
        scribeline_y = params['scribeline_y']
        matrix_offset_x = params['matrix_offset_x']
        matrix_offset_y = params['matrix_offset_y']

        step_size_x = die_size_x + 2 * boarder_size + 2 * seal_ring + scribeline_x
        step_size_y = die_size_y + 2 * boarder_size + 2 * seal_ring + scribeline_y

        effective_radius = (wafer_diameter / 2) - edge_removal
        y_threshold = - (effective_radius - flat_height)

        def is_in_circle(x, y):
            return 1 if x ** 2 + y ** 2 <= effective_radius ** 2 else -1

        def is_outside_flat(y):
            return y >= y_threshold

        def is_in_effective_area(x, y):
            return is_in_circle(x, y) == 1 and is_outside_flat(y)

        def generate_spiral_points(start_x, start_y, step_x, step_y):
            points = []
            indices = []
            x, y = start_x, start_y
            row, col = 0, 0
            points.append((x, y))
            indices.append((row, col))

            directions = [
                (step_x, 0, (0, 1)),
                (0, -step_y, (-1, 0)),
                (-step_x, 0, (0, -1)),
                (0, step_y, (1, 0))
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
                        if x ** 2 + y ** 2 > 2 * (wafer_diameter / 2) ** 2:
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

        def plot_grid(points, grid_info, step_x, step_y):
            self.ax.clear()
            wafer_circle = Circle((0, 0), wafer_diameter / 2, color='gray', fill=False, linestyle='--')
            self.ax.add_patch(wafer_circle)

            effective_circle = Circle((0, 0), effective_radius, color='blue', fill=False)
            self.ax.add_patch(effective_circle)

            flat_width = 2 * ((effective_radius ** 2 - (effective_radius - flat_height) ** 2) ** 0.5)
            self.ax.plot([-flat_width / 2, flat_width / 2], [y_threshold, y_threshold], 'r-', linewidth=2)

            for idx, (x, y) in enumerate(points):
                info = grid_info.get(idx, {'fill': None})
                if info.get('valid'):
                    color = 'black' if info['status'] == '内部' else 'pink'
                    rect = Rectangle((x - step_x / 2, y - step_y / 2), step_x, step_y,
                                     edgecolor=color, facecolor=color, alpha=0.3)
                    self.ax.add_patch(rect)

            self.ax.set_aspect('equal')
            self.ax.set_xlim(-wafer_diameter / 2 - 5, wafer_diameter / 2 + 5)
            self.ax.set_ylim(-wafer_diameter / 2 - 5, wafer_diameter / 2 + 5)
            self.ax.set_title("晶圆有效区域覆盖情况")
            self.ax.set_xlabel("X (mm)")
            self.ax.set_ylabel("Y (mm)")
            self.canvas.draw()

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

        # 可视化
        plot_grid(spiral_points, grid_status, step_size_x, step_size_y)

    def save_to_excel(self):
        params = self.get_input_params()
        wafer_diameter = params['wafer_diameter']
        edge_removal = params['edge_removal']
        flat_height = params['flat_height']
        die_size_x = params['die_size_x']
        die_size_y = params['die_size_y']
        boarder_size = params['boarder_size']
        seal_ring = params['seal_ring']
        scribeline_x = params['scribeline_x']
        scribeline_y = params['scribeline_y']
        matrix_offset_x = params['matrix_offset_x']
        matrix_offset_y = params['matrix_offset_y']

        step_size_x = die_size_x + 2 * boarder_size + 2 * seal_ring + scribeline_x
        step_size_y = die_size_y + 2 * boarder_size + 2 * seal_ring + scribeline_y

        effective_radius = (wafer_diameter / 2) - edge_removal
        y_threshold = - (effective_radius - flat_height)

        def is_in_circle(x, y):
            return 1 if x ** 2 + y ** 2 <= effective_radius ** 2 else -1

        def is_outside_flat(y):
            return y >= y_threshold

        def is_in_effective_area(x, y):
            return is_in_circle(x, y) == 1 and is_outside_flat(y)

        def generate_spiral_points(start_x, start_y, step_x, step_y):
            points = []
            indices = []
            x, y = start_x, start_y
            row, col = 0, 0
            points.append((x, y))
            indices.append((row, col))

            directions = [
                (step_x, 0, (0, 1)),
                (0, -step_y, (-1, 0)),
                (-step_x, 0, (0, -1)),
                (0, step_y, (1, 0))
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
                        if x ** 2 + y ** 2 > 2 * (wafer_diameter / 2) ** 2:
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
            letters = []
            while n >= 0:
                letters.append(chr(65 + n % 26))
                n = n // 26 - 1
            return ''.join(reversed(letters)) if letters else 'A'

        def save_to_excel(points, validity_list, indices, filename="wafer_validity.xlsx"):
            df_list = pd.DataFrame({
                "Index": range(len(points)),
                "X": [p[0] for p in points],
                "Y": [p[1] for p in points],
                "Valid": validity_list
            })

            writer = pd.ExcelWriter(filename, engine='openpyxl')
            df_list.to_excel(writer, sheet_name="列表视图", index=False)

            wb = writer.book
            ws_matrix = wb.create_sheet("矩阵视图")

            rows = [r for r, c in indices]
            cols = [c for r, c in indices]
            min_row, max_row = min(rows), max(rows)
            min_col, max_col = min(cols), max(cols)

            matrix = [[None] * (max_col - min_col + 1) for _ in range(max_row - min_row + 1)]
            for i in range(len(validity_list)):
                r, c = indices[i]
                adj_r = r - min_row
                adj_c = c - min_col
                matrix[adj_r][adj_c] = validity_list[i]

            start_row = 137
            start_col = 118

            for r in range(len(matrix)):
                for c in range(len(matrix[0])):
                    value = matrix[r][c]
                    if value is not None:
                        ws_matrix.cell(
                            row=start_row + r,
                            column=start_col + c,
                            value=value
                        )

            writer.save()
            print(f"数据已保存到 {filename}，矩阵视图从DS137单元格开始")

        # 生成螺旋网点
        spiral_points, spiral_indices = generate_spiral_points(
            matrix_offset_x, matrix_offset_y,
            step_size_x, step_size_y
        )

        # 评估网点状态
        grid_status, valid_count, validity_list = evaluate_grid_points(
            spiral_points, step_size_x, step_size_y
        )

        # 保存到Excel
        save_to_excel(spiral_points, validity_list, spiral_indices)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = WaferPlotWidget()
    sys.exit(app.exec_())

