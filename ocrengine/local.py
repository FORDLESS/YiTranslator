import logging
import time

import Global
from ocrengine.baseOCR import BaseOCR
from ctypes import CDLL, c_char_p, create_string_buffer, c_uint32, POINTER, c_int32
import os
import platform


class OCRwrapper:  # OCR装饰器
    def __init__(self) -> None:  # 判断使用设备是32/64位系统，并加载相应dll文件
        if platform.architecture()[0] == '64bit':
            bit = '64'
        else:
            bit = '32'
        self.dll = CDLL(os.path.abspath(f'{Global.parent_dir}/files/plugins/ocr{bit}.dll'))

    def _OcrInit(self, szDetModel, szRecModel, szKeyPath, szClsModel='', nThreads=4):  # 初始化OCR实例-隐
        _OcrInit = self.dll.OcrInit
        _OcrInit.restype = POINTER(c_uint32)
        self.pOcrObj = _OcrInit(c_char_p(szDetModel.encode('utf8')), c_char_p(szClsModel.encode('utf8')),
                                c_char_p(szRecModel.encode('utf8')), c_char_p(szKeyPath.encode('utf8')), nThreads)

    def _OcrDetect(self, imgPath, imgName, angle):  # OCR文本检测方法
        _OcrDetect = self.dll.OcrDetect
        return _OcrDetect(self.pOcrObj, c_char_p(imgPath.encode('utf8')), c_char_p(imgName.encode('utf8')),
                          c_int32(angle))

    def _OcrGet(self):  # 获取OCR返回的文本
        _OcrGetLen = self.dll.OcrGetLen
        _OcrGetResult = self.dll.OcrGetResult
        length = _OcrGetLen(self.pOcrObj)
        buff = create_string_buffer(length)

        _OcrGetResult(self.pOcrObj, buff, length)
        return buff.value

    def _OcrDestroy(self):  # 销毁OCR实例
        _OcrDestroy = self.dll.OcrDestroy
        _OcrDestroy(self.pOcrObj)

    def init(self, det, rec, key):  # 供调用的OCR初始化接口，参数为检测模型，识别模型和关键路径
        self._OcrInit(det, rec, key)

    def ocr(self, path, name, angle=0):  # 供返回识别结果的接口，参数为图片路径，图片名，是否竖向识别（true/false)
        try:
            self._OcrDetect(path, name, angle)
            return self._OcrGet().decode('utf8')
        except:
            return ''

    def trydestroy(self):  # 供调用的销毁OCR实例接口
        try:
            self._OcrDestroy()
        except:
            pass


class OCR(BaseOCR):  # 这个类继承于baseocr，self._ocr来自ocrwrapper
    def __init__(self, typename):
        super().__init__(typename)
        self._savelang = None
        try:
            self._ocr = OCRwrapper()
        except Exception as error:
            logging.error(f"初始化OCR时出现错误: {error}")
            return
        self.checkChange()

    def initocr(self):
        pass

    def end(self):
        self._ocr.trydestroy()

    def checkChange(self):  # 检查语种变更
        if self._savelang == self.srclang:  # 如果当前的语种是设置的语种，直接返回
            return True
        self._ocr.trydestroy()  # 否则先销毁已创建的OCR引擎

        path = f'{Global.parent_dir}/files/ocr/{self.srclang}'  # 对应语种的路劲文件夹下
        if not (os.path.exists(f'{path}/det.onnx') and os.path.exists(f'{path}/rec.onnx') and os.path.exists(
                f'{path}/dict.txt')):  # 如果不存在所需的模型文件
            return False
        self._ocr.init(f'{path}/det.onnx', f'{path}/rec.onnx', f'{path}/dict.txt')  # 初始化正确的OCR引擎
        self._savelang = self.srclang  # 将当前语种更新为设置的语种
        return True

    def ocr(self, imgfile):
        if not self.checkChange():  # 扫描前检查是否变更语种并且是否存在对应语言的识别模型，不存在则将提示作为扫描内容返回
            return '未下载该语言的OCR模型,请下载模型后解压到files/ocr路径后使用'
        # 得到初始的识别文本
        s = self._ocr.ocr(os.path.dirname(imgfile) + '/', os.path.basename(imgfile), 0)
        vertical = False  # 是否竖排

        # 文本格式化处理

        ls = s.split('\n')  # 将识别文本s按换行符 \n 分割为多行文本，存储在列表ls中。
        juhe = []  # 存储聚合后的文本行
        box = []  # 存储每个文本框的坐标信息
        mids = []  # 存储每个文本框的中间点坐标
        ranges = []  # 存储每个文本框的范围
        text = []  # 存储每个文本框的文本内容
        for i in range(len(ls) // 2):
            # 将每个索引对应的偶数索引位置的文本以 , 分割为多个数字，并将其转换为整数。然后将这些数字以列表的形式添加到 box 列表中
            box.append([int(_) for _ in ls[i * 2].split(',')])
            text.append(ls[i * 2 + 1])  # 将每个索引对应的奇数索引位置的文本添加到 text 列表中。
        for i in range(len(box)):
            if vertical:
                mid = box[i][0] + box[i][2] + box[i][4] + box[i][6]
            else:
                mid = box[i][1] + box[i][3] + box[i][5] + box[i][7]
            mid /= 4
            mids.append(mid)  # 计算文本框的中间点坐标 mid并添加到列表
            if vertical:
                range_ = ((box[i][0] + box[i][6]) / 2, (box[i][2] + box[i][4]) / 2)
            else:
                range_ = ((box[i][1] + box[i][3]) / 2, (box[i][7] + box[i][5]) / 2)
            ranges.append(range_)  # 计算文本框的范围 range_并添加到列表

        passed = []  # 存储已经处理过的文本框的索引
        for i in range(len(box)):
            ls = [i]
            if i in passed:
                continue
            for j in range(i + 1, len(box)):
                if j in passed:
                    continue
                # 如果文本框 j 的范围在文本框 i 的中间点的范围内，并且文本框 i 的范围在文本框 j 的中间点的范围内：
                if ranges[j][0] < mids[i] < ranges[j][1] and ranges[i][0] < mids[j] < ranges[i][1]:
                    passed.append(j)
                    ls.append(j)
            juhe.append(ls)

        for i in range(len(juhe)):  # 对聚合后的文本进行排序
            if vertical:
                juhe[i].sort(key=lambda x: box[x][1])  # 顶部
            else:
                juhe[i].sort(key=lambda x: box[x][0])  # 对列表 juhe 中的每个元素按照文本框索引 x 所对应的左侧坐标排序
        if vertical:
            juhe.sort(key=lambda x: -box[x[0]][0])
        else:
            juhe.sort(key=lambda x: box[x[0]][1])

        lines = []  # 用于存储最终的文本行
        for _j in juhe:
            # 将每个文本框索引 _ 对应的文本内容添加到列表 text 中。
            # 将列表 text 中的文本内容用空格连接起来，并添加到列表 lines 中
            lines.append(' '.join([text[_] for _ in _j]))
        return self.space.join(lines)  # 根据规则加入分隔符并返回最终文本


if __name__ == '__main__':
    Global.language = "英语"
    Global.ocr_setting = {"mergelines": False}
    ocr = OCR("local")
    start_time = time.time()
    print(ocr.ocr(r"E:\APEXtranslate\1.png"))
    end_time = time.time()
    print(end_time - start_time)  # 0.36
