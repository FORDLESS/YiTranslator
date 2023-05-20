import tkinter as tk
from tkinter import ttk, messagebox
import Global
import public
from public import ImageLoader, Tooltip, validateInt, read_settings, save_settings
import keyboard
from easyOCR import CudaCheck, aiOCR
from API import tencent_parse, baidu_parse


# noinspection PyGlobalUndefined,PyUnusedLocal
class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("简单翻译")
        self.resizable(False, False)  # 禁止改变窗口大小x,y
        self.configure(background='#f0f0f0')  # 设置背景颜色
        self.screenWidth = self.winfo_screenwidth()
        self.screenHeight = self.winfo_screenheight()

        self.data = read_settings(Global.data_path)
        self.data["User"]["screenwidth"] = self.screenWidth
        self.data["User"]["screenheight"] = self.screenHeight

        self.geometry("800x495+%d+%d" % (self.screenWidth / 3, self.screenHeight / 4))
        self.imageLoader = ImageLoader()
        self.imageLoader.load_image("icon", "icon.png")
        self.iconphoto(False, self.imageLoader.get_image("icon"))

        self.key_handle = None
        if Global.hotkey_use:
            self.update_key_handle()
        Global.uuid, Global.key = public.secret_load()
        self.hotkeyCheckVar = tk.IntVar(value=Global.hotkey_use)
        self.cudaCheckVar = tk.IntVar(value=Global.haveCUDA)
        self.threadNum = tk.StringVar(value=Global.batchSize)
        self.uuid = tk.StringVar(value=Global.uuid)
        self.key = tk.StringVar(value=Global.key)
        self.top_frame = None
        self.top_canvas = None
        self.button_frame_1 = None
        self.button_frame_2 = None
        self.text_frame = None
        self.api_frame = None
        self.source_textbox = None
        self.post_textbox = None
        self.tips = None
        self.area_setButton = None
        self.key_setButton = None
        self.keyCheck = None
        self.hotkey_setting_mode = False
        self.thread_setting_mode = False
        self.api_setting_mode = False
        self.lanCombobox = None
        self.cudaCheck = None
        self.insButton = None
        self.threadsEntry = None
        self.api_uuid_entry = None
        self.api_key_entry = None
        self.threadSetButton = None
        self.cancelButton = None
        self.cancelButton2 = None
        self.api_set_button = None
        self.api_select_combobox = None
        self.translateButton = None
        self.clearButton = None
        self.copyButton = None

        self.imageLoader.load_image("thread_setting_image", "thread_setting.png")
        self.imageLoader.load_image("thread_setting_close_image", "thread_setting_close.png")
        self.imageLoader.load_image("thread_setting_tick_image", "thread_setting_tick.png")
        self.imageLoader.load_image("arrow-right_image", "arrow-right.png")
        self.imageLoader.load_image("help_image", "help.png")
        self.imageLoader.load_image("copy_image", "copy.png")

        self.frame_init()
        self.interface_init()
        self.textView()

        style = ttk.Style()
        style.configure('ins.TButton', relief='flat', background="#FFFFFF")
        style.configure('TCheckbutton', background="#39ac39")
        style.configure('ths.TButton', borderwidth=0, background="#39ac39")

        save_settings(Global.data_path, self.data)

    def frame_init(self):  # 布置frame
        self.top_frame = tk.Frame(self, bg="#f2f2f2", height=60, width=800)
        self.top_frame.place(x=0, y=0)
        self.top_canvas = tk.Canvas(self.top_frame, width=800, height=60, background="black")
        self.top_canvas.place(x=-2, y=0)
        self.button_frame_1 = tk.Frame(self, bg="#00a3cc", height=255, width=340, highlightthickness=0)
        self.button_frame_1.place(x=30, y=90)
        self.button_frame_2 = tk.Frame(self, bg="#39ac39", height=255, width=340, highlightthickness=0)
        self.button_frame_2.place(x=400, y=90)
        self.text_frame = tk.Frame(self, bg="#e6e6e6", height=125, width=710, highlightthickness=0)
        self.text_frame.place(x=30, y=360)
        self.api_frame = tk.Frame(self.button_frame_2, height=50, width=280, highlightthickness=0)

    def interface_init(self):  # 布置控件
        self.area_setButton = ttk.Button(self.button_frame_1, text="点此查看/设置", command=self.areaSetting)
        self.area_setButton.place(x=100, y=10)
        self.key_setButton = ttk.Button(self.button_frame_2, text='%s' % Global.hotKey, command=self.setHotkey)
        self.key_setButton.place(x=100, y=10)
        self.keyCheck = ttk.Checkbutton(self.button_frame_2, variable=self.hotkeyCheckVar, command=self.hotkey_enabled)
        self.keyCheck.place(x=205, y=10)
        self.bind('<Key>', self.handle_key_event)
        self.lanCombobox = ttk.Combobox(self.button_frame_2, state='readonly', values=['English', 'Japanese', 'Korean',
                                                                                       'French', 'German', 'Spanish',
                                                                                       'Russian'], width=10)
        self.lanCombobox.set("%s" % self.data["language"])
        self.lanCombobox.place(x=100, y=45)
        self.lanCombobox.bind("<<ComboboxSelected>>", self.langSet)
        self.cudaCheck = ttk.Checkbutton(self.button_frame_2, variable=self.cudaCheckVar, command=self.cuda_enabled)
        self.cudaCheck.place(x=13, y=75)
        self.cudaCheck["state"] = "enabled" if CudaCheck() else "disabled"
        self.insButton = ttk.Button(self.button_frame_2, image=self.imageLoader.get_image("help_image"),
                                    command=self.CUDAins, style='ins.TButton')
        self.insButton.place(x=130, y=75)
        verifyInt = (self.register(validateInt), '%P')
        self.threadsEntry = ttk.Entry(self.button_frame_2, state='readonly', width=3, validate='key',
                                      validatecommand=verifyInt, textvariable=self.threadNum)
        self.threadsEntry.place(x=100, y=106)
        self.threadSetButton = ttk.Button(self.button_frame_2, image=self.imageLoader.get_image('thread_setting_image'),
                                          command=self.paraEntSet, style='ths.TButton')

        self.threadSetButton.place(x=135, y=104)
        self.cancelButton = ttk.Button(self.button_frame_2, image=self.imageLoader.
                                       get_image('thread_setting_close_image'), command=self.paraCancel,
                                       style='ths.TButton')
        self.source_textbox = tk.Text(self.text_frame, width=43, height=8)
        self.source_textbox.place(x=17, y=8)
        self.post_textbox = tk.Text(self.text_frame, width=43, height=8)
        self.post_textbox.place(x=385, y=8)
        self.api_set_button = ttk.Button(self.button_frame_2, image=self.imageLoader.get_image('thread_setting_image'),
                                         style='ths.TButton', command=self.apiSet)
        self.api_set_button.place(x=135, y=135)
        self.api_select_combobox = ttk.Combobox(self.button_frame_2, state='readonly', values=['Baidu', 'Tencent'],
                                                width=8)
        self.api_select_combobox.set("%s" % Global.api_co)

        self.api_select_combobox.bind("<<ComboboxSelected>>", self.api_select)
        self.cancelButton2 = ttk.Button(self.button_frame_2,
                                        image=self.imageLoader.get_image('thread_setting_close_image'),
                                        command=self.apiSetCancel, style='ths.TButton')

        self.api_uuid_entry = tk.Entry(self.api_frame, width=25, textvariable=self.uuid)
        self.api_uuid_entry.place(relx=0.3, rely=0.05)
        self.api_key_entry = tk.Entry(self.api_frame, width=25, textvariable=self.key, show="*")
        self.api_key_entry.place(relx=0.3, rely=0.5)
        self.translateButton = tk.Button(self.text_frame, image=self.imageLoader.get_image("arrow-right_image"),
                                         command=self.translate_byHand, borderwidth=0, bg="#e6e6e6")
        self.translateButton.place(relx=0.475, rely=0.40)
        self.clearButton = ttk.Button(self.text_frame, image=self.imageLoader.get_image('thread_setting_close_image'),
                                      command=self.clearText, style='ths.TButton')
        self.clearButton.place(relx=0.931, rely=0.09)
        self.copyButton = ttk.Button(self.source_textbox, command=self.copySource,
                                     image=self.imageLoader.get_image('copy_image'), style='ins.TButton')
        self.copyButton.place(relx=0.91, rely=0)

    def textView(self):  # 布置文本
        self.tips = self.top_canvas.create_text(100, 30, text="阿巴阿巴...", font=("微软雅黑", 20, "bold"), fill="red")
        tk.Label(self.button_frame_1, text="当前识别范围:", bg="#00a3cc").place(x=13, y=11)
        tk.Label(self.button_frame_2, text="设置识别热键:", bg="#39ac39").place(x=13, y=11)
        tk.Label(self.button_frame_2, text="启用", bg="#39ac39").place(x=220, y=10)
        tk.Label(self.button_frame_2, text="设置识别语言:", bg="#39ac39").place(x=13, y=45)
        tk.Label(self.button_frame_2, text="启用CUDA加速", bg="#39ac39").place(x=30, y=75)
        tk.Label(self.button_frame_2, text="多线程处理：", bg="#39ac39").place(x=13, y=106)
        setTip1 = Tooltip(self.threadsEntry, "创建多线程并行处理文本，合理设置线程数可以加快识别速度")
        self.threadsEntry.bind("<Enter>", lambda event: setTip1.showtip())
        self.threadsEntry.bind("<Leave>", lambda event: setTip1.hidetip())
        tk.Label(self.button_frame_2, text="翻译接口设置", bg="#39ac39").place(x=13, y=135)
        tk.Label(self.api_frame, text="UUID:").place(relx=0, rely=0)
        tk.Label(self.api_frame, text="Key:").place(relx=0, rely=0.5)

    def areaSetting(self):  # 创建翻译区域设置蒙版
        self.area_setButton["state"] = "disabled"
        win = tk.Toplevel(self)
        win.wm_attributes('-fullscreen', True, '-topmost', True, '-transparentcolor', "#000000")  # 所有白色会被替换为透明像素
        win.config(bg="#000001")
        drawCanvas = tk.Canvas(win, width=self.screenWidth, height=self.screenHeight, bg="#000000")
        win.overrideredirect(True)

        def update_rectangle(value):
            drawCanvas.coords(rectangle, xScale.get(), yScale.get(),
                              xScale.get() + wScale.get(), yScale.get() + hScale.get())

        def saveCord():
            x1, y1, x2, y2 = drawCanvas.coords(rectangle)
            self.data["area"]["x"] = x1
            self.data["area"]["y"] = y1
            self.data["area"]["width"] = x2 - x1
            self.data["area"]["height"] = y2 - y1
            save_settings(Global.data_path, self.data)
            public.update_global()
            self.update_key_handle()
            self.top_canvas.itemconfig(self.tips, text="定义矩形已成功保存！", font=("微软雅黑", 16, "bold"))
            self.top_canvas.coords(self.tips, 400, 30)
            self.area_setButton["state"] = "enabled"
            win.destroy()

        useLabel = tk.Label(win, text="通过下方滑块调节矩形，它将作为翻译识别的区域\n长按滑块可微调",
                            font=("微软雅黑", 12, "bold"), fg="red", bg="#000000", anchor="center")
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
        label1 = tk.Label(win, text="矩形宽度", font=("微软雅黑", 12, "bold"), fg="red", bg="#000000")
        label2 = tk.Label(win, text="矩形高度", font=("微软雅黑", 12, "bold"), fg="red", bg="#000000")
        label3 = tk.Label(win, text="矩形X轴", font=("微软雅黑", 12, "bold"), fg="red", bg="#000000")
        label4 = tk.Label(win, text="矩形Y轴", font=("微软雅黑", 12, "bold"), fg="red", bg="#000000")

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

    def setHotkey(self):
        self.hotkey_setting_mode = not self.hotkey_setting_mode
        if self.hotkey_setting_mode:
            if self.key_handle:
                keyboard.remove_hotkey(self.key_handle)
            '''
            上一句只是断开了热键连接，实际上self.key_handle还在
            会导致update_key_handle中keyboard.remove_hotkey(self.key_handle)报错，因为这里已经移除了热键，所以赋值为None
            '''
            self.key_handle = None
            self.key_setButton.config(text='退出设置模式')
            self.top_canvas.itemconfig(self.tips, text="在英文输入法下按下任意键\n%12s即可设置完成" % '', font=("微软雅黑", 16, "bold"))
            self.top_canvas.coords(self.tips, 400, 30)
        else:
            self.update_key_handle()
            self.key_setButton.config(text='%s' % Global.hotKey)
            self.top_canvas.itemconfig(self.tips, text="已退出热键设置", font=("微软雅黑", 16, "bold"))
            self.top_canvas.coords(self.tips, 400, 30)

    def handle_key_event(self, event):
        if self.hotkey_setting_mode:
            hotKey = event.keysym
            self.data["hotKey"] = hotKey
            save_settings(Global.data_path, self.data)
            public.update_global()
            self.setHotkey()
            self.top_canvas.itemconfig(self.tips, text="已设置热键为%s" % hotKey, font=("微软雅黑", 16, "bold"))
            self.top_canvas.coords(self.tips, 400, 30)

    def hotkey_enabled(self):
        if self.hotkeyCheckVar.get() == 1:
            self.top_canvas.itemconfig(self.tips, text="热键已启用", font=("微软雅黑", 16, "bold"))
            self.top_canvas.coords(self.tips, 400, 30)
            self.data["hotkey_use"] = True
            save_settings(Global.data_path, self.data)
            public.update_global()
            self.update_key_handle()
        else:
            if self.key_handle:
                keyboard.remove_hotkey(self.key_handle)
                self.key_handle = None  # remove后变成<function add_hotkey.<locals>.remove_ 是真的坑啊，不能直接None吗
            self.top_canvas.itemconfig(self.tips, text="热键已停用", font=("微软雅黑", 16, "bold"))
            self.top_canvas.coords(self.tips, 400, 30)
            self.data["hotkey_use"] = False
            public.update_global()
            save_settings(Global.data_path, self.data)

    def cuda_enabled(self):
        if self.cudaCheckVar.get() == 1:
            Global.haveCUDA = True
            self.update_key_handle()
            self.data["User"]["CUDA"] = True
            save_settings(Global.data_path, self.data)
            self.top_canvas.itemconfig(self.tips, text="CUDA加速已启用", font=("微软雅黑", 16, "bold"))
            self.top_canvas.coords(self.tips, 400, 30)
        else:
            Global.haveCUDA = False
            self.update_key_handle()
            self.data["User"]["CUDA"] = False
            save_settings(Global.data_path, self.data)
            self.top_canvas.itemconfig(self.tips, text="CUDA加速已关闭", font=("微软雅黑", 16, "bold"))
            self.top_canvas.coords(self.tips, 400, 30)

    def langSet(self, event):
        self.data["language"] = self.lanCombobox.get()
        save_settings(Global.data_path, self.data)
        public.update_global()
        self.update_key_handle()
        self.top_canvas.itemconfig(self.tips, text="当前识别语言为%s" % self.data["language"], font=("微软雅黑", 16, "bold"))
        self.top_canvas.coords(self.tips, 400, 30)

    def CUDAins(self):
        if messagebox.askokcancel("CUDA说明", "CUDA是一种NVIDIA显卡独有的用于并行计算的平行计算架构，在本功能中将用于深度学习OCR加速计算，可以极大的提升识别速度。"
                                            "若需要，可按确定获取CUDA安装教程链接。"):
            self.clipboard_clear()
            self.clipboard_append("https://blog.csdn.net/HuangZT521/article/details/108545818")
            self.top_canvas.itemconfig(self.tips, text="链接已复制到粘贴板", font=("微软雅黑", 16, "bold"))
            self.top_canvas.coords(self.tips, 400, 30)

    def paraEntSet(self):
        self.thread_setting_mode = not self.thread_setting_mode
        if self.thread_setting_mode:
            self.threadSetButton.config(image=self.imageLoader.get_image('thread_setting_tick_image'))
            self.cancelButton.place(x=165, y=104)
            self.threadsEntry.configure(state='normal')
        else:
            self.threadSetButton.config(image=self.imageLoader.get_image('thread_setting_image'))
            self.threadsEntry.configure(state='readonly')
            self.cancelButton.place_forget()
            self.data["batch_size"] = 1 if self.threadNum.get() == '' or self.threadNum.get() == str(
                0) else int(self.threadNum.get())
            save_settings(Global.data_path, self.data)
            public.update_global()
            self.update_key_handle()
            self.threadNum.set(Global.batchSize)

    def paraCancel(self):
        self.threadSetButton.config(image=self.imageLoader.get_image('thread_setting_image'))
        self.thread_setting_mode = False
        self.threadsEntry.configure(state='readonly')
        self.cancelButton.place_forget()
        self.threadNum.set(Global.batchSize)

    def api_accountWrite(self):
        Global.uuid = self.api_uuid_entry.get() or ""
        Global.key = self.api_key_entry.get() or ""
        if Global.api_co == "Tencent":
            self.data["tencentAPI"]["secretID"] = Global.uuid
            self.data["tencentAPI"]["secretKey"] = Global.key
        elif Global.api_co == "Baidu":
            self.data["baiduAPI"]["secretID"] = Global.uuid
            self.data["baiduAPI"]["secretKey"] = Global.key
        else:
            pass
        save_settings(Global.data_path, self.data)

    def api_accountRead(self):
        uuid,key = public.secret_load()
        self.api_uuid_entry.delete(0, tk.END)
        self.api_key_entry.delete(0, tk.END)
        self.api_uuid_entry.insert(0, uuid)
        self.api_key_entry.insert(0, key)

    def apiSet(self):
        self.api_setting_mode = not self.api_setting_mode
        if self.api_setting_mode:
            self.api_set_button.config(image=self.imageLoader.get_image('thread_setting_tick_image'))
            self.cancelButton2.place(x=165, y=135)
            self.api_frame.place(x=30, y=165)
            self.api_select_combobox.place(x=195, y=135)
        else:
            self.api_set_button.config(image=self.imageLoader.get_image('thread_setting_image'))
            self.cancelButton2.place_forget()
            self.api_accountWrite()
            self.update_key_handle()
            self.api_frame.place_forget()
            self.api_select_combobox.place_forget()

    def apiSetCancel(self):
        self.api_set_button.config(image=self.imageLoader.get_image('thread_setting_image'))
        self.api_setting_mode = False
        self.api_uuid_entry.delete(0, tk.END)
        self.api_key_entry.delete(0, tk.END)
        self.api_uuid_entry.insert(0, Global.uuid)
        self.api_key_entry.insert(0, Global.key)
        self.api_frame.place_forget()
        self.cancelButton2.place_forget()
        self.api_select_combobox.place_forget()

    def api_select(self, event):
        self.data["API_CO"] = self.api_select_combobox.get()
        save_settings(Global.data_path, self.data)
        public.update_global()
        self.api_accountRead()
        self.update_key_handle()
        self.top_canvas.itemconfig(self.tips, text="已切换为%sAPI" % self.api_select_combobox.get(),
                                   font=("微软雅黑", 16, "bold"))
        self.top_canvas.coords(self.tips, 400, 30)

    def update_key_handle(self):
        if self.key_handle:
            keyboard.remove_hotkey(self.key_handle)
            self.key_handle = None
        if Global.hotkey_use:
            self.key_handle = keyboard.add_hotkey('%s' % Global.hotKey if Global.hotKey not in Global.hotkey_map else
                                                  Global.hotkey_map[Global.hotKey], self.combined_function,
                                                  args=(Global.rectX, Global.rectY, Global.rectX + Global.rectW,
                                                        Global.rectY + Global.rectH, Global.haveCUDA, Global.language,
                                                        Global.batchSize))

    def combined_function(self, x1, y1, x2, y2, cuda, lan, batch):
        coordsList = []
        drawDict = {}
        result_text = aiOCR(x1, y1, x2, y2, cuda, lan, batch)  # 详细的识别列表
        post_text = ''
        source_text = ''
        uuid, key = public.secret_load()
        for i, item in enumerate(result_text):  # 列表处理
            coords, text, conf = item
            coords = [[int(x) for x in coord] for coord in coords]  # 将每个坐标点都转为整数
            coordsList.append(coords[1])  # 收集绘制坐标
            source_text += text + '\n'  # 整理源文本
        if Global.api_co == "Baidu":
            resultDict = baidu_parse(uuid, key, Global.baidu_map[lan[0]], source_text)  # 获取译文字典
            resultList = resultDict["trans_result"]  # 获取译文
            for n in range(len(resultList)):
                drawDict[n] = resultList[n]["dst"]
                post_text += resultList[n]["dst"] + '\n'  # 整理译文
        else:
            post_text = tencent_parse(uuid, key, Global.tencent_map[lan[0]], source_text)
            resultList = post_text.split("\n")
            for m in range(len(resultList)):
                drawDict[m] = resultList[m]

        self.source_textbox.delete("1.0", tk.END)
        self.source_textbox.insert(tk.END, source_text)
        self.post_textbox.delete("1.0", tk.END)
        self.post_textbox.insert(tk.END, post_text)

        def destroy_drawIn(windows):
            windows.destroy()

        def draw(x, y, coords_list, draw_dict):
            drawIn = tk.Toplevel(self)
            drawIn.wm_attributes('-fullscreen', True, '-topmost', True, '-transparentcolor', "#000000")
            drawIn.config(bg="#000000")
            translationCanvas = tk.Canvas(drawIn, width=self.screenWidth, height=self.screenHeight, bg="#000000")
            drawIn.overrideredirect(True)
            for transNum in range(len(coords_list)):
                translationCanvas.create_text(x + coords_list[transNum][0], y + coords_list[transNum][1],
                                              text=draw_dict[transNum], font=("微软雅黑", 12, "bold"), fill="red")
            translationCanvas.pack(fill='both', expand=True)
            drawIn.after(7000, destroy_drawIn, drawIn)

        if "无法解决请联系作者" in post_text:
            pass
        else:
            draw(x1, y1, coordsList, drawDict)

    def translate_byHand(self):
        source_text = self.source_textbox.get("1.0", tk.END)
        if source_text.strip() == '':
            self.post_textbox.delete("1.0", tk.END)
            self.post_textbox.insert(tk.END, "None")
        else:
            uuid, key = public.secret_load()
            if Global.api_co == "百度翻译":
                post_text = baidu_parse(uuid, key, Global.baidu_map[Global.language[0]], source_text)
                resultList = post_text["trans_result"]
                post_text = '\n'.join([d['dst'] for d in resultList])
            else:
                post_text = tencent_parse(uuid, key, Global.tencent_map[Global.language[0]], source_text)
            self.post_textbox.delete("1.0", tk.END)
            self.post_textbox.insert(tk.END, post_text)

    def clearText(self):
        self.source_textbox.delete("1.0", tk.END)
        self.post_textbox.delete("1.0", tk.END)

    def copySource(self):
        content = self.source_textbox.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(content)
        self.top_canvas.itemconfig(self.tips, text="复制成功！", font=("微软雅黑", 16, "bold"))
        self.top_canvas.coords(self.tips, 400, 30)


# noinspection PyGlobalUndefined
def update_config():
    pass
