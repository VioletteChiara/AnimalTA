from tkinter import *
import webbrowser

class Information_panel(Frame):
    def __init__(self, parent, current_version, new_update=None, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.grid(sticky="nsew")

        Grid.columnconfigure(parent, 0, weight=1)
        Grid.rowconfigure(parent, 0, weight=1)

        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=100)
        Grid.rowconfigure(self, 3, weight=1)
        Grid.rowconfigure(self, 4, weight=1)
        Grid.rowconfigure(self, 5, weight=1)

        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=100)

        #Short summary about current version, how to cite and how to find guidelines.
        Crow=0
        if new_update!=None:
            Lab_update=Label(self, text="New update available: " + new_update, font=("Arial", "20", "bold"), fg="red")
            Lab_update.grid(row=Crow, column=0,columnspan=2, sticky="nsew")
            Crow+=1

            link = Label(self, text="Download at: http://vchiara.eu/index.php/animalta", fg="#b448cd", cursor="hand2")
            link.grid(row=Crow, column=0, columnspan=2, sticky="nsew")
            link.bind("<Button-1>", self.send_link)
            Crow += 1
            # Space
            Crow += 1
            #Space
            Crow += 1

            Lab_version=Label(self, text="AnimalTA. current version: " + current_version, font=("Arial", "14", "bold"))
            Lab_version.grid(row=Crow, column=1,columnspan=2, sticky="nsw")
            Crow += 1

        else:
            Lab_version=Label(self, text="AnimalTA. " + current_version, font=("Arial", "14", "bold"))
            Lab_version.grid(row=Crow, column=0,columnspan=2, sticky="nsw")
            Crow += 1

        Lab_cite=Label(self, text="How to cite:")
        Lab_cite.grid(row=Crow, column=0,columnspan=2, sticky="nsw")
        Crow += 1

        Citation= Text(self, height=5, width=75, wrap=WORD)
        Citation.grid(row=Crow, column=0,columnspan=2, sticky="nswe")
        Citation.insert("1.0", "Chiara, V., & Kim, S.-Y. (2023). AnimalTA: A highly flexible and easy-to-use program for tracking and analysing animal movement in different environments. Methods in Ecology and Evolution, 14, 1699– 1707. https://doi.org/10.1111/2041-210X.14115")
        Citation.configure(state="disabled")
        Crow += 1

        #Space
        Crow += 1

        Lab_contact=Label(self, text="Contact:")
        Lab_contact.grid(row=Crow, column=0, sticky="nsw")
        Crow += 1

        mail= Text(self, height=1, width=30)
        mail.insert("1.0", "contact.AnimalTA@vchiara.eu")
        mail.configure(state="disabled")
        mail.grid(row=Crow, column=1, sticky="nsw")
        Crow += 1

        #Space
        Crow += 1

        Lab_Help=Label(self, text="Need help? Go check the guidelines or the video tutorials:")
        Lab_Help.grid(row=Crow, column=0,columnspan=2, sticky="nsew")
        Crow += 1

        link = Label(self, text="http://vchiara.eu/index.php/animalta", fg="#b448cd", cursor="hand2")
        link.grid(row=Crow, column=0,columnspan=2, sticky="nsew")
        link.bind("<Button-1>", self.send_link)
        Crow += 1

        for irow in range(Crow+1):
            self.rowconfigure(irow, minsize=30)

        self.stay_on_top()

    def stay_on_top(self):
        # We want this window to be always on top of the others
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)

    def send_link(self, event):
        webbrowser.open_new_tab("http://vchiara.eu/index.php/animalta")
