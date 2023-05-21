import tkinter as tk
from tkinter import ttk

import Global
import public
from Global import save_settings, set_config
from public import ImageLoader, MyButton, SwitchButton, BreathingLabel, Tooltip


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.resizable(False, False)  # 禁止改变窗口大小x,y
        self.screenWidth = self.winfo_screenwidth()
        self.screenHeight = self.winfo_screenheight()
        self.geometry("700x500+%d+%d" % (self.screenWidth / 3, self.screenHeight / 4))
        self.configure(bg="#666666")
        self.wm_attributes('-alpha', 0.9, '-topmost', 'true', '-transparentcolor', "#666666")
        self.overrideredirect(True)

        self.imageLoader = ImageLoader()
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
        self.settingGUI = None  # 设置窗体对象名
        self.exist_setting = False  # 是否存在设置界面
        self.visible = True

        self.frame_init()
        self.interface_init()
        self.textView()
        self.bind_event()

    def bind_event(self):
        self.function_frame.bind("<ButtonPress-1>", self.start_drag)
        self.function_frame.bind("<B1-Motion>", self.drag)
        self.function_frame.bind("<ButtonRelease-1>", self.stop_drag)
        self.bind("<Map>", self.on_window_mapped)

    def frame_init(self):  # 布置frame
        self.function_frame = tk.Frame(self, bg="#99ffcc", bd=0, height=30, width=700)
        self.function_frame.pack()
        self.text_canvas = tk.Canvas(self, bg="#e6e6e6", bd=0, highlightthickness=0, height=60, width=700)
        self.text_canvas.pack()
        # self.text_bg = self.text_canvas.create_image(0, 0, anchor="nw", image=self.imageLoader.get_image("text_bg"))

    def interface_init(self):
        self.start_pause_button = SwitchButton(self.function_frame, bg="#99ffcc", command=self.start_pause,
                                               borderwidth=0, hover_bg="#80ffbf",
                                               switch=Global.start_pause, off_image=self.imageLoader.get_image("pause"),
                                               on_image=self.imageLoader.get_image("start"), activebackground="#99ffcc")
        self.start_pause_button.place(relx=0.3, rely=0.01)
        self.area_set_button = MyButton(self.function_frame, bg="#99ffcc", hover_bg="#80ffbf", command=self.areaSetting,
                                        normal_image=self.imageLoader.get_image("area"), borderwidth=0,
                                        activebackground="#99ffcc")
        self.area_set_button.place(relx=0.35, rely=0.01)
        self.setting_button = MyButton(self.function_frame, bg="#99ffcc", hover_bg="#80ffbf", borderwidth=0,
                                       activebackground="#99ffcc", normal_image=self.imageLoader.get_image("setting"),
                                       command=self.create_settingGui)
        self.setting_button.place(relx=0.4, rely=0.01)
        self.manual_auto_button = SwitchButton(self.function_frame, bg="#99ffcc", command=self.auto_switch,
                                               relief="sunken",
                                               off_image=self.imageLoader.get_image("switch_manual"), borderwidth=0,
                                               on_image=self.imageLoader.get_image("switch_auto"),
                                               activebackground="#99ffcc", switch=Global.auto)
        self.manual_auto_button.place(relx=0.45, rely=0.01)
        self.visibility_button = SwitchButton(self.function_frame, bg="#99ffcc", command=self.visibility,
                                              relief="sunken", switch=True,
                                              off_image=self.imageLoader.get_image("invisible"), borderwidth=0,
                                              on_image=self.imageLoader.get_image("visible"), hover_bg="#80ffbf",
                                              activebackground="#99ffcc")
        self.visibility_button.place(relx=0.6, rely=0.01)
        self.minsize_button = MyButton(self.function_frame, bg="#99ffcc", hover_bg="#80ffbf", command=self.minsize,
                                       normal_image=self.imageLoader.get_image("minsize_normal"), borderwidth=0,
                                       pressed_image=self.imageLoader.get_image("minsize_press"),
                                       activebackground="#99ffcc")
        self.minsize_button.place(relx=0.65, rely=0.01)
        self.power_button = MyButton(self.function_frame, bg="#99ffcc", hover_bg="#80ffbf", command=self.power,
                                     normal_image=self.imageLoader.get_image("power_normal"), borderwidth=0,
                                     pressed_image=self.imageLoader.get_image("power_press"),
                                     activebackground="#99ffcc")
        self.power_button.place(relx=0.7, rely=0.01)

    def textView(self):  # 布置文本
        self.tips = self.text_canvas.create_text(370, 13, text="初始化已完成~", font=("微软雅黑", 10, "bold"), fill="black")
        BreathingLabel(self.text_canvas, image_name='breathing.png', width=50, height=2,
                       duration=100, bg="#ffffff").place(relx=0.48, rely=0.9)

    def start_drag(self, event):  # 读取鼠标开始拖拽时的坐标
        self._drag_data = {"x": event.x, "y": event.y}

    def drag(self, event):  # 窗体左上角坐标 + （- 起始拖拽坐标 + 当前鼠标坐标）-->鼠标变化量 = 窗体坐标变化量
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        if self._drag_data:
            del self._drag_data

    def minsize(self):  # 最小化需要先恢复成普通窗体
        self.overrideredirect(False)
        self.iconify()

    def power(self):
        self.destroy()

    def on_window_mapped(self, event):  # 显示窗口重新设置无状态栏窗体
        if self.state() != "iconic":
            self.overrideredirect(True)

    def on_setting_closed(self, event):  # 检测到设置窗体关闭时调整变量状态
        SwitchButton.button_groups = {}
        if self.exist_setting:
            self.exist_setting = False

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

    def turn_visible(self, event):
        if not self.visible:
            self.visible = not self.visible
            self.function_frame.pack(before=self.text_canvas)
            self.text_canvas.configure(bg="#e6e6e6")
            '''h = self.text_canvas.winfo_height()
            h += 10
            self.text_canvas.configure(height=h)
            print(self.text_canvas.winfo_height())
            # 不把这句分离出来内存会被回收...
            self.buffer_image = resizeImage(self.text_canvas, self.imageLoader.load_image("text_bg2", "text_bg2.png"))
            # 返回的图像id被储存在self.text_bg这个变量中
            self.text_bg = replace_canvas_image(self.text_canvas, self.buffer_image, self.text_bg)'''

    def turn_invisible(self, event):
        if self.visible:
            self.visible = not self.visible
            self.function_frame.pack_forget()
            self.text_canvas.configure(bg="#666666")

    def auto_switch(self):
        if Global.auto:
            set_config["Auto"] = False
            self.tip_create_without("已切换为手动模式", 3000)
        else:
            set_config["Auto"] = True
            self.tip_create_without("已切换为自动模式", 3000)
        save_settings(Global.setting_path)
        public.update_global()
        print(Global.auto)

    def visibility(self):  # 移入text_canvas显示UI，移出function_frame隐藏UI
        if not self.visibility_button.switch:
            self.text_canvas.bind("<Enter>", lambda event: self.turn_visible(event))
            self.function_frame.bind("<Leave>", lambda event: self.turn_invisible(event))
        else:
            self.text_canvas.unbind("<Enter>")
            self.function_frame.unbind("<Leave>")

    def start_pause(self):
        if Global.start_pause:
            set_config["start_pause"] = False
            self.tip_create_without("已暂停...", 3000)
        else:
            set_config["start_pause"] = True
            self.tip_create_without("工作中......", 3000)
        save_settings(Global.setting_path)
        public.update_global()
        print(Global.start_pause)

    def areaSetting(self):
        self.area_set_button["state"] = "disabled"
        win = tk.Toplevel(self)
        win.wm_attributes('-fullscreen', True, '-topmost', True, '-transparentcolor', "#666666")  # 所有6色会被替换为透明像素
        win.config(bg="#666667")
        drawCanvas = tk.Canvas(win, width=self.screenWidth, height=self.screenHeight, bg="#666666")
        win.overrideredirect(True)

        def update_rectangle(value):
            drawCanvas.coords(rectangle, xScale.get(), yScale.get(),
                              xScale.get() + wScale.get(), yScale.get() + hScale.get())

        def saveCord():
            x1, y1, x2, y2 = drawCanvas.coords(rectangle)
            set_config["area"]["x"] = x1
            set_config["area"]["y"] = y1
            set_config["area"]["width"] = x2 - x1
            set_config["area"]["height"] = y2 - y1
            save_settings(Global.setting_path)
            public.update_global()
            # self.update_key_handle()
            self.tip_create_without("识别范围重设成功！", 3000)
            self.area_set_button["state"] = "normal"
            win.destroy()

        useLabel = tk.Label(win, text="通过下方滑块调节矩形，它将作为翻译识别的区域\n长按滑块可微调",
                            font=("微软雅黑", 12, "bold"), fg="red", bg="#666666", anchor="center")
        wScale = ttk.Scale(win, orient='horizontal', length=200, from_=1, to=self.screenWidth, command=update_rectangle,
                           value=Global.rectW)
        hScale = ttk.Scale(win, orient='horizontal', length=200, from_=1, to=self.screenHeight,
                           command=update_rectangle,
                           value=Global.rectH)
        xScale = ttk.Scale(win, orient='horizontal', length=200, from_=0, to=self.screenWidth, command=update_rectangle,
                           value=Global.rectX)
        yScale = ttk.Scale(win, orient='horizontal', length=200, from_=0, to=self.screenHeight,
                           command=update_rectangle,
                           value=Global.rectY)
        label1 = tk.Label(win, text="矩形宽度", font=("微软雅黑", 12, "bold"), fg="red", bg="#666666")
        label2 = tk.Label(win, text="矩形高度", font=("微软雅黑", 12, "bold"), fg="red", bg="#666666")
        label3 = tk.Label(win, text="矩形X轴", font=("微软雅黑", 12, "bold"), fg="red", bg="#666666")
        label4 = tk.Label(win, text="矩形Y轴", font=("微软雅黑", 12, "bold"), fg="red", bg="#666666")

        saveButton = ttk.Button(win, command=saveCord, text="点击保存")
        rectangle = drawCanvas.create_rectangle(Global.rectX, Global.rectY, Global.rectX + Global.rectW, Global.rectY +
                                                Global.rectH, outline='red', width=3)
        wScale.place(relx=0.35, rely=0.15)
        hScale.place(relx=0.6, rely=0.15)
        xScale.place(relx=0.35, rely=0.2)
        yScale.place(relx=0.6, rely=0.2)
        label1.place(relx=0.3, rely=0.15)
        label2.place(relx=0.55, rely=0.15)
        label3.place(relx=0.3, rely=0.2)
        label4.place(relx=0.55, rely=0.2)
        useLabel.place(relx=0.42, rely=0.05)
        saveButton.place(relx=0.48, rely=0.1)
        drawCanvas.pack()

    def create_settingGui(self):  # 窗体不会马上被回收，连续开关会导致内存占用上涨
        self.exist_setting = not self.exist_setting
        if self.exist_setting:
            try:

                from set_interface import SetGUI
                self.settingGUI = SetGUI()
                self.settingGUI.bind("<Destroy>", self.on_setting_closed)
                self.settingGUI.mainloop()
            except KeyboardInterrupt:
                pass
        else:
            self.settingGUI.quit()
            self.settingGUI.destroy()
            self.settingGUI = None


def start():
    try:
        Global.global_init()
        root = MainGUI()
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    start()
