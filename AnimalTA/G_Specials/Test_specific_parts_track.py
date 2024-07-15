import cv2
import decord
from AnimalTA.A_General_tools import Function_draw_mask as Dr, UserMessages, Message_simple_question as MsgBox
from AnimalTA.D_Tracking_process import Function_prepare_images, Function_assign_cnts, security_settings_track
import numpy as np
from tkinter import *
import threading
import queue


'''
To improve the speed of the tracking, we will separate the work in 3 threads.
1. Image loading, and modifications (stabilization, light correction, greyscale...) until contours are get
2. Target assignment and data recording
3. k-means clustering if two targets are touching each others.
'''


def collect_silhouettes(Vid):
    '''This is the main tracking function of the program.
    parent=container (main window)
    Vid=current video
    portion= True if it is a rerun of the tracking over a short part of the video (for corrections)
    prev_row=If portion is True, this correspond to the last known coordinates of the targets.
    '''

    # if the user choose to reduce the frame rate.
    one_every = Vid.Frame_rate[0] / Vid.Frame_rate[1]
    Which_part = 0

    mask = Dr.draw_mask(Vid)  # A mask for the arenas
    start = Vid.Cropped[1][0]  # Video beginning (after crop)
    one_every=max(1,round((Vid.Cropped[1][1]-Vid.Cropped[1][0])/200))
    end = Vid.Cropped[1][1]-1-one_every  # Video end (after crop)



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

    AD=DoubleVar()

    Extracted_cnts = queue.Queue()
    Too_much_frame=threading.Event()


    cnts=Function_prepare_images.Image_modif(Vid, start, end, one_every, Which_part, Prem_image_to_show, mask, or_bright, Extracted_cnts, Too_much_frame, AD, silhouette=False)
    print(cnts)

