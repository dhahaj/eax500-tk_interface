import tkinter as tk
import tkinter.font


class FontChooser(tk.Toplevel):
    """
    A font chooser dialog. This will create the dialog and show it.

    :param master: The root window. 
    """

    def __init__(self, master=None):
        """
        Initialize the FontChooser class. 
        """
        super().__init__(master)

        self.title("Choose a font")
        self.fonts = list(tkinter.font.families())
        self.fonts.sort()

        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=1)
        self.listbox.config(font=("Arial", 12))

        for f in self.fonts:
            self.listbox.insert(tk.END, f)

        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ok_button = tk.Button(
            button_frame, text="OK", command=self.ok, font=("Arial", 16)
        )
        ok_button.pack(side=tk.RIGHT)
        ok_button.config(width=4, height=2)

        cancel_button = tk.Button(
            button_frame, text="Cancel", command=self.cancel, font=("Arial", 16)
        )
        cancel_button.pack(side=tk.RIGHT)
        cancel_button.config(width=4, height=2)

        self.selected_font = None

    def on_select(self, event):
        index = self.listbox.curselection()[0]
        self.selected_font = self.listbox.get(index)

    def ok(self):
        self.destroy()

    def cancel(self):
        self.selected_font = None
        self.destroy()

    def get_font(self):
        return self.selected_font


# root = tk.Tk()

# font_chooser = FontChooser(root)
# root.wait_window(
#     font_chooser
# )  # this makes the parent window wait until the FontChooser window is closed

# selected_font = font_chooser.get_font()
# if selected_font:
#     print("Selected font:", selected_font)
# else:
#     print("No font selected")

# root.mainloop()
