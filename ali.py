import logging
import re

import requests


def translate(content, lang):
    ss = requests.session()
    csrf = ss.get('https://translate.alibaba.com/api/translate/csrftoken', timeout=5,
                  ).json()['token']
    headers = {
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
    form_data = {
        "srcLang": lang,
        "tgtLang": "zh",
        "domain": 'general',
        'query': content,
        "_csrf": csrf
    }
    r = ss.post('https://translate.alibaba.com/api/translate/text', headers=headers,
                timeout=5, params=form_data)

    data = r.json()
    try:
        trans = data['data']['translateText']
    except KeyError:
        trans = "阿里公共接口抽风中，请重试或更换接口"
    xx = re.findall("&#(.*?);", trans)
    xx = set(xx)
    for _x in xx:  # 转换 HTML 实体字符
        try:
            trans = trans.replace(f'&#{_x};', chr(int(_x)))
        except Exception as e:
            logging.error(f"阿里公共接口:", e)
    return trans


if __name__ == '__main__':
    print(translate("大変な数ヶ月です。", "ja"))
