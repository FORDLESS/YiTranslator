from PIL import Image, ImageTk
import tkinter as tk
import logging
import Global
from Global import BASE_DIR, ocr_language_map, set_config

logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MyButton(tk.Button):
    def __init__(self, master=None, hover_bg=None, normal_image=None, pressed_image=None, **kw):
        super().__init__(master, **kw)
        self.normal_bg = self["bg"]
        self.hover_bg = hover_bg
        self.normal_image = normal_image
        self.pressed_image = pressed_image
        self.current_image = normal_image  # 当前显示的图片
        if self.normal_image is not None:
            self["image"] = self.normal_image
        if self.pressed_image is not None:
            self.bind("<Button-1>", self.on_click)
        if self.hover_bg is not None:
            self.bind("<Enter>", self.on_enter)
            self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self["bg"] = self.hover_bg

    def on_leave(self, event):
        self["bg"] = self.normal_bg

    def on_click(self, event):
        if self.current_image == self.normal_image:
            self.current_image = self.pressed_image
        else:
            self.current_image = self.normal_image
        self["image"] = self.current_image


class SwitchButton(MyButton):  # 特殊的能持续保持按下状态的按钮类
    button_groups = {}  # 用于存储按钮编组的字典

    def __init__(self, master=None, switch=False, marshalling=None, hover_bg=None, off_image=None, on_image=None, **kw):
        super().__init__(master, hover_bg=hover_bg, **kw)
        self.switch = switch  # 按钮状态
        self.marshalling = marshalling  # 编组用于控制同类按钮之间的协调
        self.off_image = off_image
        self.on_image = on_image
        if self.switch:
            self["image"] = self.on_image
        else:
            self["image"] = self.off_image
        self.bind("<Button-1>", self.on_click)
        self.add_to_group()

    def on_click(self, event):
        if not self.marshalling:
            if self.switch:
                self.switch = False
                self["image"] = self.off_image
            else:
                self.switch = True
                self["image"] = self.on_image
        else:  # 编组按钮再次按下不切换，仍维持状态
            if self.switch:
                pass
            else:
                self.switch = True
                self["image"] = self.on_image
        self.update_group_buttons()

    def add_to_group(self):
        if self.marshalling is not None:
            if self.marshalling not in SwitchButton.button_groups:
                SwitchButton.button_groups[self.marshalling] = []
            SwitchButton.button_groups[self.marshalling].append(self)

    def update_group_buttons(self):  # 实现同组按钮不能同时选中
        if self.marshalling is not None and self.marshalling in SwitchButton.button_groups:
            group_buttons = SwitchButton.button_groups[self.marshalling]
            for button in group_buttons:
                if button != self:
                    button.switch = not self.switch
                    button["image"] = button.off_image


