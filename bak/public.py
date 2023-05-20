import json
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
import tkinter as tk
import logging
import Global
from Global import BASE_DIR, ocr_language_map

logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipWindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self):
        if self.tipWindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tipWindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffff", relief=tk.FLAT, borderwidth=1,
                         font=("微软雅黑", "10", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipWindow
        self.tipWindow = None
        if tw:
            tw.destroy()

    ''' setTip = function.Tooltip(self.keyButton, "请在英文输入法下设置")
        self.keyButton.bind("<Enter>", lambda event: setTip.showtip())
        self.keyButton.bind("<Leave>", lambda event: setTip.hidetip())
    '''


# 图片资源管理类
class ImageLoader:
    def __init__(self):
        self.image = {}

    def load_image(self, name, path):
        image = Image.open(BASE_DIR + "\\res\\" + path)
        photo = ImageTk.PhotoImage(image)
        self.image[name] = photo

    def get_image(self, name):
        return self.image[name]


def validateInt(value):
    if value.isdigit() or value == '':
        return True
    return False


def read_settings(file_path):
    with open(file_path, "r") as file:
        settings = json.load(file)
    return settings


def save_settings(file_path, new_settings):
    with open(file_path, "w") as file:
        json.dump(new_settings, file, indent=4)


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

    with open("settings.json", "w") as file:
        json.dump(default_settings, file, indent=4)


def update_global():
    try:
        data = read_settings(Global.data_path)
        Global.screenWidth = data["User"]["screenwidth"]
        Global.screenHeight = data["User"]["screenheight"]
        Global.rectW = data["area"]["width"]
        Global.rectH = data["area"]["height"]
        Global.rectX = data["area"]["x"]
        Global.rectY = data["area"]["y"]
        Global.hotKey = data["hotKey"]
        Global.language = [ocr_language_map[data["language"]]]
        Global.haveCUDA = data["User"]["CUDA"]
        Global.batchSize = data["batch_size"]
        Global.hotkey_use = data["hotkey_use"]
        Global.api_co = data["API_CO"]
    except FileNotFoundError:
        messagebox.showerror("文件丢失", "(/ﾟДﾟ)/！怎么把配置文件丢了？给你初始化一个！\n请重新打开软件！")
        create_default_json()
    except json.JSONDecodeError:
        messagebox.showerror("解码错误", "！！！ Σ(っ °Д °;)っ你小子往配置文件里下毒了？\n无法解决请联系作者！")
    except Exception as error:
        messagebox.showerror("未知错误", "Σ( ° △ °|||)是我没有预料到的错误\n请将运行日志发送给作者！")
        logging.error(f"打开时出现未知错误: {error}")


def secret_load():
    data = read_settings(Global.data_path)
    if Global.api_co == "Tencent":
        uuid = data["tencentAPI"]["secretID"]
        key = data["tencentAPI"]["secretKey"]
    elif Global.api_co == "Baidu":
        uuid = data["baiduAPI"]["secretID"]
        key = data["baiduAPI"]["secretKey"]
    else:
        uuid = "请填写你的id"
        key = "请填写你的密钥"
    return uuid, key


if __name__ == "__main__":
    update_global()
