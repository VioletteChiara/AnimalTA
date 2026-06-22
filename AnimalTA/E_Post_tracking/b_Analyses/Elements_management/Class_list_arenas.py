from tkinter import *
from tkinter import ttk
from AnimalTA.A_General_tools import Function_draw_arenas, Color_settings, UserMessages
import cv2
import PIL
import os

class List_arenas(Frame):
    """ This Frame displays a list of the videos and their arenas from the project that have been tracked.
    The user can select some arenas to copy-paste there the elements of interest from the current arena"""
    def __init__(self, parent, boss, liste_videos, Current_Vid, Current_Area, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.boss=boss
        self.Current_Vid = Current_Vid
        self.Current_Area = Current_Area
        self.liste_videos = liste_videos

        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=1000)  ########NEW
        Grid.columnconfigure(self, 0, weight=10)  ########NEW
        Grid.columnconfigure(self, 1, weight=10)  ########NEW
        Grid.columnconfigure(self, 2, weight=1)  ########NEW


        #Import messages
        self.Messages = UserMessages.get_dict()

        self.Button_sel_al_o = Button(self, text=self.Messages["ExtendB1"], command=self.select_all_areas,
                                      **Color_settings.My_colors.Button_Base)
        self.Button_sel_al_o.grid(row=0, column=0)

        self.all_sel_areas = False
        self.yscrollbar2 = ttk.Scrollbar(self)
        self.yscrollbar2.grid(row=1, column=1, sticky="ns")
        self.Liste_Vids = Listbox(self, selectmode=EXTENDED, width=50, exportselection=0,
                                  yscrollcommand=self.yscrollbar2.set, **Color_settings.My_colors.ListBox)
        self.yscrollbar2.config(command=self.Liste_Vids.yview)

        self.to_remove_sel = []  # The Video cannot be selecetd, only the arenas
        self.pointers = []  # To then allow to associate the text in the list to the arenas
        for Vid in liste_videos:
            if Vid.Tracked:  # We consider only tracked videos
                if Vid == Current_Vid:  # We highlight in red the current Vid and it will be placed in the top of the list
                    self.Liste_Vids.insert(0, self.Messages["Video"] + ": " + Vid.User_Name)
                    self.Liste_Vids.itemconfig(0, fg=Color_settings.My_colors.list_colors["Fg_not_valide"],
                                               bg=Color_settings.My_colors.list_colors["Table2"])
                    self.to_remove_sel = [val + 1 for val in self.to_remove_sel]
                    self.to_remove_sel.append(0)
                    self.pointers.insert(0, [Vid, None])
                else:
                    self.Liste_Vids.insert(END, self.Messages["Video"] + ": " + Vid.User_Name)
                    self.Liste_Vids.itemconfig("end", fg=Color_settings.My_colors.list_colors["Fg_T2"],
                                               bg=Color_settings.My_colors.list_colors["Table2"])
                    self.to_remove_sel.append(self.Liste_Vids.size() - 1)
                    self.pointers.append([Vid, None])

                AID = 0
                Ar_cur_vid = 1
                for Arena in Vid.Analyses[1]:
                    if not (AID == Current_Area and Vid == Current_Vid):
                        if Vid == Current_Vid:
                            self.Liste_Vids.insert(Ar_cur_vid, "  -" + self.Messages["Arena"] + "_" + str(AID))
                            self.pointers.insert(Ar_cur_vid, [Vid, AID])
                            self.Liste_Vids.itemconfig(Ar_cur_vid, fg=Color_settings.My_colors.list_colors["Fg_T1"],
                                                       bg=Color_settings.My_colors.list_colors["Table1"])
                            self.to_remove_sel = [0] + [val + 1 for val in self.to_remove_sel if val > 0]
                            Ar_cur_vid += 1
                        else:
                            self.Liste_Vids.insert(END, "  -" + self.Messages["Arena"] + "_" + str(AID))
                            self.Liste_Vids.itemconfig("end", fg=Color_settings.My_colors.list_colors["Fg_T1"],
                                                       bg=Color_settings.My_colors.list_colors["Table1"])
                            self.pointers.append([Vid, AID])
                    AID += 1

        self.Liste_Vids.grid(row=1, column=0, sticky="nsew")
        self.Liste_Vids.bind('<<ListboxSelect>>', self.remove_sel)
        self.Liste_Vids.bind("<Motion>", self.show_Arenas)
        self.Liste_Vids.bind("<Leave>", self.stop_show_Arenas)

        #In this canves, we will show the video and position of arenas
        self.Canvas_shaow_Ar=Canvas(self, width=600, height=300, **Color_settings.My_colors.Frame_Base)
        self.Canvas_shaow_Ar.grid(row=0, column=2, rowspan=2, sticky="nsew")
        self.Canvas_shaow_Ar.update()



    def select_all_areas(self):
        #Select/unselect all arenas
        if not self.all_sel_areas:
            self.Liste_Vids.select_set(0, END)
            self.Button_sel_al_o.config(text=self.Messages["ExtendB2"])
            self.all_sel_areas=True
        else:
            self.Liste_Vids.selection_clear(0, END)
            self.Button_sel_al_o.config(text=self.Messages["ExtendB1"])
            self.all_sel_areas=False

        for index in range(len(self.to_remove_sel)): #The video names cannot be selected.
            self.Liste_Vids.selection_clear(self.to_remove_sel[index])

        self.parent.check_button()#On actualise le bouton de validation



    def show_Arenas(self, event):
        #This function display an image of the video over which the cursor is in the list.
        #The contours of arenas are highlighted and if the cursor is over a specifi arena, this arena is highlighted itself
        index = self.Liste_Vids.index("@%s,%s" % (event.x, event.y))

        Which_part = 0
        if self.pointers[index][0].Cropped[0]:
            if len(self.pointers[index][0].Fusion) > 1:  # If the video result from a concatenation of two videos
                Which_part = [index0 for index0, Fu_inf in enumerate(self.pointers[index][0].Fusion) if Fu_inf[0] <= self.pointers[index][0].Cropped[1][0]][-1]

        if self.pointers[index][0].type == "Video":
            capture = cv2.VideoCapture(self.pointers[index][0].Fusion[Which_part][1])  # Faster with opencv and the accuracy is not highly important here
            capture.set(cv2.CAP_PROP_POS_FRAMES, self.pointers[index][0].Cropped[1][0] - self.pointers[index][0].Fusion[Which_part][0])
            _, img = capture.read()
            del capture
        else:
            img=cv2.imread(os.path.join(self.pointers[index][0].Fusion[Which_part][1], self.self.pointers[index][0].img_list[self.pointers[index][0].Cropped[1][0] - self.pointers[index][0].Fusion[Which_part][0]]))

        img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if self.pointers[index][0].Cropped_sp[0]:
            img = img[self.pointers[index][0].Cropped_sp[1][0]:self.pointers[index][0].Cropped_sp[1][2], self.pointers[index][0].Cropped_sp[1][1]:self.pointers[index][0].Cropped_sp[1][3]]

        self.Arenas = Function_draw_arenas.get_arenas(self.pointers[index][0])

        for Ar in range(len(self.Arenas)):
            cnt_M=cv2.moments(self.Arenas[Ar])
            if cnt_M["m00"] > 0:
                cX = int(cnt_M["m10"] / cnt_M["m00"])
                cY = int(cnt_M["m01"] / cnt_M["m00"])

                if Ar==self.pointers[index][1]:
                    img=cv2.putText(img, str(Ar), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    img=cv2.drawContours(img, self.Arenas, Ar, (0, 0, 0), 6)
                    img = cv2.drawContours(img, self.Arenas, Ar, (0, 0, 255), 2)

                else:
                    img=cv2.drawContours(img, self.Arenas, Ar,(255,0,0),2)
                    img=cv2.putText(img,str(Ar),(cX,cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

        ratio=max(img.shape[1]/self.Canvas_shaow_Ar.winfo_width(), img.shape[0]/self.Canvas_shaow_Ar.winfo_height())
        img=cv2.resize(img,(int(img.shape[1]/ratio),int(img.shape[0]/ratio)))
        img2=self.image_to_show3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img))
        self.Canvas_shaow_Ar.create_image(0, 0, image=img2, anchor=NW)

    def stop_show_Arenas(self, event):
        cv2.destroyAllWindows()

    def remove_sel(self,*arg):
        #Avoid that user can select a vido.
        selection=self.Liste_Vids.curselection()
        for index in range(len(self.to_remove_sel)):
            if self.to_remove_sel[index] in selection:
                try:
                    next=self.to_remove_sel[index+1]
                except:
                    next=self.Liste_Vids.size()

                was_sel=0
                for elem_to_add in range(self.to_remove_sel[index]+1, next):
                    if elem_to_add not in selection:
                        was_sel +=1
                        self.Liste_Vids.select_set(elem_to_add)
                if was_sel==0:
                    for elem_to_add in range(self.to_remove_sel[index] + 1, next):
                        self.Liste_Vids.selection_clear(elem_to_add)
                self.Liste_Vids.selection_clear(self.to_remove_sel[index])
        self.parent.check_button()

