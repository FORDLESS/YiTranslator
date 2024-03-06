from Global import global_init
from gui.main_interface import MainGUI


def start():
    try:
        global_init()
        root = MainGUI()
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    start()
