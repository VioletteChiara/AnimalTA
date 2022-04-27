import cv2
from BioTrack import Class_stabilise, Function_draw_mask as Dr
import numpy as np
import csv
import math
import os
import decord

def Do_tracking(parent, Vid, folder, portion = False, prev_row=None, close_pos=False):
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

    fr_rate = Vid.Frame_rate[1]
    one_every = int(round(round(Vid.Frame_rate[0], 2) / Vid.Frame_rate[1]))

    Which_part = 0

    with open(To_save, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=";")
        capture=decord.VideoReader(Vid.File_name, ctx=decord.cpu(0))

        kernel=np.ones((3,3), np.uint8)
        mask=Dr.draw_mask(Vid)

        if Vid.Cropped[0]:
            start=Vid.Cropped[1][0]
            end=Vid.Cropped[1][1]

            if Vid.Cropped[0]:
                if len(Vid.Fusion) > 1:  # Si on a plus d'une video
                    Which_part = \
                        [index for index, Fu_inf in enumerate(Vid.Fusion) if Fu_inf[0] <= start][-1]
                    if Which_part != 0:  # si on est pas dans la première partie de la vidéo
                        capture = decord.VideoReader(Vid.Fusion[Which_part][1], ctx=decord.cpu(0))
        else:
            start=0
            end=Vid.Frame_nb[1]-1

        Prem_image_to_show = capture[start - Vid.Fusion[Which_part][0]].asnumpy()
        img=Prem_image_to_show

        # We identify the different arenas:
        if Vid.Mask[0]:
            Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            Arenas = Dr.Organise_Ars(Arenas)
        else:
            Arenas=[np.array([[[0,0]],[[Vid.shape[0],0]],[[Vid.shape[0],Vid.shape[1]]],[[0,Vid.shape[1]]]], dtype="int32")]

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
            parent.timer=(frame-start)/(end-start-1)
            parent.show_load()
            new_row=[]
            new_row.append(frame_one_ev)

            if len(Vid.Fusion)>1 and Which_part<(len(Vid.Fusion)-1) and frame>=(Vid.Fusion[Which_part+1][0]):
                Which_part += 1
                capture = decord.VideoReader(Vid.Fusion[Which_part][1], ctx=decord.cpu(0))

            img=capture[frame - Vid.Fusion[Which_part][0]].asnumpy()

            #Satbilisation
            if Vid.Stab:
                img = Class_stabilise.find_best_position(Prem_Im=Prem_image_to_show, frame=img, show=False)

            #Backgroud
            img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            if Vid.Back[0]:
                img = cv2.subtract(Vid.Back[1], img) + cv2.subtract(img, Vid.Back[1])
            else:
                White_screen = np.zeros([img.shape[0], img.shape[1], 1], np.uint8)
                White_screen.fill(255)
                img = cv2.subtract(White_screen, img)

            #Tresh
            _, img = cv2.threshold(img, Vid.Track[1][0], 255, cv2.THRESH_BINARY)

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

                rec = cv2.minAreaRect(cnt)
                if max(rec[1][0], rec[1][1])>0:
                    cnt_comp = min(rec[1][0], rec[1][1]) / max(rec[1][0], rec[1][1])
                else:
                    cnt_comp = 0


                #Cnt area + Inertie cnt
                if cnt_area >= Vid.Track[1][3][0] and cnt_area <= Vid.Track[1][3][1]:
                    kept_cnts.append(cnt)

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
                        elif len(Ar_cnts)>0:
                            final_cnts=Ar_cnts+[Ar_cnts[0]]*(Vid.Track[1][6][Are]-len(Ar_cnts))
                        final_positions=[cnt_info[1] for cnt_info in final_cnts]
                        all_NA[Are] = False

                    else:
                        final_positions=[["NA","NA"]]*Vid.Track[1][6][Are]
                        all_NA[Are]=True

                else:
                    final_cnts = [["Not_yet"]]*Vid.Track[1][6][Are]
                    list_of_poss_dists=[]

                    if prev_row != None and frame == start:
                        last_row = prev_row

                    for ind in range(Vid.Track[1][6][Are]):
                        OldCoos=last_row[(1+Are*2*Vid.Track[1][6][Are-1]+ind*2):(3+Are*2*Vid.Track[1][6][Are-1]+ind*2)]
                        for new_pt in range(len(Ar_cnts)):
                            if OldCoos[0]!="NA":
                                dist=math.sqrt((float(OldCoos[0])-float(Ar_cnts[new_pt][1][0]))**2+(float(OldCoos[1])-float(Ar_cnts[new_pt][1][1]))**2)
                                if (dist/float(Vid.Scale[0]))<Vid.Track[1][5]:
                                    list_of_poss_dists.append([ind,new_pt,dist])
                            else:
                                list_of_poss_dists.append([ind,new_pt,0])

                    list_of_poss_dists=sorted(list_of_poss_dists, key=lambda x:x[2])
                    final_association=[]

                    list_of_poss_dists2=list_of_poss_dists.copy()
                    while len(list_of_poss_dists2)>0:
                        kept=list_of_poss_dists2[0]
                        final_association.append(kept)
                        list_of_poss_dists2=[poss_dists for poss_dists in list_of_poss_dists2 if poss_dists[0]!=kept[0] and poss_dists[1]!=kept[1]]


                    for pair in final_association:
                        final_cnts[pair[0]]=Ar_cnts[pair[1]][1]

                    while ["Not_yet"] in final_cnts:
                        missing=final_cnts.index(["Not_yet"])
                        if len([cbn[1] for cbn in list_of_poss_dists if cbn[0]==missing])>0:
                            new_pos=[cbn[1] for cbn in list_of_poss_dists if cbn[0]==missing][0]
                            final_cnts[missing] = Ar_cnts[new_pos][1]
                        else:
                            final_cnts[missing] = ["NA","NA"]
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


            frame_one_ev+=1

        for row in all_rows:
            writer.writerow(row)

    if close_pos and parent.stop_tracking:
        parent.close()
