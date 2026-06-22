#Function_prepare_images_multi.py
import time
import multiprocessing
import cv2
import numpy as np
from AnimalTA.A_General_tools import Class_stabilise, UserMessages
from multiprocessing import shared_memory, Lock
import os

def send_cap_to(capture, capture_pos, frame):
    while capture_pos<=frame:
        capture_pos+=1
        capture.grab()
    return(capture_pos)




def Image_modif(Queue_cnts, Queue_frames, Vid, Prem_image_to_show, mask, or_bright, ID, lock_cnt, ):
    cv2.setNumThreads(1)
    if Vid.Stab[0]:
        prev_pts = Vid.Stab[1]

    if Vid.Back[0] == 2:  # Dynamic background
        progressive_back = cv2.createBackgroundSubtractorMOG2(history=int(Vid.Track[1][10][3] * Vid.Frame_rate[1]),
                                                              varThreshold=Vid.Track[1][0], detectShadows=False)

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

    #We load the tasks
    first = True
    cap_pos = 0
    while True:
        all_cnts_kept=[]

        try:
            chunck_id, Images_to_treat = Queue_frames.get_nowait()
        except:
            break

        # simulate variable processing time

        if first:
            Which_part=0
            while len(Vid.Fusion) > 1 and Which_part < (len(Vid.Fusion) - 1) and Images_to_treat[0] >= (Vid.Fusion[Which_part + 1][0]):
                Which_part += 1

            try:
                if Vid.type=="Video":
                    capture = cv2.VideoCapture(Vid.Fusion[Which_part][1])
            except Exception as e:
                print(f"Error initializing video reader: {e}")
                return
            first=False

            # We first look at what is the best strategy (doing all intermediate frames or jumping from one to the other)

        for frame in Images_to_treat:  # Process frames respecting the defined frame rate
            frame = round(frame)

            # If we are at the limit between two videos:
            if len(Vid.Fusion) > 1 and Which_part < (len(Vid.Fusion) - 1) and frame >= (Vid.Fusion[Which_part + 1][0]):
                while len(Vid.Fusion) > 1 and Which_part < (len(Vid.Fusion) - 1) and frame >= (
                Vid.Fusion[Which_part + 1][0]):
                    Which_part += 1

                if Vid.type=="Video":
                    capture.release()
                    capture = cv2.VideoCapture(Vid.Fusion[Which_part][1])
                    cap_pos = 0

            if Vid.type == "Video":
                cap_pos = send_cap_to(capture, cap_pos, frame - Vid.Fusion[Which_part][0])  # Set starting frame
                ret, image = capture.retrieve()
            else:
                image=cv2.imread(os.path.join(Vid.Fusion[Which_part][1], Vid.img_list[frame - Vid.Fusion[Which_part][0]]))

            if not image is None:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                Timg = image

                if Vid.Rotation == 1:
                    Timg = cv2.rotate(Timg, cv2.ROTATE_90_CLOCKWISE)
                elif Vid.Rotation == 2:
                    Timg = cv2.rotate(Timg, cv2.ROTATE_180)
                if Vid.Rotation == 3:
                    Timg = cv2.rotate(Timg, cv2.ROTATE_90_COUNTERCLOCKWISE)

                if Vid.Cropped_sp[0]:
                    Timg = Timg[Vid.Cropped_sp[1][0]:Vid.Cropped_sp[1][2],Vid.Cropped_sp[1][1]:Vid.Cropped_sp[1][3]]


                kernel = np.ones((3, 3), np.uint8)
                # Stabilisation

                if Vid.Stab[0]:
                    Timg = Class_stabilise.find_best_position(Vid=Vid, Prem_Im=Prem_image_to_show, frame=Timg, show=False, prev_pts=prev_pts)
                #Timg_or=Timg.copy()


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

                    if Vid.Track[1][0] % 2 == 0:
                        tresh= Vid.Track[1][0] + 1
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
                kept_cnts=filter_cnts(cnts, Vid)

                # if frame % 10 == 0:
                #     if frame % 80 == 0 or frame % 90 == 0:
                #         folder = "F:/AnimalTA/AnimalTA_developpement/TestAI/dataset/images/val"
                #         folder_lab = "F:/AnimalTA/AnimalTA_developpement/TestAI/dataset/labels/val"
                #     else:
                #         folder = "F:/AnimalTA/AnimalTA_developpement/TestAI/dataset/images/train"
                #         folder_lab = "F:/AnimalTA/AnimalTA_developpement/TestAI/dataset/labels/train"
                #     #Timg_or = cv2.cvtColor(Timg_or, cv2.COLOR_RGB2BGR)
                #
                #     cv2.imwrite(folder + "/" + "Mouse_vid1_" + str(frame) + ".jpeg", Timg_or)
                #
                #     txt_filename = folder_lab + "/" + "Mouse_vid1_" + str(frame) + ".txt"
                #     species = 0  # 0=mouse
                #     height, width, _ = Timg_or.shape  # Get image dimensions
                #     with open(txt_filename, "w") as f:
                #         for cnt in kept_cnts:
                #             x, y, w, h = cv2.boundingRect(cnt)
                #             # Convert to YOLO format (normalize values)
                #             x_center = (x + w / 2) / width
                #             y_center = (y + h / 2) / height
                #             w_norm = w / width
                #             h_norm = h / height
                #
                #             # Write to the file
                #             f.write(f"{species} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n")
            else:
                kept_cnts=[]

            all_cnts_kept.append([frame, kept_cnts])
            if len(all_cnts_kept)>=25:
                Queue_cnts.put(all_cnts_kept)
                all_cnts_kept=[]




        with lock_cnt:
            Queue_cnts.put(all_cnts_kept)



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