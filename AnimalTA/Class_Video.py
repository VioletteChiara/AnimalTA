import cv2
import numpy as np
import ntpath
from AnimalTA import Class_stabilise, UserMessages
import os
from tkinter import messagebox
from tkinter import *

# Import language

f = open("Files/Language", "r", encoding="utf-8")
Language=(f.read())
f.close()
Messages = UserMessages.Mess[Language]


class Video:
    '''
    This class is used to save the information about the videos.
    '''
    def __init__(self, File_name, Folder):
        self.File_name=File_name #The name and path to the video file
        self.Folder=Folder #The folder in which the project is stored
        self.Name = ntpath.basename(self.File_name)#The name of the video
        capture=cv2.VideoCapture(self.File_name)#We choose to use Opencv and not decord here because opencv is much faster at initiation. But, opencv is not calculating correcty the number of frames in videos, also this value is recalculated later.
        self.shape=(int(capture.get(4)),int(capture.get(3)))#The width/height of the frames

        nb_fr=int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fr_rate = int(capture.get(cv2.CAP_PROP_FPS))
        self.Frame_nb=[nb_fr,nb_fr]  #The number of frame inside the file. 0 is the original number, 1 is the number after concatenation
        self.Frame_rate=[fr_rate,fr_rate]#First is the original fps, second the modified one (user option)

        self.corrected = False #When the video is implemented, the trackings have not been corrected
        self.Fusion=[[0,self.File_name]] #If videos are concatenated, the will be save here. The patern is [[0, name of 1st video],[number of frame before the second video (duration of 1st video) + 1, name of 2nd video],[number of frame before the thrid video (duration of 1st video + 2nd video)+1, name of 3rd video],...]

        self.Cropped=[False,[0,self.Frame_nb[0]-1]]#0 whether the video has been cropped or not, 1 where the video begins and stops after cropping [frame at the beginning of the video, frame at the end of the video]
        self.Stab = [False,None] #0: False if no stabilisation, true if stabilisation. 1: array with the coordinates for the stabilisation.
        self.Back = [False,[]] #0: False if no background defined,True if so. 1 Background used with this video.
        self.Mask = [False,[]] #0: False if no mask defined,True if so. 1 List of shapes used to draw the mask.
        self.Scale=[1,"px"] # The scale and its unit
        self.liste_of_colors=[] # The list of colors used to draw the targets and their trajectories
        self.Tracked=False #Whether the video has already been tracked or not

        self.Track=[False,[50,0,0,[0.0001,5000],[0,1],500,[1], False]]
        #0 Tresh , 1 Erosion ,2 Dilation ,3 Area ,4 Compact ,5 Distance (px), 6 number of targets, 7 Apply light correction
        self.Smoothed=[0,0]
        self.Analyses=[0,[[] for n in self.Track[1][6]],[0,1,2],0]#0 = seuil de mouvement, 1=list of elements of interest (one [] per arena at the implementation), 2=style d'exploration(2.0 = type, 2.1=surface, 2.2=parametres pour cercles, 3=dist_nei)

        self.Color_profiles="default.CPR"

    def check_coos(self):
        point_pos = self.Name.rfind(".")
        # We check if the video has already been tracked:
        file_tracked = self.Folder + "/coordinates/" + self.Name[:point_pos] + "_Coordinates.csv"
        if os.path.isfile(file_tracked):
            self.Tracked = True
        else:
            self.Tracked = False

    def clear_files(self):
        '''If we need to remove the tracking that were done (i.e. if the user want to change tracking parameters while the tracking has already be done)'''
        point_pos = self.Name.rfind(".")
        # Suppress coordinates from tracking
        file_tracked = self.Folder + "/coordinates/" + self.Name[:point_pos] + "_Coordinates.csv"
        file_tracked_with_corr = self.Folder + "/corrected_coordinates/" + self.Name[:point_pos] + "_Corrected.csv"

        while True:
            try:
                if os.path.isfile(file_tracked):
                    os.rename(file_tracked,file_tracked)

                if os.path.isfile(file_tracked_with_corr):
                    os.rename(file_tracked_with_corr, file_tracked_with_corr)

                if os.path.isfile(file_tracked):
                    os.remove(file_tracked)

                if os.path.isfile(file_tracked_with_corr):
                    os.remove(file_tracked_with_corr)

                self.Tracked=False
                self.Smoothed=[0,0]
                self.Analyses=[0,[[] for n in self.Track[1][6]],[0,1,2],0]#0 = movement threshold, 1=list of elements of interest, 2=exploration kind of measurement(2.0 = type, 2.1=area, 2.2=parameter for circular mesh), 3=inter-individual threshold
                return True

            except PermissionError as e:
                Response = messagebox.askretrycancel(title=Messages["TError"],message=Messages["Error_Permission"].format(e.filename))
                if not Response:
                    return False



    def make_back(self,  Nb_Back=10):
        '''This function is used to create a background in which the moving targets are erased.
        It works by calculating the median value of all the pixels for N=Nb_Back images taken at regular intervals.
        '''
        Liste_Images=[]
        i = 0
        #intervals=how much space between two frame we will use
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

        Capture = cv2.VideoCapture(self.Fusion[0][1])
        for image_ID in Rank:
            Which_part=0
            if len(self.Fusion) > 1:  # If the video results from concatenation
                Which_part = [index for index, Fu_inf in enumerate(self.Fusion) if Fu_inf[0] <= image_ID][-1]
                Capture.release()
                Capture = cv2.VideoCapture(self.Fusion[Which_part][1])
            Capture.set(cv2.CAP_PROP_POS_FRAMES, int(image_ID-self.Fusion[Which_part][0]))
            _, frame=Capture.read()

            if i==0:
                Prem_img=np.copy(frame)

            if self.Stab[0] and i>0:#If the user choose the stabilization tool
                frame = Class_stabilise.find_best_position(Vid=self, Prem_Im=Prem_img, frame=frame, show=False)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            Liste_Images.append(np.copy(frame))
            i += 1
        Capture.release()

        Liste_Images[0] = np.median(Liste_Images, axis=0)#We calculate the median value for all pixels
        Liste_Images[0]=Liste_Images[0].astype("uint8")

        self.Back[0]=True
        self.Back[1] = Liste_Images[0]#Save the background

    def effacer_back(self):
        #Remove the background associated with the video
        self.Back[0]=False
        self.Back[1]=[]

    def effacer_mask(self):
        # Remove the arenas associated with the video
        self.Mask[0]=False
        self.Mask[1]=[]
