import logging
import subprocess
import tkinter as tk
import webbrowser
from tkinter import messagebox, colorchooser, filedialog
from tkinter import ttk
import tkinter.font as tkfont

import Global
from utils import public
from Global import save_settings, set_config
from getText.OCRengine import OCR
from utils.public import ImageLoader, MyButton, PageButton, SwitchButton, MyLabel
from getText.clipboard import Clipboard


# noinspection PyAttributeOutsideInit
class SetGUI(tk.Toplevel):
    def __init__(self, mainGUI):
        super().__init__()

        self.main_gui = mainGUI

        self.title("设置")
        self.bg = set_config["background"]
        self.resizable(False, False)
        self.wm_attributes('-alpha', self.bg["spr"], '-transparentcolor', "#666666")
        self.config(bg="#cccccc")
        self.screenWidth = self.winfo_screenwidth()
        self.screenHeight = self.winfo_screenheight()
        self.geometry("768x432+%d+%d" % (self.screenWidth / 3, self.screenHeight / 3))
        self.overrideredirect(False)

        self.fontName = set_config["font"]["setting"][0]
        self.fontName = self.fontName if self.check_font_exists() else "等线"
        self.fontSize = set_config["font"]["setting"][1]
        self.fontWeight = set_config["font"]["setting"][3]
        self.fontColor = set_config["font"]["setting"][2]

        self.imageLoader = ImageLoader()
        self.imageLoader.load_image("icon", "icon.png")
        self.iconphoto(False, self.imageLoader.get_image("icon"))

        self.tp = {"bg": 70, "bg2": 70}
        self.inter_val = tk.DoubleVar()
        self.sim_val = tk.DoubleVar()

        self.current_page = None
        self.current_specific_page = None
        self.bak_text = None
        self.hotkey_setting_mode = False
        self.patch_canvas_text_dict = {}
        self.desired_hotkey = []
        self.current_button = None

        self.image_load()
        self.frame_init()
        self.interface_init()
        self.horizontal_set()
        self.controls_set()
        self.textView()
        self.bind_event()

        style = ttk.Style()
        style.configure("Custom.TCombobox", font=self.font12, padding=(10, 5, 10, 5))
        style.configure('Custom.TSpinbox', padding=(5, 2, 5, 0))

    def frame_init(self):
        self.vertical_frame = tk.Frame(self, height=432, width=120, bg="#666666")
        self.vertical_frame.pack(side="left", fill="both")
        self.horizontal_frame = tk.Frame(self, height=40, width=648, bg="#f0f0f0")
        self.horizontal_frame.pack(side="top", fill="both")
        self.bg_label = tk.Label(self, image=self.imageLoader.get_image("bg"), compound="center", bd=0)
        self.bg_label.pack(side="top", fill="both")

    # **********************主体按钮布局********************* #
    def interface_init(self):
        self.line_page_button = PageButton(self.vertical_frame, bg="white", switch=False,
                                           marshalling="vertical", command=self.line_page_show,
                                           off_image=self.imageLoader.get_image("line_normal"),
                                           on_image=self.imageLoader.get_image("line_press"))
        self.line_page_button.pack(side="top", fill="both")
        self.mode_page_button = PageButton(self.vertical_frame, bg="white", switch=False,
                                           marshalling="vertical", command=self.mode_page_show,
                                           off_image=self.imageLoader.get_image("mode_normal"),
                                           on_image=self.imageLoader.get_image("mode_press"))
        self.mode_page_button.pack(side="top", fill="both")
        self.function_page_button = PageButton(self.vertical_frame, bg="white", switch=False,
                                               command=self.function_page_show, marshalling="vertical",
                                               off_image=self.imageLoader.get_image("function_normal"),
                                               on_image=self.imageLoader.get_image("function_press"))
        self.function_page_button.pack(side="top", fill="both")
        self.personalise_page_button = PageButton(self.vertical_frame, bg="white", switch=False,
                                                  command=self.personalise_page_show,
                                                  off_image=self.imageLoader.get_image("personalise_normal"),
                                                  on_image=self.imageLoader.get_image("personalise_press"),
                                                  marshalling="vertical")
        self.personalise_page_button.pack(side="top", fill="both")
        self.about_page_button = PageButton(self.vertical_frame, bg="white", switch=False,
                                            command=self.about_page_show, marshalling="vertical",
                                            off_image=self.imageLoader.get_image("about_normal"),
                                            on_image=self.imageLoader.get_image("about_press"))
        self.about_page_button.pack(side="top", fill="both")
        self.block_page_button = PageButton(self.vertical_frame, bg="white",
                                            off_image=self.imageLoader.get_image("block"))
        self.block_page_button.pack(side="top", fill="both", expand=True)  # 竖排空白填充
        # self.block_canvas = tk.Canvas(self.horizontal_frame, height=40, width=648)  # 顶部剩余空间填充横幅
        # self.block_canvas.pack(side="top", fill="both")

    def textView(self):
        pass

    def bind_event(self):
        self.patch_canvas.bind("<Motion>", lambda event: (self.enter_text(event), self.leave_text(event)))
        self.patch_canvas.bind("<Button-1>", lambda event: self.clickTextInCanvas(event, self.current_specific_page))

    def hotkey_bind(self):  # 只在热键设置模式下绑定，避免不必要的错误
        if self.hotkey_setting_mode:
            self.bind('<KeyRelease>', self.hotkey_detect)
            self.bind('<KeyPress>', self.key_press)
        else:
            self.unbind('<KeyRelease>')
            self.unbind('<KeyPress>')

    # **********************主体按钮函数********************* #
    def line_page_show(self):
        if self.current_page != "line":
            self.current_page = "line"
            self.personal_page_button.place(x=-1, y=0)
            self.public_page_button.place(x=100, y=0)
            hide_all_buttons_except(self.current_page, self.pages)
            self.patch_canvas.place(x=200, y=0, relwidth=1, relheight=1)  # 删除后创建canvas，始终保持只有一个canvas
            if self.personal_page_button.switch:
                self.personal_page_show()
            else:
                self.public_page_show()

    def mode_page_show(self):
        if self.current_page != "mode":
            self.current_page = "mode"
            self.input_page_button.place(x=-1, y=0)
            self.OCR_page_button.place(x=100, y=0)

            hide_all_buttons_except(self.current_page, self.pages)
            self.patch_canvas.place(x=200, y=0, relwidth=1, relheight=1)

            if self.input_page_button.switch:
                self.input_page_show()
            else:
                self.OCR_page_show()

    def function_page_show(self):
        if self.current_page != "function":
            self.current_page = "function"
            self.language_page_button.place(x=-1, y=0)
            self.hotkey_page_button.place(x=100, y=0)
            hide_all_buttons_except(self.current_page, self.pages)
            self.patch_canvas.place(x=200, y=0, relwidth=1, relheight=1)

            if self.language_page_button.switch:
                self.language_page_show()
            else:
                self.hotkey_page_show()

    def personalise_page_show(self):
        if self.current_page != "personalise":
            self.current_page = "personalise"
            self.font_page_button.place(x=-1, y=0)
            self.theme_page_button.place(x=100, y=0)
            self.other_page_button.place(x=200, y=0)
            hide_all_buttons_except(self.current_page, self.pages)
            self.patch_canvas.place(x=300, y=0, relwidth=1, relheight=1)

            if self.font_page_button.switch:
                self.font_page_show()
            elif self.theme_page_button.switch:
                self.theme_page_show()
            else:
                self.other_page_show()

    def about_page_show(self):
        if self.current_page != "about":
            self.current_page = "about"
            hide_all_buttons_except(self.current_page, self.pages)
            self.patch_canvas.place(x=300, y=0, relwidth=1, relheight=1)

            self.update_page("abaochi")

    # **********************水平按钮函数********************* #
    def personal_page_show(self):
        self.update_page("personal", "注册教程点击此处", True)

    def public_page_show(self):
        self.update_page("public")

    def input_page_show(self):
        self.update_page("input")

    def OCR_page_show(self):
        self.update_page("OCR", "更多语言识别模型下载点击此处", True)

    def language_page_show(self):
        self.update_page("language")

    def hotkey_page_show(self):
        self.update_page("hotkey", "请在英文输入法下设置,按ESC可置空", x=130, y=22)

    def font_page_show(self):
        self.update_page("font")

    def theme_page_show(self):
        self.update_page("theme")

    def other_page_show(self):
        self.update_page("other")

    # **********************对于patch_canvas上文本的操作********************* #
    def is_within_text(self, event):  # 判断鼠标点击是否在文本区域内
        if self.current_specific_page in self.patch_canvas_text_dict:
            bbox = self.patch_canvas.bbox(self.patch_canvas_text_dict[self.current_specific_page][0])
            if bbox[0] <= event.x <= bbox[2] and bbox[1] <= event.y <= bbox[3]:
                return True
        return False

    def clickTextInCanvas(self, event, page):  # 处理 Canvas 的点击事件
        if self.is_within_text(event):
            if page == "personal":
                readme()
            elif page == "OCR":
                download_model()

    def enter_text(self, event):  # 处理进入文本区域的事件
        if self.is_within_text(event):
            self.patch_canvas.itemconfigure(self.patch_canvas_text_dict[self.current_specific_page][0], fill="red")

    def leave_text(self, event):  # 处理离开文本区域的事件
        if self.current_specific_page in self.patch_canvas_text_dict:
            if not self.is_within_text(event):
                self.patch_canvas.itemconfigure(self.patch_canvas_text_dict[self.current_specific_page][0],
                                                fill="black")

    # ***********************具体选项中页面及canvas的更新*******************#
    def update_page(self, page, text=None, withline=False, x=100, y=18):
        if self.current_specific_page != page:
            # 先清除之前patch_canvas上的元素
            if self.current_specific_page in self.patch_canvas_text_dict:
                for item in self.patch_canvas_text_dict[self.current_specific_page]:
                    self.patch_canvas.delete(item)

            self.current_specific_page = page  # 然后标识为当前页
            # 如果存在文本则在patch_canvas上绘制文字
            patch_canvas_text = None
            if text:
                patch_canvas_text = self.patch_canvas.create_text(x, y, text=text, font=("微软雅黑", 10, "bold"),
                                                                  fill="black", anchor="center")
                self.patch_canvas_text_dict[self.current_specific_page] = [patch_canvas_text]
            if withline:
                x1, y1, x2, y2 = self.patch_canvas.bbox(patch_canvas_text)  # 获取文本边界框
                patch_canvas_line = self.patch_canvas.create_line(x1, y2, x2, y2, fill="black")
                self.patch_canvas_text_dict[self.current_specific_page].append(patch_canvas_line)

            self.specific_pages[page][0].place(x=0, y=0)  # 放置整个页面label
            hide_all_buttons_except(self.current_specific_page, self.specific_pages)  # forget其他页面label

    # **********************加载所有资源********************* #
    def image_load(self):
        self.font12 = tkfont.Font(family=self.fontName, size=self.fontSize, weight=self.fontWeight)
        self.font10 = tkfont.Font(family=self.fontName, size=10)
        self.imageLoader.load_image("bg", self.bg["bg"])
        self.imageLoader.load_image("bg2", self.bg["bg2"])
        self.imageLoader.load_image("line_normal", "line_select_1.png")
        self.imageLoader.load_image("line_press", "line_select_2.png")
        self.imageLoader.load_image("mode_normal", "translate_mode_1.png")
        self.imageLoader.load_image("mode_press", "translate_mode_2.png")
        self.imageLoader.load_image("function_normal", "function_1.png")
        self.imageLoader.load_image("function_press", "function_2.png")
        self.imageLoader.load_image("personalise_normal", "personalise_1.png")
        self.imageLoader.load_image("personalise_press", "personalise_2.png")
        self.imageLoader.load_image("about_normal", "about_1.png")
        self.imageLoader.load_image("about_press", "about_2.png")
        self.imageLoader.load_image("block", "block.png")
        self.imageLoader.load_image("block_2", "block_2.png")
        self.imageLoader.load_image("personal_normal", "personal_1.png")
        self.imageLoader.load_image("personal_press", "personal_2.png")
        self.imageLoader.load_image("public_normal", "public_1.png")
        self.imageLoader.load_image("public_press", "public_2.png")
        self.imageLoader.load_image("OCR_normal", "OCR_1.png")
        self.imageLoader.load_image("OCR_press", "OCR_2.png")
        self.imageLoader.load_image("input_normal", "input_1.png")
        self.imageLoader.load_image("input_press", "input_2.png")
        self.imageLoader.load_image("hotkey_normal", "hotkey_1.png")
        self.imageLoader.load_image("hotkey_press", "hotkey_2.png")
        self.imageLoader.load_image("language_normal", "language_1.png")
        self.imageLoader.load_image("language_press", "language_2.png")
        self.imageLoader.load_image("font_normal", "font_1.png")
        self.imageLoader.load_image("font_press", "font_2.png")
        self.imageLoader.load_image("theme_normal", "theme_1.png")
        self.imageLoader.load_image("theme_press", "theme_2.png")
        self.imageLoader.load_image("other_normal", "other_1.png")
        self.imageLoader.load_image("other_press", "other_2.png")
        self.imageLoader.load_image("api_on", "api_on.png")
        self.imageLoader.load_image("api_off", "api_off.png")
        self.imageLoader.load_image("access", "access.png")
        self.imageLoader.load_image("delay", "delay.png")
        self.imageLoader.load_image("show", "show.png")
        self.imageLoader.load_image("hide", "hide.png")
        self.imageLoader.load_image("unselect", "unselect.png")
        self.imageLoader.load_image("select", "select.png")
        self.imageLoader.load_image("close", "close.png")
        self.imageLoader.load_image("tick", "tick.png")

    def check_font_exists(self):
        available_fonts = tk.font.families()
        if self.fontName in available_fonts:
            return True
        return False

    # **********************所有水平页内的按钮********************* #
    def horizontal_set(self):
        # line_page_show
        self.personal_page_button = PageButton(self.horizontal_frame, switch=True, command=self.personal_page_show,
                                               marshalling="horizontal_line", activebackground="white", bg="white",
                                               off_image=self.imageLoader.get_image("personal_normal"),
                                               on_image=self.imageLoader.get_image("personal_press"))
        self.public_page_button = PageButton(self.horizontal_frame, switch=False, command=self.public_page_show,
                                             marshalling="horizontal_line", activebackground="white", bg="white",
                                             off_image=self.imageLoader.get_image("public_normal"),
                                             on_image=self.imageLoader.get_image("public_press"))
        self.patch_canvas = tk.Canvas(self.horizontal_frame)
        # mode_page_show
        self.input_page_button = PageButton(self.horizontal_frame, switch=True, command=self.input_page_show,
                                            marshalling="horizontal_mode", activebackground="white", bg="white",
                                            off_image=self.imageLoader.get_image("input_normal"),
                                            on_image=self.imageLoader.get_image("input_press"))
        self.OCR_page_button = PageButton(self.horizontal_frame, bg="white", switch=False, command=self.OCR_page_show,
                                          marshalling="horizontal_mode", activebackground="white",
                                          off_image=self.imageLoader.get_image("OCR_normal"),
                                          on_image=self.imageLoader.get_image("OCR_press"))
        # function_page_show
        self.language_page_button = PageButton(self.horizontal_frame, bg="white", activebackground="white", switch=True,
                                               marshalling="horizontal_function", command=self.language_page_show,
                                               off_image=self.imageLoader.get_image("language_normal"),
                                               on_image=self.imageLoader.get_image("language_press"))
        self.hotkey_page_button = PageButton(self.horizontal_frame, bg="white", activebackground="white", switch=False,
                                             marshalling="horizontal_function", command=self.hotkey_page_show,
                                             off_image=self.imageLoader.get_image("hotkey_normal"),
                                             on_image=self.imageLoader.get_image("hotkey_press"))
        # personalise_page_show
        self.font_page_button = PageButton(self.horizontal_frame, bg="white", activebackground="white", switch=True,
                                           marshalling="horizontal_personalise", command=self.font_page_show,
                                           off_image=self.imageLoader.get_image("font_normal"),
                                           on_image=self.imageLoader.get_image("font_press"))
        self.theme_page_button = PageButton(self.horizontal_frame, bg="white", activebackground="white", switch=False,
                                            marshalling="horizontal_personalise", command=self.theme_page_show,
                                            off_image=self.imageLoader.get_image("theme_normal"),
                                            on_image=self.imageLoader.get_image("theme_press"))
        self.other_page_button = PageButton(self.horizontal_frame, off_image=self.imageLoader.get_image("other_normal"),
                                            bg="white", activebackground="white", command=self.other_page_show,
                                            on_image=self.imageLoader.get_image("other_press"),
                                            marshalling="horizontal_personalise")
        # about_page_show
        self.pages = {
            "patch": [self.patch_canvas],
            "line": [self.personal_page_button, self.public_page_button],
            "mode": [self.input_page_button, self.OCR_page_button],
            "function": [self.language_page_button, self.hotkey_page_button],
            "personalise": [self.font_page_button, self.theme_page_button, self.other_page_button],
            "about": []
        }

    # **************************所有具体的按钮和背景容器*************************#
    def controls_set(self):
        # personal_page_show
        self.personal_page_label = tk.Label(self.bg_label, image=self.imageLoader.get_image("bg2"), compound="center",
                                            bd=0)
        personal_label_1 = tk.Label(self.personal_page_label, text="推荐使用，效果比公共接口更加稳定，免费",
                                    font=self.font12, fg="#33ccff")
        personal_label_2 = tk.Label(self.personal_page_label, text="实验性", font=self.font12, fg="#33ccff")
        personal_label_3 = tk.Label(self.personal_page_label, text="直接在腾讯云服务器处理OCR识别与翻译，\n缓解本地运行压力，但需要较好的网络支持",
                                    font=self.font10, fg="#33ccff")
        personal_label_bd = tk.Label(self.personal_page_label, text="百度：", fg=self.fontColor, font=self.font12)
        personal_label_tx = tk.Label(self.personal_page_label, text="腾讯：", fg=self.fontColor, font=self.font12)
        personal_label_txImg = tk.Label(self.personal_page_label, text="腾讯图片翻译：", fg=self.fontColor, font=self.font12)
        self.personal_baidu_button = SwitchButton(self.personal_page_label, switch=Global.api_co == "Baidu",
                                                  off_image=self.imageLoader.get_image("api_off"),
                                                  on_image=self.imageLoader.get_image("api_on"),
                                                  command=self.baiduSwitch, marshalling="api")
        self.personal_tencent_button = SwitchButton(self.personal_page_label, switch=Global.api_co == "Tencent",
                                                    off_image=self.imageLoader.get_image("api_off"),
                                                    on_image=self.imageLoader.get_image("api_on"),
                                                    command=self.tencentSwitch, marshalling="api")
        self.personal_tencentImg_button = SwitchButton(self.personal_page_label, switch=Global.api_co == "TencentImg",
                                                       marshalling="api", command=self.tencentImg_switch,
                                                       off_image=self.imageLoader.get_image("api_off"),
                                                       on_image=self.imageLoader.get_image("api_on"))
        bd_access_button = MyButton(self.personal_page_label, command=lambda: self.accessTk("bd"),
                                    normal_image=self.imageLoader.get_image("access"), borderwidth=0)
        tx_access_button = MyButton(self.personal_page_label, command=lambda: self.accessTk("tx"),
                                    normal_image=self.imageLoader.get_image("access"), borderwidth=0)
        bd_delay_button = MyButton(self.personal_page_label, command=self.delay_test,
                                   normal_image=self.imageLoader.get_image("delay"), borderwidth=0)
        tx_delay_button = MyButton(self.personal_page_label, command=self.delay_test,
                                   normal_image=self.imageLoader.get_image("delay"), borderwidth=0)
        txImg_delay_button = MyButton(self.personal_page_label, command=self.delay_test,
                                      normal_image=self.imageLoader.get_image("delay"), borderwidth=0)
        line_canvas = tk.Canvas(self.personal_page_label, width=350, height=10)
        line_canvas.create_line(0, 5, 350, 5, fill='#33ccff', width=2)

        personal_label_1.place(x=20, y=25)
        personal_label_2.place(x=20, y=200)
        personal_label_3.place(x=22, y=280)
        personal_label_bd.place(x=50, y=70)
        self.personal_baidu_button.place(x=100, y=64)
        personal_label_tx.place(x=50, y=120)
        self.personal_tencent_button.place(x=100, y=114)
        personal_label_txImg.place(x=50, y=250)
        self.personal_tencentImg_button.place(x=180, y=244)
        bd_access_button.place(x=200, y=67)
        tx_access_button.place(x=200, y=117)
        bd_delay_button.place(x=290, y=67)
        tx_delay_button.place(x=290, y=117)
        txImg_delay_button.place(x=285, y=247)
        line_canvas.place(x=25, y=180)

        # public_page_show

        self.public_page_label = tk.Label(self.bg_label, image=self.imageLoader.get_image("bg2"), compound="center",
                                          bd=0)
        public_label_1 = tk.Label(self.public_page_label, text="公共翻译接口可能会因网站策略变动导致失效",
                                  font=self.font12, fg="#33ccff")
        public_label_bd = tk.Label(self.public_page_label, text="百度", font=self.font12, fg=self.fontColor)
        public_label_tx = tk.Label(self.public_page_label, text="腾讯", font=self.font12, fg=self.fontColor)
        public_label_ali = tk.Label(self.public_page_label, text="阿里", font=self.font12, fg=self.fontColor)
        public_label_ms = tk.Label(self.public_page_label, text="微软", font=self.font12, fg=self.fontColor)
        public_label_gg = tk.Label(self.public_page_label, text="谷歌", font=self.font12, fg=self.fontColor)
        public_label_cy = tk.Label(self.public_page_label, text="彩云", font=self.font12, fg=self.fontColor)
        public_label_sg = tk.Label(self.public_page_label, text="搜狗", font=self.font12, fg=self.fontColor)
        public_label_yd = tk.Label(self.public_page_label, text="有道", font=self.font12, fg=self.fontColor)
        public_label_2 = tk.Label(self.public_page_label, text="若已配置私有接口则会优先使用个人API", font=self.font12,
                                  fg="#33ccff")

        self.public_button_bd = SwitchButton(self.public_page_label, switch=Global.public_trans == "bd",
                                             marshalling="pbc", off_image=self.imageLoader.get_image("unselect"),
                                             on_image=self.imageLoader.get_image("select"), command=self.publicSwitch)

        self.public_button_tx = SwitchButton(self.public_page_label, switch=Global.public_trans == "tx",
                                             marshalling="pbc", off_image=self.imageLoader.get_image("unselect"),
                                             on_image=self.imageLoader.get_image("select"), command=self.publicSwitch)

        self.public_button_ali = SwitchButton(self.public_page_label, switch=Global.public_trans == "ali",
                                              marshalling="pbc", off_image=self.imageLoader.get_image("unselect"),
                                              on_image=self.imageLoader.get_image("select"), command=self.publicSwitch)

        self.public_button_ms = SwitchButton(self.public_page_label, switch=Global.public_trans == "ms",
                                             marshalling="pbc", off_image=self.imageLoader.get_image("unselect"),
                                             on_image=self.imageLoader.get_image("select"), command=self.publicSwitch)

        self.public_button_gg = SwitchButton(self.public_page_label, switch=Global.public_trans == "gg",
                                             marshalling="pbc", off_image=self.imageLoader.get_image("unselect"),
                                             on_image=self.imageLoader.get_image("select"), command=self.publicSwitch)

        self.public_button_cy = SwitchButton(self.public_page_label, switch=Global.public_trans == "cy",
                                             marshalling="pbc", off_image=self.imageLoader.get_image("unselect"),
                                             on_image=self.imageLoader.get_image("select"), command=self.publicSwitch)

        self.public_button_sg = SwitchButton(self.public_page_label, switch=Global.public_trans == "sg",
                                             marshalling="pbc", off_image=self.imageLoader.get_image("unselect"),
                                             on_image=self.imageLoader.get_image("select"), command=self.publicSwitch)

        self.public_button_yd = SwitchButton(self.public_page_label, switch=Global.public_trans == "yd",
                                             marshalling="pbc", off_image=self.imageLoader.get_image("unselect"),
                                             on_image=self.imageLoader.get_image("select"), command=self.publicSwitch)

        public_label_1.place(x=20, y=25)
        public_label_2.place(x=20, y=220)
        public_label_bd.place(x=30, y=60)
        public_label_tx.place(x=230, y=60)
        public_label_ali.place(x=30, y=100)
        public_label_ms.place(x=230, y=100)
        public_label_gg.place(x=30, y=140)
        public_label_cy.place(x=230, y=140)
        public_label_sg.place(x=30, y=180)
        public_label_yd.place(x=230, y=180)

        self.public_button_bd.place(x=110, y=60)
        self.public_button_tx.place(x=310, y=60)
        self.public_button_ali.place(x=110, y=100)
        self.public_button_ms.place(x=310, y=100)
        self.public_button_gg.place(x=110, y=140)
        self.public_button_cy.place(x=310, y=140)
        self.public_button_sg.place(x=110, y=180)
        self.public_button_yd.place(x=310, y=180)

        # input_page_show
        self.input_page_label = tk.Label(self.bg_label, image=self.imageLoader.get_image("bg2"), compound="center",
                                         bd=0)
        input_label_1 = tk.Label(self.input_page_label, text="选择通过粘贴板或屏幕OCR识别获取原文", font=self.font12, fg="#33ccff")
        input_label_clipboard = tk.Label(self.input_page_label, text="粘贴板", font=self.font12, fg=self.fontColor)
        input_label_OCR = tk.Label(self.input_page_label, text="OCR", font=self.font12, fg=self.fontColor)
        self.input_button_clipboard = SwitchButton(self.input_page_label, switch=Global.inputSource == "cbd",
                                                   marshalling="input", off_image=self.imageLoader.get_image("close"),
                                                   on_image=self.imageLoader.get_image("tick"),
                                                   command=self.inputSwitch)
        self.input_button_OCR = SwitchButton(self.input_page_label, switch=Global.inputSource == "OCR",
                                             marshalling="input", off_image=self.imageLoader.get_image("close"),
                                             on_image=self.imageLoader.get_image("tick"), command=self.inputSwitch)

        input_label_1.place(x=20, y=25)
        input_label_clipboard.place(x=30, y=60)
        input_label_OCR.place(x=230, y=60)
        self.input_button_clipboard.place(x=100, y=63)
        self.input_button_OCR.place(x=300, y=63)

        # OCR_page_show
        self.OCR_page_label = tk.Label(self.bg_label, image=self.imageLoader.get_image("bg2"), compound="center", bd=0)
        OCR_label_1 = tk.Label(self.OCR_page_label, text="如使用本地OCR时发现CPU占用过高可适当调小扫描区域或者降低扫描频率", font=self.font12,
                               fg="#33ccff")
        OCR_label_local = tk.Label(self.OCR_page_label, text="本地OCR", font=self.font12, fg=self.fontColor)
        OCR_label_yd = tk.Label(self.OCR_page_label, text="有道OCR", font=self.font12, fg=self.fontColor)
        OCR_label_2 = tk.Label(self.OCR_page_label, text="是否合并多行文本", font=self.font12, fg=self.fontColor)
        OCR_label_3 = tk.Label(self.OCR_page_label, text="自动执行规则", font=self.font12, fg=self.fontColor)
        OCR_label_4 = tk.Label(self.OCR_page_label, text="执行周期（秒）", font=self.font12, fg=self.fontColor)
        OCR_label_5 = MyLabel(self.OCR_page_label, text="图像一致性阈值", font=self.font12, fg=self.fontColor,
                              tooltip=("比较先后两张扫描图像的像素相似度,设置值越大，扫描频率越高", "red", "#666666"))
        OCR_label_6 = MyLabel(self.OCR_page_label, text="识别场景", font=self.font12, fg=self.fontColor,
                              tooltip=("用于视频字幕请使用动态模式", "red", "#666666"))

        self.OCR_button_local = SwitchButton(self.OCR_page_label, switch=Global.OCR == "local",
                                             marshalling="ocr", off_image=self.imageLoader.get_image("close"),
                                             on_image=self.imageLoader.get_image("tick"), command=self.OCRSwitch)
        self.OCR_button_yd = SwitchButton(self.OCR_page_label, switch=Global.OCR == "yd",
                                          marshalling="ocr", off_image=self.imageLoader.get_image("close"),
                                          on_image=self.imageLoader.get_image("tick"), command=self.OCRSwitch)
        self.OCR_button_merge = SwitchButton(self.OCR_page_label, switch=Global.ocr_setting["mergelines"],
                                             off_image=self.imageLoader.get_image("close"),
                                             on_image=self.imageLoader.get_image("tick"), command=self.is_merge)
        self.autoRules_combobox = ttk.Combobox(self.OCR_page_label, state='readonly', style="Custom.TCombobox",
                                               values=["分析图像更新", "周期执行", "分析图像更新+周期执行"], width=15)
        self.autoRules_combobox.current(set_config["ocr_setting"]["ocr_auto_method"])
        self.autoRules_combobox.bind("<<ComboboxSelected>>", self.select_rules)
        self.OCR_spin_interval = ttk.Spinbox(self.OCR_page_label, from_=0, to_=30, increment=0.1,
                                             command=self.set_interval
                                             , textvariable=self.inter_val, state="readonly", wrap=True,
                                             style='Custom.TSpinbox',
                                             width=10)
        self.inter_val.set(Global.ocr_setting["ocr_interval"])
        self.OCR_spin_sim = ttk.Spinbox(self.OCR_page_label, from_=0, to_=1, increment=0.01, command=self.set_sim,
                                        width=10
                                        , textvariable=self.sim_val, state="readonly", wrap=True,
                                        style='Custom.TSpinbox')
        self.sim_val.set(Global.ocr_setting["ocr_diff_sim"])
        self.scenes_combobox = ttk.Combobox(self.OCR_page_label, state='readonly', style="Custom.TCombobox",
                                            values=["    静态", "    动态"], width=8)
        self.scenes_combobox.current(set_config["ocr_setting"]["ocr_scenes"])
        self.scenes_combobox.bind("<<ComboboxSelected>>", self.select_scenes)
        OCR_label_1.place(x=20, y=25)
        OCR_label_2.place(x=30, y=120)
        OCR_label_3.place(x=30, y=155)
        OCR_label_4.place(x=30, y=190)
        OCR_label_5.place(x=30, y=225)
        OCR_label_6.place(x=30, y=260)
        OCR_label_local.place(x=30, y=60)
        OCR_label_yd.place(x=230, y=60)
        self.OCR_button_local.place(x=130, y=63)
        self.OCR_button_yd.place(x=330, y=63)
        self.OCR_button_merge.place(x=300, y=120)
        self.autoRules_combobox.place(x=300, y=155)
        self.OCR_spin_interval.place(x=300, y=190)
        self.OCR_spin_sim.place(x=300, y=225)
        self.scenes_combobox.place(x=300, y=260)

        # language_page_show
        self.language_page_label = tk.Label(self.bg_label, image=self.imageLoader.get_image("bg2"), compound="center",
                                            bd=0)
        language_label_1 = tk.Label(self.language_page_label, text="在此选择需要识别翻译的语言", font=self.font12, fg="#33ccff")
        language_label_2 = MyLabel(self.language_page_label, text="快速切换语言，可选三种", font=self.font12, fg="#33ccff",
                                   tooltip=("选择后可在主界面左上角点击切换", "red", "#666666"))

        self.language_combobox = ttk.Combobox(self.language_page_label, state='readonly', style="Custom.TCombobox",
                                              values=["英语", "日语", "繁体中文", "韩语", "俄语", "法语", "西班牙语", "阿拉伯语"], width=7)
        self.language_combobox.set(set_config["language"])
        self.language_combobox.bind("<<ComboboxSelected>>", self.select_language)

        def on_checkbox_click():
            # 清空选择结果列表
            Global.quick_lan.clear()
            # 遍历多选框列表，检查勾选状态
            for index, checkbox in enumerate(checkboxes):
                if checkbox.get() and len(Global.quick_lan) < 3:
                    # 如果多选框被勾选且未超过最大选择数量，则将语言添加到选择结果列表
                    Global.quick_lan.append(languages[index])
                else:
                    # 如果多选框未被勾选或超过最大选择数量，则取消勾选
                    checkbox.set(0)
            set_config["selected_languages"] = Global.quick_lan
            save_settings(Global.setting_path)

        checkboxes = []
        languages = ["英语", "日语", "繁体中文", "韩语", "俄语", "西班牙语", "法语", "阿拉伯语"]
        i = 0
        for language in languages:
            i += 1
            var = tk.IntVar()
            checkbox = ttk.Checkbutton(self.language_page_label, text=language, variable=var, command=on_checkbox_click)
            checkbox.place(x=40, y=120 + 25 * i)
            checkboxes.append(var)

        language_label_1.place(x=20, y=25)
        language_label_2.place(x=20, y=110)
        self.language_combobox.place(x=30, y=60)

        # keyboard_page_show
        self.hotkey_page_label = tk.Label(self.bg_label, image=self.imageLoader.get_image("bg2"), compound="center",
                                          bd=0)
        hotkey_label_usable = tk.Label(self.hotkey_page_label, text="是否使用快捷键", font=self.font12, fg=self.fontColor)
        hotkey_label_switch = tk.Label(self.hotkey_page_label, text="暂停/运行", font=self.font12, fg=self.fontColor)
        hotkey_label_auto = tk.Label(self.hotkey_page_label, text="自动/手动", font=self.font12, fg=self.fontColor)
        hotkey_label_reTrans = tk.Label(self.hotkey_page_label, text="执行/重新翻译", font=self.font12, fg=self.fontColor)
        hotkey_label_sourceHide = tk.Label(self.hotkey_page_label, text="显示/隐藏原文", font=self.font12, fg=self.fontColor)
        hotkey_label_source = tk.Label(self.hotkey_page_label, text="复制原文", font=self.font12, fg=self.fontColor)
        hotkey_label_result = tk.Label(self.hotkey_page_label, text="复制译文", font=self.font12, fg=self.fontColor)
        hotkey_label_areaHide = tk.Label(self.hotkey_page_label, text="显示/隐藏OCR区域", font=self.font12, fg=self.fontColor)
        hotkey_label_minsize = tk.Label(self.hotkey_page_label, text="最小化/还原", font=self.font12, fg=self.fontColor)
        hotkey_label_quit = tk.Label(self.hotkey_page_label, text="关闭软件", font=self.font12, fg=self.fontColor)
        self.hotkey_button_usable = SwitchButton(self.hotkey_page_label, switch=Global.hotkey_use,
                                                 off_image=self.imageLoader.get_image("close"),
                                                 on_image=self.imageLoader.get_image("tick"), command=self.hotkeyUsable)
        self.hotkey_button_switchSet = ttk.Button(self.hotkey_page_label,
                                                  command=lambda: self.setHotkey(self.hotkey_button_switchSet),
                                                  text='%s' % public.get_hotkey_name(
                                                      Global.hotKey["start_pause"]["key"]))
        self.hotkey_button_autoSet = ttk.Button(self.hotkey_page_label,
                                                text='%s' % public.get_hotkey_name(Global.hotKey["auto_switch"]["key"]),
                                                command=lambda: self.setHotkey(self.hotkey_button_autoSet))
        self.hotkey_button_reTrans = ttk.Button(self.hotkey_page_label,
                                                text='%s' % public.get_hotkey_name(Global.hotKey["reTrans"]["key"]),
                                                command=lambda: self.setHotkey(self.hotkey_button_reTrans))
        self.hotkey_button_sourceHide = ttk.Button(self.hotkey_page_label,
                                                   text='%s' % public.get_hotkey_name(
                                                       Global.hotKey["sourceHide"]["key"]),
                                                   command=lambda: self.setHotkey(self.hotkey_button_sourceHide))
        self.hotkey_button_source = ttk.Button(self.hotkey_page_label,
                                               text='%s' % public.get_hotkey_name(Global.hotKey["source"]["key"]),
                                               command=lambda: self.setHotkey(self.hotkey_button_source))
        self.hotkey_button_result = ttk.Button(self.hotkey_page_label,
                                               text='%s' % public.get_hotkey_name(Global.hotKey["result"]["key"]),
                                               command=lambda: self.setHotkey(self.hotkey_button_result))
        self.hotkey_button_areaHide = ttk.Button(self.hotkey_page_label,
                                                 text='%s' % public.get_hotkey_name(Global.hotKey["areaHide"]["key"]),
                                                 command=lambda: self.setHotkey(self.hotkey_button_areaHide))
        self.hotkey_button_minsize = ttk.Button(self.hotkey_page_label,
                                                text='%s' % public.get_hotkey_name(Global.hotKey["minsize"]["key"]),
                                                command=lambda: self.setHotkey(self.hotkey_button_minsize))
        self.hotkey_button_quit = ttk.Button(self.hotkey_page_label,
                                             text='%s' % public.get_hotkey_name(Global.hotKey["power"]["key"]),
                                             command=lambda: self.setHotkey(self.hotkey_button_quit))
        self.hotkey_buttons = {"start_pause": self.hotkey_button_switchSet, "auto_switch": self.hotkey_button_autoSet,
                               "reTrans": self.hotkey_button_reTrans, "sourceHide": self.hotkey_button_sourceHide,
                               "source": self.hotkey_button_source, "result": self.hotkey_button_result,
                               "areaHide": self.hotkey_button_areaHide, "minsize": self.hotkey_button_minsize,
                               "power": self.hotkey_button_quit}

        hotkey_label_usable.place(x=30, y=25)
        hotkey_label_switch.place(x=30, y=60)
        hotkey_label_auto.place(x=30, y=95)
        hotkey_label_reTrans.place(x=30, y=130)
        hotkey_label_sourceHide.place(x=30, y=165)
        hotkey_label_source.place(x=30, y=200)
        hotkey_label_result.place(x=30, y=235)
        hotkey_label_areaHide.place(x=30, y=270)
        hotkey_label_minsize.place(x=30, y=305)
        hotkey_label_quit.place(x=30, y=340)
        self.hotkey_button_usable.place(x=280, y=25)
        self.hotkey_button_switchSet.place(x=250, y=60)
        self.hotkey_button_autoSet.place(x=250, y=95)
        self.hotkey_button_reTrans.place(x=250, y=130)
        self.hotkey_button_sourceHide.place(x=250, y=165)
        self.hotkey_button_source.place(x=250, y=200)
        self.hotkey_button_result.place(x=250, y=235)
        self.hotkey_button_areaHide.place(x=250, y=270)
        self.hotkey_button_minsize.place(x=250, y=305)
        self.hotkey_button_quit.place(x=250, y=340)

        # font_page_show
        self.font_page_label = tk.Label(self.bg_label, image=self.imageLoader.get_image("bg2"), compound="center",
                                        bd=0)
        font_label_1 = tk.Label(self.font_page_label, text="在此可以更改软件内的字体,关闭设置生效", font=self.font12, fg="#33ccff")
        font_label_setting = tk.Label(self.font_page_label, text="设置界面：", font=self.font12, fg=self.fontColor)
        font_label_set_font = tk.Label(self.font_page_label, text="字体", font=self.font12, fg=self.fontColor)
        font_label_set_size = tk.Label(self.font_page_label, text="字号", font=self.font12, fg=self.fontColor)
        font_label_set_weight = tk.Label(self.font_page_label, text="粗细", font=self.font12, fg=self.fontColor)
        font_label_set_color = tk.Label(self.font_page_label, text="颜色", font=self.font12, fg=self.fontColor)
        font_label_source = tk.Label(self.font_page_label, text="主界面：", font=self.font12, fg=self.fontColor)
        font_label_source_font = tk.Label(self.font_page_label, text="原文字体", font=self.font12, fg=self.fontColor)
        font_label_result_font = tk.Label(self.font_page_label, text="译文字体", font=self.font12, fg=self.fontColor)
        font_label_source_size = tk.Label(self.font_page_label, text="字号", font=self.font12, fg=self.fontColor)
        font_label_source_weight = tk.Label(self.font_page_label, text="粗细", font=self.font12, fg=self.fontColor)
        font_label_source_color = tk.Label(self.font_page_label, text="颜色", font=self.font12, fg=self.fontColor)
        font_label_result_size = tk.Label(self.font_page_label, text="字号", font=self.font12, fg=self.fontColor)
        font_label_result_weight = tk.Label(self.font_page_label, text="粗细", font=self.font12, fg=self.fontColor)
        font_label_result_color = tk.Label(self.font_page_label, text="颜色", font=self.font12, fg=self.fontColor)
        font_families = tkfont.families()
        self.font_combobox_set = ttk.Combobox(self.font_page_label, state='readonly', values=font_families, width=18)
        self.size_combobox_set = ttk.Combobox(self.font_page_label, state='readonly',
                                              values=[8, 9, 10, 11, 12, 14, 16, 18, 20], width=4)
        self.color_button_set = tk.Button(self.font_page_label, bg=set_config["font"]["setting"][2], relief='flat',
                                          width=3, command=lambda: colorChange("setting", self.color_button_set))
        self.weight_combobox_set = ttk.Combobox(self.font_page_label, state='readonly', values=["normal", "bold"],
                                                width=6)
        self.font_combobox_source = ttk.Combobox(self.font_page_label, state='readonly', values=font_families, width=18)
        self.size_combobox_source = ttk.Combobox(self.font_page_label, state='readonly',
                                                 values=[12, 14, 16, 18, 20, 22, 24, 26], width=4)
        self.color_button_source = tk.Button(self.font_page_label, bg=set_config["font"]["source"][2], relief='flat',
                                             width=3, command=lambda: colorChange("source", self.color_button_source))
        self.weight_combobox_source = ttk.Combobox(self.font_page_label, state='readonly', values=["normal", "bold"],
                                                   width=6)
        self.font_combobox_result = ttk.Combobox(self.font_page_label, state='readonly', values=font_families, width=18)
        self.size_combobox_result = ttk.Combobox(self.font_page_label, state='readonly',
                                                 values=[12, 14, 16, 18, 20, 22, 24, 26], width=4)
        self.color_button_result = tk.Button(self.font_page_label, bg=set_config["font"]["result"][2], relief='flat',
                                             width=3, command=lambda: colorChange("result", self.color_button_result))
        self.weight_combobox_result = ttk.Combobox(self.font_page_label, state='readonly', values=["normal", "bold"],
                                                   width=6)
        self.font_combobox_set.set(set_config["font"]["setting"][0])
        self.size_combobox_set.set(set_config["font"]["setting"][1])
        self.weight_combobox_set.set(set_config["font"]["setting"][3])
        self.font_combobox_set.bind("<<ComboboxSelected>>",
                                    lambda event: self.select_font(event, "setting", self.font_combobox_set))
        self.size_combobox_set.bind("<<ComboboxSelected>>",
                                    lambda event: self.select_size(event, "setting", self.size_combobox_set))
        self.weight_combobox_set.bind("<<ComboboxSelected>>",
                                      lambda event: self.select_weight(event, "setting", self.weight_combobox_set))

        self.font_combobox_source.set(set_config["font"]["source"][0])
        self.size_combobox_source.set(set_config["font"]["source"][1])
        self.weight_combobox_source.set(set_config["font"]["source"][3])
        self.font_combobox_source.bind("<<ComboboxSelected>>",
                                       lambda event: self.select_font(event, "source", self.font_combobox_source))
        self.size_combobox_source.bind("<<ComboboxSelected>>",
                                       lambda event: self.select_size(event, "source", self.size_combobox_source))
        self.weight_combobox_source.bind("<<ComboboxSelected>>",
                                         lambda event: self.select_weight(event, "source", self.weight_combobox_source))

        self.font_combobox_result.set(set_config["font"]["result"][0])
        self.size_combobox_result.set(set_config["font"]["result"][1])
        self.weight_combobox_result.set(set_config["font"]["result"][3])
        self.font_combobox_result.bind("<<ComboboxSelected>>",
                                       lambda event: self.select_font(event, "result", self.font_combobox_result))
        self.size_combobox_result.bind("<<ComboboxSelected>>",
                                       lambda event: self.select_size(event, "result", self.size_combobox_result))
        self.weight_combobox_result.bind("<<ComboboxSelected>>",
                                         lambda event: self.select_weight(event, "result", self.weight_combobox_result))

        font_label_1.place(x=30, y=25)
        font_label_setting.place(x=30, y=60)
        font_label_set_font.place(x=30, y=95)
        self.font_combobox_set.place(x=73, y=95)
        font_label_set_size.place(x=30, y=130)
        self.size_combobox_set.place(x=73, y=130)
        font_label_set_weight.place(x=147, y=130)
        self.weight_combobox_set.place(x=190, y=130)
        font_label_set_color.place(x=280, y=130)
        self.color_button_set.place(x=320, y=129)
        font_label_source.place(x=30, y=170)
        font_label_source_font.place(x=30, y=205)
        font_label_result_font.place(x=280, y=205)
        font_label_source_size.place(x=30, y=240)
        font_label_source_weight.place(x=30, y=275)
        font_label_source_color.place(x=30, y=320)
        font_label_result_size.place(x=280, y=240)
        font_label_result_weight.place(x=280, y=275)
        font_label_result_color.place(x=280, y=320)
        self.font_combobox_source.place(x=105, y=205)
        self.size_combobox_source.place(x=105, y=240)
        self.weight_combobox_source.place(x=105, y=275)
        self.color_button_source.place(x=105, y=320)
        self.font_combobox_result.place(x=355, y=205)
        self.size_combobox_result.place(x=355, y=240)
        self.weight_combobox_result.place(x=355, y=275)
        self.color_button_result.place(x=355, y=320)

        # theme_page_show
        self.theme_page_label = tk.Label(self.bg_label, image=self.imageLoader.get_image("bg2"), compound="center",
                                         bd=0)
        theme_label_1 = tk.Label(self.theme_page_label, text="累了，糊弄一下，壁纸重启生效", font=self.font12, fg="#33ccff")
        theme_label_bg = tk.Label(self.theme_page_label, text="初始界面壁纸", font=self.font12, fg=self.fontColor)
        theme_label_tp = tk.Label(self.theme_page_label, text="透明度", font=self.font12, fg=self.fontColor)
        theme_label_bg2 = tk.Label(self.theme_page_label, text="功能界面壁纸", font=self.font12, fg=self.fontColor)
        theme_label_tp2 = tk.Label(self.theme_page_label, text="透明度", font=self.font12, fg=self.fontColor)
        theme_label_spr = tk.Label(self.theme_page_label, text="窗口透明度", font=self.font12, fg=self.fontColor)
        theme_button_bg = ttk.Button(self.theme_page_label, text="选择图片", command=lambda: self.choose_bg("bg"))
        theme_button_bg2 = ttk.Button(self.theme_page_label, text="选择图片", command=lambda: self.choose_bg("bg2"))
        theme_scale_bg = ttk.Scale(self.theme_page_label, orient='horizontal', length=150, from_=10, to=100,
                                   command=lambda value: self.tp_set("bg", value), value=70)
        theme_scale_bg2 = ttk.Scale(self.theme_page_label, orient='horizontal', length=150, from_=10, to=100,
                                    command=lambda value: self.tp_set("bg2", value), value=70)
        theme_scale_spr = ttk.Scale(self.theme_page_label, orient='horizontal', length=150, from_=1, to=100,
                                    command=lambda value: self.spr_set(value), value=95)
        theme_button_apply = ttk.Button(self.theme_page_label, text="应用壁纸", command=lambda: self.apply_set("bg"))
        theme_button_apply2 = ttk.Button(self.theme_page_label, text="应用壁纸", command=lambda: self.apply_set("bg2"))
        theme_button_default = ttk.Button(self.theme_page_label, text="恢复默认", command=bg_default)

        theme_label_1.place(x=30, y=25)
        theme_label_bg.place(x=30, y=60)
        theme_button_bg.place(x=140, y=60)
        theme_label_tp.place(x=30, y=95)
        theme_label_bg2.place(x=30, y=160)
        theme_label_spr.place(x=30, y=235)
        theme_button_bg2.place(x=140, y=160)
        theme_label_tp2.place(x=30, y=195)
        theme_scale_bg.place(x=100, y=95)
        theme_scale_bg2.place(x=100, y=195)
        theme_button_apply.place(x=280, y=75)
        theme_button_apply2.place(x=280, y=175)
        theme_scale_spr.place(x=100, y=235)
        theme_button_default.place(x=30, y=330)

        # other_page_show
        self.other_page_label = tk.Label(self.bg_label, image=self.imageLoader.get_image("bg2"), compound="center",
                                         bd=0)
        other_label_1 = tk.Label(self.other_page_label, text="预留空间", font=self.font12, fg="#33ccff")
        other_label_2 = MyLabel(self.other_page_label, text="存储感知", fg=self.fontColor, font=self.font12,
                                tooltip=("用于自动清理OCR扫描的缓存图片,路径为本软件下的.cache/ocr\n设置为0则不自动清理,回车保存",
                                         "red", "#666666"))
        other_label_3 = MyLabel(self.other_page_label, text="MB", fg=self.fontColor, font=self.font12)
        self.other_entry_size = ttk.Entry(self.other_page_label, width=5)
        self.other_entry_size.insert(0, set_config["limit_size"])
        self.other_entry_size.bind("<Return>", self.save_limit)

        other_label_1.place(x=30, y=25)
        other_label_2.place(x=30, y=60)
        other_label_3.place(x=160, y=60)
        self.other_entry_size.place(x=110, y=60)

        # about_page_show
        self.about_page_label = tk.Label(self.bg_label, image=self.imageLoader.get_image("bg2"), compound="center",
                                         bd=0)
        about_label_1 = tk.Label(self.about_page_label, text="关于", font=self.font12, fg="#33ccff")
        about_label_1.place(x=30, y=25)

        self.specific_pages = {
            "personal": [self.personal_page_label],
            "public": [self.public_page_label],
            "input": [self.input_page_label],
            "OCR": [self.OCR_page_label],
            "language": [self.language_page_label],
            "hotkey": [self.hotkey_page_label],
            "font": [self.font_page_label],
            "theme": [self.theme_page_label],
            "other": [self.other_page_label],
            "abaochi": [self.about_page_label]
        }

    def baiduSwitch(self):
        if self.personal_baidu_button.switch:
            set_config["API_CO"] = "Baidu"
        else:
            set_config["API_CO"] = None
        save_settings(Global.setting_path)
        public.update_global()

    def tencentSwitch(self):
        if self.personal_tencent_button.switch:
            set_config["API_CO"] = "Tencent"
        else:
            set_config["API_CO"] = None
        save_settings(Global.setting_path)
        public.update_global()

    def tencentImg_switch(self):
        if self.personal_tencentImg_button.switch:
            set_config["API_CO"] = "TencentImg"
        else:
            set_config["API_CO"] = None
        save_settings(Global.setting_path)
        public.update_global()

    def publicSwitch(self):
        if self.public_button_bd.switch:
            set_config["public_trans"] = "bd"
        elif self.public_button_tx.switch:
            set_config["public_trans"] = "tx"
        elif self.public_button_ali.switch:
            set_config["public_trans"] = "ali"
        elif self.public_button_ms.switch:
            set_config["public_trans"] = "ms"
        elif self.public_button_gg.switch:
            set_config["public_trans"] = "gg"
        elif self.public_button_cy.switch:
            set_config["public_trans"] = "cy"
        elif self.public_button_sg.switch:
            set_config["public_trans"] = "sg"
        elif self.public_button_yd.switch:
            set_config["public_trans"] = "yd"
        else:
            set_config["public_trans"] = None
        save_settings(Global.setting_path)
        public.update_global()

    def inputSwitch(self):
        if self.input_button_clipboard.switch:
            set_config["input"] = "cbd"
            self.main_gui.inputCase = Clipboard(self.main_gui)
        elif self.input_button_OCR.switch:
            set_config["input"] = "OCR"
            self.main_gui.inputCase = OCR()
        else:
            set_config["input"] = None
            self.main_gui.inputCase = None
        save_settings(Global.setting_path)
        public.update_global()

    def OCRSwitch(self):
        if self.OCR_button_local.switch:
            set_config["OCR"] = "local"
        elif self.OCR_button_yd.switch:
            set_config["OCR"] = "yd"
        else:
            set_config["OCR"] = None
        save_settings(Global.setting_path)
        public.update_global()

    def is_merge(self):
        if self.OCR_button_merge.switch:
            set_config["ocr_setting"]["mergelines"] = True
        else:
            set_config["ocr_setting"]["mergelines"] = False
        save_settings(Global.setting_path)
        public.update_global()

    def select_rules(self, event):
        set_config["ocr_setting"]["ocr_auto_method"] = self.autoRules_combobox.current()
        save_settings(Global.setting_path)
        public.update_global()
        self.focus()

    def select_scenes(self, event):
        set_config["ocr_setting"]["ocr_scenes"] = self.scenes_combobox.current()
        save_settings(Global.setting_path)
        public.update_global()
        self.focus()

    def set_interval(self):
        set_config["ocr_setting"]["ocr_interval"] = self.inter_val.get()
        save_settings(Global.setting_path)
        public.update_global()

    def set_sim(self):
        set_config["ocr_setting"]["ocr_diff_sim"] = self.sim_val.get()
        save_settings(Global.setting_path)
        public.update_global()

    def select_language(self, event):
        set_config["language"] = self.language_combobox.get()
        save_settings(Global.setting_path)
        public.update_global()
        self.focus()
        self.main_gui.update_lan_label(Global.language[0])

    def hotkeyUsable(self):  # 全局热键启停
        if self.hotkey_button_usable.switch:
            set_config["hotKey"]["use"] = True
        else:
            set_config["hotKey"]["use"] = False
        save_settings(Global.setting_path)
        public.update_global()

    def setHotkey(self, button):
        # 当一个按钮正在设置快捷键时其他按钮不可用
        def disableButtons(self=self):
            for btm in self.hotkey_buttons.values():
                if btm != button:
                    btm.config(state='disabled')

        def enableButtons(self=self):
            for btm in self.hotkey_buttons.values():
                if btm != button:
                    btm.config(state='normal')

        def findFuncName(self=self):  # 用于确定当前是哪个按钮，后续写入json
            for key, val in self.hotkey_buttons.items():
                if val == button:
                    return key
            else:
                pass

        self.hotkey_setting_mode = not self.hotkey_setting_mode
        self.hotkey_bind()
        if self.hotkey_setting_mode:
            self.current_button = button  # 记录当前的按钮
            disableButtons()
            self.bak_text = button.cget("text")  # 备份之前的热键，若未修改可还原
            Global.hotkey_use = False  # 暂时关闭热键使用
            button.config(text='退出设置模式')
        else:
            self.current_button = None
            enableButtons()
            Global.hotkey_use = set_config["hotKey"]["use"]
            if self.desired_hotkey:
                self.desired_hotkey = public.regulate_hotkey(self.desired_hotkey)
                button.config(text="%s" % public.get_hotkey_name(self.desired_hotkey))
                set_config["hotKey"][findFuncName()]["key"] = self.desired_hotkey
                save_settings(Global.setting_path)
                public.update_global()
                func = self.main_gui.hotkey_func_dict.get(findFuncName())
                self.main_gui.hotkey.add_hkey(self.desired_hotkey, func)
                self.desired_hotkey = []
            else:
                button.config(text=self.bak_text)

    def hotkey_detect(self, event):  # 松开时传递给setHotkey
        self.hotkey_setting_mode = True  # 重新置True，执行setHotkey进入else分支
        self.setHotkey(self.current_button)

    def key_press(self, event):  # 按下时开始记录按键
        if self.hotkey_setting_mode:
            hotkey = event.keycode
            if hotkey == 27:
                self.desired_hotkey = [0, 0]  # 按esc为清除热键
                self.hotkey_setting_mode = False
            elif hotkey not in Global.modifier_key or len(self.desired_hotkey) >= 1:  # 组合键最多支持双键
                self.desired_hotkey.append(hotkey)
                self.desired_hotkey = list(set(self.desired_hotkey))  # 因为按下事件是循环的，所以需要剔除重复项
                self.hotkey_setting_mode = False  # 满足条件暂时关闭热键设置模式
            else:
                self.desired_hotkey.append(hotkey)  # 不满足条件继续添加热键，即按住修饰键还未松开或按下其他键的情况

    def accessTk(self, button_id):
        def sure():
            if button_id == "bd":
                set_config["baiduAPI"]["secretID"] = uuid_entry.get()
                set_config["baiduAPI"]["secretKey"] = key_entry.get()
            else:
                set_config["tencentAPI"]["secretID"] = uuid_entry.get()
                set_config["tencentAPI"]["secretKey"] = key_entry.get()
            save_settings(Global.setting_path)
            win.destroy()

        def focus():
            focused_widget = win.focus_get()
            if focused_widget == uuid_entry:
                uuid_entry.delete(0, tk.END)
            elif focused_widget == key_entry:
                key_entry.delete(0, tk.END)
            else:
                uuid_entry.delete(0, tk.END)
                key_entry.delete(0, tk.END)

        def close():
            win.destroy()

        def show():
            if show_button.switch:
                key_entry.configure(show="")
            else:
                key_entry.configure(show="*")

        win = tk.Toplevel(self)
        win.title("请在此输入密钥")
        win.resizable(False, False)
        win.geometry("300x110+%d+%d" % (self.screenWidth / 5, self.screenHeight / 4))
        win.grab_set()

        if button_id == "bd":
            uuid_get, key_get = set_config["baiduAPI"]["secretID"], set_config["baiduAPI"]["secretKey"]
        else:
            uuid_get, key_get = set_config["tencentAPI"]["secretID"], set_config["tencentAPI"]["secretKey"]
        uuid = tk.StringVar(value=uuid_get)
        key = tk.StringVar(value=key_get)
        tk.Label(win, text="uuid").place(relx=0.11, rely=0.04)
        uuid_entry = tk.Entry(win, width=25, textvariable=uuid)
        uuid_entry.place(relx=0.24, rely=0.06)
        tk.Label(win, text="key").place(relx=0.11, rely=0.32)
        key_entry = tk.Entry(win, width=25, textvariable=key, show="*")
        key_entry.place(relx=0.24, rely=0.32)
        show_button = SwitchButton(win, bg="#f0f0f0", relief="sunken", off_image=self.imageLoader.get_image("hide"),
                                   on_image=self.imageLoader.get_image("show"), borderwidth=0, command=show)
        show_button.place(relx=0.88, rely=0.33)

        ttk.Button(win, text="确定", width=5, command=sure).place(relx=0.18, rely=0.55)
        ttk.Button(win, text="清除", width=5, takefocus=False, command=focus).place(relx=0.43, rely=0.55)
        ttk.Button(win, text="取消", width=5, command=close).place(relx=0.68, rely=0.55)
        tk.Label(win, text="请勿向他人展示密钥，如已泄露请登录控制平台重置").place(relx=0.015, rely=0.82)

    def delay_test(self):
        pass



    def select_font(self, event, where, who):
        set_config["font"][where][0] = who.get()
        save_settings(Global.setting_path)
        self.focus()

    def select_size(self, event, where, who):
        set_config["font"][where][1] = int(who.get())
        save_settings(Global.setting_path)
        self.focus()

    def select_weight(self, event, where, who):
        set_config["font"][where][3] = who.get()
        save_settings(Global.setting_path)
        self.focus()

    def choose_bg(self, f):
        filepath = filedialog.askopenfilename(title="请选择一张图片", filetypes=[("图片", ".jpg .png .jpeg")])
        if filepath:
            self.bg[f] = filepath

    def tp_set(self, f, v):
        self.tp[f] = int(float(v))

    def apply_set(self, f):
        try:
            a = public.resizeImage(self.bg_label, self.bg[f])[0]
        except FileNotFoundError:
            return
        b = public.transparency(a, self.tp[f])[0]
        self.bg[f] = "custom_%s.png" % f
        b.save("files/res/custom_%s.png" % f, "PNG")
        set_config["background"] = self.bg
        save_settings(Global.setting_path)

    def spr_set(self, v):
        v = int(float(v)) / 100
        self.bg["spr"] = v
        set_config["background"]["spr"] = v
        save_settings(Global.setting_path)
        self.wm_attributes('-alpha', self.bg["spr"])

    def save_limit(self, event):
        size = self.other_entry_size.get()
        try:
            set_config["limit_size"] = int(size)
        except ValueError:
            messagebox.showerror("错误参数", "需要输入整数")
        save_settings(Global.setting_path)
        self.focus()

    # **********************防止重复创建终极方法********************* #


