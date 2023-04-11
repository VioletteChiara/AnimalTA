import cv2
from AnimalTA.A_General_tools import Function_draw_mask as Dr, UserMessages, Class_stabilise
from AnimalTA.D_Tracking_process import Do_the_track_fixed
import numpy as np
import csv
import math
import os
import decord
from tkinter import messagebox
from tkinter import *
from sklearn.cluster import KMeans
from scipy.optimize import linear_sum_assignment
import threading
import queue
import psutil

'''
To improve the speed of the tracking, we will separate the work in 3 threads.
1. Image loading, and modifications (stabilization, light correction, greyscale...) until contours are get
2. Target assignment and data recording
3. k-means clustering if two targets are touching each others.
'''

stop_threads = False
capture = None

def check_memory_overload():
    '''Some problems of memory leak were encountered with decord, these problems have been fixed but this is a security to control potential loss of memory.'''
    if psutil.virtual_memory()._asdict()["percent"] > 99.8:
        return 1
    elif psutil.virtual_memory()._asdict()["percent"] > 85:
        return 0
    else:
        return -1



def Do_tracking(parent, Vid, folder, portion=False, prev_row=None):
    '''This is the main tracking function of the program.
    parent=container (main window)
    Vid=current video
    portion= True if it is a rerun of the tracking over a short part of the video (for corrections)
    prev_row=If portion is True, this correspond to the last known coordinates of the targets.
    '''
    global stop_threads
    stop_threads=False

    # Language importation
    Language = StringVar()
    f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
    Language.set(f.read())
    f.close()
    Messages = UserMessages.Mess[Language.get()]

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
        if not os.path.isdir(os.path.join(folder, "coordinates")):
            os.makedirs(os.path.join(folder, "coordinates"))
    else:
        if not os.path.isdir(os.path.join(folder, "TMP_portion")):
            os.makedirs(os.path.join(folder, "TMP_portion"))

    if portion:
        To_save = os.path.join(folder, "TMP_portion", file_name + "_TMP_portion_Coordinates.csv")
    else:
        To_save = os.path.join(folder, "Coordinates", file_name + "_Coordinates.csv")

    # if the user choose to reduce the frame rate.
    one_every = int(round(round(Vid.Frame_rate[0], 2) / Vid.Frame_rate[1]))
    Which_part = 0

    mask = Dr.draw_mask(Vid)  # A mask for the arenas

    start = Vid.Cropped[1][0]  # Video beginning (after crop)
    end = Vid.Cropped[1][1]  # Video end (after crop)

    if Vid.Cropped[0]:
        if len(Vid.Fusion) > 1:  # If the video results from concatenated videos
            Which_part = [index for index, Fu_inf in enumerate(Vid.Fusion) if Fu_inf[0] <= start][-1]



    global capture
    global activate_protection
    global first_protection
    activate_protection=False
    first_protection=False
    capture = decord.VideoReader( Vid.Fusion[Which_part][1])  # Open video
    Prem_image_to_show = capture[start - Vid.Fusion[Which_part][0]].asnumpy()  # Take the first image
    capture.seek(0)
    if Vid.Cropped_sp[0]:
        Prem_image_to_show = Prem_image_to_show[Vid.Cropped_sp[1][0]:Vid.Cropped_sp[1][2],Vid.Cropped_sp[1][1]:Vid.Cropped_sp[1][3]]

    old_mask = None
    try:  # Old version of AnimalTA did not had the option for lightness correction, so Vid.Track[1][7] would result in error in case of old .ata files.
        if Vid.Track[1][7]:  # If True, the user chose to correct the lightness, this code allows to take the average lightness value of the first frame and to calculate the first and third quartiles of lightness values.
            if not Vid.Back[0]:
                grey = cv2.cvtColor(Prem_image_to_show, cv2.COLOR_BGR2GRAY)
            else:
                grey = Vid.Back[1].copy()

            if Vid.Mask[0]:  # If there were arenas defined by the user, we do the correction only for what happen inside these arenas.
                maskT = mask[:, :, 0].astype(bool)
                old_mask=mask.copy()
                or_bright = np.sum(grey[maskT]) / (255 * grey[maskT].size)  # Mean value
            else:
                or_bright = np.sum(grey) / (255 * grey.size)  # Mean value
            del grey
        else:
            or_bright = None
    except Exception as e:
        print(e)

    # We identify the different arenas:
    if Vid.Mask[0]:
        Main_Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        Main_Arenas = Dr.Organise_Ars(Main_Arenas)
    else:
        Main_Arenas = [np.array([[[0, 0]], [[Vid.shape[1], 0]], [[Vid.shape[1], Vid.shape[0]]], [[0, Vid.shape[0]]]],dtype="int32")]

    Arenas=[]
    Main_Arenas_Bimage=[]
    for Ar in range(len(Main_Arenas)):
        empty=np.zeros([Vid.shape[0],Vid.shape[1],1],np.uint8)
        empty=cv2.drawContours(empty,[Main_Arenas[Ar]],-1,255,-1)
        empty=cv2.drawContours(empty,Vid.Entrance[Ar],-1,255,-1)
        mask=cv2.drawContours(mask,Vid.Entrance[Ar],-1,255,-1)
        new_AR,_=cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        Arenas.append(new_AR[0])

        empty=cv2.drawContours(empty,Vid.Entrance[Ar],-1,0,-1)
        Main_Arenas_Bimage.append(empty)


    all_NA = [False] * len(Arenas)  # Value = True if there is only "NA" in the first frame


    Extracted_cnts = queue.Queue()
    Too_much_frame = threading.Event()

    Th_extract_cnts = threading.Thread(target=Image_modif, args=(Vid, start, end, one_every, Which_part, Prem_image_to_show, mask, old_mask, or_bright, Extracted_cnts, Too_much_frame))
    AD = IntVar()
    Th_associate_cnts = threading.Thread(target=Treat_cnts, args=(
    Vid, Arenas, Main_Arenas_Bimage, start, end, prev_row, all_NA, Extracted_cnts, Too_much_frame, Th_extract_cnts, To_save, portion,
    one_every, AD))

    Th_extract_cnts.start()
    Th_associate_cnts.start()

    while Th_associate_cnts.is_alive():
        parent.timer=(AD.get()-start)/(end-start)
        parent.show_load()

        overload = check_memory_overload()#Avoid memory leak problems
        if overload==0:
            activate_protection=True
            first_protection=True
        elif overload==1:
            break

    if overload==1:  # To prevent the effects of memory leak.
        stop_threads = True
        messagebox.showinfo(Messages["TError_memory"], Messages["Error_memory"])
        del capture
        return (False, _)

    Th_extract_cnts.join()
    Th_associate_cnts.join()

    if overload!=1:
        del capture
        if stop_threads:
            return (False, _)
        else:
            return (True, ID_kepts)



