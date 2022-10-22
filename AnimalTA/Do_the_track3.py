import cv2
from AnimalTA import Class_stabilise, Function_draw_mask as Dr, UserMessages
import numpy as np
import csv
import math
import os
import decord
import psutil
from tkinter import messagebox
from tkinter import *
from sklearn.cluster import KMeans
from scipy.optimize import linear_sum_assignment
import threading
import time
import queue

'''
To improve the speed of the tracking, we will separate the work in 3 threads.
1. Image loading, and modifications (stabilization, light correction, greyscale...) until contours are get
2. Target assignment and data recording
3. k-means clustering if two targets are touching each others.
'''


stop_threads=False

def check_memory_overload():
    '''Some problems of memory leak were encountered with decord, these problems have been fixed but this is a security to control potential loss of memory.'''
    return psutil.virtual_memory()._asdict()["percent"] > 99.8


def Do_tracking(parent, Vid, folder, portion=False, prev_row=None):
    deb=time.time()
    '''This is the main tracking function of the program.
    parent=container (main window)
    Vid=current video
    portion= True if it is a rerun of the tracking over a short part of the video (for corrections)
    prev_row=If portion is True, this correspond to the last known coordinates of the targets.
    '''

    # Language importation
    Language = StringVar()
    f = open("Files/Language", "r", encoding="utf-8")
    Language.set(f.read())
    f.close()
    Messages = UserMessages.Mess[Language.get()]

    # Where coordinates will be saved, if the folder did not exists, it is created.
    file_name = os.path.basename(Vid.File_name)
    point_pos = file_name.rfind(".")
    if not portion:
        if not os.path.isdir(folder + str("/coordinates")):
            os.makedirs(folder + str("/coordinates"))
    else:
        if not os.path.isdir(folder + str("/TMP_portion")):
            os.makedirs(folder + str("/TMP_portion"))

    if portion:
        To_save = folder + "/TMP_portion/" + file_name[:point_pos] + "_TMP_portion_Coordinates.csv"
    else:
        To_save = folder + "/Coordinates/" + file_name[:point_pos] + "_Coordinates.csv"

    # if the user choose to reduce the frame rate.
    one_every = int(round(round(Vid.Frame_rate[0], 2) / Vid.Frame_rate[1]))
    Which_part = 0


    mask = Dr.draw_mask(Vid)  # A mask for the arenas

    start = Vid.Cropped[1][0]  # Video beginning (after crop)
    end = Vid.Cropped[1][1]  # Video end (after crop)

    if Vid.Cropped[0]:
        if len(Vid.Fusion) > 1:  # If the video results from concatenated videos
            Which_part = [index for index, Fu_inf in enumerate(Vid.Fusion) if Fu_inf[0] <= start][-1]

    capture = decord.VideoReader(Vid.Fusion[Which_part][1], ctx=decord.cpu(0))  # Open video
    Prem_image_to_show = capture[start - Vid.Fusion[Which_part][0]].asnumpy()  # Take the first image
    try:  # Old version of AnimalTA did not had the option for lightness correction, so Vid.Track[1][7] would result in error in case of old .ata files.
        if Vid.Track[1][7]:  # If True, the user chose to correct the lightness, this code allows to take the average lightness value of the first frame and to calculate the first and third quartiles of lightness values.
            if not Vid.Back[0]:
                grey = cv2.cvtColor(Prem_image_to_show, cv2.COLOR_BGR2GRAY)
            else:
                grey = Vid.Back[1].copy()

            if Vid.Mask[
                0]:  # If there were arenas defined by the user, we do the correction only for what happen inside these arenas.
                maskT = mask[:, :, 0].astype(bool)
                or_bright = np.sum(grey[maskT]) / (255 * grey[maskT].size)  # Mean value
            else:
                or_bright = np.sum(grey) / (255 * grey.size)  # Mean value
            del grey
        else:
            or_bright=None
    except Exception as e:
        print(e)

    # We identify the different arenas:
    if Vid.Mask[0]:
        Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        Arenas = Dr.Organise_Ars(Arenas)
    else:
        Arenas = [np.array([[[0, 0]], [[Vid.shape[1], 0]], [[Vid.shape[1], Vid.shape[0]]], [[0, Vid.shape[0]]]],
                           dtype="int32")]

    all_NA = [False] * len(Arenas)  # Value = True if there is only "NA" in the first frame

    Extracted_cnts = queue.Queue()

    Too_much_frame=threading.Event()

    Th_extract_cnts=threading.Thread(target=Image_modif, args=(Vid, capture, start, end, one_every, Which_part, Prem_image_to_show, mask, or_bright, Extracted_cnts, Too_much_frame))
    AD=IntVar()
    Th_associate_cnts=threading.Thread(target=Treat_cnts, args=(Vid, Arenas, start, end, prev_row, all_NA, Extracted_cnts, Too_much_frame, Th_extract_cnts, To_save, portion, one_every, AD))

    Th_extract_cnts.start()
    Th_associate_cnts.start()

    while Th_associate_cnts.is_alive():
        parent.timer=(AD.get()-start)/(end-start)
        parent.show_load()
        overload = check_memory_overload()#Avoid memory leak problems
        if overload:
            break

    if overload:#To prevent the effects of memory leak.
        global stop_threads
        stop_threads=True
        Vid.Tracked = False
        messagebox.showinfo(Messages["TError_memory"], Messages["Error_memory"])
        return (False)
        del capture

    Th_extract_cnts.join()
    Th_associate_cnts.join()

    if not overload:
        return (True)
        del capture


