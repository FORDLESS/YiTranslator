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
hotkey_use = False
language = None
CUDA = False
api_co = None  # 私人接口名
auto = False  # 是否自动
start_pause = False  # 是否暂停
public_trans = None  # 公共翻译接口名
inputSource = None  # 输入方式名
OCR = None  # OCR名
sourceHide = False  # 是否隐藏原文
ocr_setting = None

b_flag = False
getresultRunning = False
getsourceRunning = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
setting_path = os.path.join(BASE_DIR,"files", "settings.json")


quick_lan = []
Baidu_ERROR_map = {"52001": "请求超时，请检查网络连接", "52002": "系统错误，百度抽风，请重试", "52003": " 请检查id是否正确或者服务是否开通",
                   "54000": "必填参数为空，不应该出现的错误，请联系作者", "54001": "签名错误，请联系作者", "54003": "访问频率过高，请稍后重试",
                   "54004": "账户免费额度用尽，建议换个接口", "54005": "超长文本频繁请求，请稍后重试", "58000": "客户端IP非法，"
                                                                                   "请删除开发者资料中的ip地址！",
                   "58002": "服务当前已关闭，请前往管理控制台开启服务", "90107": "认证未通过或未生效，请前往我的认证查看认证进度"}
modifier_key = [0, 16, 17, 18, 91]
modifier_key_T = {0: 0, 1: "Alt", 2: "Ctrl", 4: "Shift", 8: "Win", 16: 4, 17: 2, 18: 1, 91: 8}

VK_CODE = {112: "F1",
           113: "F2",
           114: "F3",
           115: "F4",
           116: "F5",
           117: "F6",
           118: "F7",
           119: "F8",
           120: "F9",
           121: "F10",
           122: "F11",
           123: "F12",
           65: "A",
           66: "B",
           67: "C",
           68: "D",
           69: "E",
           70: "F",
           71: "G",
           72: "H",
           73: "I",
           74: "J",
           75: "K",
           76: "L",
           77: "M",
           78: "N",
           79: "O",
           80: "P",
           81: "Q",
           82: "R",
           83: "S",
           84: "T",
           85: "U",
           86: "V",
           87: "W",
           88: "X",
           89: "Y",
           90: "Z",
           48: "0",
           49: "1",
           50: "2",
           51: "3",
           52: "4",
           53: "5",
           54: "6",
           55: "7",
           56: "8",
           57: "9",
           38: "UP",
           40: "DOWN",
           37: "LEFT",
           39: "RIGHT",
           33: "PRIOR",
           34: "NEXT",
           36: "HOME",
           35: "END",
           45: "INSERT",
           13: "ENTER",
           9: "TAB",
           32: "SPACE",
           8: "BACKSPACE",
           46: "DELETE",
           27: "ESCAPE",
           19: "PAUSE",
           106: "MULTIPLY",
           107: "ADD",
           108: "SEPARATOR",
           109: "SUBTRACT",
           110: "DECIMAL",
           111: "DIVIDE",
           96: "NUM 0",
           97: "NUM 1",
           98: "NUM 2",
           99: "NUM 3",
           100: "NUM 4",
           101: "NUM 5",
           102: "NUM 6",
           103: "NUM 7",
           104: "NUM 8",
           105: "NUM 9",
           186: ";",
           188: "<",
           189: "-",
           190: ">",
           191: "/",
           187: "=",
           220: "\\",
           221: "]",
           219: "[",
           222: "'",
           18: "Alt",
           17: "Control",
           16: "Shift",
           20: "Caps_Lock",
           91: "Win",
           192: "~",
           229: "！中文输入",
           0: "", 1: "Alt", 2: "Ctrl", 4: "Shift"}


def read_settings(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
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
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(set_config, file, indent=4, ensure_ascii=False)


def create_default_json():
    default_settings = {
        "User": {
            "screenwidth": 1920,
            "screenheight": 1080,
            "CUDA": False
        },
        "tencentAPI": {
            "secretID": "",
            "secretKey": ""
        },
        "baiduAPI": {
            "secretID": "",
            "secretKey": ""
        },
        "area": {
            "x": 454.1935483870968,
            "y": 528.3870967741935,
            "width": 650.9838709677417,
            "height": 325.86021505376345
        },
        "hotKey": {
            "use": False,
            "start_pause": {
                "key": [
                    2,
                    69
                ],
                "flag": True
            },
            "auto_switch": {
                "key": [
                    0,
                    0
                ],
                "flag": ""
            },
            "reTrans": {
                "key": [
                    2,
                    82
                ],
                "flag": ""
            },
            "sourceHide": {
                "key": [
                    2,
                    70
                ],
                "flag": ""
            },
            "source": {
                "key": [
                    1,
                    96
                ],
                "flag": ""
            },
            "result": {
                "key": [
                    1,
                    83
                ],
                "flag": ""
            },
            "areaHide": {
                "key": [
                    2,
                    89
                ],
                "flag": ""
            },
            "minsize": {
                "key": [
                    1,
                    40
                ],
                "flag": True
            },
            "power": {
                "key": [
                    0,
                    35
                ],
                "flag": True
            }
        },
        "font": {
            "setting": [
                "迷你简卡通",
                12,
                "#000000",
                "bold"
            ],
            "source": [
                "华文中宋",
                10,
                "#ff0000",
                "normal"
            ],
            "result": [
                "华文新魏",
                12,
                "#ffffff",
                "normal"
            ]
        },
        "language": "英语",
        "API_CO": None,
        "Auto": False,
        "start_pause": False,
        "public_trans": "ali",
        "input": "cbd",
        "OCR": "yd",
        "sourceHide": False
    }

    with open(setting_path, "w", encoding="utf-8") as file:
        json.dump(default_settings, file, indent=4, ensure_ascii=False)


def global_init():
    global screenWidth, screenHeight, rectW, rectH, rectX, rectY, hotKey, language, CUDA, hotkey_use, sourceHide, \
        start_pause, auto, api_co, public_trans, inputSource, OCR, quick_lan,ocr_setting
    try:
        screenWidth = set_config["User"]["screenwidth"]
        screenHeight = set_config["User"]["screenheight"]
        rectW = set_config["area"]["width"]
        rectH = set_config["area"]["height"]
        rectX = set_config["area"]["x"]
        rectY = set_config["area"]["y"]
        hotKey = set_config["hotKey"]
        language = set_config["language"]
        CUDA = set_config["User"]["CUDA"]
        hotkey_use = hotKey["use"]
        api_co = set_config["API_CO"]
        auto = set_config["Auto"]
        start_pause = set_config["start_pause"]
        public_trans = set_config["public_trans"]
        inputSource = set_config["input"]
        OCR = set_config["OCR"]
        sourceHide = set_config["sourceHide"]
        quick_lan = set_config["selected_languages"]
        ocr_setting = set_config["ocr_setting"]
    except Exception as error:
        messagebox.showerror("未知错误", "Σ( ° △ °|||)是我没有预料到的错误\n请将运行日志发送给作者！")
        logging.error(f"打开时出现未知错误: {error}")