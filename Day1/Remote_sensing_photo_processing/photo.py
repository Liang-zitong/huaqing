import numpy as np
import cv2
import rasterio


def enhance_brightness_cv2(image, method='percentile', low=2, high=98, gamma=1.0):
    """
    使用OpenCV增强图像亮度
    :param image: 输入图像(0-255范围)
    :param method: 'percentile'百分比拉伸, 'gamma'伽马校正
    :param low: 低百分比(仅对percentile方法有效)
    :param high: 高百分比(仅对percentile方法有效)
    :param gamma: 伽马值(仅对gamma方法有效)
    :return: 增强后的图像
    """
    if method == 'percentile':
        # 计算百分比阈值
        p_low = np.percentile(image, low)
        p_high = np.percentile(image, high)
        # 线性拉伸
        enhanced = np.clip((image - p_low) * 255.0 / (p_high - p_low), 0, 255).astype(np.uint8)
    elif method == 'gamma':
        # 伽马校正
        normalized = image / 255.0
        enhanced = (np.power(normalized, gamma) * 255).astype(np.uint8)
    else:
        enhanced = image

    return enhanced


def tif_to_png(tif_path, png_path, brightness_method='percentile'):
    # 使用rasterio打开TIFF文件
    with rasterio.open(tif_path) as src:
        # 读取所有波段数据
        data = src.read()

        # 如果是多波段图像，选择前3个波段进行可视化
        if len(data) > 1:
            enhanced_bands = []
            for i in range(min(3, len(data))):  # 最多取3个波段
                band = data[i]
                # 先归一化到0-255范围
                band_normalized = cv2.normalize(band, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                # 增强亮度
                enhanced_band = enhance_brightness_cv2(band_normalized, method=brightness_method)
                enhanced_bands.append(enhanced_band)

            # 合并波段(RGB顺序)
            rgb_image = cv2.merge(enhanced_bands)
        else:
            # 单波段图像处理
            band = data[0]
            band_normalized = cv2.normalize(band, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            rgb_image = enhance_brightness_cv2(band_normalized, method=brightness_method)
            # 将单波段转换为伪彩色(可选)
            rgb_image = cv2.applyColorMap(rgb_image, cv2.COLORMAP_JET)

        # 保存为PNG文件
        cv2.imwrite(png_path, rgb_image)
        print(f"成功将 {tif_path} 转换为 {png_path}")


# 输入和输出文件路径
tif_path = r'F:\Downloads\2019_1101_nofire_B2348_B12_10m_roi.tif'
png_path = r'F:\Downloads\2019_1101_nofire_B2348_B12_10m_roi.png'

# 方法1：百分比拉伸(默认2-98%)
tif_to_png(tif_path, png_path.replace('.png', '_percentile.png'), 'percentile')

# 方法2：伽马校正(γ=0.5 使图像变亮)
tif_to_png(tif_path, png_path.replace('.png', '_gamma.png'), 'gamma')

# 方法3：更激进的百分比拉伸(1-99%)
tif_to_png(tif_path, png_path.replace('.png', '_aggressive.png'), 'percentile')