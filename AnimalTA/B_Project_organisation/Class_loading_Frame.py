from tkinter import *
from AnimalTA.A_General_tools import UserMessages


class Loading(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bd=5)
        self.grid()

        #Import messsages
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        self.Messages = UserMessages.Mess[self.Language.get()]


        self.loading_canvas = Frame(self)
        self.loading_canvas.grid(row=4, columnspan=2)
        self.loading_state = Label(self.loading_canvas, text=self.Messages["Loading"])
        self.loading_state.grid(row=0, column=0)

        self.loading_bar = Canvas(self.loading_canvas, height=10)
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill="red")
        self.loading_bar.grid(row=0, column=1)


    def show_load(self, prop):
        #Show the progress of the conversion process
        self.loading_bar.delete('all')
        heigh=self.loading_bar.cget("height")
        self.loading_bar.create_rectangle(0, 0, 400, heigh, fill="red")
        self.loading_bar.create_rectangle(0, 0, prop*400, heigh, fill="blue")
        self.loading_bar.update()

