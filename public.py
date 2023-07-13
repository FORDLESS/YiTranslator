from PIL import Image, ImageTk
import tkinter as tk
import logging
import Global
from Global import BASE_DIR, set_config

logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MyButton(tk.Button):
    def __init__(self, master=None, hover_bg=None, normal_image=None, pressed_image=None, tooltip=None, bd=0, **kw):
        super().__init__(master, bd=bd, **kw)
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
        if tooltip is not None:  # 按钮是否有悬浮提示
            self.text, self.font_color, self.bg_color = tooltip[0], tooltip[1], tooltip[2]
            self.tipWindow = None
            self.id = None
            self.x = self.y = 0
            self.alpha = 0.0
            self.bind("<Enter>", lambda event: (self.on_enter(event), self._showtip(event)))
            self.bind("<Leave>", lambda event: (self.on_leave(event), self.hidetip(event)))

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

    def _fade_in(self):
        if self.alpha < 1.0:
            self.alpha += 0.15  # 增加透明度的值
            self.tipWindow.attributes("-alpha", self.alpha)
            self.id = self.after(100, self._fade_in)

    def _showtip(self, event):  # 加了延迟显示不会卡住（只是极大减小卡住的概率，原因不明，可能和监听触发机制有关）
        self.after(110, self.showtip())

    def showtip(self):
        if self.tipWindow:
            return
        x, y, cx, cy = self.bbox("insert")
        x += self.winfo_rootx() + 25
        y += self.winfo_rooty() + 25
        self.tipWindow = tk.Toplevel(self)
        self.tipWindow.wm_overrideredirect(True)
        self.tipWindow.wm_geometry("+%d+%d" % (x, y))
        self.tipWindow.attributes("-alpha", self.alpha, "-topmost", True, '-transparentcolor', "#666666")
        tk.Label(self.tipWindow, text=self.text, bg=self.bg_color, fg=self.font_color, relief=tk.FLAT, bd=1,
                 font=("宋体", "10")).pack(padx=1, pady=1)
        self._fade_in()

    def hidetip(self, event):
        self.after_cancel(self.id)
        self.alpha = 0
        if self.tipWindow:
            self.tipWindow.destroy()
        self.tipWindow = None


class PageButton(MyButton):  # 特殊的能持续保持按下状态的按钮类
    button_groups = {}  # 用于存储按钮编组的字典

    def __init__(self, master=None, switch=False, marshalling=None, hover_bg=None, off_image=None, on_image=None,
                 tooltip=None, relief="sunken", highlightthickness=0, **kw):
        super().__init__(master, hover_bg=hover_bg, tooltip=tooltip, relief=relief,
                         highlightthickness=highlightthickness, **kw)
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
            if self.marshalling not in PageButton.button_groups:
                PageButton.button_groups[self.marshalling] = []
            PageButton.button_groups[self.marshalling].append(self)

    def update_group_buttons(self):  # 实现同组按钮不能同时选中
        if self.marshalling is not None and self.marshalling in PageButton.button_groups:
            group_buttons = PageButton.button_groups[self.marshalling]
            for button in group_buttons:
                if button != self:
                    button.switch = not self.switch
                    button["image"] = button.off_image


class SwitchButton(PageButton):
    button_groups = {}

    def on_click(self, event):
        if self.switch:
            self.switch = False
            self["image"] = self.off_image
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
        self.image_path = BASE_DIR + "\\files\\res\\" + image_name
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


# 图片资源管理类
class ImageLoader:
    def __init__(self):
        self.image = {}

    def load_image(self, name, path):
        image = Image.open(BASE_DIR + "\\files\\res\\" + path)
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
    if not isinstance(image,Image.Image):
        image = Image.open(image)
    image = image.resize((width, height), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)
    return image,photo


def transparency(image, alpha=50):  # 设置图片透明度,传入Image对象
    image = image.convert("RGBA")
    image.putalpha(alpha)
    photo = ImageTk.PhotoImage(image)
    return image,photo


def update_global():
    Global.screenWidth = set_config["User"]["screenwidth"]
    Global.screenHeight = set_config["User"]["screenheight"]
    Global.rectW = set_config["area"]["width"]
    Global.rectH = set_config["area"]["height"]
    Global.rectX = set_config["area"]["x"]
    Global.rectY = set_config["area"]["y"]
    Global.hotKey = set_config["hotKey"]
    Global.language = set_config["language"]
    Global.hotkey_use = Global.hotKey["use"]
    Global.api_co = set_config["API_CO"]
    Global.auto = set_config["Auto"]
    Global.start_pause = set_config["start_pause"]
    Global.public_trans = set_config["public_trans"]
    Global.inputSource = set_config["input"]
    Global.OCR = set_config["OCR"]
    Global.sourceHide = set_config["sourceHide"]
    Global.ocr_setting = set_config["ocr_setting"]

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


def get_hotkey_name(hotkey):  # 只用于显示
    modifiers, vk = hotkey
    if not modifiers:  # 如果修饰键为0
        modifiers_str = ""
        if not vk:  # 并且基础键为0
            vk_str = ""
        elif vk not in Global.modifier_key:
            if vk in Global.VK_CODE:
                vk_str = Global.VK_CODE[vk]
            else:
                vk_str = "无效热键"  # 基础键为装饰键的情况
        else:
            vk_str = "热键重复"
    else:
        modifiers_str = Global.VK_CODE[modifiers] + "+"
        vk_str = Global.VK_CODE[vk]
    return modifiers_str + vk_str


def regulate_hotkey(hotkey):  # 用于同步记录和注册按键的键码
    if len(hotkey) > 1:
        hotkey = sorted(hotkey)
        if hotkey[0] in Global.modifier_key:
            hotkey[0] = Global.modifier_key_T[hotkey[0]]
            return hotkey
    else:
        hotkey = [0, hotkey[0]]
        return hotkey


if __name__ == "__main__":
    update_global()
