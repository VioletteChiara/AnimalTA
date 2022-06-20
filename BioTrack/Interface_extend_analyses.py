from tkinter import *
from BioTrack import UserMessages, Function_extend_analyses, Function_draw_mask
import cv2
import numpy as np
import PIL

class Lists(Frame):
    def __init__(self, parent, boss, liste_videos, Current_Vid, Current_Area, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss
        self.grid()
        self.Current_Vid=Current_Vid
        self.Current_Area=Current_Area
        self.liste_videos=liste_videos


        self.Language = StringVar()
        f = open("Files/Language", "r")
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

        #Listbox of shapes in actual arena
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

        self.to_remove_sel=[]
        self.pointers=[]
        for Vid in liste_videos:
            if Vid.Tracked:
                self.Liste_Vids.insert(END, self.Messages["Video"] +": "+Vid.Name)
                self.Liste_Vids.itemconfig("end", bg="grey75")
                if Vid==Current_Vid:
                    self.Liste_Vids.itemconfig("end", fg='red')
                self.to_remove_sel.append(self.Liste_Vids.size()-1)

                self.pointers.append([Vid,None])
                AID = 0
                for Arena in Vid.Analyses[1]:
                    if not (AID==Current_Area and Vid == Current_Vid):
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


        self.Canvas_shaow_Ar=Canvas(self)
        self.Canvas_shaow_Ar.grid(row=0, column=5, rowspan=4, sticky="nsew")

        self.stay_on_top()
        self.boss.ready=False
        self.parent.protocol("WM_DELETE_WINDOW", self.close)

    def select_all_areas(self):
        if not self.all_sel_areas:
            self.Liste_Vids.select_set(0, END)
            self.Button_sel_al_o.config(text=self.Messages["ExtendB2"])
            self.all_sel_areas=True
        else:
            self.Liste_Vids.selection_clear(0, END)
            self.Button_sel_al_o.config(text=self.Messages["ExtendB1"])
            self.all_sel_areas=False

        for index in range(len(self.to_remove_sel)):
            self.Liste_Vids.selection_clear(self.to_remove_sel[index])
        self.check_button()#On actualise le bouton de validation


    def select_all_objs(self):
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
        self.parent.destroy()
        self.boss.ready=True

    def validate(self):
        list_of_shapes=[self.Current_Vid.Analyses[1][self.Current_Area][i] for i in self.Liste_objects.curselection()]

        mask = Function_draw_mask.draw_mask(self.Current_Vid)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        Or_Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        Or_Arenas = Function_draw_mask.Organise_Ars(Or_Arenas)

        Np_style_pts=np.array([self.pointers[i] for i in self.Liste_Vids.curselection()])
        list_of_vids =[]
        for Vid in Np_style_pts[:,0]:
            if Vid not in list_of_vids:
                list_of_vids.append(Vid)

        for Vid in list_of_vids:#Pour chaque Video qui contient au moins une arène selectionnée
            mask = Function_draw_mask.draw_mask(Vid)
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=1)
            Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            Arenas = Function_draw_mask.Organise_Ars(Arenas)

            for Area in range(len(Arenas)):
                if Area in [self.pointers[i][1] for i in self.Liste_Vids.curselection() if self.pointers[i][0]==Vid]:#Si l'arène a été selectionnée
                    list_of_points = []
                    if not (Area==self.Current_Area and Vid == self.Current_Vid):
                        for shape in list_of_shapes:
                            #we first check if an area with similar name has already been defined:
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

                                if shape[3] not in [Ars[3] for Ars in Vid.Analyses[1][Area]]:#Si cette forme n'a pas encore été décrite
                                    Vid.Analyses[1][Area].append(["All_borders", [], Shape2, shape[3]])
                                else:
                                    position=[Ars[3] for Ars in Vid.Analyses[1][Area]].index(shape[3])#S'il y a déjà une forme avec ce nom elle est remplacée + warning
                                    Vid.Analyses[1][Area][position]=["All_borders", [], Shape2, shape[3]]

                        if len(list_of_points) > 0:
                            work, new_pts = Function_extend_analyses.match_shapes(Arenas[Area], Or_Arenas[self.Current_Area],list_of_points)
                            if work:
                                for shape in list_of_shapes:
                                    if shape[0]!="Borders" and shape[0]!="All_borders":
                                        if Vid == self.Current_Vid:#Si c'est la vidéo actuelle, on laisse style tkinter
                                            Shape2= DoubleVar(value=shape[2].get())
                                        else:#Si on change de video on change car pickle ne suporte pas les objects de tkinter
                                            Shape2=shape[2].get()
                                        if shape[3] not in [Ars[3] for Ars in Vid.Analyses[1][Area]]:  # Si cette forme n'a pas encore été décrite
                                            Vid.Analyses[1][Area].append([shape[0], new_pts[0:len(shape[1])],Shape2, shape[3]])
                                        else:
                                            position = [Ars[3] for Ars in Vid.Analyses[1][Area]].index(shape[3])  # S'il y a déjà une forme avec ce nom elle est remplacée + warning
                                            Vid.Analyses[1][Area][position] = [shape[0], new_pts[0:len(shape[1])],Shape2, shape[3]]

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
                                        if shape[3] not in [Ars[3] for Ars in Vid.Analyses[1][Area]]:  # Si cette forme n'a pas encore été décrite
                                            Vid.Analyses[1][Area].append([shape[0], new_shape2, Shape2, shape[3]])
                                        else:
                                            position = [Ars[3] for Ars in Vid.Analyses[1][Area]].index(shape[3])  # S'il y a déjà une forme avec ce nom elle est remplacée + warning
                                            Vid.Analyses[1][Area][position] = [shape[0], new_shape2, Shape2, shape[3]]

        self.parent.destroy()
        self.boss.ready=True



    def check_button(self, *arg):
        if len(self.Liste_Vids.curselection())>0 and len(self.Liste_objects.curselection())>0:
            self.Validate_button.config(state="active", activebackground="green", bg="green")
        else:
            self.Validate_button.config(state="disable", activebackground="SystemButtonFace", bg="SystemButtonFace")


    def show_Arenas(self, event):
        index = self.Liste_Vids.index("@%s,%s" % (event.x, event.y))
        Which_part = 0
        if self.pointers[index][0].Cropped[0]:
            if len(self.pointers[index][0].Fusion) > 1:  # Si on a plus d'une video
                Which_part = \
                [index for index, Fu_inf in enumerate(self.pointers[index][0].Fusion) if Fu_inf[0] <= self.pointers[index][0].Cropped[1][0]][-1]

        capture = cv2.VideoCapture(self.pointers[index][0].Fusion[Which_part][1])  # Faster with opencv
        capture.set(cv2.CAP_PROP_POS_FRAMES, self.pointers[index][0].Cropped[1][0] - self.pointers[index][0].Fusion[Which_part][0])
        _, img = capture.read()
        img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        del capture
        mask=Function_draw_mask.draw_mask(self.pointers[index][0])
        self.Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.Arenas = self.Organise_Ars(self.Arenas)

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
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)

    def Organise_Ars(self, Arenas):
        heights=[]
        centers=[]
        ID=0
        for Ar in Arenas:
            x,y,w,h=cv2.boundingRect(Ar)
            heights.append(h)
            centers.append([ID,y+(h/2),x+(w/2)])
            ID+=1

        rows=[]
        centers=np.array(centers, dtype=int)
        while len(centers)>0:
            first_row=np.where(((min(centers[:,1])-max(heights)/2)<np.array(centers[:,1])) & (np.array(centers[:,1])<(min(centers[:,1])+max(heights)/2)))
            cur_row=centers[first_row]
            cur_row=cur_row[cur_row[:,2].argsort()] [:,0]
            rows=rows+list(cur_row)
            centers=np.delete(centers, first_row, axis=0)
        return [Arenas[place] for place in rows]