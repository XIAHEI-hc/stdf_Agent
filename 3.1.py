import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


def detect_lines_convolution(channel_image, channel_name, threshold=0.2):
    """改进版固定阈值检测方法"""
    # 优化预处理流程
    channel_image_16bit = cv2.normalize(channel_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    blurred = cv2.GaussianBlur(channel_image_16bit, (3, 3), 0)
    img_float = blurred.astype(np.float32)

    # 增强型卷积核（扩大感受野）
    kernel_h = np.array([1, 2, -6, 2, 1]).reshape(1, 5)  # 水平核检测垂直结构
    kernel_v = np.array([1, 2, -6, 2, 1]).reshape(5, 1)  # 垂直核检测水平结构

    # 卷积运算（使用相同缩放系数）
    response_h = cv2.filter2D(img_float, -1, kernel_h, borderType=cv2.BORDER_REPLICATE)
    response_v = cv2.filter2D(img_float, -1, kernel_v, borderType=cv2.BORDER_REPLICATE)

    # 计算归一化响应（改进响应计算方式）
    row_response = np.mean(np.abs(response_v), axis=1)
    col_response = np.mean(np.abs(response_h), axis=0)

    # 动态阈值计算（基于全局统计）
    global_mean = np.mean(row_response) * 0.5 + np.mean(col_response) * 0.5
    threshold_value = global_mean + threshold * (np.max(row_response) - global_mean)

    # 检测异常（双条件判断）
    bad_rows = np.where(row_response > threshold_value)[0]
    bad_cols = np.where(col_response > threshold_value)[0]

    # 增强可视化
    plt.figure(figsize=(18, 6))

    # 原始图像
    plt.subplot(1, 4, 1)
    plt.imshow(channel_image_16bit, cmap='gray', vmin=0, vmax=255)
    plt.title(f'{channel_name} Channel\nSize: {channel_image.shape}')
    plt.axis('off')

    # 行响应曲线
    plt.subplot(1, 4, 2)
    plt.plot(row_response, range(len(row_response)), color='darkblue')
    plt.scatter(row_response[bad_rows], bad_rows, color='red', s=20, zorder=3)
    plt.gca().invert_yaxis()
    plt.title(f'Row Responses (Threshold: {threshold_value:.1f})')
    plt.grid(True, alpha=0.3)

    # 列响应曲线
    plt.subplot(1, 4, 3)
    plt.plot(range(len(col_response)), col_response, color='darkgreen')
    plt.scatter(bad_cols, col_response[bad_cols], color='red', s=20, zorder=3)
    plt.title(f'Column Responses (Threshold: {threshold_value:.1f})')
    plt.grid(True, alpha=0.3)

    # 响应值分布直方图
    plt.subplot(1, 4, 4)
    plt.hist(row_response, bins=50, alpha=0.5, label='Rows', color='blue')
    plt.hist(col_response, bins=50, alpha=0.5, label='Columns', color='green')
    plt.axvline(threshold_value, color='red', linestyle='--', label='Threshold')
    plt.title('Response Distribution')
    plt.legend()
    plt.xlabel('Response Value')
    plt.ylabel('Frequency')

    plt.tight_layout()
    plt.show()

    return bad_rows, bad_cols


def detect_lines_convolution_adaptive(channel_image, channel_name, min_height=10, prominence=5, width=2):
    """增强版自适应检测方法"""
    # 优化预处理
    channel_image_16bit = cv2.normalize(channel_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    img_float = cv2.GaussianBlur(channel_image_16bit, (3, 3), 0).astype(np.float32)

    # 多尺度卷积核组
    kernels = [
        np.array([1, -4, 6, -4, 1]),  # Laplacian of Gaussian近似
        np.array([1, 2, -6, 2, 1])  # 自定义差分核
    ]

    # 多核响应融合
    combined_response_v = np.zeros_like(img_float)
    combined_response_h = np.zeros_like(img_float)

    for kernel in kernels:
        kv = kernel.reshape(-1, 1)
        kh = kernel.reshape(1, -1)
        combined_response_v += np.abs(cv2.filter2D(img_float, -1, kv, borderType=cv2.BORDER_REPLICATE))
        combined_response_h += np.abs(cv2.filter2D(img_float, -1, kh, borderType=cv2.BORDER_REPLICATE))

    # 计算归一化响应
    row_response = np.mean(combined_response_v, axis=1)
    col_response = np.mean(combined_response_h, axis=0)

    # 改进的峰值检测参数
    row_peaks, _ = find_peaks(
        row_response,
        height=min_height,
        prominence=prominence,
        width=width,
        rel_height=0.8
    )
    col_peaks, _ = find_peaks(
        col_response,
        height=min_height,
        prominence=prominence,
        width=width,
        rel_height=0.8
    )

    # 专业级可视化
    fig = plt.figure(figsize=(18, 8))
    grid = plt.GridSpec(2, 4, hspace=0.4, wspace=0.3)

    # 原始图像
    ax1 = fig.add_subplot(grid[0, 0])
    ax1.imshow(channel_image_16bit, cmap='gray')
    ax1.set_title(f'{channel_name} Channel\nDetected: {len(row_peaks)}R/{len(col_peaks)}C')
    ax1.axis('off')

    # 行响应三维可视化
    ax2 = fig.add_subplot(grid[0, 1:3], projection='3d')
    x = np.arange(len(row_response))
    y = row_response
    ax2.plot(x, y, zs=0, zdir='y', color='blue')
    ax2.scatter(x[row_peaks], y[row_peaks], zs=0, color='red', s=20)
    ax2.view_init(elev=30, azim=-60)
    ax2.set_title('Row Response Surface')
    ax2.set_xlabel('Row Index')
    ax2.set_ylabel('Response Value')

    # 列响应曲面
    ax3 = fig.add_subplot(grid[0, 3], projection='3d')
    x = np.arange(len(col_response))
    y = col_response
    ax3.plot(x, y, zs=0, zdir='y', color='green')
    ax3.scatter(x[col_peaks], y[col_peaks], zs=0, color='red', s=20)
    ax3.view_init(elev=30, azim=-60)
    ax3.set_title('Column Response Surface')

    # 频谱分析
    ax4 = fig.add_subplot(grid[1, :2])
    freqs = np.fft.rfft(row_response)
    power = np.abs(freqs)
    ax4.plot(power, color='purple')
    ax4.set_title('Row Response Frequency Spectrum')
    ax4.set_xlabel('Frequency')
    ax4.set_ylabel('Power')

    # 统计面板
    ax5 = fig.add_subplot(grid[1, 2:])
    stats_text = f"""
    Response Statistics:
    - Row Max: {np.max(row_response):.1f}
    - Row Mean: {np.mean(row_response):.1f}
    - Col Max: {np.max(col_response):.1f}
    - Col Mean: {np.mean(col_response):.1f}
    Detection Parameters:
    - Min Height: {min_height}
    - Prominence: {prominence}
    - Width: {width}
    """
    ax5.text(0.05, 0.5, stats_text, fontfamily='monospace', va='center')
    ax5.axis('off')

    plt.tight_layout()
    plt.show()

    return row_peaks, col_peaks


def generate_test_image():
    """生成更真实的测试图像"""
    height, width = 500, 500
    image = np.random.normal(loc=10000, scale=2000, size=(height, width, 4)).astype(np.uint16)

    # 添加多种缺陷类型
    # 单像素坏行/列
    image[50, :, 0] = 65535  # R通道第50行
    image[:, 100, 1] = 65535  # G1通道第100列

    # 多像素坏行
    image[150:153, :, 2] = 65535  # G2通道3行

    # 渐变缺陷
    image[200:250, :, 3] = np.linspace(20000, 65535, 50)[:, None]  # B通道渐变缺陷

    # 随机点缺陷
    for _ in range(50):
        x = np.random.randint(300, 400)
        y = np.random.randint(300, 400)
        image[y, x, np.random.randint(4)] = 65535

    # 周期性干扰
    x = np.arange(width)
    image[:, :, 0] += (np.sin(x / 20) * 5000).astype(np.uint16)

    return image


def main():
    # 生成测试图像
    image = generate_test_image()

    # 保存测试数据
    image.tofile("test_image.raw")

    # 通道处理
    channel_names = ['R', 'G1', 'G2', 'B']

    for i in range(4):
        print(f"\n{'=' * 30}")
        print(f"Processing {channel_names[i]} Channel")
        print(f"{'=' * 30}")

        # 固定阈值方法
        print("\n[Enhanced Fixed Threshold Method]")
        bad_rows_fixed, bad_cols_fixed = detect_lines_convolution(image[:, :, i], channel_names[i])

        # 自适应方法
        print("\n[Advanced Adaptive Method]")
        bad_rows_adaptive, bad_cols_adaptive = detect_lines_convolution_adaptive(
            image[:, :, i],
            channel_names[i],
            min_height=15,  # 根据实际情况调整
            prominence=8,
            width=3
        )

        # 结果对比
        print("\nDetection Results Comparison:")
        print(f"Fixed Threshold: {len(bad_rows_fixed)} rows, {len(bad_cols_fixed)} cols")
        print(f"Adaptive Method: {len(bad_rows_adaptive)} rows, {len(bad_cols_adaptive)} cols")

        # 详细位置输出
        if bad_rows_fixed.size > 0:
            print(f"Fixed Threshold Bad Rows: {bad_rows_fixed}")
        if bad_cols_fixed.size > 0:
            print(f"Fixed Threshold Bad Cols: {bad_cols_fixed}")
        if bad_rows_adaptive.size > 0:
            print(f"Adaptive Bad Rows: {bad_rows_adaptive}")
        if bad_cols_adaptive.size > 0:
            print(f"Adaptive Bad Cols: {bad_cols_adaptive}")


if __name__ == "__main__":
    main()