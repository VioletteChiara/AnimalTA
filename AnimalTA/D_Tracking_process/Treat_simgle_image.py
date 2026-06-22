import cv2
import numpy as np
import time
from AnimalTA.A_General_tools import Class_stabilise, Function_draw_arenas as Dr
import decord

def Prepare_Vid(Vid, Prem_img, type, portion=False, arena_interest=None):
    mask = Dr.draw_mask(Vid)  # A mask for the arenas

    Prem_image_to_show = Prem_img  # Take the first image

    if Vid.Rotation == 1:
        Prem_image_to_show = cv2.rotate(Prem_image_to_show, cv2.ROTATE_90_CLOCKWISE)
    elif Vid.Rotation == 2:
        Prem_image_to_show = cv2.rotate(Prem_image_to_show, cv2.ROTATE_180)
    if Vid.Rotation == 3:
        Prem_image_to_show = cv2.rotate(Prem_image_to_show, cv2.ROTATE_90_COUNTERCLOCKWISE)

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
        or_bright=None

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


    if type=="fixed":
        return(mask, or_bright, Arenas, Prem_image_to_show)
    elif type=="variable":
        return (mask, or_bright, Arenas, Main_Arenas_image, Main_Arenas_Bimage, Prem_image_to_show)



#!!!! not possible if we use flicker correction or if dynamical background!!!!
def Image_modif(Vid, Timg, Prem_image_to_show, mask, or_bright, approx=True):
    if Vid.Stab[0]:
        prev_pts = Vid.Stab[1]

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

    or_img = Timg.copy()

    #Convert to grey
    if Vid.Track[1][10][0]==0:
        Timg = cv2.cvtColor(Timg, cv2.COLOR_BGR2GRAY)

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

        if Vid.Track[1][0] % 2 == 0:
            tresh = Vid.Track[1][0] + 1
        else:
            tresh = Vid.Track[1][0]

        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,  tresh , Vid.Track[1][11])


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
    kept_cnts = filter_cnts(cnts, Vid)

    if not approx:
        cnts_complete, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        kept_cnts_complete = filter_cnts(cnts_complete, Vid)
        return [kept_cnts, kept_cnts_complete, or_img]
    else:
        return [kept_cnts,or_img]




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