def urgent_close(Vid):
    global stop_threads
    stop_threads = True
    Vid.Tracked = False


def Treat_cnts(Vid, Arenas, Main_Arenas_Bimage, start, end, prev_row, all_NA, Extracted_cnts, Too_much_frame, Th_extract_cnts, To_save, portion, one_every, AD):
    global stop_threads
    global ID_kepts
    delay_lost=3 #How much frames do we wait before considering a target left the entrance area if it is lost
    delay_found=3#How much time of existance do we consider for a target to be real (inside entrance area)
    all_NA = [True] * len(Arenas)  # Value = True if there is only "NA" in the first frame
    Nb_found = [0] * len(Arenas)  # Number of targets who entered and then left the arena
    ID_kepts = [[] for i in Arenas]
    IDs=[[] for i in Arenas]
    last_row=[[] for i in Arenas]

    all_rows = [["Frame", "Time", "Arena", "Ind", "X", "Y"]]
    for ID_AR in range(len(Arenas)):
        for ID_Ind in range(Vid.Track[1][6][ID_AR]):
            all_rows[0].append("X_Arena" + str(ID_AR) + "_Ind" + str(ID_Ind))
            all_rows[0].append("Y_Arena" + str(ID_AR) + "_Ind" + str(ID_Ind))

    with open(To_save, 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")

        while Th_extract_cnts.is_alive() or Extracted_cnts.qsize() > 0:  # While we are still loading images or there are some extracted images that have not been associated yet
            if stop_threads:
                break
            frame, kept_cnts = Extracted_cnts.get()
            AD.set(frame)
            # Once all the contours are filtered, we associate them to arenas (i.e. in which arenas are they)

            if prev_row != None and frame == start:  # If we are working with a portion of video (redo part of the track)
                last_row = prev_row

            for Are in range(len(Arenas)):
                final_cnts = []
                Ar_cnts = []
                for cnt in range(len(kept_cnts)):
                    cnt_M = cv2.moments(kept_cnts[cnt])
                    if cnt_M["m00"] > 0:
                        cX = int(cnt_M["m10"] / cnt_M["m00"])
                        cY = int(cnt_M["m01"] / cnt_M["m00"])
                    else:
                        cX = int(cnt_M["m10"])
                        cY = int(cnt_M["m01"])
                    if cv2.pointPolygonTest(Arenas[Are], (cX, cY), False) >= 0:# Is the center of the contour inside the arena?
                        Ar_cnts.append([kept_cnts[cnt], (cX, cY)])  # If yes, we save this contour and consider it inside the arena

                if prev_row == None and frame == start:  # If its is the first row or if no positions were ever known
                    if len(Ar_cnts)>0:
                        final_cnts = [[cnt_info[1], Main_Arenas_Bimage[Are][cnt_info[1][1],cnt_info[1][0]]==255,0,delay_found+1] for cnt_info in Ar_cnts]  # Final list of contours
                        all_NA[Are] = False

                elif prev_row == None and all_NA[Are]:
                    final_cnts = [[cnt_info[1], False, 0, delay_found+1] for cnt_info in Ar_cnts if Main_Arenas_Bimage[Are][cnt_info[1][1], cnt_info[1][0]] == 255]  # Final list of contours
                    all_NA[Are] = False

                else:  # If we had info about target's positions
                    if len(Ar_cnts) == 0:  # If there are no contours found
                        for last_pos in last_row[Are]:
                            if not last_pos[1]:#Is the target was last seen inside the entrance area:
                                final_cnts.append(["Out",False,0,0])#we consider it left
                            else:
                                final_cnts.append([["NA", "NA"],True,last_pos[2]+1,last_pos[3]])#If it was last time seen inside the main arena, we consider it is still inside but just missing

                    else:  # Else, fill with "Not_Yet", which means we need to associate the targets with new positions, second element is None as we don't know wether point is inside main or entrance areas
                        final_cnts = [[["Not_yet"],None,lr[2],lr[3]] for lr in last_row[Are]]
                        table_dists = []  # We make a table that will cross all distances between last known position and current targets' positions
                        inds = [i[0] for i in last_row[Are] if i[0] != "Out"]
                        if len(inds) > 0:
                            for ind in inds:
                                row = []
                                for new_pt in range(len(Ar_cnts)):  # We loop through the contours that were kept
                                    if ind[0] != "NA":
                                        dist = math.sqrt((float(ind[0]) - float(Ar_cnts[new_pt][1][0])) ** 2 + (
                                                    float(ind[1]) - float(Ar_cnts[new_pt][1][1])) ** 2) / float(
                                            Vid.Scale[0])
                                        if dist < Vid.Track[1][5]:
                                            row.append(dist)
                                        else:
                                            row.append((Vid.shape[0] * Vid.shape[1]) / float(Vid.Scale[0]))  # We add an impossibly high value if the point is outside of the threshold limit
                                    else:
                                        row.append(0)
                                table_dists.append(row)

                            row_ind, col_ind = linear_sum_assignment(table_dists)

                            to_del = []
                            for ind in range(len(row_ind)):
                                if table_dists[row_ind[ind]][col_ind[ind]] < Vid.Track[1][5]:#If the distance between the points is lower than the threshold fixed by user
                                    final_cnts[row_ind[ind]][0] = Ar_cnts[col_ind[ind]][1]#We save the position in its correct place
                                    final_cnts[row_ind[ind]][1] = Main_Arenas_Bimage[Are][Ar_cnts[col_ind[ind]][1][1],Ar_cnts[col_ind[ind]][1][0]] == 255#We also check if this point is inside the main arena or entrance area
                                    final_cnts[row_ind[ind]][2] = 0
                                    final_cnts[row_ind[ind]][3] += 1
                                else:
                                    to_del.append(ind)  # We will remove contours in case they are associated with a target too far from them
                            row_ind = np.delete(row_ind, to_del)
                            col_ind = np.delete(col_ind, to_del)
                        else:
                            row_ind = []
                            col_ind = []

                        need_sep = [1] * len(Ar_cnts)
                        while ["Not_yet"] in [f[0] for f in final_cnts]:  # If not all targets are associated to a contour
                            missing = [f[0] for f in final_cnts].index(["Not_yet"])
                            if not last_row[Are][missing][1] and (final_cnts[missing][2]>=delay_lost or final_cnts[missing][3]<=delay_found):  # The last time this contour was seens, was it in entrance area?
                                final_cnts[missing]= ["Out",False,0,0]
                                row_ind = np.append(row_ind, missing)
                                col_ind = np.append(col_ind, -1) #If it was in entrance area, we consider it is lost
                            elif min(table_dists[missing]) < Vid.Track[1][5]:  # Else, if there was at least one contour that was close enought to the last target position
                                row_ind = np.append(row_ind, missing)
                                sorted_list = [[idx, elem] for idx, elem in enumerate(table_dists[missing]) if elem < Vid.Track[1][5]]
                                sorted_list.sort(key=lambda x: x[1])
                                need_sep[sorted_list[0][0]] += 1  # The contour closest to the last known position of the target but already associated with another target will be split in X (here we count the number of time we need to split the countour)
                                col_ind = np.append(col_ind, sorted_list[0][0])
                                final_cnts[missing][0] = ["Waiting_sep"]  # If we found a potential contour, we change the status of the current target position
                            else:
                                row_ind = np.append(row_ind, missing)
                                col_ind = np.append(col_ind,-1)  # If there was no contour close enough from the last known target position, the position is considered as "NA"
                                final_cnts[missing] = [["NA", "NA"],last_row[Are][missing][1],last_row[Are][missing][2]+1,last_row[Are][missing][3]]

                        col_ind = [x for _, x in sorted(zip(row_ind, col_ind))]
                        row_ind = sorted(row_ind)


                        if ["Waiting_sep"] in [cn[0] for cn in final_cnts]:  # If there were some contours to be separated
                            for Cnt in range(len(need_sep)):
                                if need_sep[Cnt] > 1:
                                    array = np.vstack([Ar_cnts[Cnt][0]])
                                    array = array.reshape(array.shape[0], array.shape[2])

                                    if len(array)<need_sep[Cnt]:#If the number of px to split is smaller than the number of targets, we will consider that some targets are missing
                                        to_split=len(array)
                                    else:
                                        to_split=need_sep[Cnt]

                                    kmeans = KMeans(n_clusters=to_split, random_state=0, n_init=5).fit(array)  # This function split the contours
                                    new_pos = kmeans.cluster_centers_

                                    inds = [ind for ind, cnt in enumerate(col_ind) if cnt == Cnt and final_cnts[ind][0] != "Out"]  # Which individuals are associated to this contour
                                    table_dists_corr = []
                                    # Here we make the similar kind of calculation as before to determine which part of the spitted contours goes to which target.
                                    for ind in inds:
                                        row = []
                                        OldCoos = last_row[Are][ind]
                                        for new_center in new_pos:
                                            if OldCoos[0][0] != "NA":
                                                dist = math.sqrt((float(OldCoos[0][0]) - float(new_center[0])) ** 2 + (float(OldCoos[0][1]) - float(new_center[1])) ** 2) / float(Vid.Scale[0])
                                                row.append(dist)
                                            else:
                                                row.append((Vid.shape[0] * Vid.shape[1]) / float(Vid.Scale[0]))  # Impossible distance

                                        table_dists_corr.append(row)

                                    row_ind2, col_ind2 = linear_sum_assignment(table_dists_corr)
                                    for i in range(len(row_ind2)):
                                        if final_cnts[row_ind[inds[i]]][0] == ["Waiting_sep"]:
                                            final_cnts[row_ind[inds[i]]][2] = last_row[Are][row_ind[inds[i]]][2]+1

                                        final_cnts[row_ind[inds[i]]][0] = [int(val) for val in new_pos[col_ind2[i]]]
                                        final_cnts[row_ind[inds[i]]][1] = Main_Arenas_Bimage[Are][int(new_pos[col_ind2[i]][1]),int(new_pos[col_ind2[i]][0])]==255

                        #If some targets are not correctly asociated because sptlit was impossible:
                        Missed= [idx for idx,cn in enumerate(final_cnts) if cn[0]== ["Waiting_sep"]]
                        for Miss in Missed:
                            final_cnts[Miss][0]=["NA","NA"]
                            final_cnts[Miss][1] = [False]
                            final_cnts[Miss][2] = last_row[Are][Miss][2] + 1

                        for cnt_remain in [Ar_cnts[i] for i in range(len(Ar_cnts)) if i not in col_ind]:
                            result = Main_Arenas_Bimage[Are][cnt_remain[1][1],cnt_remain[1][0]]==255  # Is the point inside the entrance area?
                            if not result:  # If a contour is not associated with any existing point and is inside the entrance area, we consider it entered the arena
                                final_cnts.append([cnt_remain[1],False,0,0])

                while len(final_cnts)>len(IDs[Are]):
                    Nb_found[Are]+=1
                    IDs[Are].append(Nb_found[Are]-1)
                    last_row[Are].append([["NA","NA"],False,0,0])

                if not all_NA[Are]:#If at least one target was found
                    for id in reversed(range(len(final_cnts))):
                        if final_cnts[id][0]!="Out":
                            if final_cnts[id][1]:
                                all_rows.append([(frame / one_every), round((frame / one_every) / Vid.Frame_rate[1], 2), Are, IDs[Are][id], final_cnts[id][0][0], final_cnts[id][0][1]])
                                if IDs[Are][id] not in ID_kepts[Are]:
                                    ID_kepts[Are].append(IDs[Are][id])
                            if final_cnts[id][0][0]!="NA":
                                last_row[Are][id]=final_cnts[id]
                            else:
                                last_row[Are][id][2]+=1
                        elif final_cnts[id][0]=="Out":
                            IDs[Are].pop(id)
                            last_row[Are].pop(id)

            if len(all_rows) >= 300:  # Every 300 lines, we save the data in a csv file
                for row in all_rows:
                    writer.writerow(row)
                all_rows = []

            if Extracted_cnts.qsize() < 400:
                Too_much_frame.set()

        # After we finished the tracking, we save the remaining rows in the csv file.
        if not stop_threads:
            for row in all_rows:
                writer.writerow(row)


def Image_modif(Vid, start, end, one_every, Which_part, Prem_image_to_show, mask, old_mask, or_bright, Extracted_cnts, Too_much_frame):
    global stop_threads
    global capture
    global activate_protection
    global first_protection
    if Vid.Stab[0]:
        prev_pts = Vid.Stab[1]
    last_grey=None#We keep here the last grey image for flicker correction
    penult_grey=None
    for frame in range(start, end + one_every,one_every):  # We go frame by frame respecting the frame rate defined by user
        if Extracted_cnts.qsize()>=500:
            Too_much_frame.clear()
            Too_much_frame.wait()

        if stop_threads:
            break

        if len(Vid.Fusion) > 1 and Which_part < (len(Vid.Fusion) - 1) and frame >= (
                Vid.Fusion[Which_part + 1][0]):
            Which_part += 1
            del capture
            capture = decord.VideoReader(Vid.Fusion[Which_part][1])
            capture.seek(0)
            activate_protection=False
            first_protection=False

        img = capture[frame - Vid.Fusion[Which_part][0]].asnumpy()

        if activate_protection:
            if first_protection:
                capture.seek(0)
                del capture
                capture = decord.VideoReader(Vid.Fusion[Which_part][1])
                first_protection=False
            capture.seek(0)

        if Vid.Cropped_sp[0]:
            img = img[Vid.Cropped_sp[1][0]:Vid.Cropped_sp[1][2],Vid.Cropped_sp[1][1]:Vid.Cropped_sp[1][3]]

        kernel = np.ones((3, 3), np.uint8)
        # Stabilisation
        if Vid.Stab[0]:
            img = Class_stabilise.find_best_position(Vid=Vid, Prem_Im=Prem_image_to_show, frame=img, show=False, prev_pts=prev_pts)


        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Correct flicker
        if Vid.Track[1][9]:
            if frame==start:
                last_grey=img.copy()
                penult_grey=last_grey.copy()
            elif frame>start:
                img = cv2.addWeighted(last_grey, 0.5, img, 1 - 0.5, 0)
                if frame>start+1:
                    img = cv2.addWeighted(penult_grey, 0.5, img, 1 - 0.5, 0)

                penult_grey = last_grey.copy()
                last_grey = img.copy()

        # If we want to apply light correction:
        if Vid.Track[1][7]:
            grey = np.copy(img)
            if Vid.Mask[0]:
                bool_mask = old_mask[:, :, 0].astype(bool)
            else:
                bool_mask = np.full(grey.shape, True)
            grey2 = grey[bool_mask]

            # Inspired from: https://stackoverflow.com/questions/57030125/automatically-adjusting-brightness-of-image-with-opencv
            brightness = np.sum(grey2) / (255 * grey2.size)  # Mean value
            ratio = brightness / or_bright
            img = cv2.convertScaleAbs(grey, alpha=1 / ratio, beta=0)

        # Backgroud and threshold
        if Vid.Back[0]:
            img = cv2.subtract(Vid.Back[1], img) + cv2.subtract(img, Vid.Back[1])
            _, img = cv2.threshold(img, Vid.Track[1][0], 255, cv2.THRESH_BINARY)
        else:
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
