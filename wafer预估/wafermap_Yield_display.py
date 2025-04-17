import sys
import pandas as pd
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QWidget, QMenu, QAction, QInputDialog,
                             QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
                             QFileDialog, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont


# ================== 新增 StatsPanel 类定义 ==================
class StatsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.value_counts = defaultdict(int)
        self.total = 0

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title = QLabel("数值分布统计 (Top 20)")
        self.list_widget = QListWidget()

        layout.addWidget(self.title)
        layout.addWidget(self.list_widget)

    def update_stats(self, data_matrix):
        self.value_counts.clear()
        self.total = 0

        for row in data_matrix:
            for value in row:
                if value != 0:  # 排除原始0值
                    self.value_counts[value] += 1
                    self.total += 1

        sorted_items = sorted(self.value_counts.items(),
                              key=lambda x: x[1], reverse=True)[:20]

        self.list_widget.clear()
        for value, count in sorted_items:
            percentage = count / self.total * 100 if self.total > 0 else 0
            item = QListWidgetItem(
                f"{value}: {count}次 ({percentage:.2f}%)"
            )
            if value == 1:
                item.setForeground(QColor(0, 255, 0))
            elif value == -50:
                item.setForeground(QColor(0, 0, 0))
            else:
                hue = (value % 10000) / 10000 * 270
                item.setForeground(QColor.fromHsvF(hue / 360, 0.8, 0.9))
            self.list_widget.addItem(item)


class WaferMapWidget(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.data_matrix = []
        self.original_data = []
        self.rows = 0
        self.cols = 0
        self.initUI()

        self.font = QFont()
        self.font.setBold(True)
        self.coord_font = QFont("Arial", 8)

    def initUI(self):
        self.setWindowTitle('Wafer Map Viewer Pro')
        self.setMinimumSize(800, 600)

    def set_data(self, data_matrix):
        self.original_data = [row[:] for row in data_matrix]
        self.data_matrix = [row[:] for row in data_matrix]
        self.rows = len(data_matrix)
        self.cols = len(data_matrix[0]) if self.rows > 0 else 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.black)

        w = self.width()
        h = self.height()
        header_size = 30  # 坐标轴宽度

        # 计算单元格尺寸
        cell_w = (w - header_size) / self.cols
        cell_h = (h - header_size) / self.rows

        # 绘制列坐标
        for col in range(self.cols):
            x = header_size + col * cell_w
            painter.setFont(self.coord_font)
            painter.drawText(x, 0, cell_w, header_size,
                             Qt.AlignCenter, str(col + 1))

        # 绘制行坐标
        for row in range(self.rows):
            y = header_size + row * cell_h
            painter.setFont(self.coord_font)
            painter.drawText(0, y, header_size, cell_h,
                             Qt.AlignCenter, str(row + 1))

        # 绘制单元格
        for row in range(self.rows):
            for col in range(self.cols):
                x = header_size + col * cell_w
                y = header_size + row * cell_h
                value = self.data_matrix[row][col]

                color = self._get_color(value)
                painter.setBrush(color)
                painter.drawRect(x, y, cell_w, cell_h)

                if value not in (0, -50):
                    painter.setFont(self.font)
                    font_size = min(cell_w / 3, cell_h / 3)
                    self.font.setPixelSize(int(font_size))
                    painter.setPen(Qt.black)
                    painter.drawText(x, y, cell_w, cell_h,
                                     Qt.AlignCenter, str(value))

    def _get_color(self, value):
        if value == 1:
            return QColor(0, 255, 0)
        elif value == -50:
            return QColor(0, 0, 0)
        elif value == 0:
            return QColor(255, 255, 255)
        else:
            hue = (value % 10000) / 10000 * 270
            return QColor.fromHsvF(hue / 360, 0.8, 0.9)

    def mousePressEvent(self, event):
        header_size = 30
        x = event.x() - header_size
        y = event.y() - header_size
        cell_w = (self.width() - header_size) / self.cols
        cell_h = (self.height() - header_size) / self.rows

        col = int(x // cell_w)
        row = int(y // cell_h)

        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return

        cell_value = self.data_matrix[row][col]
        if cell_value == 0:
            return

        if event.button() == Qt.LeftButton:
            self._show_info(row, col)
        elif event.button() == Qt.RightButton:
            self._show_menu(row, col, event.globalPos())

    # 其余方法保持不变...


class ExcelImportDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sheet_selector = QListWidget()
        self.range_input = QInputDialog()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        btn = QPushButton("选择Excel文件")
        btn.clicked.connect(self.load_excel)
        layout.addWidget(btn)

        layout.addWidget(QLabel("选择工作表:"))
        layout.addWidget(self.sheet_selector)

        self.range_input.setLabelText("输入数据范围 (如A5:G37):")
        self.range_input.setOkButtonText("确认")
        self.range_input.setCancelButtonText("取消")

    def load_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "打开Excel文件", "", "Excel文件 (*.xlsx *.xls)")

        if path:
            try:
                self.df_dict = pd.read_excel(path, sheet_name=None)
                self.sheet_selector.clear()
                self.sheet_selector.addItems(self.df_dict.keys())
                self.sheet_selector.itemDoubleClicked.connect(self.select_sheet)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"读取文件失败: {str(e)}")

    def select_sheet(self, item):
        self.selected_sheet = item.text()
        self.range_input.exec_()
        if self.range_input.result():
            self.parse_range()

    def parse_range(self):
        range_str = self.range_input.textValue().upper()
        try:
            start_end = range_str.split(':')
            start_col = ord(start_end[0][0]) - ord('A')
            start_row = int(start_end[0][1:]) - 1
            end_col = ord(start_end[1][0]) - ord('A')
            end_row = int(start_end[1][1:]) - 1

            df = self.df_dict[self.selected_sheet].iloc[
                 start_row:end_row + 1, start_col:end_col + 1
                 ]
            data = df.fillna(0).values.tolist()
            self.parent().wafer_map.set_data(data)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解析范围失败: {str(e)}")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 工具栏
        toolbar = QHBoxLayout()
        self.import_btn = QPushButton("导入Excel")
        self.export_btn = QPushButton("导出CSV")
        toolbar.addWidget(self.import_btn)
        toolbar.addWidget(self.export_btn)
        main_layout.addLayout(toolbar)

        # 主界面
        content_layout = QHBoxLayout()
        self.wafer_map = WaferMapWidget()
        self.stats_panel = StatsPanel()
        content_layout.addWidget(self.wafer_map, 3)
        content_layout.addWidget(self.stats_panel, 1)
        main_layout.addLayout(content_layout)

        # 信号连接
        self.import_btn.clicked.connect(self.show_import_dialog)
        self.export_btn.clicked.connect(self.export_csv)
        self.wafer_map.dataChanged.connect(
            lambda: self.stats_panel.update_stats(self.wafer_map.data_matrix)
        )

    def show_import_dialog(self):
        dialog = ExcelImportDialog(self)
        dialog.show()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "保存CSV文件", "", "CSV文件 (*.csv)")

        if path:
            try:
                df = pd.DataFrame(self.wafer_map.data_matrix)
                df.to_csv(path, index=False, header=False)
                QMessageBox.information(self, "成功", "文件导出成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")


# StatsPanel 类保持不变...

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("完整版WaferMap分析工具")
    window.show()
    sys.exit(app.exec_())