import base64
import datetime
import hashlib
import hmac
import json
import uuid
from datetime import datetime
from urllib.parse import quote

import requests


class Tsa:
    def __init__(self):
        self.url = 'api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=zh'
        self.language_map = {'日语': 'ja', '英语': 'en', '法语': 'fr', '韩语': 'ko', '阿拉伯语': 'ar', '西班牙语': 'es',
                             '俄语': 'ru', '繁体中文': 'zh-TW'}
        self._privateKey = [
            0xa2, 0x29, 0x3a, 0x3d, 0xd0, 0xdd, 0x32, 0x73,
            0x97, 0x7a, 0x64, 0xdb, 0xc2, 0xf3, 0x27, 0xf5,
            0xd7, 0xbf, 0x87, 0xd9, 0x45, 0x9d, 0xf0, 0x5a,
            0x09, 0x66, 0xc6, 0x30, 0xc6, 0x6a, 0xaa, 0x84,
            0x9a, 0x41, 0xaa, 0x94, 0x3a, 0xa8, 0xd5, 0x1a,
            0x6e, 0x4d, 0xaa, 0xc9, 0xa3, 0x70, 0x12, 0x35,
            0xc7, 0xeb, 0x12, 0xf6, 0xe8, 0x23, 0x07, 0x9e,
            0x47, 0x10, 0x95, 0x91, 0x88, 0x55, 0xd8, 0x17
        ]

    def get_signature(self, private_key):
        guid = str(uuid.uuid4()).replace('-', '')
        escaped_url = quote(self.url, safe='')
        dateTime = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        bytes_str = 'MSTranslatorAndroidApp{}{}{}'.format(escaped_url, dateTime, guid).lower().encode('utf-8')
        hash_ = hmac.new(bytes(private_key), bytes_str, hashlib.sha256).digest()
        signature = 'MSTranslatorAndroidApp::{}::{}::{}'.format(base64.b64encode(hash_).decode(), dateTime, guid)
        return signature

    def translate(self, text, from_language=None):
        if text == "" or text == "未下载该语言的OCR模型,请下载模型后解压到files/ocr路径后使用":
            return ""
        if from_language is not None:
            self.url += '&from={}'.format(self.language_map[from_language])
        headers = {
            'X-MT-Signature': self.get_signature(self._privateKey),
            'Content-Type': 'application/json'
        }
        json_data = [{"Text": text}]
        try:
            response = requests.post('https://{}'.format(self.url), headers=headers,data=json.dumps(json_data).encode('utf-8'))
            data_json = response.json()
            root = data_json[0]['translations'][0]['text']
            return root
        except Exception as e:
            return e


if __name__ == '__main__':
    ms = Tsa()
    print(ms.translate("language", "英语"))
