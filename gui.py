from tkinter import *
from image_lib import *
import easygui
from PIL import ImageTk, Image

QUANTIZATION_MSG = "Choose quantization range"
SAVE_IMAGE_MSG = "Do you want to save this image?"
SAVE_IMAGE_MSG2 = "Image saved to the current directory!"
WARNING_MSG = "Notice that pictures may look corrupted due to Tkinter's interface." \
              "It is therefore recommended to save the final image to your local drive" \
              "in order to get the best quality image."
WARNING_MSG2 = "Bad Input!"


class Gui:
    def __init__(self, parent):
        self.parent = parent
        self.im = None
        self.canvas = None
        self.show_again = True
        self.menu_image = ImageTk.PhotoImage(Image.open('im1.jfif'))
    
    def save_image_message(self, im):
        if easygui.buttonbox(SAVE_IMAGE_MSG, "Save image", choices=['Yes', 'No']) == 'Yes':
            plt.imsave('./new_im.png', im)
            easygui.buttonbox(SAVE_IMAGE_MSG2, 'Attention', choices=['ok'])
            self.back_to_menu()
        
    def choose_quant_range(self, f, im):
        n_quant = easygui.buttonbox(QUANTIZATION_MSG, 'Attention', choices=list(map(str, range(2, 13))))
        return f(im, int(n_quant)) if n_quant else None
        
    def back_to_menu(self):
        """
        destroy current window and open a new windows with the main menu
        """
        root = Tk()
        self.menu_image = ImageTk.PhotoImage(Image.open('im1.jfif'))
        self.parent.destroy()
        self.parent = root
        self.main_menu()
    
    def show_image(self, f, rep=0):
        """
        show the user's image after applying the function f on it
        """
        image_path = easygui.fileopenbox()
        if not image_path:
            return
        im = read_image(image_path, rep)
        im_orig = f(im)
        if im_orig is None:
            easygui.buttonbox(WARNING_MSG2, 'Notice', choices=['ok'])
            return
        im_as_uint8 = im_to_uint8(im_orig)
        
        if self.show_again:
            ans = easygui.buttonbox(WARNING_MSG, 'Notice', choices=['ok', 'Do not Show Again'])
            if ans == 'Do not Show Again':
                self.show_again = False

        root = Tk()
        self.im = ImageTk.PhotoImage(Image.fromarray(im_as_uint8).resize(size=(500, 500)), master=root)
        self.canvas = Canvas(root, width=500, height=500)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=NW, image=self.im)
        save_im = Button(root, bg='lavender', fg='black',
                         font=("Helvetica", 15),
                         text="save image",
                         command=lambda: self.save_image_message(im_orig))
        menu = Button(root, bg='lavender', fg='black',
                      font=("Helvetica", 15),
                      text="main menu",
                      command=lambda: self.back_to_menu())
        self.canvas.create_window(10, 10, anchor=NW, window=save_im)
        self.canvas.create_window(10, 100, anchor=SW, window=menu)
        
        self.parent.destroy()
        self.parent = root
    
    def main_menu(self):
        """
        create the main menu window
        """
        self.parent.geometry("500x500")
        self.parent.columnconfigure((0, 1, 2), weight=1)
        self.parent.rowconfigure(list(range(30)), weight=1)
        label_text = Label(self.parent, text="Image Manipulation", bg="alice blue",
                           fg="Black", font=("Courier", 30))
        label_text.grid(row=0, column=1)
        image_label = Label(self.parent, image=self.menu_image)
        image_label.grid(row=1, column=1)
        self.parent.configure(background='alice blue')
        
        bw_image = Button(self.parent, bg='lavender', fg='black',
                          font=("Helvetica", 15),
                          text="Black and White",
                          command=lambda: self.show_image(lambda im: im, rep=1), width=30)
        quantization = Button(self.parent, bg='lavender', fg='black',
                              font=("Helvetica", 15),
                              text="Quantization",
                              command=lambda: self.show_image(lambda im: self.choose_quant_range(quantize, im)))
        contrast_adj = Button(self.parent, bg='lavender', fg='black',
                              font=("Helvetica", 15),
                              text="Contrast Adjustment",
                              command=lambda: self.show_image(lambda im: histogram_equalize(im)))
        im_magnitude = Button(self.parent, bg='lavender', fg='black',
                              font=("Helvetica", 15),
                              text="Sketch",
                              command=lambda: self.show_image(lambda im: 1 - conv_2d(im), 1))
        
        bw_image.grid(row=2, column=1, pady=5, sticky='NSEW')
        quantization.grid(row=3, column=1, pady=5, sticky='NSEW')
        contrast_adj.grid(row=4, column=1, pady=5, sticky='NSEW')
        im_magnitude.grid(row=5, column=1, pady=5, sticky='NSEW')

