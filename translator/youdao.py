import time
import hashlib
import requests
import random


def getSign(useragent, content):
    t = hashlib.md5(bytes(useragent, encoding='utf-8')).hexdigest()
    r = int(1000 * time.time())
    i = r + int(10 * random.random())
    return {'ts': r, 'bv': t, 'salt': i, 'sign': hashlib.md5(
        bytes("fanyideskweb" + str(content) + str(i) + "Ygy_4c=r#e#4EX^NUGUc5", encoding='utf-8')).hexdigest()}

class Youdao:
    def __init__(self):
        self.language_map = {'日语': 'ja', '英语': 'en', '法语': 'fr', '韩语': 'ko', '阿拉伯语': 'ar', '西班牙语': 'es',
                             '俄语': 'ru'}
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://fanyi.youdao.com',
            'Pragma': 'no-cache',
            'Referer': 'https://fanyi.youdao.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.session = requests.session()
        self.session.trust_env = False
        self.session.headers.update(self.headers)
        self.session.get('https://fanyi.youdao.com')


    def translate(self, content, from_lang):
        if content == "" or content == "未下载该语言的OCR模型,请从软件主页下载模型解压到files/ocr路径后使用":
            content = ""
        try:
            from_lang = self.language_map[from_lang]
        except KeyError:
            return "不受支持的语种"
        params = {
            'smartresult': [
                'dict',
                'rule',
            ],
        }
        sign = getSign(self.headers['User-Agent'], content)
        data = {
            'i': content,
            'from': from_lang,
            'to': "zh",
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': sign['salt'],
            'sign': sign['sign'],
            'lts': sign['ts'],
            'bv': sign['bv'],
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_CLICKBUTTION',
        }

        response = self.session.post('https://fanyi.youdao.com/translate_o', params=params, headers=self.headers,
                                     data=data)

        res = ''
        for js in response.json()['translateResult']:
            if res != '':
                res += '\n'
            for _ in js:
                res += _['tgt']
        return res


if __name__ == '__main__':
    yd = Youdao()
    print(yd.translate("힘든 몇 달입니다.。", "韩语"))
