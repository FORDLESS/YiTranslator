import logging
from utils import autoThread
import tkinter as tk
from utils.OCRwindow import DraggableWindow
import Global
import public
from utils import winhotkey
from Global import save_settings, set_config
from getText.clipboard import Clipboard
from public import ImageLoader, MyButton, PageButton, BreathingLabel, SwitchButton
from translator import ali, baidu, tencent, microsoft, caiyun, youdao, sogou
from utils.canvasText import TextCanvas
from getText.OCRengine import OCR


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.resizable(False, False)  # 禁止改变窗口大小x,y
        self.screenWidth = self.winfo_screenwidth()
        self.screenHeight = self.winfo_screenheight()
        self.geometry("700x1080+%d+%d" % (self.screenWidth / 3, self.screenHeight / 4))
        self.configure(bg="#666666")
        self.wm_attributes('-alpha', 0.9, '-topmost', 'true', '-transparentcolor', "#666666")
        self.overrideredirect(True)

        self.imageLoader = ImageLoader()
        self.imageLoader.load_image("sourceOn", "sourceHide.png")
        self.imageLoader.load_image("sourceOff", "sourceHide_2.png")
        self.imageLoader.load_image("reTrans", "reTrans.png")
        self.imageLoader.load_image("minsize_normal", "minsize_1.png")
        self.imageLoader.load_image("minsize_press", "minsize_2.png")
        self.imageLoader.load_image("power_normal", "power_1.png")
        self.imageLoader.load_image("power_press", "power_2.png")
        self.imageLoader.load_image("switch_manual", "switch_1.png")
        self.imageLoader.load_image("switch_auto", "switch_2.png")
        self.imageLoader.load_image("area", "area.png")
        self.imageLoader.load_image("setting", "setting.png")
        self.imageLoader.load_image("start", "start.png")
        self.imageLoader.load_image("pause", "pause.png")
        self.imageLoader.load_image("invisible", "UI_close.png")
        self.imageLoader.load_image("visible", "UI_open.png")
        self.imageLoader.load_image("text_bg", "text_bg.png")
        set_config["User"]["screenwidth"] = self.screenWidth
        set_config["User"]["screenheight"] = self.screenHeight
        save_settings(Global.setting_path)

        self.buffer_image = None
        self.tips_clear_timer = None
        self.win_timer = None
        self.settingGUI = None  # 设置窗体对象名
        self.exist_setting = False  # 是否存在设置界面
        self.visible = True
        self.area = None
        self.quick_index = 0

        self.source_text = None
        self.result_text = None
        self.text_cache = ["", ""]
        self.update_font()

        self.inputCase = None  # 输入源实例
        self.tsaCase = None  # 翻译器实例
        self.autoWorker = None
        self.auto = autoThread.Autowork(self)

        self.frame_init()
        self.interface_init()
        self.textView()
        self.bind_event()
        self.hotkey_init()

        try:
            self.other_init()
        except Exception as error:
            logging.error(f"初始化时出现错误: {error}")

        self.textOBJ = TextCanvas(self)  # 用于绘制文本的类实例

        if Global.auto:
            self.autoTrans()

    def bind_event(self):
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<B1-Motion>", self.drag)
        self.bind("<ButtonRelease-1>", self.stop_drag)
        self.bind("<Map>", self.on_window_mapped)
        self.lan_label.bind("<Button-1>", self.quick_switch_lan)

    def frame_init(self):  # 布置frame
        self.function_frame = tk.Frame(self, bg="#99ffcc", bd=0, height=30, width=700)
        self.function_frame.pack()
        self.text_canvas = tk.Canvas(self, bg="#e6e6e6", bd=0, highlightthickness=0, height=60, width=700)
        self.text_canvas.pack()

    def interface_init(self):
        self.sourceHide_button = SwitchButton(self.function_frame, bg="#99ffcc", command=self.sourceHide,
                                              hover_bg="#80ffbf", tooltip=["显示/隐藏原文", "black", "white"],
                                              switch=Global.sourceHide, activebackground="#99ffcc",
                                              off_image=self.imageLoader.get_image("sourceOff"),
                                              on_image=self.imageLoader.get_image("sourceOn"))
        self.sourceHide_button.place(relx=0.2, rely=0.01)
        self.reTrans_button = MyButton(self.function_frame, bg="#99ffcc", hover_bg="#80ffbf", command=self.reTrans,
                                       normal_image=self.imageLoader.get_image("reTrans"),
                                       activebackground="#99ffcc", tooltip=["翻译/重译", "black", "white"])
        self.reTrans_button.place(relx=0.25, rely=0.01)
        self.start_pause_button = SwitchButton(self.function_frame, bg="#99ffcc", command=self.start_pause,
                                               hover_bg="#80ffbf", tooltip=["暂停/运行", "black", "white"],
                                               switch=Global.start_pause, off_image=self.imageLoader.get_image("pause"),
                                               on_image=self.imageLoader.get_image("start"), activebackground="#99ffcc")
        self.start_pause_button.place(relx=0.3, rely=0.01)
        self.area_set_button = MyButton(self.function_frame, bg="#99ffcc", hover_bg="#80ffbf", command=self.areaSetting,
                                        normal_image=self.imageLoader.get_image("area"),
                                        activebackground="#99ffcc", tooltip=["翻译区域", "black", "white"])
        self.area_set_button.place(relx=0.35, rely=0.01)
        self.setting_button = MyButton(self.function_frame, bg="#99ffcc", hover_bg="#80ffbf",
                                       activebackground="#99ffcc", normal_image=self.imageLoader.get_image("setting"),
                                       command=self.create_settingGui, tooltip=["设置", "black", "white"])
        self.setting_button.place(relx=0.4, rely=0.01)
        self.manual_auto_button = SwitchButton(self.function_frame, bg="#99ffcc", command=self.auto_switch,
                                               off_image=self.imageLoader.get_image("switch_manual"),
                                               on_image=self.imageLoader.get_image("switch_auto"),
                                               activebackground="#99ffcc", switch=Global.auto)
        self.manual_auto_button.place(relx=0.45, rely=0.01)
        self.visibility_button = SwitchButton(self.function_frame, bg="#99ffcc", command=self.visibility,
                                              off_image=self.imageLoader.get_image("invisible"), switch=True,
                                              on_image=self.imageLoader.get_image("visible"), hover_bg="#80ffbf",
                                              activebackground="#99ffcc", tooltip=["隐藏工具栏", "black", "white"])
        self.visibility_button.place(relx=0.6, rely=0.01)
        self.minsize_button = MyButton(self.function_frame, bg="#99ffcc", hover_bg="#80ffbf", command=self.minsize,
                                       normal_image=self.imageLoader.get_image("minsize_normal"),
                                       pressed_image=self.imageLoader.get_image("minsize_press"),
                                       activebackground="#99ffcc", tooltip=["最小化", "black", "white"])
        self.minsize_button.place(relx=0.65, rely=0.01)
        self.power_button = MyButton(self.function_frame, bg="#99ffcc", hover_bg="red", command=self.power,
                                     normal_image=self.imageLoader.get_image("power_normal"),
                                     pressed_image=self.imageLoader.get_image("power_press"),
                                     activebackground="#99ffcc", tooltip=["关闭", "black", "white"])
        self.power_button.place(relx=0.7, rely=0.01)
        self.hotkey_func_dict = {"start_pause": self.start_pause, "auto_switch": self.auto_switch,
                                 "reTrans": self.reTrans, "sourceHide": self.sourceHide, "source": self.source,
                                 "result": self.result, "areaHide": self.areaSetting, "minsize": self.minsize,
                                 "power": self.power}

    def hotkey_init(self):
        self.hotkey = winhotkey.HotkeyListener(self)
        self.hotkey.daemon = True
        for hotkey_name, hotkey_info in Global.hotKey.items():
            if hotkey_name != "use":
                key = hotkey_info["key"]
                func_name = hotkey_name
                func = self.hotkey_func_dict.get(func_name)
                self.hotkey.add_hkey(key, func)
        self.hotkey.start()

    def other_init(self):  # 其他根据设置初始化的信息
        if Global.inputSource == "cbd":
            self.inputCase = Clipboard(self)
        elif Global.inputSource == "OCR":
            self.inputCase = OCR()  # OCR实例
        if Global.api_co:
            if Global.api_co == "Baidu":
                pass
            elif Global.api_co == "Tencent":
                pass
            elif Global.api_co == "TencentImg":
                pass
        elif Global.public_trans == "ali":
            self.tsaCase = ali.Ali()
        elif Global.public_trans == "bd":
            self.tsaCase = baidu.Baidu()
        elif Global.public_trans == "tx":
            self.tsaCase = tencent.QQTranSmart()
        elif Global.public_trans == "ms":
            self.tsaCase = microsoft.MS()
        elif Global.public_trans == "cy":
            self.tsaCase = caiyun.Caiyun()
        elif Global.public_trans == "yd":
            self.tsaCase = youdao.Youdao()
        elif Global.public_trans == "sg":
            self.tsaCase = sogou.Sogou()

    def textView(self):  # 布置文本
        self.tips = self.text_canvas.create_text(370, 13, text="", font=("微软雅黑", 10, "bold"), fill="black")
        BreathingLabel(self.text_canvas, image_name='breathing.png', width=2, height=2,
                       duration=100, bg="#ffffff").place(relx=0.5, rely=0.90)
        self.lan_label = tk.Label(self.function_frame, text="%s" % set_config["language"][0], bg="#99ffcc", fg="white")
        self.lan_label.place(relx=0.005, rely=0.025)

    def drawText(self, extra=None):
        self.textOBJ.draw_text(self.source_text, self.result_text, extra)

    def start_drag(self, event):  # 读取鼠标开始拖拽时的坐标
        self._drag_data = {"x": event.x, "y": event.y}

    def drag(self, event):  # 窗体左上角坐标 + （- 起始拖拽坐标 + 当前鼠标坐标）-->鼠标变化量 = 窗体坐标变化量
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        if self._drag_data is not None:
            self._drag_data = None

    def minsize(self):  # 最小化需要先恢复成普通窗体
        if self.state() != "iconic":
            self.overrideredirect(False)
            self.iconify()
        else:
            self.deiconify()

    def power(self):
        self.destroy()

    def on_window_mapped(self, event):  # 显示窗口重新设置无状态栏窗体
        if self.state() != "iconic":
            self.overrideredirect(True)

    def on_setting_closed(self, event):  # 检测到设置窗体关闭时调整变量状态
        SwitchButton.button_groups = {}
        PageButton.button_groups = {}  # 必须置空否则出错
        if self.exist_setting:
            self.exist_setting = False
        self.update_font()

    def tip_create_without(self, text, timeout, x=350, y=13):
        if self.tips is not None:
            self.text_canvas.itemconfigure(self.tips, text=text)
        else:
            self.tips = self.text_canvas.create_text(x, y, text=text, font=("微软雅黑", 10, "bold"), fill="black")
        if self.tips_clear_timer is not None:  # 用于取消之前的计时，防止timeout内的文字更新在第timeout秒瞬间清除
            self.text_canvas.after_cancel(self.tips_clear_timer)
        self.tips_clear_timer = self.text_canvas.after(timeout, self.tips_clear)  # 设置定时器，在指定时间后删除文本元素

    def tips_clear(self):
        if self.tips is not None:
            self.text_canvas.delete(self.tips)
            self.tips = None  # 清除文本元素的引用
            self.tips_clear_timer = None

    def turn_visible(self, event=None):
        if not self.visible:
            self.visible = not self.visible
            self.function_frame.pack(before=self.text_canvas)
            self.text_canvas.configure(bg="#e6e6e6")

    def turn_invisible(self, event=None):
        if self.visible:
            self.visible = not self.visible
            self.function_frame.pack_forget()
            self.text_canvas.configure(bg="#666666")

    def visibility(self):  # 移入text_canvas显示UI，移出function_frame或者离开text_canvas超过三秒隐藏UI
        if not self.visibility_button.switch:
            self.text_canvas.bind("<Enter>", lambda event: self.reset_timer())
            self.text_canvas.bind("<Leave>", lambda event: self.start_timer())
            self.function_frame.bind("<Leave>", lambda event: self.turn_invisible(event))

        else:
            self.reset_timer()
            self.text_canvas.unbind("<Enter>")
            self.text_canvas.unbind("<Leave>")
            self.function_frame.unbind("<Leave>")
        print(self.visibility_button.switch)

    def reset_timer(self):
        if self.win_timer:
            self.after_cancel(self.win_timer)
        self.turn_visible()

    def start_timer(self):
        self.win_timer = self.after(2000, self.turn_invisible)

    def auto_switch(self):
        if Global.b_flag:  # 如果是热键触发的函数
            Global.b_flag = not Global.b_flag
            self.toggle_auto_switch()
            self.manual_auto_button.on_click(None)  # 主动触发按钮图片切换
        else:
            self.toggle_auto_switch()

    def toggle_auto_switch(self):
        if Global.auto:
            set_config["Auto"] = False
            self.tip_create_without("已切换为手动模式", 3000)
        else:
            set_config["Auto"] = True
            self.tip_create_without("已切换为自动模式", 3000)
            Global.auto = True
            self.autoTrans()
        save_settings(Global.setting_path)
        public.update_global()
        print(Global.auto)

    def start_pause(self):
        if Global.b_flag:  # 如果是热键触发的函数
            Global.b_flag = not Global.b_flag
            self.toggle_start_pause()
            self.start_pause_button.on_click(None)  # 主动触发按钮图片切换
        else:
            self.toggle_start_pause()

    def toggle_start_pause(self):
        if Global.start_pause:
            set_config["start_pause"] = False
            self.tip_create_without("已暂停...", 3000)
        else:
            set_config["start_pause"] = True
            self.tip_create_without("工作中......", 3000)
        save_settings(Global.setting_path)
        public.update_global()

    def sourceHide(self):
        if Global.b_flag:  # 如果是热键触发的函数
            Global.b_flag = not Global.b_flag
            self.toggle_sourceHide()
            self.sourceHide_button.on_click(None)  # 主动触发按钮图片切换
        else:
            self.toggle_sourceHide()

    def toggle_sourceHide(self):
        if Global.sourceHide:
            set_config["sourceHide"] = False
            self.tip_create_without("显示原文", 3000)
        else:
            set_config["sourceHide"] = True
            self.tip_create_without("隐藏原文", 3000)
        save_settings(Global.setting_path)
        public.update_global()

    def areaSetting(self):
        if not self.area:
            self.area = DraggableWindow(self)
            self.area.run()
        else:
            self.area.destroy()
            self.area = None

    def create_settingGui(self):  # 窗体不会马上被回收，连续开关会导致内存占用上涨
        self.exist_setting = not self.exist_setting
        if self.exist_setting:
            try:

                from set_interface import SetGUI
                self.settingGUI = SetGUI(self)
                self.settingGUI.bind("<Destroy>", self.on_setting_closed)
                self.settingGUI.mainloop()
            except KeyboardInterrupt:
                pass
        else:
            self.settingGUI.quit()
            self.settingGUI.destroy()
            self.settingGUI = None

    def update_lan_label(self, new_lan):
        # 更新现识别语言提示
        self.lan_label.config(text=new_lan)

    def quick_switch_lan(self, event):
        try:
            Global.language = Global.quick_lan[self.quick_index]
        except IndexError:  # 中途更改快速语言列表导致越界的处理
            if len(Global.quick_lan) == 0:
                return
            else:
                self.quick_index = 0
                Global.language = Global.quick_lan[self.quick_index]
        self.lan_label.config(text=Global.language[0])
        self.quick_index += 1
        if self.quick_index == len(Global.quick_lan):
            self.quick_index = 0
        set_config["language"] = Global.language
        save_settings(Global.setting_path)

    def update_font(self):
        self.source_fontName = set_config["font"]["source"][0]
        self.source_fontSize = set_config["font"]["source"][1]
        self.source_fontColor = set_config["font"]["source"][2]
        self.source_fontWeight = set_config["font"]["source"][3]
        self.result_fontName = set_config["font"]["result"][0]
        self.result_fontSize = set_config["font"]["result"][1]
        self.result_fontWeight = set_config["font"]["result"][3]
        self.result_fontColor = set_config["font"]["result"][2]

    def reTrans(self):
        if Global.inputSource == "cbd":
            self.source_text = self.inputCase.gettext()
        else:
            self.source_text = self.inputCase.runonce()
        if self.tsaCase:
            self.result_text = self.tsaCase.translate(self.source_text, Global.language)
        else:
            self.drawText("未选择翻译接口")
            return
        self.drawText()

    def autoTrans(self):
        if Global.auto:
            if Global.start_pause:
                self.auto.start_source_task()               # 只要没有暂停就一直扫描
                if not Global.getsourceRunning:             # 扫描完成时获取原文本否则文本为”“
                    self.source_text = self.auto.source
                else:
                    self.source_text = ""
                if self.source_text != "":                  # 如果不为”“才进入翻译分支，减少对翻译api的调用
                    self.text_cache[0] = self.source_text   # 不为""时为有效原文本，将其保存在缓存列表中
                    self.auto.start_result_task()           # 启动翻译任务
                if not Global.getresultRunning:             # 翻译完成时获取译文，并将译文保存至缓存列表
                    self.result_text = self.auto.getResult()
                    self.text_cache[1] = self.result_text
                self.source_text = self.text_cache[0]       # 将原文和译文从缓存列表中读出赋值给将要绘制的文本
                self.result_text = self.text_cache[1]

                self.drawText()
                self.autoWorker = self.after(250, self.autoTrans)
            else:
                self.autoWorker = self.after(250, self.autoTrans)
        else:
            if self.autoWorker:
                self.after_cancel(self.autoWorker)
                self.autoWorker = None

    def source(self):
        self.clipboard_clear()
        self.clipboard_append(self.source_text)

    def result(self):
        self.clipboard_clear()
        self.clipboard_append(self.result_text)


def start():
    try:
        Global.global_init()
        root = MainGUI()
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    start()
