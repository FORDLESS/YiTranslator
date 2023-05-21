import tkinter as tk

import Global
import public
from Global import read_settings, save_settings
from public import ImageLoader, MyButton, SwitchButton, BreathingLabel


# noinspection PyAttributeOutsideInit
class SetGUI(tk.Toplevel):
    def __init__(self):
        super().__init__()

        self.title("设置")
        # self.resizable(False, False)
        self.wm_attributes('-alpha', 0.95, '-transparentcolor', "#666666")
        self.config(bg="#cccccc")
        self.screenWidth = self.winfo_screenwidth()
        self.screenHeight = self.winfo_screenheight()
        self.geometry("768x432+%d+%d" % (self.screenWidth / 3, self.screenHeight / 4))
        self.overrideredirect(False)

        self.imageLoader = ImageLoader()
        self.imageLoader.load_image("icon", "icon.png")
        self.iconphoto(False, self.imageLoader.get_image("icon"))

        self.current_page = None

        self.image_load()
        self.frame_init()
        self.interface_init()
        self.horizontal_set()
        self.textView()
        self.bind_event()

    def frame_init(self):
        # self.operate_frame = tk.Frame(self, height=402, width=648, bg="black")
        # self.operate_frame.place(x=120, y=30)
        self.bg_label = tk.Label(self, image=self.imageLoader.get_image("bg"), compound="center", bd=0)
        self.bg_label.pack(fill="both", expand=True)
        self.vertical_frame = tk.Frame(self.bg_label, height=432, width=120, bg="#666666")
        self.vertical_frame.pack(side="left", fill="both")
        self.horizontal_frame = tk.Frame(self.bg_label, height=40, width=648, bg="#666666")
        self.horizontal_frame.pack(side="top", fill="both")

    def interface_init(self):
        self.line_page_button = SwitchButton(self.vertical_frame, bg="white", switch=False,
                                             marshalling="vertical", command=self.line_page_show, relief="sunken",
                                             activebackground="white", borderwidth=0, highlightthickness=0,
                                             off_image=self.imageLoader.get_image("line_normal"),
                                             on_image=self.imageLoader.get_image("line_press"))
        self.line_page_button.pack(side="top", fill="both")
        self.mode_page_button = SwitchButton(self.vertical_frame, bg="white", switch=False,
                                             marshalling="vertical", relief="sunken", activebackground="white",
                                             command=self.mode_page_show, borderwidth=0, highlightthickness=0,
                                             off_image=self.imageLoader.get_image("mode_normal"),
                                             on_image=self.imageLoader.get_image("mode_press"))
        self.mode_page_button.pack(side="top", fill="both")
        self.function_page_button = SwitchButton(self.vertical_frame, bg="white", switch=False,
                                                 marshalling="vertical", activebackground="white", highlightthickness=0,
                                                 command=self.function_page_show, borderwidth=0, relief="sunken",
                                                 off_image=self.imageLoader.get_image("function_normal"),
                                                 on_image=self.imageLoader.get_image("function_press"))
        self.function_page_button.pack(side="top", fill="both")
        self.personalise_page_button = SwitchButton(self.vertical_frame, bg="white", switch=False, relief="sunken",
                                                    command=self.personalise_page_show, activebackground="white",
                                                    off_image=self.imageLoader.get_image("personalise_normal"),
                                                    on_image=self.imageLoader.get_image("personalise_press"),
                                                    highlightthickness=0, borderwidth=0, marshalling="vertical")
        self.personalise_page_button.pack(side="top", fill="both")
        self.about_page_button = SwitchButton(self.vertical_frame, bg="white", switch=False,
                                              marshalling="vertical", relief="sunken", activebackground="white",
                                              command=self.about_page_show, borderwidth=0, highlightthickness=0,
                                              off_image=self.imageLoader.get_image("about_normal"),
                                              on_image=self.imageLoader.get_image("about_press"))
        self.about_page_button.pack(side="top", fill="both")
        self.block_page_button = SwitchButton(self.vertical_frame, bg="white", relief="sunken", highlightthickness=0,
                                              activebackground="white", borderwidth=0,
                                              off_image=self.imageLoader.get_image("block"))
        self.block_page_button.pack(side="top", fill="both", expand=True)  # 竖排空白填充
        self.block_canvas = tk.Canvas(self.horizontal_frame, height=40, width=648)  # 顶部剩余空间填充横幅
        self.block_canvas.pack(side="top", fill="both")

    def textView(self):
        pass

    def bind_event(self):
        pass

    def line_page_show(self):
        if self.current_page != "line":
            self.current_page = "line"
            self.personal_page_button.place(x=-1, y=0)
            self.public_page_button.place(x=100, y=0)
            self.patch_canvas.place(x=200, y=0, relwidth=1, relheight=1)
            self.hide_all_buttons_except("line")

    def mode_page_show(self):
        if self.current_page != "mode":
            self.current_page = "mode"
            self.input_page_button.place(x=-1, y=0)
            self.OCR_page_button.place(x=100, y=0)
            self.patch_canvas.place(x=200, y=0, relwidth=1, relheight=1)
            self.hide_all_buttons_except("mode")

    def function_page_show(self):
        if self.current_page != "function":
            self.current_page = "function"
            self.language_page_button.place(x=-1, y=0)
            self.hotkey_page_button.place(x=100, y=0)
            self.patch_canvas.place(x=200, y=0, relwidth=1, relheight=1)
            self.hide_all_buttons_except("function")

    def personalise_page_show(self):
        if self.current_page != "personalise":
            self.current_page = "personalise"
            self.font_page_button.place(x=-1, y=0)
            self.theme_page_button.place(x=100, y=0)
            self.other_page_button.place(x=200, y=0)
            self.patch_canvas.place(x=300, y=0, relwidth=1, relheight=1)
            self.hide_all_buttons_except("personalise")

    def about_page_show(self):
        if self.current_page != "about":
            self.current_page = "about"
            self.hide_all_buttons_except("about")

    def personal_page_show(self):
        pass

    def hide_all_buttons_except(self, page):  # 防止重复创建终极方法
        for keys in self.pages.keys():
            if keys != page:
                delete_list = self.pages[keys]
                for delete in delete_list:
                    if delete.winfo_manager() == 'place':
                        delete.place_forget()

    def test(self):
        print(self.horizontal_frame.winfo_children())

    def image_load(self):
        self.imageLoader.load_image("bg", "background1.png")
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

    def horizontal_set(self):
        # line_page_show
        self.personal_page_button = SwitchButton(self.horizontal_frame, bg="white", switch=True,
                                                 marshalling="horizontal_line", relief="sunken",
                                                 activebackground="white",
                                                 command=self.test, borderwidth=0, highlightthickness=0,
                                                 off_image=self.imageLoader.get_image("personal_normal"),
                                                 on_image=self.imageLoader.get_image("personal_press"))
        self.public_page_button = SwitchButton(self.horizontal_frame, bg="white", switch=False,
                                               marshalling="horizontal_line", relief="sunken", activebackground="white",
                                               command=self.test, borderwidth=0, highlightthickness=0,
                                               off_image=self.imageLoader.get_image("public_normal"),
                                               on_image=self.imageLoader.get_image("public_press"))
        self.patch_canvas = tk.Canvas(self.horizontal_frame)
        # mode_page_show
        self.input_page_button = SwitchButton(self.horizontal_frame, bg="white", switch=True,
                                              marshalling="horizontal_mode", relief="sunken", activebackground="white",
                                              command=self.test, borderwidth=0, highlightthickness=0,
                                              off_image=self.imageLoader.get_image("input_normal"),
                                              on_image=self.imageLoader.get_image("input_press"))
        self.OCR_page_button = SwitchButton(self.horizontal_frame, bg="white", switch=False,
                                            marshalling="horizontal_mode", relief="sunken", activebackground="white",
                                            command=self.test, borderwidth=0, highlightthickness=0,
                                            off_image=self.imageLoader.get_image("OCR_normal"),
                                            on_image=self.imageLoader.get_image("OCR_press"))
        # function_page_show
        self.language_page_button = SwitchButton(self.horizontal_frame, bg="white", activebackground="white",
                                                 marshalling="horizontal_function", relief="sunken", switch=True,
                                                 command=self.test, borderwidth=0, highlightthickness=0,
                                                 off_image=self.imageLoader.get_image("language_normal"),
                                                 on_image=self.imageLoader.get_image("language_press"))
        self.hotkey_page_button = SwitchButton(self.horizontal_frame, bg="white", activebackground="white",
                                               marshalling="horizontal_function", relief="sunken", switch=False,
                                               command=self.test, borderwidth=0, highlightthickness=0,
                                               off_image=self.imageLoader.get_image("hotkey_normal"),
                                               on_image=self.imageLoader.get_image("hotkey_press"))
        # personalise_page_show
        self.font_page_button = SwitchButton(self.horizontal_frame, bg="white", activebackground="white",
                                             marshalling="horizontal_personalise", relief="sunken", switch=True,
                                             command=self.test, borderwidth=0, highlightthickness=0,
                                             off_image=self.imageLoader.get_image("font_normal"),
                                             on_image=self.imageLoader.get_image("font_press"))
        self.theme_page_button = SwitchButton(self.horizontal_frame, bg="white", activebackground="white",
                                              marshalling="horizontal_personalise", relief="sunken", switch=False,
                                              command=self.test, borderwidth=0, highlightthickness=0,
                                              off_image=self.imageLoader.get_image("theme_normal"),
                                              on_image=self.imageLoader.get_image("theme_press"))
        self.other_page_button = SwitchButton(self.horizontal_frame, bg="white", activebackground="white",
                                              marshalling="horizontal_personalise", relief="sunken", switch=False,
                                              command=self.test, borderwidth=0, highlightthickness=0,
                                              off_image=self.imageLoader.get_image("other_normal"),
                                              on_image=self.imageLoader.get_image("other_press"))
        self.pages = {
            "patch": [self.patch_canvas],
            "line": [self.personal_page_button, self.public_page_button],
            "mode": [self.input_page_button, self.OCR_page_button],
            "function": [self.language_page_button, self.hotkey_page_button],
            "personalise": [self.font_page_button, self.theme_page_button, self.other_page_button],
            "about": []
        }


def start():
    try:
        root = SetGUI()
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    start()
