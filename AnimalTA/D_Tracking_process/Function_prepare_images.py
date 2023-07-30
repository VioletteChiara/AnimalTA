import time

import cv2
import decord
import numpy as np
from AnimalTA.A_General_tools import Class_stabilise
from AnimalTA.D_Tracking_process import security_settings_track
import math
import operator

def Image_modif(Vid, start, end, one_every, Which_part, Prem_image_to_show, mask, or_bright, Extracted_cnts, Too_much_frame, AD):
    if Vid.Stab[0]:
        prev_pts = Vid.Stab[1]
    last_grey=None#We keep here the last grey image for flicker correction
    penult_grey=None
    saved_future=[]
    for frame in range(start, end + one_every,one_every):  # We go frame by frame respecting the frame rate defined by user
        if Extracted_cnts.qsize()>=500:
            Too_much_frame.clear()
            Too_much_frame.wait()

        if security_settings_track.stop_threads:
            break

        if frame == start and Vid.Back[0]==2:#If it is the first frame and we choose dynamical background, we first treat the 90 first frames
            fr_to_do=range(start, min([start + 100*one_every ,end + one_every]),one_every)
        elif Vid.Back[0]==2:#Else we do frame by frame
            fr_to_do=[frame+100*one_every]
            if fr_to_do[0]>end + one_every:
                fr_to_do=[]
        else:
            fr_to_do=[frame]

        for frame_for_fut in fr_to_do:
            if frame==start:
                AD.set(frame_for_fut / len(fr_to_do))
            if len(Vid.Fusion) > 1 and Which_part < (len(Vid.Fusion) - 1) and frame_for_fut >= (Vid.Fusion[Which_part + 1][0]):
                Which_part += 1
                del security_settings_track.capture
                security_settings_track.capture = decord.VideoReader(Vid.Fusion[Which_part][1])
                security_settings_track.capture.seek(0)
                security_settings_track.activate_protection=False

            Timg = security_settings_track.capture[frame_for_fut - Vid.Fusion[Which_part][0]].asnumpy()

            if security_settings_track.activate_protection:
                security_settings_track.capture.seek(0)

            if Vid.Cropped_sp[0]:
                Timg = Timg[Vid.Cropped_sp[1][0]:Vid.Cropped_sp[1][2],Vid.Cropped_sp[1][1]:Vid.Cropped_sp[1][3]]

            kernel = np.ones((3, 3), np.uint8)
            # Stabilisation
            if Vid.Stab[0]:
                Timg = Class_stabilise.find_best_position(Vid=Vid, Prem_Im=Prem_image_to_show, frame=Timg, show=False, prev_pts=prev_pts)

            Timg = cv2.cvtColor(Timg, cv2.COLOR_BGR2GRAY)

            # Correct flicker
            if Vid.Track[1][9]:
                if frame_for_fut==start:
                    last_grey=Timg.copy()
                    penult_grey=last_grey.copy()
                elif frame_for_fut>start:
                    Timg = cv2.addWeighted(last_grey, 0.5, Timg, 1 - 0.5, 0)
                    if frame_for_fut>start+1:
                        Timg = cv2.addWeighted(penult_grey, 0.5, Timg, 1 - 0.5, 0)

                    penult_grey = last_grey.copy()
                    last_grey = Timg.copy()

            # If we want to apply light correction:
            if Vid.Track[1][7]:
                grey = np.copy(Timg)
                if Vid.Mask[0]:
                    bool_mask = mask[:, :, 0].astype(bool)
                else:
                    bool_mask = np.full(grey.shape, True)
                grey2 = grey[bool_mask]

                # Inspired from: https://stackoverflow.com/questions/57030125/automatically-adjusting-brightness-of-image-with-opencv
                brightness = np.sum(grey2) / (255 * grey2.size)  # Mean value
                ratio = brightness / or_bright
                Timg = cv2.convertScaleAbs(grey, alpha=1 / ratio, beta=0)

            if Vid.Back[0] == 2:
                saved_future.append(Timg)


        if frame != start and Vid.Back[0] == 2:
            saved_future.pop(0)

        if Vid.Back[0] == 2:#If it was the last one of the first group and that we were saving future images
            img=saved_future[0].copy()
        else:
            img=Timg.copy()



        # Backgroud and threshold
        if Vid.Back[0]==1:
            img = cv2.subtract(Vid.Back[1], img) + cv2.subtract(img, Vid.Back[1])

        if Vid.Back[0]==2:
            if len(saved_future)>4:
                of_int=list(range(len(saved_future)-1,0,-math.floor(len(saved_future)/4)))
                batch=operator.itemgetter(*of_int)(saved_future)
                Tim1=batch[0].copy()

                ref_frame = np.median(batch, axis=0)  # We calculate the median value for all pixels
                ref_frame = ref_frame.astype("uint8")
                img = cv2.subtract(ref_frame, img) + cv2.subtract(img, ref_frame)

            else:
                img = cv2.subtract(img, img) + cv2.subtract(img, img)

        if Vid.Back[0] == 1 or Vid.Back[0] == 2:
            _, img = cv2.threshold(img, Vid.Track[1][0], 255, cv2.THRESH_BINARY)

        elif Vid.Back[0]==0:
            odd_val = int(Vid.Track[1][0]) + (1 - (int(Vid.Track[1][0]) % 2))
            img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, odd_val,10)

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


        kept_cnts = []  # We make a list of the contours that fit in the limitations defined by user
        for cnt in cnts:
            cnt_area = cv2.contourArea(cnt)
            if float(Vid.Scale[0]) > 0:  # We convert the area in units
                cnt_area = cnt_area * (1 / float(Vid.Scale[0])) ** 2

            # Filter the contours by size
            if cnt_area >= Vid.Track[1][3][0] and cnt_area <= Vid.Track[1][3][1]:
                kept_cnts.append(cnt)

            # Contours are sorted by area
            kept_cnts = sorted(kept_cnts, key=lambda x: cv2.contourArea(x), reverse=True)

        Extracted_cnts.put([frame,kept_cnts])
