import matplotlib.pyplot as plt
import numpy as np
import random


class WaferMap:
    def __init__(self, rows, cols, blacklist, yield_rate):
        self.rows = rows
        self.cols = cols
        self.matrix = np.zeros((rows, cols), dtype=int)
        self.blacklist = set((x, y) for x, y in blacklist if 0 <= x < rows and 0 <= y < cols)

        # 标记黑名单
        for x, y in self.blacklist:
            self.matrix[x][y] = -3

        # 计算可用白名单坐标
        white_coords = []
        for x in range(rows):
            for y in range(cols):
                if (x, y) not in self.blacklist:
                    white_coords.append((x, y))

        total_chips = rows * cols
        total_fail = int(round(yield_rate * total_chips))
        black_fail = len(self.blacklist)
        required_white_fail = total_fail - black_fail

        if required_white_fail < 0:
            raise ValueError("良率过高，黑名单数量已超过总失败数量")
        if required_white_fail > len(white_coords):
            raise ValueError("白名单芯片数量不足以满足失败需求")

        # 随机选择白名单失败芯片
        random.shuffle(white_coords)
        self.white_fail = white_coords[:required_white_fail]
        for x, y in self.white_fail:
            self.matrix[x][y] = -1  # 标记为待分配

    def assign_soft_bins(self, soft_bin_list):
        # 收集待分配坐标
        fail_coords = [(x, y) for x in range(self.rows)
                       for y in range(self.cols) if self.matrix[x][y] == -1]

        # 处理比例分配
        total = sum(ratio for _, ratio in soft_bin_list)
        ratios = [(bin_num, ratio / total) for bin_num, ratio in soft_bin_list]

        # 随机分配
        random.shuffle(fail_coords)
        ptr = 0
        for i, (bin_num, ratio) in enumerate(ratios):
            if i == len(ratios) - 1:
                count = len(fail_coords) - ptr
            else:
                count = int(round(len(fail_coords) * ratio))

            for j in range(count):
                if ptr + j >= len(fail_coords):
                    break
                x, y = fail_coords[ptr + j]
                self.matrix[x][y] = bin_num
            ptr += count

    def get_soft_bin(self, x, y):
        if 0 <= x < self.rows and 0 <= y < self.cols:
            return self.matrix[x][y]
        raise ValueError("坐标超出晶圆范围")

    def plot(self):
        plt.figure(figsize=(10, 10))
        plt.imshow(self.matrix, cmap='Paired', interpolation='nearest')
        plt.colorbar()

        # 添加文本标注
        for x in range(self.rows):
            for y in range(self.cols):
                plt.text(y, x, str(self.matrix[x][y]),
                         ha='center', va='center',
                         color='white' if self.matrix[x][y] in {-3, -1} else 'black')

        plt.title("Wafer Map Visualization")
        plt.xlabel("Column")
        plt.ylabel("Row")
        plt.show()


# 使用示例
if __name__ == "__main__":
    # 初始化参数
    rows, cols = 10, 10
    blacklist = [(0, 0), (1, 1), (2, 2), (3, 3)]
    yield_rate = 0.25  # 25%的总失败率
    soft_bins = [(1, 60), (2, 30), (3, 10)]  # bin编号及其比例

    # 创建WaferMap实例
    try:
        wafer = WaferMap(rows, cols, blacklist, yield_rate)
        wafer.assign_soft_bins(soft_bins)
        wafer.plot()

        # 查询示例
        print("坐标(4,5)的soft bin:", wafer.get_soft_bin(4, 5))
    except ValueError as e:
        print(f"错误: {e}")