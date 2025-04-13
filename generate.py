import numpy as np
import random
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import cv2


def generate_raw_image(width, height, bad_lines=None):
    # 初始化图像，每个通道的像素值在 64 左右波动
    image = np.random.normal(loc=64, scale=3, size=(height, width, 4)).astype(np.uint16)

    if bad_lines:
        for channel, position, length, is_horizontal in bad_lines:
            if is_horizontal:
                start = random.randint(0, width - length)
                line_values = np.random.randint(80, 90, size=length)  # 增加坏线与背景的对比度
                image[position, start:start + length, channel] = line_values
            else:
                start = random.randint(0, height - length)
                line_values = np.random.randint(80, 90, size=length)  # 增加坏线与背景的对比度
                image[start:start + length, position, channel] = line_values

    return image


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


def detect_lines(channel_image, channel_name):
    # 转换为 8 位图像
    channel_image_8bit = cv2.convertScaleAbs(channel_image)

    # 显示原始通道图像
    plt.figure(figsize=(15, 5))
    plt.subplot(1, 4, 1)
    plt.imshow(channel_image_8bit, cmap='gray')
    plt.title(f'{channel_name} - Original')
    plt.axis('off')

    # 高斯模糊减少噪声
    blurred = cv2.GaussianBlur(channel_image_8bit, (5, 5), 0)

    # Canny 边缘检测 (调整参数)
    edges = cv2.Canny(blurred, 30, 100)  # 降低阈值

    # 显示Canny边缘检测结果
    plt.subplot(1, 4, 2)
    plt.imshow(edges, cmap='gray')
    plt.title(f'{channel_name} - Canny Edges')
    plt.axis('off')

    # 霍夫变换检测直线 (调整参数)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=30, minLineLength=30, maxLineGap=10)

    # 创建中间结果图像
    intermediate_result = cv2.cvtColor(channel_image_8bit, cv2.COLOR_GRAY2BGR)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(intermediate_result, (x1, y1), (x2, y2), (0, 255, 255), 1)  # 黄色表示所有检测到的线

    plt.subplot(1, 4, 3)
    plt.imshow(cv2.cvtColor(intermediate_result, cv2.COLOR_BGR2RGB))
    plt.title(f'{channel_name} - All Detected Lines')
    plt.axis('off')

    horizontal_lines = []
    vertical_lines = []

    # 创建最终结果图像
    result = cv2.cvtColor(channel_image_8bit, cv2.COLOR_GRAY2BGR)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y2 - y1) < 5:  # 水平直线
                horizontal_lines.append(line)
                cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 绿色表示水平线
            elif abs(x2 - x1) < 5:  # 垂直直线
                vertical_lines.append(line)
                cv2.line(result, (x1, y1), (x2, y2), (0, 0, 255), 2)  # 红色表示垂直线

    # 显示最终结果
    plt.subplot(1, 4, 4)
    plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    plt.title(f'{channel_name} - Filtered Lines')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

    return horizontal_lines, vertical_lines


if __name__ == "__main__":
    width = 500
    height = 500
    # 坏线信息格式：(通道, 位置, 长度, 是否水平)
    bad_lines = [
        (0, 100, 200, True),  # 通道 0，第 100 行，长度 200 的横向坏线
        (1, 200, 150, False)  # 通道 1，第 200 列，长度 150 的纵向坏线
    ]

    image = generate_raw_image(width, height, bad_lines)
    save_raw_image(image, "output.raw")
    print("RAW 图像已生成并保存为 output.raw")

    visualize_channels(image)

    channel_names = ['R', 'G1', 'G2', 'B']
    for i in range(4):
        horizontal_lines, vertical_lines = detect_lines(image[:, :, i], channel_names[i])

        if horizontal_lines or vertical_lines:
            print(f"在通道 {channel_names[i]} 中检测到直线：")
            if horizontal_lines:
                print(f"  检测到 {len(horizontal_lines)} 条水平直线")
                for idx, line in enumerate(horizontal_lines, 1):
                    x1, y1, x2, y2 = line[0]
                    print(f"    线 {idx}: 从 ({x1}, {y1}) 到 ({x2}, {y2})")
            if vertical_lines:
                print(f"  检测到 {len(vertical_lines)} 条垂直直线")
                for idx, line in enumerate(vertical_lines, 1):
                    x1, y1, x2, y2 = line[0]
                    print(f"    线 {idx}: 从 ({x1}, {y1}) 到 ({x2}, {y2})")