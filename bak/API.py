import base64
import hashlib
import hmac
import http.client
import json
import logging
import random
import time
import urllib
import requests
import Global
from urllib.parse import quote
from datetime import datetime


# 私人百度文本翻译api


def baidu_parse(uuid, key, fromLang, text):
    httpClient = None
    endpoint = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    if text == '':
        text = 'No text detected in the selected area'
    toLang = 'zh'  # 译文语种
    salt = random.randint(16384, 65536)
    sign_str = uuid + text + str(salt) + key
    sign_hex = hashlib.md5(sign_str.encode()).hexdigest()
    my_url = endpoint + '?appid=' + uuid + '&q=' + urllib.parse.quote(
        text) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign_hex

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', my_url)

        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        if "error_code" in result:
            logging.error(f"Baidu Error occurred: {result['error_code']}'")
            return {
                "trans_result": [{"src": "钝角", "dst": "无法解决请联系作者:" + Global.Baidu_ERROR_map[result['error_code']]}]}
        return result
    except Exception as error:
        logging.error(f"Baidu Error occurred: {error}")
        return "请前往错误日志查看报错"
    finally:
        if httpClient:
            httpClient.close()


# 私人腾讯文本翻译api
def tencent_parse(uuid, key, fromLang, text):
    timestamp = int(time.time())
    salt = random.randint(16384, 65536)
    toLang = 'zh'
    api_url = 'tmt.tencentcloudapi.com/'
    if text == '':
        text = 'No text detected in the selected area'

    content = '?Action=' + 'TextTranslate' + '&Nonce=' + str(salt) + '&ProjectId=' + '0' + '&Region=' + \
              'ap-guangzhou' + '&SecretId=' + uuid + '&Source=' + fromLang + '&SourceText=' + text + '&Target=' + \
              toLang + '&Timestamp=' + str(timestamp) + '&Version=' + '2018-03-21'

    # 拼接签名原文字符串
    signature_raw = 'GET' + api_url + content
    # 生成签名串，并进行url编码
    hmac_code = hmac.new(bytes(key, 'utf8'), signature_raw.encode('utf8'), hashlib.sha1).digest()
    sign = quote(base64.b64encode(hmac_code))
    # 添加签名请求参数
    my_url = content + '&Signature=' + sign
    url_with_args = 'https://tmt.tencentcloudapi.com/' + my_url
    try:
        res = requests.get(url_with_args)
        json_res = json.loads(res.text)
        if "Error" in json_res['Response']:
            logging.error(f"Error occurred: {json_res['Response']['Error']}'")
            return "请前往错误日志查看报错"
        result = json_res['Response']['TargetText']
        return result
    except Exception as error:
        logging.error(f"Tencent Error occurred: {error}")
        return "请前往错误日志查看报错"


# 计算签名摘要函数
def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


# 私人腾讯图片翻译api
def online_translate(uuid, key, fromLang, path):
    secret_id = uuid
    secret_key = key

    image_path = path
    with open(image_path, 'rb') as f:
        image_data = f.read()

        # 将图片数据编码为 Base64 字符串
    base64_data = base64.b64encode(image_data).decode('utf-8')
    params = {
        'SessionUuid': "1",
        'Scene': 'doc',
        'Data': base64_data,
        'Source': fromLang,
        'Target': 'zh',
        'ProjectId': 0
    }

    host = 'tmt.tencentcloudapi.com'
    action = 'ImageTranslate'
    timestamp = int(time.time())
    date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

    # ************* 步骤 1：拼接规范请求串 *************
    payload = json.dumps(params)
    canonical_headers = "content-type:application/json; charset=utf-8\nhost:%s\nx-tc-action:%s\n" % (
        host, action.lower())
    signed_headers = "content-type;host;x-tc-action"
    hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    canonical_request = ("POST" + "\n" + "/" + "\n" + "" + "\n" + canonical_headers + "\n" +
                         "content-type;host;x-tc-action" + "\n" + hashed_request_payload)

    # ************* 步骤 2：拼接待签名字符串 *************
    credential_scope = date + "/" + "tmt" + "/" + "tc3_request"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    string_to_sign = ("TC3-HMAC-SHA256" + "\n" +
                      str(timestamp) + "\n" +
                      credential_scope + "\n" +
                      hashed_canonical_request)

    # ************* 步骤 3：计算签名 *************

    secret_date = sign(("TC3" + secret_key).encode("utf-8"), date)
    secret_service = sign(secret_date, "tmt")
    secret_signing = sign(secret_service, "tc3_request")
    signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    # ************* 步骤 4：拼接 Authorization *************
    authorization = ("TC3-HMAC-SHA256" + " " +
                     "Credential=" + secret_id + "/" + credential_scope + ", " +
                     "SignedHeaders=" + signed_headers + ", " +
                     "Signature=" + signature)

    my_headers = {"Authorization": authorization,
                  "Content-Type": "application/json; charset=utf-8",
                  "Host": host,
                  "X-TC-Action": action,
                  "X-TC-Timestamp": str(timestamp),
                  "X-TC-Version": '2018-03-21',
                  "X-TC-Region": "ap-guangzhou",
                  }

    response = requests.post('https://tmt.tencentcloudapi.com', headers=my_headers, data=payload)
    print(response.json())
    return response.json()
