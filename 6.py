import numpy as np
import cv2
import matplotlib.pyplot as plt


def detect_lines_convolution(channel_image, channel_name, threshold=40):
    # 转换为8位图像并高斯滤波
    channel_image_8bit = cv2.convertScaleAbs(channel_image)
    blurred = cv2.GaussianBlur(channel_image_8bit, (3, 3), 0)
    img_float = blurred.astype(np.float32)

    # 定义卷积核（二阶差分核）
    kernel_h = np.array([1, -2, 1]).reshape(1, 3)  # 水平核检测垂直结构（坏列）
    kernel_v = np.array([1, -2, 1]).reshape(3, 1)  # 垂直核检测水平结构（坏行）

    # 卷积运算
    response_h = cv2.filter2D(img_float, -1, kernel_h, borderType=cv2.BORDER_REPLICATE)
    response_v = cv2.filter2D(img_float, -1, kernel_v, borderType=cv2.BORDER_REPLICATE)

    # 计算行/列平均响应（取绝对值）
    row_means = np.mean(np.abs(response_v), axis=1)  # 垂直响应检测坏行
    col_means = np.mean(np.abs(response_h), axis=0)  # 水平响应检测坏列

    # 减去全局均值
    row_diff = row_means - np.mean(row_means)
    col_diff = col_means - np.mean(col_means)

    # 应用阈值检测异常
    bad_rows = np.where(row_diff > threshold)[0]
    bad_cols = np.where(col_diff > threshold)[0]

    # 可视化结果
    plt.figure(figsize=(15, 5))

    # 原始图像
    plt.subplot(1, 3, 1)
    plt.imshow(channel_image_8bit, cmap='gray')
    plt.title(f'{channel_name} - Original')
    plt.axis('off')

    # 行响应曲线
    plt.subplot(1, 3, 2)
    plt.plot(row_diff, range(len(row_diff)))
    plt.gca().invert_yaxis()
    plt.title('Row Responses')
    plt.xlabel('Response Value')
    plt.ylabel('Row Index')

    # 列响应曲线
    plt.subplot(1, 3, 3)
    plt.plot(range(len(col_diff)), col_diff)
    plt.title('Column Responses')
    plt.xlabel('Column Index')
    plt.ylabel('Response Value')

    plt.tight_layout()
    plt.show()

    return bad_rows, bad_cols


if __name__ == "__main__":
    # 加载生成的RAW图像（这里复用之前的生成逻辑）
    image = np.fromfile("output.raw", dtype=np.uint16).reshape(500, 500, 4)

    channel_names = ['R', 'G1', 'G2', 'B']
    for i in range(4):
        print(f"\nProcessing channel {channel_names[i]}:")
        bad_rows, bad_cols = detect_lines_convolution(image[:, :, i], channel_names[i], threshold=40)

        if len(bad_rows) > 0 or len(bad_cols) > 0:
            print(f"检测到异常：{len(bad_rows)} 条坏行, {len(bad_cols)} 条坏列")
            if len(bad_rows) > 0:
                print("坏行位置:", bad_rows)
            if len(bad_cols) > 0:
                print("坏列位置:", bad_cols)