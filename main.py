"""
Image manipulation gui, allows to perform various image
transformations on an input image via a convenient Tkinter Gui
"""

from gui import *

if __name__ == '__main__':
    root = Tk()
    gui = Gui(root)
    gui.main_menu()
    mainloop()
