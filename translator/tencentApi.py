import base64
import hashlib
import hmac
import json
import logging
import random
import time
from urllib.parse import quote
import requests

import public


def get_string_to_sign(method, endpoint, params):
    s = method + endpoint + "/?"
    query_str = "&".join("%s=%s" % (k, params[k]) for k in sorted(params))
    return s + query_str


def sign_str(key, s, method):
    hmac_str = hmac.new(key.encode("utf8"), s.encode("utf8"), method).digest()
    return base64.b64encode(hmac_str)


class Tsa:
    def __init__(self):
        self.toLang = 'zh'
        self.api_url = 'tmt.tencentcloudapi.com/'
        self.uuid, self.key = public.secret_load("Tencent")
        self.language_map = {'日语': 'ja', '英语': 'en', '法语': 'fr', '韩语': 'ko', '阿拉伯语': 'ar', '西班牙语': 'es', '俄语': 'ru',
                             '繁体中文': 'zh-TW'}

    def translate1(self, text, fromLang):
        if text == '':
            return 'No text detected in the selected area'
        timestamp = int(time.time())
        salt = random.randint(16384, 65536)
        fromLang = self.language_map[fromLang]

        content = '?Action=' + 'TextTranslate' + '&Nonce=' + str(salt) + '&ProjectId=' + '0' + '&Region=' + \
                  'ap-guangzhou' + '&SecretId=' + self.uuid + '&Source=' + fromLang + '&SourceText=' + text + '&Target=' + \
                  self.toLang + '&Timestamp=' + str(timestamp) + '&Version=' + '2018-03-21'

        # 拼接签名原文字符串
        signature_raw = 'GET' + self.api_url + content
        # 生成签名串，并进行url编码
        hmac_code = hmac.new(bytes(self.key, 'utf8'), signature_raw.encode('utf8'), hashlib.sha1).digest()
        sign = quote(base64.b64encode(hmac_code))
        # 添加签名请求参数
        my_url = content + '&Signature=' + sign
        url_with_args = 'https://tmt.tencentcloudapi.com/' + my_url
        try:
            res = requests.get(url_with_args)
            json_res = json.loads(res.text)
            if "Error" in json_res['Response']:
                logging.error(f"Tencent Error occurred: {json_res['Response']['Error']}'")
                return "请前往错误日志查看报错"
            result = json_res['Response']['TargetText']
            return result
        except Exception as error:
            logging.error(f"Tencent Error occurred: {error}")
            return "请前往错误日志查看报错"

    def translate(self, text, fromLang='auto', toLang='zh'):
        if text == '':
            return 'No text detected in the selected area'
        fromLang = self.language_map[fromLang]
        endpoint = "tmt.tencentcloudapi.com"
        data = {
            'SourceText': text,
            'Source': fromLang,
            'Target': toLang,
            'Action': "TextTranslate",
            'Nonce': random.randint(32768, 65536),
            'ProjectId': 0,
            'Region': 'ap-hongkong',
            'SecretId': self.uuid,
            'SignatureMethod': 'HmacSHA1',
            'Timestamp': int(time.time()),
            'Version': '2018-03-21',
        }
        s = get_string_to_sign("GET", endpoint, data)
        data["Signature"] = sign_str(self.key, s, hashlib.sha1)
        try:
            res = requests.get("https://" + endpoint, params=data, timeout=3)
            json_res = json.loads(res.text)
            if "Error" in json_res['Response']:
                logging.error(f"Tencent Error occurred: {json_res['Response']['Error']}'")
                return "请前往错误日志查看报错"
            result = json_res['Response']['TargetText']
            return result
        except Exception as error:
            logging.error(f"Tencent Error occurred: {error}")
            return "请前往错误日志查看报错"


if __name__ == '__main__':
    bd = Tsa()
    print(bd.translate("憂郁的臺灣烏龜。", "繁体中文"))