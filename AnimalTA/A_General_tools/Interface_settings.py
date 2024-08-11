from tkinter import *
from AnimalTA.A_General_tools import UserMessages, Diverse_functions, Color_settings, Small_info, Message_simple_question as MsgBox
import os
import pickle




def change_params(Param,new_val):
    Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
    with open(Param_file, 'rb') as fp:
        Params = pickle.load(fp)

    Params[Param]=new_val

    with open(Param_file, 'wb') as fp:
        data_to_save = Params
        pickle.dump(data_to_save, fp)


class Settings_panel(Frame):
    def __init__(self, parent, main, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.parent.iconbitmap(UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Logo.ico")))
        self.main=main
        Grid.columnconfigure(parent, 0, weight=1)
        Grid.rowconfigure(parent, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=1)
        Grid.rowconfigure(self, 3, weight=1)
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)

        self.parent.grab_set()

        self.grid(sticky="nsew")

        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        self.Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
        with open(self.Param_file, 'rb') as fp:
            self.Params = pickle.load(fp)

        self.Color_GUI=StringVar()
        self.Color_GUI.set(self.Params["Color_GUI"])

        self.Auto_update=BooleanVar()
        self.Auto_update.set(self.Params["Auto_update"])

        self.Sound_track=BooleanVar()
        self.Sound_track.set(self.Params["Sound_alert_track"])

        self.Pop_track=BooleanVar()
        self.Pop_track.set(self.Params["Pop_alert_track"])

        self.Size_img_display=IntVar()
        self.Size_img_display.set(self.Params["Size_img_display"])

        self.Back_tool=IntVar()
        self.Back_tool.set(self.Params["Back_tool"])

        self.Low_prio=BooleanVar()
        self.Low_prio.set(self.Params["Low_priority"])

        self.Kalmna_filter=BooleanVar()
        self.Kalmna_filter.set(self.Params["Use_Kalman"])

        self.Hide_columns=BooleanVar()
        self.Hide_columns.set(self.Params["Check_hide_missing"])

        self.Relative_back=BooleanVar()
        self.Relative_back.set(self.Params["Relative_background"])#0=greyscaled, 1=based on color, 3=based on hsv

        self.Keep_entrance=BooleanVar()
        self.Keep_entrance.set(self.Params["Keep_entrance"])  # 0=greyscaled, 1=based on color, 3=based on hsv

        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 0, weight=100)
        Grid.rowconfigure(self, 1, weight=1)

        #View and esthetical parameters
        list_colors=Color_settings.My_colors.list_colors
        row_colors=[list_colors["Table1"],list_colors["Table2"],list_colors["Glider_T1"],list_colors["Glider_T2"],list_colors["Fg_T1"],list_colors["Fg_T2"], list_colors["Rad_T1"], list_colors["Rad_T2"]]

        self.config(background=list_colors["Base"])

        Frame_view=Frame(self, highlightbackground=list_colors["Frame"], highlightthickness=2, borderwidth=2, background=list_colors["Table1"], relief="ridge")
        Frame_view.grid(row=0,column=0, sticky="nsew")
        Grid.columnconfigure(Frame_view, 0, weight=1)
        Grid.columnconfigure(Frame_view, 1, weight=10)

        pos=0
        Label(Frame_view, text=self.Messages["Settings0"], font=("Helvetica",15,"bold"), justify=CENTER, bg=list_colors["Title1"], fg=list_colors["Fg_Title1"]).grid(row=pos, columnspan=2, sticky="enw")
        Grid.rowconfigure(Frame_view, pos, weight=0)
        pos +=1

        Checkbutton(Frame_view, text=self.Messages["Settings5"], variable=self.Low_prio, wraplength=300, justify=LEFT, selectcolor=row_colors[pos%2+6], activeforeground=row_colors[pos%2+4], fg=row_colors[pos%2+4], activebackground=row_colors[pos%2], bg=row_colors[pos%2], anchor="w").grid(row=pos, columnspan=2, sticky="new")
        Grid.rowconfigure(Frame_view, pos, weight=1)
        pos += 1

        Checkbutton(Frame_view, text="Allow automatic update", variable=self.Auto_update, wraplength=300, justify=LEFT, selectcolor=row_colors[pos%2+6], activeforeground=row_colors[pos%2+4], fg=row_colors[pos%2+4], activebackground=row_colors[pos%2], bg=row_colors[pos%2], anchor="w").grid(row=pos, columnspan=2, sticky="new")
        Grid.rowconfigure(Frame_view, pos, weight=1)
        pos += 1

        Radiobutton(Frame_view, text=self.Messages["Settings10A"], variable=self.Color_GUI, value="Dark", wraplength=300, justify=LEFT, selectcolor=row_colors[pos%2+6], activeforeground=row_colors[pos%2+4], fg=row_colors[pos%2+4], bg=row_colors[pos%2], activebackground=row_colors[pos%2], anchor="w").grid(row=pos, column=0, sticky="new")
        Radiobutton(Frame_view, text=self.Messages["Settings10B"], variable=self.Color_GUI, value="Light", wraplength=300, justify=LEFT, selectcolor=row_colors[pos%2+6], activeforeground=row_colors[pos%2+4], fg=row_colors[pos%2+4],bg=row_colors[pos % 2], activebackground=row_colors[pos%2], anchor="w").grid(row=pos, column=1, sticky="new")
        Grid.rowconfigure(Frame_view, pos, weight=1)
        pos+=1

        Checkbutton(Frame_view, text=self.Messages["Settings1"], variable=self.Sound_track, activeforeground=row_colors[pos%2+4], fg=row_colors[pos%2+4], selectcolor=row_colors[pos%2+6], bg=row_colors[pos%2], activebackground=row_colors[pos%2], anchor="w").grid(row=pos, columnspan=2, sticky="new")
        Grid.rowconfigure(Frame_view, pos, weight=1)
        pos += 1

        Checkbutton(Frame_view, text=self.Messages["Settings2"], variable=self.Pop_track, activeforeground=row_colors[pos%2+4], fg=row_colors[pos%2+4], selectcolor=row_colors[pos%2+6], bg=row_colors[pos%2], activebackground=row_colors[pos%2], anchor="w").grid(row=pos, columnspan=2, sticky="enw")
        Grid.rowconfigure(Frame_view, pos, weight=1)
        pos += 1

        Frame_set3 = Frame(Frame_view, background=row_colors[pos%2])
        Grid.columnconfigure(Frame_set3, 0, weight=1)
        Grid.columnconfigure(Frame_set3, 1, weight=10)
        Label(Frame_set3, text=self.Messages["Settings3"], anchor="w", activeforeground=row_colors[pos%2+4], fg=row_colors[pos%2+4], bg=row_colors[pos%2], activebackground=row_colors[pos%2]).grid(row=0, column=0, sticky="enw")
        Scale(Frame_set3, from_=100, to=2000, variable=self.Size_img_display, orient=HORIZONTAL, fg=row_colors[pos%2+4], bg=row_colors[pos%2], activebackground=row_colors[pos%2], highlightbackground=row_colors[pos%2], troughcolor=row_colors[pos%2+2]).grid(row=0,column=1, sticky="new")
        Frame_set3.grid(row=pos,columnspan=2, sticky="nesw")
        Grid.rowconfigure(Frame_view, 4, weight=1)
        pos+=1

        Frame_set4=Frame(Frame_view, background=row_colors[pos%2])
        Grid.columnconfigure(Frame_set4, 0, weight=1)
        Grid.columnconfigure(Frame_set4, 1, weight=10)
        Label(Frame_set4, text=self.Messages["Settings4"], activeforeground=row_colors[pos%2+4], fg=row_colors[pos%2+4], bg=row_colors[pos%2], activebackground=row_colors[pos%2], anchor="w").grid(row=0, column=0, sticky="new")
        Scale(Frame_set4, from_=1, to=100, variable=self.Back_tool, orient=HORIZONTAL, fg=row_colors[pos%2+4], bg=row_colors[pos%2], activebackground=row_colors[pos%2], highlightbackground=row_colors[pos%2], troughcolor=row_colors[pos%2+2]).grid(row=0,column=1, sticky="new")
        Frame_set4.grid(row=pos,columnspan=2, sticky="new")
        Grid.rowconfigure(Frame_view, 5, weight=1)
        pos+=1

        #Tracking parameters
        Frame_tracking=Frame(self, highlightbackground=list_colors["Frame"], highlightthickness=2,borderwidth=2, background=list_colors["Table1"], relief="ridge")
        Frame_tracking.grid(row=0,column=1, sticky="nsew")
        Grid.columnconfigure(Frame_tracking, 0, weight=1)
        Grid.columnconfigure(Frame_tracking, 1, weight=1)
        pos=0

        Label(Frame_tracking, text=self.Messages["Settings0b"], font=("Helvetica",15,"bold"), bg=list_colors["Title1"], fg=list_colors["Fg_Title1"], justify=CENTER).grid(row=pos, columnspan=2, sticky="enw")
        Grid.rowconfigure(Frame_tracking, pos, weight=0)
        pos+=1

        Kal_button=Checkbutton(Frame_tracking, text=self.Messages["Settings6"], variable=self.Kalmna_filter, selectcolor=row_colors[pos%2+6], activeforeground=row_colors[pos%2+4], fg=row_colors[pos%2+4], bg=row_colors[pos%2], activebackground=row_colors[pos%2], anchor="nw")
        Small_info.small_info(elem=Kal_button, parent=self, message=self.Messages["Small_info2"])
        Kal_button.grid(row=pos, columnspan=2, sticky="new")
        Grid.rowconfigure(Frame_tracking, pos, weight=1)
        pos+=1

        Keep_ent=Checkbutton(Frame_tracking, text=self.Messages["Settings11"], activeforeground=row_colors[pos%2+4], selectcolor=row_colors[pos%2+6], variable=self.Keep_entrance, fg=row_colors[pos%2+4], bg=row_colors[pos%2], activebackground=row_colors[pos%2], anchor="nw")
        Keep_ent.grid(row=pos, columnspan=2, sticky="new")
        Small_info.small_info(elem=Keep_ent, parent=self, message=self.Messages["Settings11B"])

        Grid.rowconfigure(Frame_tracking, pos, weight=1)
        pos+=1

        Grid.rowconfigure(Frame_tracking, pos, weight=1000)



        #Correction parameters
        Frame_correction = Frame(self, highlightbackground=list_colors["Frame"], highlightthickness=2, borderwidth=2, background=list_colors["Table1"], relief="ridge")
        #Frame_correction.grid(row=0, column=2, sticky="nsew")
        Grid.columnconfigure(Frame_correction, 0, weight=1)
        Grid.columnconfigure(Frame_correction, 1, weight=10)

        pos=0
        Label(Frame_correction, text=self.Messages["Settings0c"], font=("Helvetica",15,"bold"), justify=CENTER, bg=list_colors["Title1"], fg=list_colors["Fg_Title1"]).grid(row=pos, columnspan=2, sticky="enw")
        Grid.rowconfigure(Frame_correction, pos, weight=0)
        pos+=1

        #Checkbutton(Frame_correction, text=self.Messages["Settings7"], variable=self.Hide_columns, selectcolor=row_colors[pos%2+6], activeforeground=row_colors[pos%2+4], fg=row_colors[pos%2+4], activebackground=row_colors[pos%2], bg=row_colors[pos%2], anchor="w").grid(row=pos, columnspan=2, sticky="new")
        #Grid.rowconfigure(Frame_correction, pos, weight=1)
        #pos+=1


        #General
        Button(self, text=self.Messages["Validate"], background=list_colors["Validate"], activebackground=list_colors["Validate"], fg=list_colors["Fg_Validate"], activeforeground=list_colors["Fg_Validate"], command=self.validate, borderwidth=4).grid(row=1, columnspan=3, sticky="nsew")



    def validate(self):
        rerun = False
        save = False

        if self.Color_GUI.get()!=self.Params["Color_GUI"]:
            if self.main.folder != None:
                question = MsgBox.Messagebox(parent=self, title=self.Messages["General8"],
                                             message=self.Messages["General9"],
                                             Possibilities=[self.Messages["Yes"], self.Messages["No"],
                                                            self.Messages["Cancel"]])
                self.wait_window(question)
                answer = question.result


                if answer == 0:
                    rerun=True
                    save=True
                elif answer == 1:
                    rerun=True
                    save=False
                else:
                    return
            else:
                rerun = True
                save = False

        with open(self.Param_file, 'wb') as fp:
            data_to_save = dict(Sound_alert_track=self.Sound_track.get(), Pop_alert_track=self.Pop_track.get(), Size_img_display=self.Size_img_display.get(), Back_tool=self.Back_tool.get(), Low_priority=self.Low_prio.get(), Use_Kalman=self.Kalmna_filter.get(), Check_hide_missing=self.Hide_columns.get(), Relative_background=self.Relative_back.get(), Keep_entrance=self.Keep_entrance.get(), Color_GUI=self.Color_GUI.get(), Auto_update=self.Auto_update.get())
            pickle.dump(data_to_save, fp)

        Diverse_functions.low_priority(self.Low_prio.get())

        if not rerun:
            try:#If there is a project open, we update
                self.main.update_projects()
            except:
                pass
            self.destroy()
            self.parent.destroy()

        else:
            if save:
                self.main.save()
            self.main.fermer()
