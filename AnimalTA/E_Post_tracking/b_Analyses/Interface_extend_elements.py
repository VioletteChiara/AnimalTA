from tkinter import *
from tkinter import messagebox
from AnimalTA.E_Post_tracking.b_Analyses import Function_extend_elements
from AnimalTA.A_General_tools import Function_draw_mask, UserMessages
import cv2
import numpy as np
import PIL

class Lists(Frame):
    """ This Frame displays a list of the videos and their arenas from the project that have been tracked.
    The user can select some arenas to copy-paste there the elements of interest from the current arena"""
    def __init__(self, parent, boss, liste_videos, Current_Vid, Current_Area, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss
        self.grid()
        self.Current_Vid=Current_Vid
        self.Current_Area=Current_Area
        self.liste_videos=liste_videos

        #Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW

        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Extend_Ana0"])


        #User help
        User_help=Label(self,text=self.Messages["Extend_Ana1"], wraplength=800, justify=LEFT)
        User_help.grid(row=0, column=0, columnspan=5)

        #Listbox of shapes in current arena with button to select/unselect all
        self.Button_sel_al=Button(self,text=self.Messages["ExtendB1"], command=self.select_all_objs)
        self.Button_sel_al.grid(row=1, column=0, columnspan=2)
        self.all_sel_objs = False
        self.yscrollbar = Scrollbar(self)
        self.yscrollbar.grid(row=2,column=1, sticky="ns")
        self.Liste_objects=Listbox(self, selectmode = "multiple", width=50, height=20, exportselection=0, yscrollcommand=self.yscrollbar.set)
        self.yscrollbar.config(command=self.Liste_objects.yview)
        ID = 0
        for Shape in Current_Vid.Analyses[1][Current_Area]:
            self.Liste_objects.insert(END, Shape[3])
            ID += 1

        self.Liste_objects.grid(row=2, column=0, sticky="nsew")
        self.Liste_objects.bind('<<ListboxSelect>>', self.check_button)

        Arrow=Label(self, text=u'\u279F', font=('Helvatical bold',20))
        Arrow.grid(row=2,column=2)

        # Listbox of other arenas
        self.Button_sel_al_o=Button(self,text=self.Messages["ExtendB1"], command=self.select_all_areas)
        self.Button_sel_al_o.grid(row=1, column=3, columnspan=2)
        self.all_sel_areas=False
        self.yscrollbar2 = Scrollbar(self)
        self.yscrollbar2.grid(row=2, column=4, sticky="ns")
        self.Liste_Vids = Listbox(self, selectmode = EXTENDED, width=50, exportselection=0, yscrollcommand=self.yscrollbar2.set)
        self.yscrollbar2.config(command=self.Liste_Vids.yview)

        self.to_remove_sel=[]#The Video cannot be selecetd, only the arenas
        self.pointers=[]#To then allow to associate the text in the list to the arenas
        for Vid in liste_videos:
            if Vid.Tracked:#We consider only tracked videos
                if Vid == Current_Vid:  # We highlight in red the current Vid and it will be placed in the top of the list
                    self.Liste_Vids.insert(0, self.Messages["Video"] + ": " + Vid.User_Name)
                    self.Liste_Vids.itemconfig(0, fg='red', bg="grey75")
                    self.to_remove_sel=[val+1 for val in self.to_remove_sel]
                    self.to_remove_sel.append(0)
                    self.pointers.insert(0,[Vid, None])
                else:
                    self.Liste_Vids.insert(END, self.Messages["Video"] +": "+Vid.User_Name)
                    self.Liste_Vids.itemconfig("end", bg="grey75")
                    self.to_remove_sel.append(self.Liste_Vids.size()-1)
                    self.pointers.append([Vid,None])

                AID = 0
                Ar_cur_vid=1
                for Arena in Vid.Analyses[1]:
                    if not (AID==Current_Area and Vid == Current_Vid):
                        if Vid == Current_Vid:
                            self.Liste_Vids.insert(Ar_cur_vid, "  -" + self.Messages["Arena"] + "_" + str(AID))
                            self.pointers.insert(Ar_cur_vid, [Vid, AID])
                            self.to_remove_sel = [0] + [val + 1 for val in self.to_remove_sel if val>0]
                            Ar_cur_vid += 1
                        else:
                            self.Liste_Vids.insert(END, "  -"+ self.Messages["Arena"]+"_" + str(AID))
                            self.pointers.append([Vid, AID])
                    AID+=1

        self.Liste_Vids.grid(row=2, column=3, sticky="nsew")
        self.Liste_Vids.bind('<<ListboxSelect>>',self.remove_sel)
        self.Liste_Vids.bind("<Motion>", self.show_Arenas)
        self.Liste_Vids.bind("<Leave>", self.stop_show_Arenas)

        self.Validate_button=Button(self, text=self.Messages["Validate"], command=self.validate)
        self.Validate_button.grid(row=3, columnspan=5, sticky="nsew")
        self.Validate_button.config(state="disable")

        self.parent.update()
        self.max_can_height = self.parent.winfo_height()
        self.max_can_width = self.parent.winfo_screenwidth()-self.parent.winfo_width()-200

        #In this canves, we will show the video and position of arenas
        self.Canvas_shaow_Ar=Canvas(self)
        self.Canvas_shaow_Ar.grid(row=0, column=5, rowspan=4, sticky="nsew")

        self.stay_on_top()
        self.boss.ready=False
        self.parent.protocol("WM_DELETE_WINDOW", self.close)

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

        self.check_button()#On actualise le bouton de validation


    def select_all_objs(self):
        #Select all the elements of interest inside the current arena
        if not self.all_sel_objs:
            self.Liste_objects.select_set(0, END)
            self.Button_sel_al.config(text=self.Messages["ExtendB2"])
            self.all_sel_objs=True
        else:
            self.Liste_objects.selection_clear(0, END)
            self.Button_sel_al.config(text=self.Messages["ExtendB1"])
            self.all_sel_objs=False
        self.check_button()#On actualise le bouton de validation

    def close(self):
        #Close this window properly
        self.parent.destroy()
        self.boss.ready=True

    def validate(self):
        #Extend the elements to other arenas
        list_of_shapes=[self.Current_Vid.Analyses[1][self.Current_Area][i] for i in self.Liste_objects.curselection()]
        Show_warn=False#Flag to determine whether the user should be aware of a remplacement of existing elements

        mask = Function_draw_mask.draw_mask(self.Current_Vid)
        Or_Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        Or_Arenas = Function_draw_mask.Organise_Ars(Or_Arenas)

        Np_style_pts=np.array([self.pointers[i] for i in self.Liste_Vids.curselection()])
        list_of_vids =[]
        for Vid in Np_style_pts[:,0]:#Look for all videos with at least one selected arena
            if Vid not in list_of_vids:
                list_of_vids.append(Vid)

        for Vid in list_of_vids:#For each of these videos, we look for the arenas
            mask = Function_draw_mask.draw_mask(Vid)
            Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            Arenas = Function_draw_mask.Organise_Ars(Arenas)

            for Area in range(len(Arenas)):
                if Area in [self.pointers[i][1] for i in self.Liste_Vids.curselection() if self.pointers[i][0]==Vid]:#If the arena was selected
                    list_of_points = []
                    if not (Area==self.Current_Area and Vid == self.Current_Vid):#We ensure it is not the current arena
                        for shape in list_of_shapes:
                            #we first check if an element of interest with similar name has already been defined:
                            if shape[0] != "Borders" and shape[0] != "All_borders":
                                list_of_points = list_of_points + shape[1]
                            elif shape[0] == "Borders":
                                for bd in shape[1]:
                                    list_of_points = list_of_points + bd
                            elif shape[0] == "All_borders":
                                if Vid == self.Current_Vid:
                                    Shape2= DoubleVar(value=shape[2].get())
                                else:
                                    Shape2=shape[2].get()

                                if shape[3] not in [Ars[3] for Ars in Vid.Analyses[1][Area]]:#If this shape does not exist yet
                                    Vid.Analyses[1][Area].append(["All_borders", [], Shape2, shape[3]])
                                else:
                                    position=[Ars[3] for Ars in Vid.Analyses[1][Area]].index(shape[3])#If this shape already exists inside the arena, we remplace it and a warning will be displayed
                                    Vid.Analyses[1][Area][position]=["All_borders", [], Shape2, shape[3]]
                                    Show_warn = True

                        if len(list_of_points) > 0:
                            work, new_pts = Function_extend_elements.match_shapes(Arenas[Area], Or_Arenas[self.Current_Area], list_of_points)
                            if work:
                                for shape in list_of_shapes:
                                    if shape[0]!="Borders" and shape[0]!="All_borders":
                                        if Vid == self.Current_Vid:#If it is the current shape, we keep it the way it was
                                            Shape2= DoubleVar(value=shape[2].get())
                                        else:#If not, we must change and change DoubleVar to flaot (pickle does not accept DoubleVar)
                                            Shape2=shape[2].get()
                                        if shape[3] not in [Ars[3] for Ars in Vid.Analyses[1][Area]]:  # if this element did not exist
                                            Vid.Analyses[1][Area].append([shape[0], new_pts[0:len(shape[1])],Shape2, shape[3]])
                                        else:
                                            position = [Ars[3] for Ars in Vid.Analyses[1][Area]].index(shape[3])  # if an element with similar name was already present in the arena, we replace it and throw a warning.
                                            Vid.Analyses[1][Area][position] = [shape[0], new_pts[0:len(shape[1])],Shape2, shape[3]]
                                            Show_warn = True

                                        del new_pts[0:len(shape[1])]

                                    elif shape[0] == "Borders":
                                        new_shape2 = []
                                        for bd in shape[1]:
                                            new_shape2.append(new_pts[0:len(bd)])
                                            del new_pts[0:len(bd)]
                                        if Vid == self.Current_Vid:
                                            Shape2=DoubleVar(value=shape[2].get())
                                        else:
                                            Shape2=shape[2].get()
                                        if shape[3] not in [Ars[3] for Ars in Vid.Analyses[1][Area]]:
                                            Vid.Analyses[1][Area].append([shape[0], new_shape2, Shape2, shape[3]])
                                        else:
                                            position = [Ars[3] for Ars in Vid.Analyses[1][Area]].index(shape[3])
                                            Vid.Analyses[1][Area][position] = [shape[0], new_shape2, Shape2, shape[3]]
                                            Show_warn = True

        self.parent.destroy()
        self.boss.ready=True

        #If some elements were replaced in the selected arenas.
        if Show_warn:
            messagebox.showinfo(message=self.Messages["GError1"], title=self.Messages["GErrorT1"])

    def check_button(self, *arg):
        #The user can validate only if at least one element and one arena were selected
        if len(self.Liste_Vids.curselection())>0 and len(self.Liste_objects.curselection())>0:
            self.Validate_button.config(state="active", activebackground="green", bg="#6AED35")
        else:
            self.Validate_button.config(state="disable", activebackground="SystemButtonFace", bg="SystemButtonFace")


    def show_Arenas(self, event):
        #This function display an image of the video over which the cursor is in the list.
        #The contours of arenas are highlighted and if the cursor is over a specifi arena, this arena is highlighted itself
        index = self.Liste_Vids.index("@%s,%s" % (event.x, event.y))
        Which_part = 0
        if self.pointers[index][0].Cropped[0]:
            if len(self.pointers[index][0].Fusion) > 1:  # If the video result from a concatenation of two videos
                Which_part = [index0 for index0, Fu_inf in enumerate(self.pointers[index][0].Fusion) if Fu_inf[0] <= self.pointers[index][0].Cropped[1][0]][-1]

        capture = cv2.VideoCapture(self.pointers[index][0].Fusion[Which_part][1])  # Faster with opencv and the accuracy is not highly important here
        capture.set(cv2.CAP_PROP_POS_FRAMES, self.pointers[index][0].Cropped[1][0] - self.pointers[index][0].Fusion[Which_part][0])
        _, img = capture.read()
        img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if self.pointers[index][0].Cropped_sp[0]:
            img = img[self.pointers[index][0].Cropped_sp[1][0]:self.pointers[index][0].Cropped_sp[1][2], self.pointers[index][0].Cropped_sp[1][1]:self.pointers[index][0].Cropped_sp[1][3]]


        del capture
        mask= Function_draw_mask.draw_mask(self.pointers[index][0])
        self.Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.Arenas = Function_draw_mask.Organise_Ars(self.Arenas)

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

        ratio=max(img.shape[1]/self.max_can_width, img.shape[0]/self.max_can_height)
        img=cv2.resize(img,(int(img.shape[1]/ratio),int(img.shape[0]/ratio)))
        img2=self.image_to_show3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img))
        self.Canvas_shaow_Ar.create_image(0, 0, image=img2, anchor=NW)
        self.Canvas_shaow_Ar.config(height=img.shape[0], width=img.shape[1])

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
        self.check_button()


    def stay_on_top(self):
        #Maintain this window on top
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)