class BreathingLabel(tk.Label):
    def __init__(self, master=None, image_name='breathing.png', duration=1000, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.image_path = BASE_DIR + "\\res\\" + image_name
        self.duration = duration
        self.current_alpha = 0
        self.fade_out()

    def fade_out(self):
        self.current_alpha = max(self.current_alpha - 10, 0)
        self.update_image()
        if self.current_alpha > 0:
            self.after(self.duration, self.fade_out)
        else:
            self.fade_in()

    def fade_in(self):
        self.current_alpha = min(self.current_alpha + 10, 255)
        self.update_image()
        if self.current_alpha < 255:
            self.after(self.duration, self.fade_in)
        else:
            self.fade_out()

    def update_image(self):
        image = Image.open(self.image_path).convert('RGBA')
        image = image.resize((self.winfo_width(), self.winfo_height()))
        image_with_alpha = image.copy()
        alpha = int(self.current_alpha * 0.9)  # 调整透明度范围
        alpha_image = image_with_alpha.split()[3]
        alpha_image = alpha_image.point(lambda p: p * alpha / 255)
        image_with_alpha.putalpha(alpha_image)
        photo = ImageTk.PhotoImage(image_with_alpha)
        self.config(image=photo)
        self.image = photo  # 防止图像被垃圾回收机制自动清理


class Tooltip:
    def __init__(self, widget, text, font_color="black", bg_color="#666666"):
        self.widget = widget
        self.text = text
        self.font_color = font_color
        self.bg_color = bg_color
        self.tipWindow = None
        self.id = None
        self.x = self.y = 0
        self.alpha = 0.0

        self.widget.bind("<Enter>", self.showtip)
        self.widget.bind("<Leave>", self.hidetip)

    def showtip(self, event):
        if self.tipWindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() - 15
        self.tipWindow = tk.Toplevel(self.widget)
        self.tipWindow.wm_overrideredirect(True)
        self.tipWindow.wm_geometry("+%d+%d" % (x, y))
        self.tipWindow.attributes("-alpha", self.alpha, "-topmost", True, '-transparentcolor', "#666666")
        tk.Label(self.tipWindow, text=self.text, bg=self.bg_color, fg=self.font_color, relief=tk.FLAT, bd=1,
                 font=("微软雅黑", "11", "bold")).pack(padx=1, pady=1, ipadx=5, ipady=5)

        self._fade_in()

    def hidetip(self, event):
        self.widget.after_cancel(self.id)
        self.alpha = 0
        if self.tipWindow:
            self.tipWindow.destroy()
        self.tipWindow = None

    def _fade_in(self):
        if self.alpha < 1.0:
            self.alpha += 0.1  # 增加透明度的值
            self.tipWindow.attributes("-alpha", self.alpha)
            self.id = self.widget.after(100, self._fade_in)

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
        if name not in self.image:
            self.image[name] = photo
        return image  # 顺便返回Image对象可能有用

    def get_image(self, name):
        return self.image[name]


# 依据窗体改变图像的大小
def resizeImage(container, image, width=None, height=None):  # 父容器，Image对象
    if width is None:
        width = container.winfo_width()
        height = container.winfo_height()
    image = image.resize((width, height), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)
    return photo


def transparency(image, alpha=50):  # 设置图片透明度,传入Image对象
    image = image.convert("RGBA")
    image = image.putalpha(alpha)
    photo = ImageTk.PhotoImage(image)
    return photo


def replace_canvas_image(canvas, new_image, latest_image_id):
    # 删除旧的图像项
    canvas.delete(latest_image_id)
    # 创建新的图像项
    latest_image_id = canvas.create_image(0, 0, anchor="nw", image=new_image)
    return latest_image_id


def validateInt(value):
    if value.isdigit() or value == '':
        return True
    return False


def update_global():
    Global.screenWidth = set_config["User"]["screenwidth"]
    Global.screenHeight = set_config["User"]["screenheight"]
    Global.rectW = set_config["area"]["width"]
    Global.rectH = set_config["area"]["height"]
    Global.rectX = set_config["area"]["x"]
    Global.rectY = set_config["area"]["y"]
    Global.hotKey = set_config["hotKey"]
    Global.language = [ocr_language_map[set_config["language"]]]
    Global.CUDA = set_config["User"]["CUDA"]
    Global.batchSize = set_config["batch_size"]
    Global.hotkey_use = set_config["hotkey_use"]
    Global.api_co = set_config["API_CO"]
    Global.auto = set_config["Auto"]
    Global.start_pause = set_config["start_pause"]
    Global.in_function_page = set_config["h_page"]["in_personal_page"]
    Global.in_public_page = set_config["h_page"]["in_public_page"]


def secret_load():
    if Global.api_co == "Tencent":
        uuid = set_config["tencentAPI"]["secretID"]
        key = set_config["tencentAPI"]["secretKey"]
    elif Global.api_co == "Baidu":
        uuid = set_config["baiduAPI"]["secretID"]
        key = set_config["baiduAPI"]["secretKey"]
    else:
        uuid = "请填写你的id"
        key = "请填写你的密钥"
    return uuid, key


if __name__ == "__main__":
    update_global()
