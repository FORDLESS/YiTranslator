import win32api
import win32con

def display_character(char, x, y, font_size=20, font_name='Arial', font_weight=win32con.FW_NORMAL):
    hdc = win32gui.GetDC(0)
    font = win32gui.LOGFONT()
    font.lfHeight = font_size
    font.lfWeight = font_weight
    font.lfFaceName = font_name
    hfont = win32gui.CreateFontIndirect(font)
    win32gui.SelectObject(hdc, hfont)
    win32gui.SetTextColor(hdc, win32api.RGB(0, 0, 0))  # 设置字符颜色为黑色
    win32gui.SetBkMode(hdc, win32con.TRANSPARENT)  # 设置背景透明

    win32gui.TextOut(hdc, x, y, char, len(char))

    win32gui.DeleteObject(hfont)
    win32gui.ReleaseDC(0, hdc)

# 示例：在屏幕上显示字符"Hello"
display_character("Hello", 100, 100)

# 示例：在屏幕上显示字符"World"，字体大小为30
display_character("World", 200, 200, font_size=30)
