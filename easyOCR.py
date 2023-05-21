import logging
import re
import subprocess
import easyocr
import numpy as np
from PIL import ImageGrab


def CudaCheck():
    cmd = 'nvcc -V'
    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, encoding='ansi')
        return True
    except subprocess.CalledProcessError:
        return False


def cudaVersionGet():  # 获取当前电脑上的CUDA版本，便于后面安装相应的Pytorch-GPU版本
    cmd = 'nvcc -V'
    try:
        back = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, encoding='ansi')
        version = re.search(r'release\s+(\d+\.\d+)', back)
        if version:
            return back.group(1).replace('.', '')
        else:
            logging.error(f"Error occurred: 未成功获取CUDA版本，请手动选择")
            return False
    except subprocess.CalledProcessError:
        return False


# noinspection PyTypeChecker
def aiOCR(x1=0, y1=0, x2=10, y2=10, cuda=False, lan=None, batch_size=1, min_size=10):
    # 截取指定范围的屏幕截图
    if lan == ['en']:
        lan = ['ch_sim', 'en']
    else:
        lan.append('en')

    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    img.save("111.png")
    imgArray = np.array(img)
    reader = easyocr.Reader(lan, gpu=cuda)
    '''
    horizontalList, freeList = reader.detect("2.png", min_size=10, text_threshold=0.7, low_text=0.4,
                                               link_threshold=0.4,
                                               canvas_size=2560, mag_ratio=1, slope_ths=0.1, ycenter_ths=0.5,
                                               height_ths=0.5, width_ths=0.5, add_margin=0.1,
                                               optimal_num_chars=None)

    print(horizontalList,freeList)
    para:
    optimal_num_chars (int, default = None) - 如果指定，则首先返回具有接近此值的估计字符数的边界框。
    '''

    result = reader.readtext(imgArray, detail=1, batch_size=batch_size, paragraph=False, min_size=min_size,
                             rotation_info=None,
                             contrast_ths=0.1, adjust_contrast=0.5, text_threshold=0.7, low_text=0.4,
                             link_threshold=0.4,
                             canvas_size=2560, mag_ratio=1.5, slope_ths=0.1, ycenter_ths=0.5, height_ths=0.5,
                             width_ths=0.5,
                             add_margin=0.1, x_ths=1, y_ths=0.5)
    '''
    para:
    detail (int, default = 1) - 将其设置为 0 以进行简单输出
    batch_size (int, default = 1) - batch_size>1 将使 EasyOCR 更快但使用更多内存
    paragraph (bool, default = False) - 将结果组合成段落
    min_size (int, default = 10) - 过滤小于像素最小值的文本框
    rotation_info (list, default = None) - 允许 EasyOCR 旋转每个文本框并返回具有最佳置信度分数的文本框。
    符合条件的值为 90、180 和 270。例如，尝试 [90, 180 ,270] 所有可能的文本方向
    contrast_ths (float, default = 0.1) - 对比度低于此值的文本框将被传递到模型中 2 次。第一个是原始图像，
    第二个是将对比度调整为“adjust_contrast”值。结果将返回具有更高置信度的那个。
    adjust_contrast (float, default = 0.5) - 低对比度文本框的目标对比度级别
    text_threshold (float, default = 0.7) - 文本置信度阈值
    low_text (float, default = 0.4) - 文本下限分数
    link_threshold (float, default = 0.4) - 链接置信度阈值
    canvas_size (int, default = 2560) - 最大图像大小。大于此值的图像将被缩小。
    mag_ratio (float, default = 1) - 图像放大率
    slope_ths (float, default = 0.1) - 考虑合并的最大斜率（delta y/delta x）。低值意味着不会合并平铺的框。
    ycenter_ths (float, default = 0.5) - y 方向的最大位移。不应合并具有不同级别的框。
    height_ths (float, default = 0.5) - 盒子高度的最大差异。文本大小差异很大的框不应合并。
    width_ths (float, default = 0.5) - 合并框的最大水平距离。
    add_margin (float, default = 0.1) - 按特定值在所有方向上扩展边界框。这对于具有复杂脚本的语言（例如泰语）很重要。
    x_ths (float, default = 1.0) - 当 paragraph=True 时合并文本框的最大水平距离。
    y_ths (float, default = 0.5) - 当 paragraph=True 时合并文本框的最大垂直距离。
    '''
    del reader
    return result
