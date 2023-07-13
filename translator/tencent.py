import time
import re
import requests
import uuid

from translator.baidu import Tse


class QQTranSmart(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = 'https://transmart.qq.com'
        self.api_url = 'https://transmart.qq.com/api/imt'
        self.get_lang_url = None
        self.get_lang_url_pattern = '/assets/vendor.(.*?).js'  # e4c6831c
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=True)
        self.language_map = {'日语': 'ja', '英语': 'en', '法语': 'fr', '韩语': 'ko', '阿拉伯语': 'ar', '西班牙语': 'es',
                             '俄语': 'ru', '繁体中文': 'zh-tw'}
        self.session = None
        self.uuid = str(uuid.uuid4())
        self.query_count = 0
        self.input_limit = int(5e3)

    def get_clientKey(self):
        return 'browser-firefox-110.0.0-Windows 10-{}-{}'.format(self.uuid, int(time.time() * 1e3))

    def split_sentence(self, data):
        index_pair_list = [[item['start'], item['start'] + item['len']] for item in data['sentence_list']]
        index_list = [i for ii in index_pair_list for i in ii]
        return [data['text'][index_list[i]: index_list[i + 1]] for i in range(len(index_list) - 1)]

    def translate(self, query_text: str, from_language: str = 'auto', to_language: str = 'zh'):
        if query_text == "" or query_text == "未下载该语言的OCR模型,请从软件主页下载模型解压到files/ocr路径后使用":
            query_text = ""
        from_language = self.language_map[from_language]
        sleep_seconds = 0
        update_session_after_freq = self.default_session_freq
        update_session_after_seconds = self.default_session_seconds

        not_update_cond_freq = 1 if self.query_count < update_session_after_freq else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=5).text

            if not self.get_lang_url:
                self.get_lang_url = self.host_url + re.compile(self.get_lang_url_pattern).search(host_html).group()

        client_key = self.get_clientKey()
        self.api_headers.update({'Cookie': 'client_key={}'.format(client_key)})

        split_form_data = {
            'header': {
                'fn': 'text_analysis',
                'client_key': client_key,
            },
            'type': 'plain',
            'text': query_text,
            'normalize': {'merge_broken_line': 'false'}
        }
        split_data = self.session.post(self.api_url, json=split_form_data, headers=self.api_headers, timeout=5).json()
        text_list = self.split_sentence(split_data)

        api_form_data = {
            'header': {
                'fn': 'auto_translation',
                'client_key': client_key,
            },
            'type': 'plain',
            'model_category': 'normal',
            'source': {
                'lang': from_language,
                'text_list': [''] + text_list + [''],
            },
            'target': {'lang': to_language}
        }
        r = self.session.post(self.api_url, json=api_form_data, headers=self.api_headers, timeout=5)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return ''.join(data['auto_translation'])


if __name__ == '__main__':
    tx = QQTranSmart()
    print(tx.translate("憂郁的臺灣烏龜。", "繁体中文"))
