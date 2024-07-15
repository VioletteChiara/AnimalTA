import time

import cv2
import decord
import numpy as np
from AnimalTA.A_General_tools import Class_stabilise, UserMessages
from AnimalTA.D_Tracking_process import security_settings_track
import os
import pickle


def Image_modif(Vid, start, end, one_every, Which_part, Prem_image_to_show, mask, or_bright, Extracted_cnts, Too_much_frame, AD, silhouette=False):
    if Vid.Stab[0]:
        prev_pts = Vid.Stab[1]
    last_grey=None#We keep here the last grey image for flicker correction
    penult_grey=None
    if Vid.Back[0] == 2:  # Dynamic background
        progressive_back = cv2.createBackgroundSubtractorMOG2(history=1000, varThreshold= Vid.Track[1][0], detectShadows=False)

    Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
    with open(Param_file, 'rb') as fp:
        Params = pickle.load(fp)

    relative_back = Params["Relative_background"]

    if Vid.Track[1][10][0] == 0:
        try:
            TMP_back = cv2.cvtColor(Vid.Back[1].copy(), cv2.COLOR_BGR2GRAY)
        except:
            TMP_back = Vid.Back[1].copy()
    else:
        try:
            TMP_back = cv2.cvtColor(Vid.Back[1].copy(), cv2.COLOR_GRAY2BGR)
        except:
            TMP_back = Vid.Back[1].copy()


    for frame in np.arange(start, end + one_every,one_every):  # We go frame by frame respecting the frame rate defined by user
        frame=round(frame)
        if Extracted_cnts.qsize()>=500:
            Too_much_frame.clear()
            Too_much_frame.wait()

        if security_settings_track.stop_threads:
            break

        if len(Vid.Fusion) > 1 and Which_part < (len(Vid.Fusion) - 1) and frame >= (Vid.Fusion[Which_part + 1][0]):
            Which_part += 1
            del security_settings_track.capture
            security_settings_track.capture = decord.VideoReader(Vid.Fusion[Which_part][1])
            security_settings_track.capture.seek(0)
            security_settings_track.activate_protection=False

        Timg = security_settings_track.capture[frame - Vid.Fusion[Which_part][0]].asnumpy()

        if security_settings_track.activate_protection:
            security_settings_track.capture.seek(0)

        if Vid.Cropped_sp[0]:
            Timg = Timg[Vid.Cropped_sp[1][0]:Vid.Cropped_sp[1][2],Vid.Cropped_sp[1][1]:Vid.Cropped_sp[1][3]]

        if Vid.Rotation == 1:
            Timg = cv2.rotate(Timg, cv2.ROTATE_90_CLOCKWISE)
        elif Vid.Rotation == 2:
            Timg = cv2.rotate(Timg, cv2.ROTATE_180)
        if Vid.Rotation == 3:
            Timg = cv2.rotate(Timg, cv2.ROTATE_90_COUNTERCLOCKWISE)

        kernel = np.ones((3, 3), np.uint8)
        # Stabilisation
        if Vid.Stab[0]:
            Timg = Class_stabilise.find_best_position(Vid=Vid, Prem_Im=Prem_image_to_show, frame=Timg, show=False, prev_pts=prev_pts)

        #Convert to grey
        if Vid.Track[1][10][0]==0:
            Timg = cv2.cvtColor(Timg, cv2.COLOR_BGR2GRAY)

        # Correct flicker
        if Vid.Track[1][9]:
            if frame==start:
                last_grey=Timg.copy()
                penult_grey=last_grey.copy()
            elif frame>start:
                Timg = cv2.addWeighted(last_grey, 0.5, Timg, 1 - 0.5, 0)
                if frame>start+1:
                    Timg = cv2.addWeighted(penult_grey, 0.5, Timg, 1 - 0.5, 0)

                penult_grey = last_grey.copy()
                last_grey = Timg.copy()

        # If we want to apply light correction:
        if Vid.Track[1][7]:
            grey = np.copy(Timg)
            if Vid.Mask[0]:
                bool_mask = mask[:, :].astype(bool)
            else:
                bool_mask = np.full(grey.shape, True)
            grey2 = grey[bool_mask]

            # Inspired from: https://stackoverflow.com/questions/57030125/automatically-adjusting-brightness-of-image-with-opencv
            brightness = np.sum(grey2) / (255 * grey2.size)  # Mean value
            ratio = brightness / or_bright
            Timg = cv2.convertScaleAbs(grey, alpha=1 / ratio, beta=0)

        img=Timg

        # Backgroud and threshold
        if Vid.Back[0] == 2:  # Dynamic background
            TMP_back = progressive_back.getBackgroundImage()
            if TMP_back is None:
                TMP_back=img.copy()
            progressive_back.apply(img)


        if Vid.Back[0] == 1 or Vid.Back[0] == 2: #A background is defined or dynamical background
            if Vid.Track[1][10][1] == 0:
                img = cv2.absdiff(TMP_back, img)
            elif Vid.Track[1][10][1] == 1:
                img = cv2.subtract(TMP_back, img)
            elif Vid.Track[1][10][1] == 2:
                img = cv2.subtract(img, TMP_back)

            if Vid.Track[1][10][2] == 1:
                img = img.astype(np.uint16)
                img = (img * 255) // TMP_back
                img = img.astype(np.uint8)

            if Vid.Track[1][10][0] == 1:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        elif Vid.Back[0]==0 and Vid.Track[1][10][0] == 1:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


        #Threshold
        if Vid.Back[0]==1 or Vid.Back[0]==2:# ABack subtraction
            _, img = cv2.threshold(img, Vid.Track[1][0], 255, cv2.THRESH_BINARY)

        elif Vid.Back[0]==0: #Adpative threshold
            if Vid.Track[1][10][1] == 2:
                img = cv2.bitwise_not(img)
            img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,  Vid.Track[1][0] + 1 , 10)





        # Mask
        if Vid.Mask[0]:
            img = cv2.bitwise_and(img, img, mask=mask)

        # Erosion
        if Vid.Track[1][1] > 0:
            img = cv2.erode(img, kernel, iterations=Vid.Track[1][1])

        # Dilation
        if Vid.Track[1][2] > 0:
            img = cv2.dilate(img, kernel, iterations=Vid.Track[1][2])

        # Find contours:
        cnts, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        kept_cnts=filter_cnts(cnts, Vid)
        Extracted_cnts.put([frame,kept_cnts])



def filter_cnts(cnts, Vid):
    kept_cnts = []  # We make a list of the contours that fit in the limitations defined by user
    cnts_areas=[]
    kept_cnts2=[]
    for cnt in cnts:
        cnt_area = cv2.contourArea(cnt)
        if float(Vid.Scale[0]) > 0:  # We convert the area in units
            cnt_area = cnt_area * (1 / float(Vid.Scale[0])) ** 2

        # Filter the contours by size
        if cnt_area >= Vid.Track[1][3][0] and cnt_area <= Vid.Track[1][3][1]:
            kept_cnts.append(cnt)
            cnts_areas.append(cnt_area)

        # Contours are sorted by area
        kept_cnts2= [kept_cnts[idx] for idx in np.argsort(cnts_areas)[::-1]]
    return(kept_cnts2)