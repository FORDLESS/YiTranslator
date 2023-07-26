import json
import time
from lxml import etree
import requests
from urllib import parse
from translator.baidu import Tse


class Tsa(Tse):
    def __init__(self, server_region='EN'):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://translate.google.com'
        self.api_url = None
        self.api_url_path = '/_/TranslateWebserverUi/data/batchexecute'
        self.server_region = server_region
        self.host_headers = None
        self.language_map = None
        self.session = None
        self.rpcid = 'MkEWBc'
        self.query_count = 0
        self.output_zh = 'zh-CN'
        self.input_limit = int(5e3)
        self.session = requests.Session()
        self.language_map = {'日语': 'ja', '英语': 'en', '法语': 'fr', '韩语': 'ko', '阿拉伯语': 'ar', '西班牙语': 'es',
                             '俄语': 'ru', '繁体中文': 'zh-TW'}



    def get_rpc(self, query_text: str, from_language: str, to_language: str) -> dict:
        param = json.dumps([[query_text, from_language, to_language, True], [1]])
        rpc = json.dumps([[[self.rpcid, param, None, "generic"]]])
        return {'f.req': rpc}

    @staticmethod
    def get_consent_cookie(consent_html: str) -> str:  # by mercuree. merged but not verify.
        et = etree.HTML(consent_html)
        input_element = et.xpath('.//input[@type="hidden"][@name="v"]')
        cookie_value = input_element[0].attrib.get('value') if input_element else 'cb'
        return f'CONSENT=YES+{cookie_value}'  # cookie CONSENT=YES+cb works for now


    def translate(self, query_text: str, from_language: str = 'auto', to_language: str = 'zh-CN'):
        if query_text == "" or query_text == "未下载该语言的OCR模型,请下载模型后解压到files/ocr路径后使用":
            return ""
        from_language = self.language_map[from_language]
        if len(query_text) > self.input_limit:
            return "超出字数限制"

        self.api_url = f'{self.host_url}{self.api_url_path}'
        self.host_headers = self.host_headers or self.get_headers(self.host_url, if_api=False)  # reuse cookie header
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_referer_for_host=True, if_ajax_for_api=True)

        proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
        is_detail_result = False

        not_update_cond_freq = 1 if self.query_count % self.default_session_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < self.default_session_seconds else 0
        if not (not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            r = self.session.get(self.host_url, headers=self.host_headers, timeout=5, proxies=proxies)
            if 'consent.google.com' == parse.urlparse(r.url).hostname:
                self.host_headers.update({'cookie': self.get_consent_cookie(r.text)})


        rpc_data = self.get_rpc(query_text, from_language, to_language)
        rpc_data = parse.urlencode(rpc_data)
        r = self.session.post(self.api_url, headers=self.api_headers, data=rpc_data, timeout=5, proxies=proxies)
        r.raise_for_status()
        json_data = json.loads(r.text[6:])
        data = json.loads(json_data[0][2])
        self.query_count += 1
        return {'data': data} if is_detail_result else ' '.join(
            [x[0] for x in (data[1][0][0][5] or data[1][0]) if x[0]])


if __name__ == '__main__':
    bd = Tsa()
    print(bd.translate("憂郁的臺灣烏龜。", "繁体中文"))
