import logging
import threading
import time
from ctypes import wintypes
from tkinter import messagebox
from queue import Queue
import Global
import win32con
import ctypes


class HotkeyListener(threading.Thread):
    def __init__(self, root):
        threading.Thread.__init__(self)
        self.root = root
        self.user32 = ctypes.windll.user32
        self.hkey_dict = {}  # alt-->0x0001,ctrl-->0x0002,shift-->0x0004,win-->0x0008
        self.hkey_queue = Queue()

    def run(self):
        try:
            while True:
                if not self.hkey_queue.empty():
                    hkey = self.hkey_queue.get()
                    hkey()
                msg = ctypes.wintypes.MSG()
                if not Global.hotkey_use:  # 处理热键关闭时接收到的消息-->直接移除，否则会堆积至打开热键时继续执行
                    self.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, win32con.PM_REMOVE)
                if self.user32.PeekMessageA(ctypes.byref(msg), None, 0, 0, win32con.PM_REMOVE):
                    if msg.message == win32con.WM_HOTKEY:  # 是否热键消息
                        if msg.wParam in self.hkey_dict:  # id是否在字典中
                            flag()
                            self.root.after(0, self.hkey_dict[msg.wParam]["func"])

                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageA(ctypes.byref(msg))
                time.sleep(0.01)  # 降低CPU占用

        finally:
            for ID in self.hkey_dict:
                self.user32.UnregisterHotKey(None, ID)

    def register_hotkey(self, ID, modifiers, vk):
        try:
            self.user32.RegisterHotKey(None, ID, modifiers, vk)
        except Exception as error:
            messagebox.showerror("热键注册失败", "Failed to register hotkey！\n请将运行日志发送给作者！")
            logging.error(f"打开时出现未知错误: {error}")

    def unregister_hotkey(self, ID):  # 运行时解绑必须推入队列，不然会因为占用问题解绑失败
        self.hkey_queue.put(lambda: self.user32.UnregisterHotKey(None, ID))
        '''code = self.user32.UnregisterHotKey(None, ID)
        if code == 0:
            error_code = win32api.GetLastError()
            # 解绑失败，根据错误代码进行相应处理
            print("解绑失败，错误代码:", error_code)
        else:
            print("解绑成功")'''

    def add_hkey(self, key, func, flag=True):
        pop_id = None
        for hotkey_id, hotkey_info in self.hkey_dict.items():  # 先根据函数判断热键字典中是否已经存在要注册的热键功能
            if hotkey_info["func"] == func:
                self.unregister_hotkey(hotkey_id)  # 存在就需要先解绑之前的按键
                pop_id = hotkey_id  # 记录下需要从字典删除的热键id
        if not pop_id:  # 初始化注册不会重复,生成新id
            pop_id = self.generate_id()
        info = dict(key=key, func=func, flag=flag)
        self.hkey_dict[pop_id] = info
        self.hkey_queue.put(lambda: self.register_hotkey(pop_id, key[0], key[1]))

    def generate_id(self):
        return len(self.hkey_dict) + 1

    def disable_global_hotkey(self):
        for ID in self.hkey_dict.keys():
            self.unregister_hotkey(ID)


def flag():
    Global.b_flag = True


def main():
    pass


if __name__ == '__main__':
    main()
