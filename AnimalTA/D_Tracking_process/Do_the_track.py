import cv2
import decord
from AnimalTA.A_General_tools import Function_draw_mask as Dr, UserMessages, Message_simple_question as MsgBox
from AnimalTA.D_Tracking_process import Function_prepare_images, Function_assign_cnts, security_settings_track
import numpy as np
import os
from tkinter import *
import threading
import queue
import pickle
import sys
import re

'''
To improve the speed of the tracking, we will separate the work in 3 threads.
1. Image loading, and modifications (stabilization, light correction, greyscale...) until contours are get
2. Target assignment and data recording
3. k-means clustering if two targets are touching each others.
'''


security_settings_track.stop_threads=False




def Do_tracking(parent, Vid, folder, type, portion=False, prev_row=None, arena_interest=None):
    '''This is the main tracking function of the program.
    parent=container (main window)
    Vid=current video
    portion= True if it is a rerun of the tracking over a short part of the video (for corrections)
    prev_row=If portion is True, this correspond to the last known coordinates of the targets.
    '''
    security_settings_track.stop_threads=False
    # Language importation
    Language = StringVar()
    f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
    Language.set(f.read())
    f.close()
    Messages = UserMessages.Mess[Language.get()]

    Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
    with open(Param_file, 'rb') as fp:
        Params = pickle.load(fp)
        use_Kalman=Params["Use_Kalman"]

    # Where coordinates will be saved, if the folder did not exists, it is created.
    if Vid.User_Name == Vid.Name:
        file_name = Vid.Name
        point_pos = file_name.rfind(".")
        if file_name[point_pos:].lower()!=".avi":
            file_name = Vid.User_Name
        else:
            file_name = file_name[:point_pos]
    else:
        file_name = Vid.User_Name

    if not portion:
        if not os.path.isdir(os.path.join(folder,"coordinates")):
            os.makedirs(os.path.join(folder, "coordinates"))
    else:
        if not os.path.isdir(os.path.join(folder,"TMP_portion")):
            os.makedirs(os.path.join(folder,"TMP_portion"))

    if portion:
        To_save = os.path.join(folder, "TMP_portion", file_name + "_TMP_portion_Coordinates.csv")
    else:
        To_save = os.path.join(folder, "Coordinates", file_name + "_Coordinates.csv")

    # if the user choose to reduce the frame rate.
    one_every = Vid.Frame_rate[0] / Vid.Frame_rate[1]
    Which_part = 0

    mask = Dr.draw_mask(Vid)  # A mask for the arenas
    start = Vid.Cropped[1][0]  # Video beginning (after crop)
    end = Vid.Cropped[1][1]  # Video end (after crop)

    if Vid.Cropped[0]:
        if len(Vid.Fusion) > 1:  # If the video results from concatenated videos
            Which_part = [index for index, Fu_inf in enumerate(Vid.Fusion) if Fu_inf[0] <= start][-1]


    security_settings_track.activate_protection=False
    security_settings_track.first_protection=False


    security_settings_track.capture = decord.VideoReader(Vid.Fusion[Which_part][1])  # Open video
    Prem_image_to_show = security_settings_track.capture[start - Vid.Fusion[Which_part][0]].asnumpy()  # Take the first image
    security_settings_track.capture.seek(0)
    if Vid.Cropped_sp[0]:
        Prem_image_to_show = Prem_image_to_show[Vid.Cropped_sp[1][0]:Vid.Cropped_sp[1][2],Vid.Cropped_sp[1][1]:Vid.Cropped_sp[1][3]]

    try:  # Old version of AnimalTA did not had the option for lightness correction, so Vid.Track[1][7] would result in error in case of old .ata files.
        if Vid.Track[1][7]:  # If True, the user chose to correct the lightness, this code allows to take the average lightness value of the first frame and to calculate the first and third quartiles of lightness values.
            if Vid.Back[0]!=1:
                grey = cv2.cvtColor(Prem_image_to_show, cv2.COLOR_BGR2GRAY)
            else:
                grey = Vid.Back[1].copy()

            if Vid.Mask[0]:  # If there were arenas defined by the user, we do the correction only for what happen inside these arenas.
                maskT = mask[:, :].astype(bool)
                or_bright = np.sum(grey[maskT]) / (255 * grey[maskT].size)  # Mean value
            else:
                or_bright = np.sum(grey) / (255 * grey.size)  # Mean value
            del grey
        else:
            or_bright=None
    except Exception as e:
        print(e)

    # We identify the different arenas:
    if type=="fixed":
        if Vid.Mask[0]:
            Arenas_with_holes, Arenas = Dr.exclude_inside(mask)
            Arenas = Dr.Organise_Ars(Arenas)
        else:
            Arenas = [np.array([[[0, 0]], [[Vid.shape[1], 0]], [[Vid.shape[1], Vid.shape[0]]], [[0, Vid.shape[0]]]], dtype="int32")]

        if portion and arena_interest!=None:
            Arenas = [Arenas[arena_interest]]


    elif type=="variable":
        if Vid.Mask[0]:
            Arenas_with_holes, Main_Arenas = Dr.exclude_inside(mask)
            Main_Arenas = Dr.Organise_Ars(Main_Arenas)

        else:
            Main_Arenas = [np.array([[[0, 0]], [[Vid.shape[1], 0]], [[Vid.shape[1], Vid.shape[0]]], [[0, Vid.shape[0]]]], dtype="int32")]

        Arenas = []
        Main_Arenas_image = []
        Main_Arenas_Bimage = []

        for Ar in range(len(Main_Arenas)):
            empty = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
            empty = cv2.drawContours(empty, [Main_Arenas[Ar]], -1, 255, -1)
            Main_Arenas_image.append(mask.copy())
            empty = cv2.drawContours(empty, Vid.Entrance[Ar], -1, 255, -1)
            mask = cv2.drawContours(mask, Vid.Entrance[Ar], -1, 255, -1)
            new_AR, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            Arenas.append(new_AR[0])

            empty = cv2.drawContours(empty, Vid.Entrance[Ar], -1, 0, -1)
            Main_Arenas_Bimage.append(empty)

    Extracted_cnts = queue.Queue()
    Too_much_frame=threading.Event()

    AD=DoubleVar()
    Th_extract_cnts=threading.Thread(target=Function_prepare_images.Image_modif, args=(Vid, start, end, one_every, Which_part, Prem_image_to_show, mask, or_bright, Extracted_cnts, Too_much_frame, AD))

    if type=="fixed":
        Th_associate_cnts=threading.Thread(target=Function_assign_cnts.Treat_cnts_fixed, args=(Vid, Arenas, start, end, prev_row, Extracted_cnts, Too_much_frame, Th_extract_cnts, To_save, portion, one_every, AD, use_Kalman))
    elif type=="variable":
        keep_entrance=Params["Keep_entrance"]
        Th_associate_cnts=threading.Thread(target=Function_assign_cnts.Treat_cnts_variable, args=(Vid, Arenas, Main_Arenas_image, Main_Arenas_Bimage, start, end, prev_row, Extracted_cnts, Too_much_frame, Th_extract_cnts, To_save, portion, one_every, AD, not keep_entrance, use_Kalman))

    Th_extract_cnts.start()
    Th_associate_cnts.start()

    while Th_associate_cnts.is_alive():
        parent.timer=(AD.get()-start)/(end + one_every - start)
        parent.show_load()

        overload = security_settings_track.check_memory_overload()#Avoid memory leak problems
        if overload==1:
            break

        elif overload==0:
            security_settings_track.activate_protection=True

        elif overload==-1:
            security_settings_track.activate_protection=False

    parent.timer = 1
    parent.show_load()


    if overload==1:  # To prevent the effects of memory leak.
        security_settings_track.stop_threads = True
        question = MsgBox.Messagebox(parent=parent, title=Messages["TError_memory"],
                                     message=Messages["Error_memory"],
                                     Possibilities=Messages["Continue"])
        parent.wait_window(question)

        del security_settings_track.capture
        if type == "fixed":
            return (False)
        elif type == "variable":
            return (False, _)

    Th_extract_cnts.join()
    Th_associate_cnts.join()


    if overload!=1:
        del security_settings_track.capture
        if security_settings_track.stop_threads:
            if type=="fixed":
                return (False)
            elif type=="variable":
                return (False,_)
        else:
            if type == "fixed":
                return (True)
            elif type=="variable":
                return (True,security_settings_track.ID_kepts)


def urgent_close(Vid):
    security_settings_track.stop_threads = True