def hide_all_buttons_except(page, dic):
    # print(dic)
    for key in dic.keys():
        if key != page:
            delete_list = dic[key]
            for delete in delete_list:
                if delete.winfo_manager() == 'place':
                    delete.place_forget()


def get_container(widget):
    parent_id = widget.winfo_parent()
    parent = widget.nametowidget(parent_id)
    container_class = parent.winfo_class()
    return parent, container_class


def readme():  # 处理点击事件的函数
    try:
        subprocess.run(["start", "", Global.parent_dir + "/files/readme.docx"], shell=True)
    except FileNotFoundError:
        messagebox.showerror("打开失败", "使用文档不存在")
    except subprocess.CalledProcessError:
        messagebox.showerror("打开失败", "电脑中无可打开docx的软件或无法调起该软件")
    except Exception as e:
        messagebox.showerror("打开失败", "请前往日志查看具体原因")
        logging.error(f"打开使用文档时出现错误: {e}")


def colorChange(who, button):
    color = colorchooser.askcolor(title="选择颜色")
    if color[1]:
        selected_color = color[1]
        button.configure(bg=selected_color)
        set_config["font"][who][2] = selected_color
        save_settings(Global.setting_path)


def bg_default():
    set_config["background"] = {
        "bg": "background1.png",
        "bg2": "background2.png",
        "spr": 0.95}
    save_settings(Global.setting_path)


def download_model():
    webbrowser.open("https://github.com/Jotalz/YiTranslator/releases/tag/v1.0.0")


def start():
    try:
        root = SetGUI(mainGUI=tk)
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    start()
