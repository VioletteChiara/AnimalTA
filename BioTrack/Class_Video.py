import cv2
import numpy as np
import ntpath
from BioTrack import Class_stabilise
import os
import decord


class Video:
    def __init__(self, File_name, Folder):
        self.File_name=File_name #The name and directory of the file
        self.Folder=Folder
        self.Name = ntpath.basename(self.File_name)
        capture=cv2.VideoCapture(self.File_name)
        ret, img = capture.read()
        self.shape=(img.shape[0],img.shape[1])
        self.corrected=False

        self.Frame_nb=[int(capture.get(cv2.CAP_PROP_FRAME_COUNT)),int(capture.get(cv2.CAP_PROP_FRAME_COUNT))]  #The number of frame inside the file
        self.Frame_rate=[capture.get(cv2.CAP_PROP_FPS),capture.get(cv2.CAP_PROP_FPS)]#First is the original fps, second the modified one

        self.Fusion=[[0,self.File_name]]

        self.Cropped=[False,[0,self.Frame_nb[0]]]
        self.Stab = False #first value = 0 if no stabilisation, 1 if stabilisation. Second value = array with the coordinates for the stabilisation.
        self.Back = [False,[]] #Background used with this video
        self.Mask = [False,[]] #Mask used for this video
        self.Scale=[1,"px"]
        self.liste_of_colors=[]
        self.Arenas=[]
        self.Tracked=False

        self.Track=[False,[0,0,0,[0.0001,1000000],[0,1],1000000,[1]]]
        #0 Tresh , 1 Erosion ,2 Dilation ,3 Area ,4 Compact ,5 Distance, 6 Kind of track
        self.Smoothed=[0,0]
        self.Analyses=[0,[]]#0 = seuil de mouvement, 1=liste des zones

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
        self.Analyses=[0,[[] for n in self.Track[1][6]],[0,1,2]]#0 = seuil de mouvement, 1=liste des zones, 2=style d'exploration(2.0 = type, 2.1=surface, 2.2=parametres pour cercles)

    def make_back(self,  Nb_Back=10):
        Capture = decord.VideoReader(self.File_name)
        Liste_Images=[]
        i = 0
        if self.Cropped[0]:
            Rank=range(self.Cropped[1][0], self.Cropped[1][1], int((self.Cropped[1][1]-self.Cropped[1][0]) / Nb_Back))
        else:
            Rank=range(0, self.Frame_nb[0], int(self.Frame_nb[0]/ Nb_Back))

        for image_ID in Rank:
            Which_part=0
            if len(self.Fusion) > 1:  # Si on a plus d'une video
                Which_part = [index for index, Fu_inf in enumerate(self.Fusion) if Fu_inf[0] <= image_ID][-1]
                if Which_part != 0:  # si on veut aller à un endroit différent
                    Capture = decord.VideoReader(self.Fusion[Which_part][1])

            frame = Capture[image_ID-self.Fusion[Which_part][0]].asnumpy()

            if i==0:
                Prem_img=np.copy(frame)

            if self.Stab and i>0:
                frame = Class_stabilise.find_best_position(Prem_Im=Prem_img, frame=frame, show=False)

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