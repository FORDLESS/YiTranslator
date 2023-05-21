import json
import logging
import os
from tkinter import messagebox

screenWidth = 0
screenHeight = 0
rectW = 0
rectH = 0
rectX = 0
rectY = 0
hotKey = None
language = None
CUDA = False
batchSize = 0
hotkey_use = False
api_co = None
uuid = ""
key = ""
auto = False
start_pause = False

in_personal_page = True
in_public_page = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
setting_path = os.path.join(BASE_DIR, "settings.json")

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


def read_settings(filepath):
    try:
        with open(filepath, "r") as file:
            settings = json.load(file)
        return settings
    except FileNotFoundError:
        messagebox.showerror("文件丢失", "(/ﾟДﾟ)/！怎么把配置文件丢了？给你初始化一个！\n请重新打开软件！")
        create_default_json()
    except json.JSONDecodeError:
        messagebox.showerror("解码错误", "！！！ Σ(っ °Д °;)っ你小子往配置文件里下毒了？\n无法解决请联系作者！")
    except Exception as error:
        messagebox.showerror("未知错误", "Σ( ° △ °|||)是我没有预料到的错误\n请将运行日志发送给作者！")
        logging.error(f"打开时出现未知错误: {error}")


set_config = read_settings(setting_path)


def save_settings(filepath):
    with open(filepath, "w") as file:
        json.dump(set_config, file, indent=4)


def create_default_json():
    default_settings = {
        "User": {"screenwidth": 1920, "screenheight": 1080, "CUDA": "False"},
        "tencentAPI": {"secretID": "",
                       "secretKey": ""},
        "baiduAPI": {"secretID": "", "secretKey": ""},
        "area": {"x": 0, "y": 0, "width": 200, "height": 200},
        "hotKey": "NEXT",
        "language": "English",
        "batch_size": 0,
        "hotkey_use": "True",
        "API_CO": "Tencent"
    }

    with open(setting_path, "w") as file:
        json.dump(default_settings, file, indent=4)


def global_init():
    global screenWidth, screenHeight, rectW, rectH, rectX, rectY, hotKey, language, CUDA, batchSize, hotkey_use, \
        start_pause, in_personal_page, in_public_page, auto, api_co
    try:
        screenWidth = set_config["User"]["screenwidth"]
        screenHeight = set_config["User"]["screenheight"]
        rectW = set_config["area"]["width"]
        rectH = set_config["area"]["height"]
        rectX = set_config["area"]["x"]
        rectY = set_config["area"]["y"]
        hotKey = set_config["hotKey"]
        language = [ocr_language_map[set_config["language"]]]
        CUDA = set_config["User"]["CUDA"]
        batchSize = set_config["batch_size"]
        hotkey_use = set_config["hotkey_use"]
        api_co = set_config["API_CO"]
        auto = set_config["Auto"]
        start_pause = set_config["start_pause"]
        in_personal_page = set_config["h_page"]["in_personal_page"]
        in_public_page = set_config["h_page"]["in_public_page"]
    except Exception as error:
        messagebox.showerror("未知错误", "Σ( ° △ °|||)是我没有预料到的错误\n请将运行日志发送给作者！")
        logging.error(f"打开时出现未知错误: {error}")


