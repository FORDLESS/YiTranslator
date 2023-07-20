import hashlib
import requests
import random
from translator.baidu import Tse


def get_form(query_text, from_language):
    uuid = ''
    for i in range(8):
        uuid += hex(int(65536 * (1 + random.random())))[2:][1:]
        if i in range(1, 5):
            uuid += '-'
    sign_text = "" + from_language + "zh-CHS" + query_text + '109984457'  # window.__INITIAL_STATE__.common.CONFIG.secretCode
    sign = hashlib.md5(sign_text.encode()).hexdigest()
    form = {
        "from": from_language,
        "to": "zh-CHS",
        "text": query_text,
        "uuid": uuid,
        "s": sign,
        "client": "pc",  # wap
        "fr": "browser_pc",  # browser_wap
        "needQc": "1",
    }
    return form


class Tsa(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = 'https://fanyi.sogou.com'
        self.api_url = 'https://fanyi.sogou.com/api/transpc/text/result'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = {'日语': 'ja', '英语': 'en', '法语': 'fr', '韩语': 'ko', '阿拉伯语': 'ar', '西班牙语': 'es',
                             '俄语': 'ru'}
        self.form_data = None
        self.query_count = 0
        self.input_limit = 5000

    def translate(self, query_text, from_lang):
        if query_text == "" or query_text == "未下载该语言的OCR模型,请下载模型后解压到files/ocr路径后使用":
            return ""
        try:
            from_lang = self.language_map[from_lang]
        except KeyError:
            return "不支持该语种"
        with requests.Session() as ss:
            _ = ss.get(self.host_url, headers=self.host_headers).text
            self.form_data = get_form(query_text, from_lang)
            r = ss.post(self.api_url, headers=self.api_headers, data=self.form_data)
            data = r.json()
        return data['data']['translate']['dit']


if __name__ == '__main__':
    sg = Tsa()
    print(sg.translate("大変な数ヶ月です。", "日语"))

