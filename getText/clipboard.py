import tkinter as tk


class Clipboard:
    copy_content = None

    def __init__(self, parent):
        self.root = parent
        self.on_clipboard_change()

    def on_clipboard_change(self):
        self.root.after(100, self.on_clipboard_change)
        try:
            if Clipboard.copy_content != self.root.clipboard_get():
                Clipboard.copy_content = self.root.clipboard_get()
                return Clipboard.copy_content
        except tk.TclError:
            pass

    def gettext(self):
        return self.copy_content



if __name__ == '__main__':
    ro = tk.Tk()
    cp = Clipboard(ro)
    ro.mainloop()
