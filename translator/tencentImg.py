import base64
import hashlib
import hmac
import io
import json
import time
import mss
import requests
from PIL import Image
import Global
from datetime import datetime

from utils import public


def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


class Tsa:
    def __init__(self):
        self.image_stream = io.BytesIO()
        self.sct = mss.mss()
        self.secret_id, self.secret_key = public.secret_load("Tencent")
        self.canonical_headers = "content-type:application/json; charset=utf-8\nhost:tmt.tencentcloudapi.com\nx-tc-action:imagetranslate\n"
        self.language_map = {'日语': 'ja', '英语': 'en', '法语': 'fr', '韩语': 'ko', '阿拉伯语': 'ar', '西班牙语': 'es', '俄语': 'ru',
                             '繁体中文': 'zh-TW'}

    def get_imgbytes(self):
        rect = (Global.rectX, Global.rectY, Global.rectX + Global.rectW, Global.rectY + Global.rectH)
        shot = self.sct.grab(rect)
        pix = Image.frombytes('RGB', shot.size, shot.rgb)
        self.image_stream.seek(0)
        self.image_stream.truncate(0)
        pix.save(self.image_stream, format='PNG')
        return self.image_stream.getvalue()

    def space(self, fromLang):
        if not Global.ocr_setting["mergelines"]:  # 是否换行
            space = '\n'
        elif fromLang in ['日语', '繁体中文']:  # 不换行且是这几种语言则分隔符为空字符
            space = ''
        else:  # 否则分隔符为空格
            space = ' '
        return space

    # 私人腾讯图片翻译api
    def translate(self,_, fromLang):
        fromLang = self.language_map[fromLang]

        image_bytes = self.get_imgbytes()

        # 将图片数据编码为 Base64 字符串
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        params = {
            'SessionUuid': "1",
            'Scene': 'doc',
            'Data': base64_data,
            'Source': fromLang,
            'Target': 'zh',
            'ProjectId': 0
        }

        timestamp = int(time.time())
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

        # ************* 步骤 1：拼接规范请求串 *************
        payload = json.dumps(params)
        hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        canonical_request = ("POST" + "\n" + "/" + "\n" + "" + "\n" + self.canonical_headers + "\n" +
                             "content-type;host;x-tc-action" + "\n" + hashed_request_payload)

        # ************* 步骤 2：拼接待签名字符串 *************
        credential_scope = date + "/" + "tmt" + "/" + "tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = ("TC3-HMAC-SHA256" + "\n" +
                          str(timestamp) + "\n" +
                          credential_scope + "\n" +
                          hashed_canonical_request)

        # ************* 步骤 3：计算签名 *************

        secret_date = sign(("TC3" + self.secret_key).encode("utf-8"), date)
        secret_service = sign(secret_date, "tmt")
        secret_signing = sign(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        # ************* 步骤 4：拼接 Authorization *************
        authorization = ("TC3-HMAC-SHA256" + " " +
                         "Credential=" + self.secret_id + "/" + credential_scope + ", " +
                         "SignedHeaders=content-type;host;x-tc-action" + ", " +
                         "Signature=" + signature)

        my_headers = {"Authorization": authorization,
                      "Content-Type": "application/json; charset=utf-8",
                      "Host": "tmt.tencentcloudapi.com",
                      "X-TC-Action": "ImageTranslate",
                      "X-TC-Timestamp": str(timestamp),
                      "X-TC-Version": '2018-03-21',
                      "X-TC-Region": "ap-guangzhou",
                      }

        response = requests.post('https://tmt.tencentcloudapi.com', headers=my_headers, data=payload)
        res = response.json()
        result = []
        source = []
        for item in res['Response']['ImageRecord']['Value']:
            x = item['X']
            y = item['Y']
            w = item['W']
            h = item['H']
            target_text = item['TargetText']
            source_text = item['SourceText']
            coords = f"{x},{y},{x + w},{y},{x + w},{y + h},{x},{y + h}"
            result.append(coords)
            source.append(coords)
            result.append(target_text)
            source.append(source_text)
        over_s = public.text_process(source)
        over_r = public.text_process(result)
        return self.space(fromLang).join(over_s), self.space(fromLang).join(over_r)


if __name__ == '__main__':
    txp = Tsa()
    Global.rectW = 450
    Global.rectH = 150
    Global.rectX = 200
    Global.rectY = 300
    Global.ocr_setting = {"mergelines": False}
    print(txp.translate("_","英语"))