def Treat_cnts(Vid, Arenas, start, end, prev_row, all_NA, Extracted_cnts, Too_much_frame, Th_extract_cnts, To_save, portion, one_every, AD):
    all_NA = [False] * len(Arenas)  # Value = True if there is only "NA" in the first frame
    global stop_threads
    if not portion:  # If we are building a new csv file (and not correcting an existing one)
        all_rows = [["Frame", "Time"]]
        for ID_AR in range(len(Arenas)):
            for ID_Ind in range(Vid.Track[1][6][ID_AR]):
                all_rows[0].append("X_Arena" + str(ID_AR) + "_Ind" + str(ID_Ind))
                all_rows[0].append("Y_Arena" + str(ID_AR) + "_Ind" + str(ID_Ind))
    else:
        all_rows = []
    with open(To_save, 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")

        while Th_extract_cnts.is_alive() or Extracted_cnts.qsize()>0:#While we are still loading images or there are some extracted images that have not been associated yet
            if stop_threads:
                break
            frame, kept_cnts = Extracted_cnts.get()
            AD.set(frame)
            # Once all the contours are filtered, we associate them to arenas (i.e. in which arenas are they)
            new_row = []#The nest row that will be saved in the csv file
            new_row.append((frame/one_every))#Frame number (after frame rate modification)
            new_row.append(round((frame/one_every)/Vid.Frame_rate[1],2))#Time since the biginning of the video

            for Are in range(len(Arenas)):
                Ar_cnts = []
                for cnt in range(len(kept_cnts)):
                    cnt_M = cv2.moments(kept_cnts[cnt])
                    if cnt_M["m00"] > 0:
                        cX = int(cnt_M["m10"] / cnt_M["m00"])
                        cY = int(cnt_M["m01"] / cnt_M["m00"])
                    else:
                        cX = int(cnt_M["m10"])
                        cY = int(cnt_M["m01"])
                    result = cv2.pointPolygonTest(Arenas[Are], (cX, cY),
                                                  False)  # Is the center of the contour inside the arena?
                    if result >= 0:
                        Ar_cnts.append(
                            [kept_cnts[cnt], (cX, cY)])  # If yes, we save this contour and add it as part of the arena

                if prev_row == None and (frame == start or all_NA[Are]):  # If its is the first row or if no positions were ever known
                    if len(Ar_cnts) > 0:  # If there is at least one contour
                        if len(Ar_cnts) >= Vid.Track[1][6][Are]:
                            final_cnts = Ar_cnts[0:(Vid.Track[1][6][
                                Are])]  # If there are enought countours, we take the biggets ones one per expected target

                        else:  # Else if there are less contours than expected targets, we separate the contour into subcontours
                            array = np.vstack([cnt[0] for cnt in Ar_cnts])
                            array = array.reshape(array.shape[0], array.shape[2])
                            kmeans = KMeans(n_clusters=Vid.Track[1][6][Are], random_state=0, n_init=50).fit(array)
                            new_pos = kmeans.cluster_centers_
                            final_cnts = new_pos.tolist()
                            final_cnts = [[[], (int(nf[0]), int(nf[1]))] for nf in final_cnts]

                        final_positions = [cnt_info[1] for cnt_info in final_cnts]  # Final list of contours
                        all_NA[Are] = False

                    else:  # If we have no information about the target's previous positions and that ther is no visible contour, we fill the row with NAs
                        final_positions = [["NA", "NA"]] * Vid.Track[1][6][Are]
                        all_NA[Are] = True

                else:  # If we had info about target's positions
                    if len(Ar_cnts) == 0:  # If there are no contours found, fill wih NAs
                        final_cnts = [["NA", "NA"]] * Vid.Track[1][6][Are]
                    else:  # Else, fill with "Not_Yet"
                        final_cnts = [["Not_yet"]] * Vid.Track[1][6][Are]

                        if prev_row != None and frame == start:  # If we are working with a portion of video (redo part of the track)
                            last_row = prev_row

                        table_dists = []  # We make a table that will cross all distances between last known position and current targets' positions
                        for ind in range(Vid.Track[1][6][Are]):
                            row = []
                            passed_inds = sum(Vid.Track[1][6][
                                              0:Are])  # We find the column position of the first individual within this arena
                            OldCoos = last_row[(2 + 2 * passed_inds + ind * 2):(4 + 2 * passed_inds + ind * 2)]
                            for new_pt in range(len(Ar_cnts)):  # We loop through the contours that were kept
                                if OldCoos[0] != "NA":
                                    dist = math.sqrt((float(OldCoos[0]) - float(Ar_cnts[new_pt][1][0])) ** 2 + (float(OldCoos[1]) - float(Ar_cnts[new_pt][1][1])) ** 2) / float(Vid.Scale[0])

                                    if dist < Vid.Track[1][5]:
                                        row.append(dist)
                                    else:
                                        row.append((Vid.shape[0] * Vid.shape[1]) / float(Vid.Scale[
                                                                                             0]))  # We add an impossibly high value if the point is outside of the threshold limit
                                else:
                                    row.append(0)
                            table_dists.append(row)

                        row_ind, col_ind = linear_sum_assignment(table_dists)

                        to_del = []
                        for ind in range(len(row_ind)):
                            if table_dists[row_ind[ind]][col_ind[ind]] < Vid.Track[1][5]:
                                final_cnts[row_ind[ind]] = Ar_cnts[col_ind[ind]][1]
                            else:
                                to_del.append(
                                    ind)  # We will remove contours in case they are associated with a target too far from them
                        row_ind = np.delete(row_ind, to_del)
                        col_ind = np.delete(col_ind, to_del)

                        need_sep = [1] * len(Ar_cnts)

                        while ["Not_yet"] in final_cnts:  # If not all targets are associated to a contour
                            missing = final_cnts.index(["Not_yet"])
                            row_ind = np.append(row_ind, missing)
                            if min(table_dists[missing]) < Vid.Track[1][
                                5]:  # If there was at least one contour that was close enought to the last target position
                                sorted_list = [[idx, elem] for idx, elem in enumerate(table_dists[missing]) if
                                               elem < Vid.Track[1][5]]
                                sorted_list.sort(key=lambda x: x[1])
                                need_sep[sorted_list[0][
                                    0]] += 1  # The contour closest to the last known position of the target but already associated with another target will be split in X (here we count the number of time we need to split the countour)
                                col_ind = np.append(col_ind, sorted_list[0][0])
                                final_cnts[missing] = [
                                    "Waiting_sep"]  # If we found a potential contour, we change the status of the current target position
                            else:
                                col_ind = np.append(col_ind,
                                                    -1)  # If there was no contour close enough from the last known target position, the position is considered as "NA"
                                final_cnts[missing] = ["NA", "NA"]

                        if ["Waiting_sep"] in final_cnts:  # If there were some contours to be splitted
                            for Cnt in range(len(need_sep)):
                                if need_sep[Cnt] > 1:
                                    array = np.vstack([Ar_cnts[Cnt][0]])
                                    array = array.reshape(array.shape[0], array.shape[2])
                                    kmeans = KMeans(n_clusters=need_sep[Cnt], random_state=0, n_init=5).fit(
                                        array)  # This function split the contours
                                    new_pos = kmeans.cluster_centers_

                                    inds = [ind for ind, cnt in enumerate(col_ind) if
                                            cnt == Cnt]  # Which individuals are sassociated to this contour

                                    table_dists_corr = []
                                    # Here we make the similar kind of calculation as before to determine which part of the spitted contours goes to which target.
                                    for ind in inds:
                                        row = []
                                        passed_inds = sum(Vid.Track[1][6][0:Are])
                                        OldCoos = last_row[(2 + 2 * passed_inds + row_ind[ind] * 2):(
                                                    4 + 2 * passed_inds + row_ind[ind] * 2)]
                                        for new_center in new_pos:
                                            if OldCoos[0] != "NA":
                                                dist = math.sqrt((float(OldCoos[0]) - float(new_center[0])) ** 2 + (
                                                            float(OldCoos[1]) - float(new_center[1])) ** 2) / float(
                                                    Vid.Scale[0])
                                                row.append(dist)

                                        table_dists_corr.append(row)

                                    row_ind2, col_ind2 = linear_sum_assignment(table_dists_corr)

                                    for i in range(len(row_ind2)):
                                        final_cnts[row_ind[inds[i]]] = [int(val) for val in new_pos[col_ind2[i]]]

                    final_positions = final_cnts.copy()

                new_row = new_row + [coo for sublist in final_positions for coo in sublist]  # We keep the positions here

            all_rows.append(new_row)
            last_row_WNA = new_row.copy()

            # The new row is saved to be used as next last row. If individuals were lost, we keep their last known position
            if frame > start or (portion and prev_row != None):
                for val in range(len(last_row_WNA)):
                    if last_row_WNA[val] == "NA":
                        last_row_WNA[val] = last_row[val]

            last_row = last_row_WNA
            if len(all_rows) >= 300:  # Every 1000 lines, we save the data in a csv file
                for row in all_rows:
                    writer.writerow(row)
                all_rows = []


            if Extracted_cnts.qsize()<400:
                Too_much_frame.set()

        # After we finished the tracking, we save the remaining rows in the csv file.
        if not stop_threads:
            for row in all_rows:
                writer.writerow(row)



def Image_modif(Vid, capture, start, end, one_every, Which_part, Prem_image_to_show, mask, or_bright, Extracted_cnts, Too_much_frame):
    global stop_threads
    for frame in range(start, end + one_every,one_every):  # We go frame by frame respecting the frame rate defined by user
        if Extracted_cnts.qsize()>=500:
            Too_much_frame.clear()
            Too_much_frame.wait()

        if stop_threads:
            break

        #parent.timer = (frame - start) / (end - start - 1)
        #parent.show_load()  # To show the loading bar to the user
        if len(Vid.Fusion) > 1 and Which_part < (len(Vid.Fusion) - 1) and frame >= (
                Vid.Fusion[Which_part + 1][0]):
            Which_part += 1
            capture = decord.VideoReader(Vid.Fusion[Which_part][1], ctx=decord.cpu(0))

        img = capture[frame - Vid.Fusion[Which_part][0]].asnumpy()

        kernel = np.ones((3, 3), np.uint8)
        # Stabilisation
        if Vid.Stab[0]:
            img = Class_stabilise.find_best_position(Vid=Vid, Prem_Im=Prem_image_to_show, frame=img, show=False)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # If we want to apply light correction:
        if Vid.Track[1][7]:
            grey = np.copy(img)
            if Vid.Mask[0]:
                bool_mask = mask[:, :, 0].astype(bool)
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
            img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, odd_val,
                                        10)

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
