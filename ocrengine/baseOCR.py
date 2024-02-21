import Global


class BaseOCR:
    def __init__(self, typename):
        self.typename = typename

    def langmap(self):
        return {}

    def initocr(self):
        pass

    def ocr(self, imgpath):
        pass

    def end(self):
        pass

    ############################################################
    @property
    def srclang(self) -> str:
        try:
            l = {'日语': 'ja', '英语': 'en', '法语': 'latin', '韩语': 'ko', '阿拉伯语': 'ar', '西班牙语': 'latin', '俄语': 'ru',
                 '繁体中文': 'cht'}[Global.language]
            return l
        except:
            return ''

    @property
    def space(self):
        if not Global.ocr_setting["mergelines"]:  # 是否换行
            space = '\n'
        elif self.srclang in ['zh', 'ja', 'cht']:  # 不换行且是这几种语言则分隔符为空字符
            space = ''
        else:  # 否则分隔符为空格
            space = ' '
        return space

    ############################################################
