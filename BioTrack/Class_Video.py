import cv2
import numpy as np
import ntpath
from BioTrack import Class_stabilise
import os


class Video:
    def __init__(self, File_name, Folder):
        self.File_name=File_name #The name and directory of the file
        self.Folder=Folder
        self.Name = ntpath.basename(self.File_name)
        capture=cv2.VideoCapture(self.File_name)#We choose to use Opencv and not decord here because opencv is much faster at initiation
        self.shape=(int(capture.get(4)),int(capture.get(3)))

        nb_fr=int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fr_rate = int(capture.get(cv2.CAP_PROP_FPS))
        self.Frame_nb=[nb_fr,nb_fr]  #The number of frame inside the file
        self.Frame_rate=[fr_rate,fr_rate]#First is the original fps, second the modified one

        self.corrected = False
        self.Fusion=[[0,self.File_name]]

        self.Cropped=[False,[0,self.Frame_nb[0]-1]]
        self.Stab = [False,None] #first value = 0 if no stabilisation, 1 if stabilisation. Second value = array with the coordinates for the stabilisation.
        self.Back = [False,[]] #Background used with this video
        self.Mask = [False,[]] #Mask used for this video
        self.Scale=[1,"px"]
        self.liste_of_colors=[]
        self.Arenas=[]
        self.Tracked=False

        self.Track=[False,[0,0,0,[0.0001,1000000],[0,1],1000000,[1]]]
        #0 Tresh , 1 Erosion ,2 Dilation ,3 Area ,4 Compact ,5 Distance (px), 6 number of targets
        self.Smoothed=[0,0]
        self.Analyses=[0,[[] for n in self.Track[1][6]],[0,1,2],0]#0 = seuil de mouvement, 1=list of elements of interest (one [] per arena at the implementation), 2=style d'exploration(2.0 = type, 2.1=surface, 2.2=parametres pour cercles, 3=dist_nei)

        self.Color_profiles="default.CPR"

    def check_coos(self):
        point_pos = self.Name.rfind(".")
        # On verifie s'il y a des coos:
        file_tracked = self.Folder + "/coordinates/" + self.Name[:point_pos] + "_Coordinates.csv"
        if os.path.isfile(file_tracked):
            self.Tracked = True
        else:
            self.Tracked = False

    def clear_files(self):
        point_pos = self.Name.rfind(".")
        # Suprime les coos
        file_tracked = self.Folder + "/coordinates/" + self.Name[:point_pos] + "_Coordinates.csv"
        if os.path.isfile(file_tracked):
            os.remove(file_tracked)
        # Suprime les coos corrigées
        file_tracked_with_corr = self.Folder + "/corrected_coordinates/" + self.Name[:point_pos] + "_Corrected.csv"
        if os.path.isfile(file_tracked_with_corr):
            os.remove(file_tracked_with_corr)

        self.Tracked=False
        self.Smoothed=[0,0]
        self.Analyses=[0,[[] for n in self.Track[1][6]],[0,1,2],0]#0 = seuil de mouvement, 1=liste des zones, 2=style d'exploration(2.0 = type, 2.1=surface, 2.2=parametres pour cercles), 3=nter-ind thresh


    def make_back(self,  Nb_Back=10):
        Liste_Images=[]
        i = 0
        if self.Cropped[0]:
            if int((self.Cropped[1][1]-self.Cropped[1][0]) / Nb_Back)>0:
                intervals=int((self.Cropped[1][1]-self.Cropped[1][0]) / Nb_Back)
            else:
                intervals=1
            Rank=range(self.Cropped[1][0], self.Cropped[1][1], intervals)
        else:
            if int(self.Frame_nb[0]/ Nb_Back)>0:
                intervals=int((self.Cropped[1][1]-self.Cropped[1][0]) / Nb_Back)
            else:
                intervals=1
            Rank=range(0, self.Frame_nb[0], intervals)

        for image_ID in Rank:
            Which_part=0
            if len(self.Fusion) > 1:  # Si on a plus d'une video
                Which_part = [index for index, Fu_inf in enumerate(self.Fusion) if Fu_inf[0] <= image_ID][-1]


            Capture = cv2.VideoCapture(self.Fusion[Which_part][1])
            Capture.set(cv2.CAP_PROP_POS_FRAMES, int(image_ID-self.Fusion[Which_part][0]))
            _, frame=Capture.read()

            if i==0:
                Prem_img=np.copy(frame)

            if self.Stab[0] and i>0:
                frame = Class_stabilise.find_best_position(Vid=self, Prem_Im=Prem_img, frame=frame, show=False)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            Liste_Images.append(np.copy(frame))
            i += 1


        Liste_Images[0] = np.median(Liste_Images, axis=0)
        Liste_Images[0]=Liste_Images[0].astype("uint8")


        self.Back[0]=True
        self.Back[1] = Liste_Images[0]

    def effacer_back(self):
        self.Back[0]=False
        self.Back[1]=[]

    def effacer_mask(self):
        self.Mask[0]=False
        self.Mask[1]=[]


    #def change_loc(self):
    #    self.File_name="G:/BioTrack_For_Papa/Videos/Poisson preference test1 (beaucoup de videos nombre d'individus variable et arenes rectangulaires)/"+self.Name