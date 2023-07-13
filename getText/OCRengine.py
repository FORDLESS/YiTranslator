import importlib
import time
from difflib import SequenceMatcher
import Global
import mss
import numpy as np
from PIL import Image


def image2np(PImage) -> np.ndarray:  # 将image对象转为np数组形式
    pic = PImage.convert("L")
    return np.array(pic)


def compareImage(img1: np.ndarray, img2: np.ndarray) -> float:  # 比较两张图片的像素相似度
    size = img1.size
    cnt = np.sum(img1 == img2)
    return cnt / size


def getEqualRate(str1, str2) -> float:
    return SequenceMatcher(None, str1, str2).quick_ratio()


class OCR:
    def __init__(self):
        self.last_img = None
        self.last_rec_img = None
        self.last_text = None
        self.last_ocr_time = 0
        self.now_use_ocr = None
        self.ocr_engine = None
        self.timestamp = time.time()
        self.sec = mss.mss()
        self.runonce()

    def imageCut(self, x1, y1, x2, y2):  # 截图返回Image对象
        if x2 > x1 and y2 > y1:
            shot = self.sec.grab((x1, y1, x2, y2))
            pix = Image.frombytes('RGB', shot.size, shot.rgb)
            return pix
        else:
            return None

    def gettext1(self) -> str:  # 也许下面的方法更好
        time.sleep(0.01)
        with mss.mss() as sct:
            rect = (Global.rectX, Global.rectY, Global.rectX + Global.rectW, Global.rectY + Global.rectH)
            shot = sct.grab(rect)
            grab_img = Image.frombytes('RGB', shot.size, shot.rgb)
        """
        Due to the use of multi-threading problems,
        there will be problems when the screenshot method is initialized in the class and encapsulated separately
        so put it directly in the function
        """

        if grab_img is None:
            return "no scope"

        ok = True
        # 0,2 indicates that the recognition method for detecting image updates is selected
        if Global.ocr_setting["ocr_auto_method"] in [0, 2]:
            img_np = image2np(grab_img)
            if self.last_img is not None and (img_np.shape == self.last_img.shape):
                # If there is a picture saved last time, and the size of the picture is the same
                # compare the similarity between the picture saved last time and the current picture
                # The more similar the higher the score
                sim_score = compareImage(img_np, self.last_img)
            else:
                sim_score = 0
            # After the judgment is completed, the last saved picture is set as the current picture
            self.last_img = img_np
            # Compared with the preset threshold, decide whether to scan
            if sim_score <= Global.ocr_setting['ocr_diff_sim']:
                self.last_rec_img = img_np  # The picture is saved as the last recognized image, waiting to be scanned
            else:
                ok = False  # Explain that the pictures are highly similar and do not need OCR scanning
        if Global.ocr_setting['ocr_auto_method'] in [1, 2]:  # use time period detection
            if time.time() - self.last_ocr_time > Global.ocr_setting['ocr_interval']:
                # If the elapsed time exceeds the set interval
                ok = True
                self.last_ocr_time = time.time()  # update last scan time
            else:
                ok = False
        if not ok:  # If no OCR scanning is performed, return ""
            return ""
        text = self.runOCR(grab_img)  # Execute the OCR scanning function and return the text
        # If the saved text is not empty, compare the text similarity
        if self.last_text is not None:
            sim = getEqualRate(self.last_text, text)
            if sim > 0.95:
                return ""  # Return the "" to avoid repeated translation
        self.last_text = text
        return text

    def gettext(self) -> str:
        time.sleep(0.01)
        with mss.mss() as sct:
            rect = (Global.rectX, Global.rectY, Global.rectX + Global.rectW, Global.rectY + Global.rectH)
            shot = sct.grab(rect)
            grab_img = Image.frombytes('RGB', shot.size, shot.rgb)

        if grab_img is None:
            return "no scope"

        ok = True
        if Global.ocr_setting["ocr_auto_method"] in [0, 2]:
            img_np = image2np(grab_img)
            if self.last_img is not None and (img_np.shape == self.last_img.shape):
                stable_score = compareImage(img_np, self.last_img)
            else:
                stable_score = 0
            self.last_img = img_np
            if stable_score >= Global.ocr_setting['ocr_stable_sim']:
                if self.last_rec_img is not None and (img_np.shape == self.last_rec_img.shape):
                    sim_score = compareImage(img_np, self.last_rec_img)
                else:
                    sim_score = 0
                if sim_score > Global.ocr_setting['ocr_diff_sim']:  # 如果相似度分数高于预设图像一致性值
                    ok = False  # 说明图片高度相似，无需OCR扫描
                else:
                    self.last_rec_img = img_np  # 否则该图片被保存为最后识别图像，等待扫描
            else:
                ok = False
        if Global.ocr_setting['ocr_auto_method'] in [1, 2]:
            if time.time() - self.last_ocr_time > Global.ocr_setting['ocr_interval']:
                # If the elapsed time exceeds the set interval
                ok = True
                self.last_ocr_time = time.time()  # update last scan time
            else:
                ok = False
        if not ok:  # If no OCR scanning is performed, return ""
            return ""
        text = self.runOCR(grab_img)  # Execute the OCR scanning function and return the text
        # If the saved text is not empty, compare the text similarity
        if self.last_text is not None:
            sim = getEqualRate(self.last_text, text)
            if sim > 0.95:
                return ""  # Return the "" to avoid repeated translation
        self.last_text = text
        return text

    def runonce(self):
        img = self.imageCut(Global.rectX, Global.rectY, Global.rectX + Global.rectW, Global.rectY + Global.rectH)
        if img is not None:
            text = self.runOCR(img)
            img_np = image2np(img)
            self.last_img = img_np
            self.last_rec_img = img_np
            self.last_ocr_time = time.time()
            self.last_text = text
            return self.last_text
        else:
            return None

    def runOCR(self, img):
        # 判断使用的是哪个OCR引擎并且确定是否存在
        if Global.OCR is None:
            return None
        fname = f'{Global.BASE_DIR}/.cache/ocr/{self.timestamp}.png'  # 以时间戳命名图片名称缓存在指定文件夹
        img.save(fname)
        if self.now_use_ocr == "local" and Global.OCR != "local":  # 判断当前使用的OCR引擎是否为本地OCR
            try:
                self.ocr_engine.end()  # 如果是则关闭
            except:
                pass
        if self.ocr_engine is not None and Global.OCR == self.now_use_ocr:  # 如果已经实例化过并且没有更改OCR
            return self.ocr_engine.ocr(fname)
        aclass = importlib.import_module('ocrengine.' + Global.OCR).OCR  # 根据use动态的导入对应py文件中的OCR类并赋值给aclass
        self.ocr_engine = aclass(Global.OCR)  # 然后将这个OCR类实例化赋值给self.ocrengine
        self.now_use_ocr = Global.OCR  # 将设置项赋值给当前使用的引擎
        return self.ocr_engine.ocr(fname)  # 返回识别完成的字符串


if __name__ == '__main__':
    Global.ocr_setting = {
        "mergelines": False,
        "ocr_auto_method": 1,
        "ocr_stable_sim": 0.8,
        "ocr_diff_sim": 0.8,
        "ocr_interval": 5
    }
    Global.rectW = 450
    Global.rectH = 150
    Global.rectX = 200
    Global.rectY = 300
    Global.language = "英语"
    Global.OCR = "local"
    ocr = OCR()
    while True:
        print(ocr.gettext())
