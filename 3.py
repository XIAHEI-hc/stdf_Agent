import numpy as np
import random
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import cv2
from sklearn.cluster import DBSCAN
from sklearn.linear_model import LinearRegression


def generate_raw_image(width, height, bad_lines=None, bad_pixels=None):
    # 初始化图像，每个通道的像素值在 64 左右波动
    image = np.random.normal(loc=64, scale=3, size=(height, width, 4)).astype(np.uint16)

    # 添加坏线
    if bad_lines:
        for channel, position, length, is_horizontal in bad_lines:
            if is_horizontal:
                start = random.randint(0, width - length)
                line_values = np.random.randint(80, 90, size=length)
                image[position, start:start + length, channel] = line_values
            else:
                start = random.randint(0, height - length)
                line_values = np.random.randint(80, 90, size=length)
                image[start:start + length, position, channel] = line_values

    # 添加随机坏点
    if bad_pixels:
        for channel, num in bad_pixels.items():
            coords = np.random.choice(height * width, num, replace=False)
            rows = coords // width
            cols = coords % width
            image[rows, cols, channel] = np.random.randint(80, 90, size=num)

    return image


def detect_bad_pixels(channel_data, threshold=12.8):
    """检测坏点并返回坐标"""
    base_value = 64
    deviation = np.abs(channel_data.astype(np.float32) - base_value)
    bad_points = np.argwhere(deviation > threshold)
    return bad_points


def cluster_and_detect_lines(bad_points, eps=5, min_samples=3):
    """聚类分析并检测直线"""
    if len(bad_points) < 2:
        return []

    # DBSCAN聚类
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(bad_points)
    clusters = []
    for label in np.unique(clustering.labels_):
        if label != -1:
            cluster = bad_points[clustering.labels_ == label]
            clusters.append(cluster)

    # 直线拟合分析
    detected_lines = []
    for cluster in clusters:
        if len(cluster) < 10:  # 忽略小簇
            continue

        # 计算主方向
        model = LinearRegression()
        X = cluster[:, 1].reshape(-1, 1)  # x坐标（列）
        y = cluster[:, 0]  # y坐标（行）
        model.fit(X, y)

        # 计算R²得分
        r_sq = model.score(X, y)
        if r_sq > 0.9:  # 线性拟合阈值
            x_min, x_max = X.min(), X.max()
            y_pred_min = model.predict([[x_min]])
            y_pred_max = model.predict([[x_max]])
            detected_lines.append(((x_min, y_pred_min[0]), (x_max, y_pred_max[0])))

    return detected_lines


def enhanced_detect_lines(channel_data, channel_name, threshold=12.8):
    """增强的坏点检测和直线检测"""
    # 转换为8bit用于显示
    channel_8bit = cv2.convertScaleAbs(channel_data)

    # 检测坏点
    bad_points = detect_bad_pixels(channel_data, threshold)

    # 可视化准备
    vis = cv2.cvtColor(channel_8bit, cv2.COLOR_GRAY2BGR)

    # 绘制坏点（红色）
    for y, x in bad_points:
        cv2.circle(vis, (x, y), 1, (0, 0, 255), -1)

    # 聚类和直线检测
    detected_lines = cluster_and_detect_lines(bad_points)

    # 绘制检测到的直线（绿色）
    for (x1, y1), (x2, y2) in detected_lines:
        cv2.line(vis, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

    # 可视化结果
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.imshow(channel_8bit, cmap='gray')
    plt.title(f'{channel_name} - Original')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
    plt.title(f'{channel_name} - Bad Points (Red) and Lines (Green)')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

    return bad_points, detected_lines
def save_raw_image(image, filename):
    image.tofile(filename)



def visualize_channels(image):
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    channel_names = ['R', 'G1', 'G2', 'B']

    for i in range(4):
        row = i // 2
        col = i % 2
        axes[row, col].imshow(image[:, :, i], cmap='gray')
        axes[row, col].set_title(f'Channel {channel_names[i]}')
        axes[row, col].axis('off')

    plt.tight_layout()
    plt.show()







if __name__ == "__main__":
    width = 500
    height = 500
    # 坏线参数
    bad_lines = [
        (0, 100, 200, True),  # 水平坏线
        (1, 200, 150, False)  # 垂直坏线
    ]
    # 坏点参数（每个通道随机坏点数）
    bad_pixels = {
        0: 50,  # R通道50个坏点
        2: 30  # G2通道30个坏点
    }

    image = generate_raw_image(width, height, bad_lines, bad_pixels)
    save_raw_image(image, "output.raw")
    print("RAW 图像已生成并保存为 output.raw")

    visualize_channels(image)

    channel_names = ['R', 'G1', 'G2', 'B']
    for i in range(4):
        print(f"\n正在处理通道 {channel_names[i]}:")
        bad_points, detected_lines = enhanced_detect_lines(image[:, :, i], channel_names[i], threshold=12.8)

        # 输出坏点信息
        print(f"检测到 {len(bad_points)} 个异常点")
        if len(bad_points) > 0:
            print("示例坐标（前5个）：")
            for pt in bad_points[:5]:
                print(f"  (行: {pt[0]}, 列: {pt[1]})")

        # 输出直线信息
        print(f"检测到 {len(detected_lines)} 条坏线")
        for idx, line in enumerate(detected_lines, 1):
            (x1, y1), (x2, y2) = line
            print(f"  线 {idx}: 从 (列: {x1:.0f}, 行: {y1:.0f}) 到 (列: {x2:.0f}, 行: {y2:.0f})")