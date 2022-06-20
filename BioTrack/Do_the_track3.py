import cv2
from BioTrack import Class_stabilise, Function_draw_mask as Dr, UserMessages
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



def check_memory_overload(parent):
    return psutil.virtual_memory()._asdict()["percent"] > 99.8

def Do_tracking(parent, Vid, folder, portion = False, prev_row=None, close_pos=False):
    Language = StringVar()
    f = open("Files/Language", "r")
    Language.set(f.read())
    f.close()
    Messages = UserMessages.Mess[Language.get()]

    file_name=os.path.basename(Vid.File_name)
    point_pos=file_name.rfind(".")
    if not portion:
        if not os.path.isdir(folder+str("/coordinates")):
            os.makedirs(folder+str("/coordinates"))
    else:
        if not os.path.isdir(folder+str("/TMP_portion")):
            os.makedirs(folder+str("/TMP_portion"))

    #Import video:
    if portion:
        To_save=folder + "/TMP_portion/" +file_name[:point_pos]+"_TMP_portion_Coordinates.csv"
    else:
        To_save=folder + "/Coordinates/" +file_name[:point_pos]+"_Coordinates.csv"

    one_every = int(round(round(Vid.Frame_rate[0], 2) / Vid.Frame_rate[1]))



    Which_part = 0

    with open(To_save, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=";")

        kernel=np.ones((3,3), np.uint8)
        mask=Dr.draw_mask(Vid)

        start=Vid.Cropped[1][0]
        end=Vid.Cropped[1][1]

        if Vid.Cropped[0]:
            if len(Vid.Fusion) > 1:  # Si on a plus d'une video
                Which_part = [index for index, Fu_inf in enumerate(Vid.Fusion) if Fu_inf[0] <= start][-1]

        capture = decord.VideoReader(Vid.Fusion[Which_part][1], ctx=decord.cpu(0))
        Prem_image_to_show = capture[start - Vid.Fusion[Which_part][0]].asnumpy()

        # We identify the different arenas:
        if Vid.Mask[0]:
            Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            Arenas = Dr.Organise_Ars(Arenas)
        else:
            Arenas=[np.array([[[0,0]],[[Vid.shape[1],0]],[[Vid.shape[1],Vid.shape[0]]],[[0,Vid.shape[0]]]], dtype="int32")]

        all_NA = [False] * len(Arenas)  # Value = True if there is only "NA" in the first frame

        if not portion:
            all_rows = [["Frame"]]
            for ID_AR in range(len(Arenas)):
                for ID_Ind in range(Vid.Track[1][6][ID_AR]):
                    all_rows[0].append("X_Arena"+str(ID_AR)+"_Ind"+str(ID_Ind))
                    all_rows[0].append("Y_Arena"+str(ID_AR)+"_Ind"+str(ID_Ind))
        else:
            all_rows=[]

        frame_one_ev=0

        for frame in range(start,end+one_every,one_every):
            overload=check_memory_overload(parent)

            if overload:
                break

            #try:
            parent.timer = (frame - start) / (end - start - 1)
            parent.show_load()
            new_row = []
            new_row.append(frame_one_ev)

            if len(Vid.Fusion) > 1 and Which_part < (len(Vid.Fusion) - 1) and frame >= (
            Vid.Fusion[Which_part + 1][0]):
                Which_part += 1
                capture = decord.VideoReader(Vid.Fusion[Which_part][1], ctx=decord.cpu(0))

            img=capture[frame - Vid.Fusion[Which_part][0]].asnumpy()

            #Satbilisation
            if Vid.Stab[0]:
                img = Class_stabilise.find_best_position(Vid=Vid,Prem_Im=Prem_image_to_show, frame=img, show=False)

            #Backgroud and threshold
            img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            if Vid.Back[0]:
                img = cv2.subtract(Vid.Back[1], img) + cv2.subtract(img, Vid.Back[1])
                _, img = cv2.threshold(img, Vid.Track[1][0], 255, cv2.THRESH_BINARY)

            else:
                odd_val=int(Vid.Track[1][0])+(1-(int(Vid.Track[1][0])%2))
                img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, odd_val,10)

            #Erosion
            if Vid.Track[1][1]>0:
                img = cv2.erode(img, kernel, iterations=Vid.Track[1][1])

            #Dilation
            if Vid.Track[1][2]>0:
                img = cv2.dilate(img, kernel, iterations=Vid.Track[1][2])

            if Vid.Mask[0]:
                img = cv2.bitwise_and(img, img, mask=mask)

            #Find contours:
            cnts, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            kept_cnts=[]
            for cnt in cnts:
                cnt_area = cv2.contourArea(cnt)
                if float(Vid.Scale[0]) > 0:
                   cnt_area = cnt_area * (1 / float(Vid.Scale[0])) ** 2


                #Cnt area + Inertie cnt
                if cnt_area >= Vid.Track[1][3][0] and cnt_area <= Vid.Track[1][3][1]:
                    kept_cnts.append(cnt)

                kept_cnts=sorted(kept_cnts, key=lambda x: cv2.contourArea(x), reverse=True)


            # Once all the cnts are filtered, we associate them to arenas:
            for Are in range(len(Arenas)):
                Ar_cnts=[]
                for cnt in range(len(kept_cnts)):
                    cnt_M = cv2.moments(kept_cnts[cnt])
                    if cnt_M["m00"]>0:
                        cX = int(cnt_M["m10"] / cnt_M["m00"])
                        cY = int(cnt_M["m01"] / cnt_M["m00"])
                    else:
                        cX = int(cnt_M["m10"])
                        cY = int(cnt_M["m01"])
                    result = cv2.pointPolygonTest(Arenas[Are], (cX, cY), False)
                    if result>=0:
                        Ar_cnts.append([kept_cnts[cnt],(cX,cY)])

                if prev_row==None and (frame==start or all_NA[Are]):
                    if len(Ar_cnts)>0:
                        if len(Ar_cnts)>=Vid.Track[1][6][Are]:
                            final_cnts=Ar_cnts[0:(Vid.Track[1][6][Are])]

                        else:
                            array = np.vstack([cnt[0] for cnt in Ar_cnts])
                            array = array.reshape(array.shape[0], array.shape[2])
                            kmeans = KMeans(n_clusters=Vid.Track[1][6][Are], random_state=0, n_init=50).fit(array)
                            new_pos = kmeans.cluster_centers_
                            final_cnts = new_pos.tolist()
                            final_cnts = [[[], (int(nf[0]), int(nf[1]))] for nf in final_cnts]

                        final_positions=[cnt_info[1] for cnt_info in final_cnts]
                        all_NA[Are] = False

                    else:
                        final_positions=[["NA","NA"]]*Vid.Track[1][6][Are]
                        all_NA[Are]=True






                else:
                    if len(Ar_cnts)==0:
                        final_cnts = [["NA","NA"]] * Vid.Track[1][6][Are]
                    else:
                        final_cnts = [["Not_yet"]] * Vid.Track[1][6][Are]

                        if prev_row != None and frame == start:
                            last_row = prev_row

                        table_dists=[]
                        for ind in range(Vid.Track[1][6][Are]):
                            row=[]
                            passed_inds = sum(Vid.Track[1][6][0:Are])
                            OldCoos=last_row[(1+2*passed_inds+ind*2):(3+2*passed_inds+ind*2)]
                            for new_pt in range(len(Ar_cnts)):
                                if OldCoos[0]!="NA":
                                    dist=math.sqrt((float(OldCoos[0])-float(Ar_cnts[new_pt][1][0]))**2+(float(OldCoos[1])-float(Ar_cnts[new_pt][1][1]))**2)/float(Vid.Scale[0])
                                    row.append(dist)
                                else:
                                    row.append(0)
                            table_dists.append(row)


                        row_ind, col_ind = linear_sum_assignment(table_dists)


                        for ind in range(len(row_ind)):
                            if table_dists[row_ind[ind]][col_ind[ind]] < Vid.Track[1][5]:
                                final_cnts[row_ind[ind]] = Ar_cnts[col_ind[ind]][1]


                        need_sep = [1] * len(Ar_cnts)

                        while ["Not_yet"] in final_cnts:
                            missing=final_cnts.index(["Not_yet"])
                            row_ind = np.append(row_ind, missing)
                            if min(table_dists[missing])<Vid.Track[1][5]:
                                list_pos=[idx for idx,elem in enumerate(table_dists[missing]) if elem<Vid.Track[1][5]]
                                need_sep[list_pos[0]]+=1
                                col_ind=np.append(col_ind,list_pos[0])
                                final_cnts[missing] = ["Waiting_sep"]#Ar_cnts[list_pos[0]][1]#The biggest that is not too far
                            else:
                                col_ind = np.append(col_ind, -1)
                                final_cnts[missing] = ["NA", "NA"]





                        if ["Waiting_sep"] in final_cnts:
                            for Cnt in range(len(need_sep)):
                                if need_sep[Cnt]>1:
                                    array = np.vstack([Ar_cnts[Cnt][0]])
                                    array = array.reshape(array.shape[0], array.shape[2])
                                    kmeans = KMeans(n_clusters=need_sep[Cnt], random_state=0, n_init=50).fit(array)
                                    new_pos = kmeans.cluster_centers_

                                    inds=[ind for ind,cnt in enumerate(col_ind) if cnt==Cnt]


                                    table_dists_corr = []
                                    for ind in inds:
                                        row = []
                                        passed_inds = sum(Vid.Track[1][6][0:Are])
                                        OldCoos = last_row[(1 + 2 * passed_inds + row_ind[ind] * 2):(3 + 2 * passed_inds + row_ind[ind] * 2)]

                                        for new_center in new_pos:
                                            if OldCoos[0] != "NA":
                                                dist = math.sqrt((float(OldCoos[0]) - float(new_center[0])) ** 2 + (float(OldCoos[1]) - float(new_center[1])) ** 2) / float(Vid.Scale[0])
                                                row.append(dist)

                                        table_dists_corr.append(row)

                                    row_ind2, col_ind2 = linear_sum_assignment(table_dists_corr)


                                    for i in range(len(row_ind2)):
                                        final_cnts[row_ind[inds[i]]] = [int(val) for val in new_pos[col_ind2[i]]]

                    final_positions=final_cnts.copy()

                new_row=new_row+[coo for sublist in final_positions for coo in sublist]

            all_rows.append(new_row)
            last_row_WNA=new_row.copy()

            if frame>start or (portion and prev_row != None):
                for val in range(len(last_row_WNA)):
                    if last_row_WNA[val]=="NA":
                        last_row_WNA[val]=last_row[val]

            last_row=last_row_WNA


            if len(all_rows)>=300:
                for row in all_rows:
                    writer.writerow(row)
                all_rows=[]

            #except Exception as e:
            #     print(e)
            #     pass

            frame_one_ev+=1


        for row in all_rows:
            writer.writerow(row)

    if overload:
        if os.path.isfile(To_save):
            os.remove(To_save)
            Vid.Tracked=False
            messagebox.showinfo(Messages["TError_memory"], Messages["Error_memory"])


    if close_pos and parent.stop_tracking:
        parent.close()

    if not overload:
        return(True)
        del capture
    else:
        return(False)
        del capture

