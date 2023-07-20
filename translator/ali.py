import logging
import re
import requests


class BaseTSA:
    pass


class Tsa(BaseTSA):
    def __init__(self):

        self.ss = requests.session()
        self.csrf = self.ss.get('https://translate.alibaba.com/api/translate/csrftoken', timeout=5).json()['token']
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://translate.alibaba.com',
            'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version': '"105.0.1343.53"',
            'sec-ch-ua-full-version-list': '"Microsoft Edge";v="105.0.1343.53", "Not)A;Brand";v="8.0.0.0", '
                                           '"Chromium";v="105.0.5195.127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
        }
        self.language_map = {'日语': 'ja', '英语': 'en', '法语': 'fr', '韩语': 'ko', '阿拉伯语': 'ar', '西班牙语': 'es', '俄语': 'ru',
                             '繁体中文': 'zh-tw'}

    def translate(self, content, lang):
        if content == "" or content == "未下载该语言的OCR模型,请下载模型后解压到files/ocr路径后使用":
            return ""
        lang = self.language_map[lang]
        form_data = {
            "srcLang": lang,
            "tgtLang": "zh",
            "domain": 'general',
            'query': content,
            "_csrf": self.csrf
        }
        r = self.ss.post('https://translate.alibaba.com/api/translate/text', headers=self.headers,
                         timeout=5, params=form_data)
        data = r.json()
        try:
            trans = data['data']['translateText']
        except (KeyError, TypeError):
            trans = "无内容或接口出错，请重试或更换接口"
        xx = re.findall("&#(.*?);", trans)
        xx = set(xx)
        for _x in xx:  # 转换 HTML 实体字符
            try:
                trans = trans.replace(f'&#{_x};', chr(int(_x)))
            except Exception as e:
                logging.error(f"阿里公共接口:", e)
        return trans


if __name__ == '__main__':
    ali = Tsa()
    print(ali.translate("تحقق", "阿拉伯语"))
