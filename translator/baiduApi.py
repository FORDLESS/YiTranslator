import hashlib
import json
import logging
import random
import urllib.parse
from http import client
import Global
import public


class Tsa:
    def __init__(self):
        self.endpoint = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
        self.httpClient = None
        self.toLang = 'zh'  # 译文语种
        self.uuid, self.key = public.secret_load("Baidu")
        self.language_map = {'日语': 'jp', '英语': 'en', '法语': 'fra', '韩语': 'kor', '阿拉伯语': 'ara', '西班牙语': 'spa', '俄语': 'ru',
                             '繁体中文': 'cht'}

    def translate(self, text, fromLang):
        if text == '':
            return 'No text detected in the selected area'
        fromLang = self.language_map[fromLang]
        salt = random.randint(16384, 65536)
        sign_str = self.uuid + text + str(salt) + self.key
        sign_hex = hashlib.md5(sign_str.encode()).hexdigest()
        my_url = self.endpoint + '?appid=' + self.uuid + '&q=' + urllib.parse.quote(
            text) + '&from=' + fromLang + '&to=' + self.toLang + '&salt=' + str(
            salt) + '&sign=' + sign_hex

        try:
            self.httpClient = client.HTTPConnection('api.fanyi.baidu.com')
            self.httpClient.request('GET', my_url)

            response = self.httpClient.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)

            if "error_code" in result:
                logging.error(f"Baidu Error occurred: {result['error_code']}'")
                return Global.Baidu_ERROR_map[result['error_code']]
            return result["trans_result"][0]["dst"]
        except Exception as error:
            logging.error(f"Baidu Error occurred: {error}")
            return "请前往错误日志查看报错"
        finally:
            if self.httpClient:
                self.httpClient.close()


if __name__ == '__main__':
    ali = Tsa()
    print(ali.translate("تحقق", "阿拉伯语"))
