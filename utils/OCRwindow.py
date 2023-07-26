import tkinter as tk
from tkinter import ttk
import Global
from utils import public


class DraggableWindow:
    def __init__(self, parent):
        alpha = Global.set_config["area"]["transparency"]
        bg_color = Global.set_config["area"]["bg_color"]
        bd_width = Global.set_config["area"]["bdwidth"]
        bd_color = Global.set_config["area"]["bd_color"]
        self.root = tk.Toplevel(parent)
        self.root.geometry(f"{Global.rectW}x{Global.rectH}+{Global.rectX}+{Global.rectY}")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True, "-alpha", alpha)
        if Global.set_config["area"]["transparent"]:
            self.root.wm_attributes("-transparentcolor", bg_color)
        self.root.config(bg='#f0f0f0')

        self.frame = tk.Frame(self.root, bg=bg_color, highlightthickness=bd_width, highlightbackground=bd_color)
        self.frame.pack(expand=True, fill="both")

        self.resize_handle = ttk.Sizegrip(self.frame)
        self.resize_handle.place(relx=1.0, rely=1.0, anchor='se')

        self.frame.bind("<ButtonPress-1>", self.start_drag)
        self.frame.bind("<B1-Motion>", self.drag)
        self.frame.bind("<ButtonRelease-1>", self.end_drag)
        self.resize_handle.bind("<ButtonRelease-1>", self.end_drag)

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def drag(self, event):
        x = self.root.winfo_x() + (event.x - self.x)
        y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{x}+{y}")

    def end_drag(self, event):
        x, y, width, height = self.get_window_geometry()
        Global.set_config["area"].update({"x": x, "y": y, "width": width, "height": height})
        Global.save_settings(Global.setting_path)
        public.update_global()

    def get_window_geometry(self):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        return x, y, width, height

    def run(self):
        self.root.mainloop()

    def destroy(self):
        self.root.destroy()


if __name__ == '__main__':
    area = DraggableWindow(tk.Tk())
    area.run()
