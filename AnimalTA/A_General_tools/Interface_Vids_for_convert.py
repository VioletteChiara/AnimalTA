from tkinter import *
from tkinter import ttk
import os
import pickle
from AnimalTA.A_General_tools import UserMessages, Class_converter, Color_settings, Message_simple_question as MsgBox, Small_info, Class_loading_Frame
from AnimalTA import Class_Video
import ntpath
import multiprocessing
import time


class Convert(Frame):
    """When the user ask to add new videos, these videos must be avi. If they are not, this window will open and ask the user which of the videos have to be converted to avi."""
    def __init__(self, parent, boss, list_to_convert, Video=None):
        Frame.__init__(self, parent, bd=5)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.boss=boss
        self.grid(sticky="nsew")
        self.list_vid=list_to_convert
        self.grab_set()
        self.all_sel=False
        self.timer=0
        self.cache=False
        self.Vid=Video


        #Import messsages
        self.Messages = UserMessages.get_dict()

        #We import colors
        list_colors=Color_settings.My_colors.list_colors

        self.winfo_toplevel().title(self.Messages["Conversion"])

        self.sel_state=StringVar()
        self.sel_state.set(self.Messages["ExtendB1"])

        #Explication of what is this window
        self.explanations=Label(self, text=self.Messages["ExtendConvert_EX"], wraplength=800,**Color_settings.My_colors.Label_Base)
        self.explanations.grid(row=0,columnspan=2)

        #Button to select the whole list
        self.bouton_sel_all=Button(self,textvariable=self.sel_state,command=self.select_all, **Color_settings.My_colors.Button_Base)
        self.bouton_sel_all.grid(row=1,columnspan=2)

        #The list of videos to be converted
        self.yscrollbar = ttk.Scrollbar(self)
        self.Liste=Listbox(self, selectmode = EXTENDED, yscrollcommand=self.yscrollbar.set, **Color_settings.My_colors.ListBox)
        self.Liste.config(height=15, width=150)
        self.list_vid_minus=[]
        for i in range(len(self.list_vid)):
            self.list_vid_minus.append(self.list_vid[i])

            self.Liste.insert(i, self.list_vid[i])

        self.Liste.grid(row=2,column=0)
        self.yscrollbar.grid(row=2,column=1, sticky="ns")

        Fr_other_options=Frame(self,**Color_settings.My_colors.Frame_Base)
        Fr_other_options.grid(row=3, sticky="nsew")

        self.FPS_corr=BooleanVar()
        self.FPS_corr.set(False)
        self.CheckB_fr = Checkbutton(Fr_other_options,text=self.Messages["Convert_fps"], variable=self.FPS_corr, command=self.ask_fps, **Color_settings.My_colors.Checkbutton_Base)
        self.CheckB_fr.grid(row=0, column=0)

        self.fps_val = 25
        self.Fr_fps = Frame_new_fps(parent=Fr_other_options, boss=self)


        self.Vid_qual=IntVar()
        self.Vid_qual.set(5)

        Scale_with_txt=Frame(Fr_other_options, **Color_settings.My_colors.Frame_Base)
        Scale_with_txt.grid(row=0, column=1)
        Label(Scale_with_txt, text=self.Messages["Convert_H"], **Color_settings.My_colors.Label_Base).grid(row=0, column=0, sticky="se")
        self.Scale_qual=Scale(Scale_with_txt, variable=self.Vid_qual, label=self.Messages["Convert_quality"], from_=1, to=31, relief="flat", **Color_settings.My_colors.Scale_Base, orient=HORIZONTAL)
        self.Scale_qual.grid(row=0, column=1)
        Small_info.small_info(elem=self.Scale_qual, parent=self, message=self.Messages["Convert_quality_expl"])
        Label(Scale_with_txt, text=self.Messages["Convert_L"], **Color_settings.My_colors.Label_Base).grid(row=0, column=2, sticky="sw")

        Grid.rowconfigure(Fr_other_options, 0, weight=1)
        Grid.rowconfigure(Fr_other_options, 1, weight=1)
        Grid.columnconfigure(Fr_other_options,0, weight=1)
        Grid.columnconfigure(Fr_other_options, 1, weight=1)



        #Validate
        Frame_Buttons=Frame(self, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        Frame_Buttons.grid(row=4, sticky="nsew")
        Grid.columnconfigure(Frame_Buttons,0, weight=1)
        Grid.columnconfigure(Frame_Buttons, 1, weight=1)
        self.bouton=Button(Frame_Buttons,text=self.Messages["Validate"], **Color_settings.My_colors.Button_Base, width=15)
        self.bouton.config(bg=list_colors["Validate"], fg=list_colors["Fg_Validate"],command=self.validate)
        self.bouton.grid(row=0, column=0, sticky="e")

        self.bouton_cancel=Button(Frame_Buttons,text=self.Messages["Cancel"], **Color_settings.My_colors.Button_Base, width=15)
        self.bouton_cancel.config(bg=list_colors["Cancel"], fg=list_colors["Fg_Cancel"],command=self.End_of_window)
        self.bouton_cancel.grid(row=0, column=1, sticky="w")
        self.yscrollbar.config(command=self.Liste.yview)

        #Show the progression of the convertions
        self.loading_canvas=Frame(self, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.loading_canvas.grid(row=5,columnspan=2)

        #Minimise the AnimalTA program to allow user to do something else while converting
        self.bouton_hide = Button(self, text=self.Messages["Do_track1"], command=self.hide, **Color_settings.My_colors.Button_Base)

        Grid.rowconfigure(self.parent, 0, weight=1)
        Grid.columnconfigure(self.parent,0, weight=1)

        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=1)
        Grid.rowconfigure(self, 3, weight=1)
        Grid.rowconfigure(self, 4, weight=1)
        Grid.rowconfigure(self, 5, weight=1)
        Grid.columnconfigure(self,0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)




        self.select_all()

    def ask_fps(self):
        if self.FPS_corr.get():
            self.Fr_fps.grid(row=4, sticky="nsew")
            self.bouton.config(state="disable", **Color_settings.My_colors.Button_Base)
        else:
            self.Fr_fps.grid_forget()
            self.bouton.config(state="normal", background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])



    def select_all(self):
        #Select all the videos of the list
        if not self.all_sel:
            self.Liste.select_set(0, END)
            self.sel_state.set(self.Messages["ExtendB2"])
            self.all_sel=True
        else:
            self.Liste.selection_clear(0, END)
            self.sel_state.set(self.Messages["ExtendB1"])
            self.all_sel=False

    def validate(self):
        #Run the convertions and close this window in the end
        list_item = self.Liste.curselection()

        #We don't want user to interact with buttons during conversions
        self.bouton.config(state="disable", **Color_settings.My_colors.Button_Base)
        self.bouton_sel_all.config(state="disable", **Color_settings.My_colors.Button_Base)
        self.Liste.config(state="disable", **Color_settings.My_colors.ListBox)
        self.CheckB_fr.config(state="disable")
        self.Scale_qual.config(state="disable", fg=Color_settings.My_colors.list_colors["Fg_Base_ina"])

        self.bouton_hide.grid(row=7)


        self.first_time_rename = True#We never asked if the user wants to rename the videos
        self.answer_rename = 2#What should we do if teh file already exists?

        manager = multiprocessing.Manager()
        all_counters = []
        all_loadings = []
        self.list_errors=[]
        all_process = []

        vid_count = 0
        for V in list_item:
            if not self.FPS_corr.get():
                self.fps_val=None

            try:
                Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
                with open(Param_file, 'rb') as fp:
                    self.Params = pickle.load(fp)

                file_name = os.path.basename(self.list_vid_minus[V])
                point_pos = file_name.rfind(".")
                file_name_cut = file_name[:point_pos]
                output_directory = os.path.join(self.boss.folder, "converted_vids")

                if not os.path.isdir(output_directory):  # Create a new directory if it doesn't exist
                    os.makedirs(output_directory)
                new_file = os.path.join(output_directory, file_name_cut + ".avi")

                if os.path.exists(new_file) or os.path.exists(new_file.replace(".avi", f"_part_1.avi")):
                    if self.first_time_rename:
                        question = MsgBox.Messagebox(parent=self, title=self.Messages["Convert1"],
                                                     message=self.Messages["Convert2"].format(
                                                         file_name_cut),
                                                     Possibilities=[self.Messages["Convert3"],
                                                                    self.Messages["Convert4"],
                                                                    self.Messages["Cancel"]])
                        self.wait_window(question)
                        answer = question.result
                        self.first_time_rename = False
                        self.answer_rename = answer

                    if answer == 1:
                        found = False
                        j = 0
                        while not found:
                            j += 1
                            file_name_cut_tmp = file_name_cut + "_(" + str(j) + ")_"
                            new_file = os.path.join(output_directory, file_name_cut_tmp + ".avi")
                            if not os.path.exists(new_file):
                                found = True

                    elif answer == 2:
                        continue

                all_counters.append(manager.Value('d', 0))  # Shared counter
                all_process.append([self.list_vid_minus[V], new_file, self.fps_val, self.Vid_qual.get(), all_counters[-1]])
                all_loadings.append(Class_loading_Frame.Loading(self.loading_canvas, text=self.Messages["Video"] + " {act}/{tot}".format(act=vid_count+1,tot=len(list_item)), grab=False))
                vid_count += 1

            except:
                self.list_errors.append(self.list_vid_minus[V])

        if self.Params["Low_priority"]:
            num_processes=1
        else:
            num_processes = min(multiprocessing.cpu_count()-1, len(all_process))
        with multiprocessing.Pool(num_processes) as pool:
            results = [pool.apply_async(Class_converter.convert_to_avi, args) for args in all_process]

            finished=False
            while not finished:  # Stop when all reach 5
                for cur_pro in range(len(all_process)):
                    progress=all_counters[cur_pro].value

                    if progress>0.00001 and not results[cur_pro].ready():
                        if not bool(all_loadings[cur_pro].grid_info()):
                            all_loadings[cur_pro].grid()
                        all_loadings[cur_pro].show_load(progress)

                    elif bool(all_loadings[cur_pro].grid_info()):
                        all_loadings[cur_pro].grid_forget()

                time.sleep(0.1)  # Check counters every second
                finished = all(res.ready() for res in results)

            formatted_res=[]
            for res in results:
                formatted_res.append(res.get())


        for result in formatted_res:
            if result[0] != "Error":
                if self.Vid == None:
                    self.boss.liste_of_videos.append(
                        Class_Video.Video(File_name=result[0][0][1], User_Name=ntpath.basename(result[2]),
                                          Folder=self.boss.folder))

                    self.boss.liste_of_videos[-1].Fusion = result[0]
                    self.boss.liste_of_videos[-1].Frame_nb = [result[1], result[1]]
                    self.boss.liste_of_videos[-1].Cropped = [False, [0, result[1] - 1]]

                    count = 1
                    all_names = [V.Name for V in self.boss.liste_of_videos]
                    while self.boss.liste_of_videos[-1].Name in all_names:
                        new_name = self.boss.liste_of_videos[-1].Name + "(" + str(count) + ")"
                        if new_name not in all_names:
                            self.boss.liste_of_videos[-1].Name = new_name
                        count += 1

                    count = 1
                    all_names = [V.User_Name for V in self.boss.liste_of_videos]
                    while self.boss.liste_of_videos[-1].User_Name in all_names:
                        new_name = self.boss.liste_of_videos[-1].User_Name + "(" + str(count) + ")"
                        if new_name not in all_names:
                            self.boss.liste_of_videos[-1].User_Name = new_name
                        count += 1

            else:
                self.list_errors.append(self.list_vid_minus[V])



        for elem in self.list_errors:
            question = MsgBox.Messagebox(parent=self, title=self.Messages["GWarnT5"],
                                       message=self.Messages["GWarn6"].format(elem), Possibilities=[self.Messages["Continue"]])
            self.wait_window(question)

            self.boss.HW.change_tmp_message(self.Messages["General1"])

        #Update the main frame
        if self.Vid == None:
            self.boss.update_projects()
            self.boss.update_selections()
            self.boss.focus_set()
            self.bouton.config(state="normal", background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
            self.bouton_sel_all.config(state="normal")
            self.boss.afficher_projects()

            if self.cache:#If the program was minimised, we bring it back
                self.boss.parent.update_idletasks()
                self.boss.parent.state('normal')
                self.boss.parent.overrideredirect(True)

        self.boss.save()

        self.End_of_window()

    def End_of_window(self):
        self.boss.update_row_display()
        self.parent.destroy()


    def hide(self):
        #Minimise the program
        self.cache=True
        self.parent.wm_state('iconic')
        self.boss.parent.update_idletasks()
        self.boss.parent.overrideredirect(False)
        self.boss.parent.state('iconic')



class Frame_new_fps(Frame):
    def __init__(self, parent, boss):
        Frame.__init__(self, parent, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.config(background=Color_settings.My_colors.list_colors["Entry_error"])
        self.parent=parent
        self.boss=boss
        self.tmp_val=StringVar()
        self.tmp_val.set(25)
        Grid.columnconfigure(self,0,weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Entry(self, textvariable=self.tmp_val, **Color_settings.My_colors.Entry_Base).grid()
        Button(self,text=self.boss.Messages["Validate"], command=self.end, **Color_settings.My_colors.Button_Base).grid()

    def end(self):
        try:
            self.parent.fps_val=float(self.tmp_val.get())
        except:
            pass

        self.parent.bouton.config(state="normal", background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.grid_forget()



"""
root = Tk()
root.geometry("+100+100")
Video_file=Class_Video.Video(File_name="D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01.avi")
Video_file.Back[0]=True

im=cv2.imread("D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01_background.bmp")
im=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
Video_file.Back[1]=im
interface = Scale(parent=root, boss=None, Video_file=Video_file)
root.mainloop()
"""