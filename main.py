from gui import *

if __name__ == '__main__':
    root = Tk()
    gui = Gui(root)
    gui.main_menu()
    mainloop()
    # root = Tk()
    # canvas = Canvas(root, width=1900, height=800)
    # canvas.pack()
    # img = ImageTk.PhotoImage(Image.open("./im.jpeg"))
    # canvas.create_image(20, 20, anchor=NW, image=img)
    # mainloop()
