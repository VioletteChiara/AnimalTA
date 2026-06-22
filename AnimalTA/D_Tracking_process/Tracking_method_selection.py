import time
from AnimalTA.D_Tracking_process import Do_the_track_multi, Do_the_track
import multiprocessing
import cv2
import os
from AnimalTA.A_General_tools import UserMessages
import pickle


#We determine whether it is better to use multiprocessing method or not:
def Choose_method(parent, Vid, folder, type, head_tail):
    parent.timer = 0
    parent.show_load()

    Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
    with open(Param_file, 'rb') as fp:
        Params = pickle.load(fp)
        Low_Priority = Params["Low_priority"]

    duration=(Vid.Cropped[1][1]-Vid.Cropped[1][0])/(Vid.Frame_rate[0] / Vid.Frame_rate[1])
    if duration < 50 or Vid.Back[0] == 2 or Low_Priority:  # Video beginning (after crop)
        method=0
    else:
        method=1
        '''#We run the analysis of 5 frames with no multiprocess and decord reader
        print("B")
        res_normal=Do_the_track.Do_tracking(parent, Vid, folder, type, portion=False, prev_row=None, arena_interest=None, test=True)
        print("C")
        parent.timer = 0.0001
        parent.show_load()

        one_every = Vid.Frame_rate[0] / Vid.Frame_rate[1]

        # We look at the time needed to load five frames using opencv
        if Vid.type!="Video":
            method=1 #If we have an image sequence, then the best strategy is to do multithreading (in case of video not always beneficial as decord does not work with multiprocessing)
        else:
            print("D")
            capture = cv2.VideoCapture(Vid.Fusion[0][1])
            deb = time.time()

            done = 0
            for i in range(0,int(one_every*5)+1,int(one_every)):
                while done<i:
                    capture.grab()  # Set starting frame
                    done+=1
                ret,frame=capture.retrieve()
            res_multi=time.time()-deb
            capture.release()
            print("E")

            parent.timer = 0.0002
            parent.show_load()

            #Using multiprocess is interesting only if the time win is enought to compensate slower oppening of the images + about 10 sec lost due to multithreading.
            print("Normal: "+str((res_normal/5)*duration))
            print("Multi: " + str((res_multi / 5) * duration+20))
            if (res_normal/5)*duration > (res_multi/5)*duration+20:
                method=1
            else:
                method=0
    '''

    if method==0:
        succeed = Do_the_track.Do_tracking(parent=parent, Vid=Vid, type=type, folder=folder, test=False, head_tail=head_tail)
        return succeed
    else:
        succeed = Do_the_track_multi.Do_tracking(parent=parent, Vid=Vid, type=type, folder=folder, head_tail=head_tail)
        return succeed

