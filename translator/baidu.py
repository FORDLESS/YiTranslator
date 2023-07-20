import re
import time
import urllib.parse
import requests
import json


class Tse:
    def __init__(self):
        self.author = 'Union.Tse'
        self.begin_time = time.time()
        self.default_session_freq = int(1e3)
        self.default_session_seconds = 1.5e3

    @staticmethod
    def get_headers(host_url: str,
                    if_api: bool = False,
                    if_referer_for_host: bool = True,
                    if_ajax_for_api: bool = True,
                    if_json_for_api: bool = False,
                    if_multipart_for_api: bool = False,
                    if_http_override_for_api: bool = False
                    ) -> dict:

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/107.0.0.0 Safari/537.36 "
        url_path = urllib.parse.urlparse(host_url).path
        host_headers = {
            'Referer' if if_referer_for_host else 'Host': host_url,
            "User-Agent": user_agent,
        }
        api_headers = {
            'Origin': host_url.split(url_path)[0] if url_path else host_url,
            'Referer': host_url,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            "User-Agent": user_agent,
        }
        if if_api and not if_ajax_for_api:
            api_headers.pop('X-Requested-With')
            api_headers.update({'Content-Type': 'text/plain'})
        if if_api and if_json_for_api:
            api_headers.update({'Content-Type': 'application/json'})
        if if_api and if_multipart_for_api:
            api_headers.pop('Content-Type')
        if if_api and if_http_override_for_api:
            api_headers.update({'X-HTTP-Method-Override': 'GET'})
        return host_headers if not if_api else api_headers


class Tsa(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = 'https://fanyi.baidu.com'
        self.api_url = 'https://fanyi.baidu.com/transapi'
        self.get_lang_url = None
        self.get_lang_url_pattern = 'https://fanyi-cdn.cdn.bcebos.com/webStatic/translation/js/index.(.*?).js'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = {'日语': 'jp', '英语': 'en', '法语': 'fra', '韩语': 'kor', '阿拉伯语': 'ara', '西班牙语': 'spa',
                             '俄语': 'ru', '繁体中文': 'cht'}
        self.session = requests.Session()
        self.query_count = 0
        self.input_limit = int(5e3)

    def translate(self, query_text: str, from_language: str = 'auto', to_language: str = 'zh'):
        """
        https://fanyi.baidu.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :return: str or dict
        """
        if query_text == "" or query_text == "未下载该语言的OCR模型,请下载模型后解压到files/ocr路径后使用":
            return ""
        from_language = self.language_map[from_language]

        not_update_cond_freq = 1 if self.query_count < self.default_session_freq else 0  # 超过这个次数更新session
        not_update_cond_time = 1 if time.time() - self.begin_time < self.default_session_seconds else 0  # 超过这个时间更新session
        if not (not_update_cond_freq and not_update_cond_time):
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=5)  # must twice, send cookies.
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=5).text

            if not self.get_lang_url:
                self.get_lang_url = re.compile(self.get_lang_url_pattern).search(host_html).group()

        form_data = {
            'from': from_language,
            'to': to_language,
            'query': query_text,
            'source': 'txt',
        }
        r = self.session.post(self.api_url, data=form_data, headers=self.api_headers, timeout=5)
        r.raise_for_status()
        data = r.json()
        time.sleep(0)
        self.query_count += 1
        try:
            result = '\n'.join([item['dst'] for item in data['data']])
            return result
        except KeyError:
            return data["errmsg"]


if __name__ == '__main__':
    bd = Tsa()
    print(bd.translate("憂郁的臺灣烏龜。", "繁体中文"))
