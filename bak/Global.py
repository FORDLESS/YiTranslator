import os

screenWidth = 0
screenHeight = 0
rectW = 0
rectH = 0
rectX = 0
rectY = 0
hotKey = None
language = None
haveCUDA = None
batchSize = 0
hotkey_use = None
api_co = None
uuid = ""
key = ""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "settings.json")

ocr_language_map = {'Japanese': 'ja', 'English': 'en', 'French': 'fr', 'Korean': 'ko', 'German': 'de', 'Spanish': 'es',
                    'Russian': 'ru'}
baidu_map = {'ja': 'jp', 'en': 'en', 'ko': 'kor', 'de': 'de', 'es': 'spa', 'ru': 'ru'}
tencent_map = {'ja': 'ja', 'en': 'en', 'ko': 'ko', 'de': 'de', 'es': 'es', 'ru': 'ru'}
l_Tmap = {'Japanese': '日语', 'English': '英语', 'French': '法语', 'Korean': '韩语', 'German': '德语', 'Spanish': '西班牙语',
          'Russian': '俄语'}
hotkey_map = {'Shift_L': 'shift', 'minus': '-', 'Shift_R': 'shift', 'Alt_L': 'alt', 'Alt_R': 'alt',
              'Next': 'page down',
              'Prior': 'page up', 'Control_L': 'ctrl', 'Control_R': 'ctrl'}

Baidu_ERROR_map = {"52001": "请求超时，请检查网络连接", "52002": "系统错误，百度抽风，请重试", "52003": " 请检查id是否正确或者服务是否开通",
                   "54000": "必填参数为空，不应该出现的错误，请联系作者", "54001": "签名错误，请联系作者", "54003": "访问频率过高，请稍后重试",
                   "54004": "账户免费额度用尽，建议换个接口", "54005": "超长文本频繁请求，请稍后重试", "58000": "客户端IP非法，"
                                                                                   "请删除开发者资料中的ip地址！",
                   "58002": "服务当前已关闭，请前往管理控制台开启服务", "90107": "认证未通过或未生效，请前往我的认证查看认证进度"}
