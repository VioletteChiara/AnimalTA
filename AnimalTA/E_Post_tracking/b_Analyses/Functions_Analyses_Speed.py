import math
import cv2
import numpy as np
import itertools
from scipy.spatial.distance import cdist
from AnimalTA.A_General_tools import Function_draw_mask
from operator import itemgetter

"""This file contains a set of functions used to extract the analyses results from the target's trajectories"""


def draw_shape(Vid, Arena, Shape):
    Xss = [pt[0] for pt in Shape[1]]
    Yss = [pt[1] for pt in Shape[1]]

    empty = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
    if Shape[0] == "Rectangle":
        empty, _ = Function_draw_mask.Draw_rect(empty, Xss, Yss, color=(255, 0, 0), thick=-1)
    elif Shape[0] == "Polygon":
        empty, _ = Function_draw_mask.Draw_Poly(empty, Xss, Yss, color=(255, 0, 0), thick=-1)
    elif Shape[0] == "Ellipse":
        empty, _ = Function_draw_mask.Draw_elli(empty, Xss, Yss, color=(255, 0, 0), thick=-1)
    elif Shape[0]== "Point":
        empty = cv2.circle(empty, (Shape[1][0][0], Shape[1][0][1]), int(Shape[2]*Vid.Scale[0]), (255, 0, 0), -1)
    elif Shape[0]== "All_borders" or Shape[0]== "Border":
        if Shape[0] == "All_borders":
            empty = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
            border = cv2.drawContours(np.copy(empty), [Arena], -1, (255, 255, 255),
                                      int(round(Shape[2] * float(Vid.Scale[0]) * 2)))
            area = cv2.drawContours(np.copy(empty), [Arena], -1, (255, 255, 255), -1)
            empty = cv2.bitwise_and(border, border, mask=area)

        elif Shape[0] == "Borders":
            empty = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
            border = np.copy(empty)

            for bord in Shape[1]:
                border = cv2.line(border, bord[0], bord[1], color=(255, 0, 0), thickness=2)
            cnts, _ = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

            border = cv2.drawContours(border, cnts, -1, (255, 255, 255), int(round(Shape[2] * float(Vid.Scale[0]) * 2)))
            area = cv2.drawContours(np.copy(empty), [Arena], -1, (255, 255, 255), -1)
            empty = cv2.bitwise_and(border, border, mask=area)

    cnts, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    mask_glob = Function_draw_mask.draw_mask(Vid)
    mask = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
    mask = cv2.drawContours(mask, [Arena], -1, (255), -1)

    mask = cv2.bitwise_and(mask, mask_glob)
    empty = cv2.bitwise_and(mask, empty)

    cnts_cleaned, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if len(cnts)>0:
        final=[True,cnts[0]]
    else:
        final=[False,[]]

    if len(cnts_cleaned)>0:
        final=final+[True,cnts_cleaned[0]]
    else:
        final=final+[False,[]]
    return(final)

def calculate_exploration(method, Vid, Coos, deb, end, Arena, show=False, image=None):
    new_row=[]
    # Exploration:
    if method[0] == 0:  # Si c'est method moderne
        radius = math.sqrt((float(method[1])) / math.pi)
        empty = np.zeros((Vid.shape[0], Vid.shape[1], 1), np.uint8)
        last_pt = [-1000, -1000]
        if radius > 0:
            for pt in Coos[deb:end + 1]:
                if pt[0] != -1000 and last_pt[0] != -1000:
                    cv2.line(empty, (int(float(last_pt[0])), int(float(last_pt[1]))),
                             (int(float(pt[0])), int(float(pt[1]))), (255),
                             max(1, int(radius * 2 * float(Vid.Scale[0]))))
                elif pt[0] != -1000:
                    cv2.circle(empty, (int(float(pt[0])), int(float(pt[1]))),
                               int(radius * float(Vid.Scale[0])), (255), -1)
                last_pt = pt

        mask_glob = Function_draw_mask.draw_mask(Vid)
        mask = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
        mask = cv2.drawContours(mask, [Arena], -1, (255), -1)
        mask = cv2.bitwise_and(mask, mask_glob)
        empty = cv2.bitwise_and(mask, empty)

        new_row.append(np.sum(empty > [0]) * (1 / float(Vid.Scale[0]) ** 2))  # We want to save the total surface explored (independantly of the size of the arena)
        new_row.append(len(np.where(empty > [0])[0]) / len(np.where(mask == [255])[0]))  # Now relative to the arena area
        new_row.append("Modern")  # Method
        new_row.append(method[1])  # Area
        new_row.append("NA")  # Param_aspect

        if not show:
            return(new_row)#Absolute, relative, method, area, param aspect
        else:
            return (new_row, empty)

    elif method[0] == 1:  # Si c'est mesh carré
        No_NA_Coos = np.array(Coos[deb:end + 1])
        No_NA_Coos = No_NA_Coos[np.all(No_NA_Coos != -1000, axis=1)]
        No_NA_Coos = No_NA_Coos.astype('float')

        largeur = math.sqrt(float(method[1]) * float(Vid.Scale[0]) ** 2)
        nb_squares_v = math.ceil((max(Arena[:, :, 0]) - min(Arena[:, :, 0])) / largeur)
        nb_squares_h = math.ceil((max(Arena[:, :, 1]) - min(Arena[:, :, 1])) / largeur)

        max_x = min(Arena[:, :, 0]) + nb_squares_v * (largeur)
        max_y = min(Arena[:, :, 1]) + nb_squares_h * (largeur)

        decal_x = (max_x - max(Arena[:, :, 0])) / 2
        decal_y = (max_y - max(Arena[:, :, 1])) / 2

        Xs = (np.floor((No_NA_Coos[:, 0] - (min(Arena[:, :, 0]) - decal_x)) / largeur))
        Ys = (np.floor((No_NA_Coos[:, 1] - (min(Arena[:, :, 1]) - decal_y)) / largeur))

        XYs = np.array(list(zip(Xs, Ys)))
        if not show:
            unique = np.unique(XYs, axis=0, return_counts=False)
        else:
            unique, count = np.unique(XYs, axis=0, return_counts=True)

        new_row.append(len(unique))  # Value
        new_row.append(len(unique) / (nb_squares_v * nb_squares_h))  # Value divided by all possible
        new_row.append("Squares_mesh")  # Method
        new_row.append("NA")  # Param_aspect
        new_row.append(method[1])  # Area
        new_row.append("NA")  # Param_aspect

        if not show:
            return(new_row)

        else:
            colors = np.array([[255] * 128 + [255] * 128 + list(reversed(range(256))),
                               [255] * 128 + list(reversed(range(0, 256, 2))) + [0] * 256,
                               list(reversed(range(0, 256, 2))) + [0] * 128 + [0] * 256], dtype=int).T

            for square in range(len(count)):
                color = colors[int(round((count[square] / sum(count)) * (len(colors) - 1)))]
                image = cv2.rectangle(image, pt1=(
                    int(min(Arena[:, :, 0]) - decal_x + unique[square][0] * (largeur)),
                    int(min(Arena[:, :, 1]) - decal_y + unique[square][1] * (largeur))),
                                           pt2=(int(min(Arena[:, :, 0]) - decal_x + (unique[square][0] + 1) * (
                                               largeur)),
                                                int(min(Arena[:, :, 1]) - decal_y + (unique[square][1] + 1) * (
                                                    largeur))),
                                           color=[int(c) for c in color], thickness=-1)

                for vert in range(nb_squares_v + 1):
                    image = cv2.line(image,
                                          pt1=(int(min(Arena[:, :, 0]) - decal_x + vert * (largeur)),
                                               int(min(Arena[:, :, 1]) - decal_y)), pt2=(
                            int(min(Arena[:, :, 0]) - decal_x + vert * (largeur)),
                            int(max(Arena[:, :, 1]) + decal_y)), color=(0, 0, 0), thickness=2)

                for horz in range(nb_squares_h + 1):
                    image = cv2.line(image, pt1=(int(min(Arena[:, :, 0]) - decal_x),
                                                           int(min(Arena[:, :, 1]) - decal_y + horz * (
                                                               largeur))),
                                          pt2=(int(max(Arena[:, :, 0]) + decal_x),
                                               int(min(Arena[:, :, 1]) - decal_y + horz * (largeur))),
                                          color=(0, 0, 0),
                                          thickness=2)

                image[(50): (image.shape[0] - 50), (image.shape[1] - 75):(image.shape[1])] = (
                150, 150, 150)

                for raw in range(image.shape[0] - 150):
                    color = colors[int((raw / (image.shape[0] - 150)) * (len(colors) - 1))]
                    image[image.shape[0] - 75 - raw,
                    (image.shape[1] - 65):(image.shape[1] - 45)] = color

                image = cv2.putText(image, "100%", (image.shape[1] - 43, 75), cv2.FONT_HERSHEY_SIMPLEX,
                                         fontScale=0.4, color=(0, 0, 0), thickness=1)
                image = cv2.putText(image, "50%", (image.shape[1] - 43, int(image.shape[0] / 2)),
                                         cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(0, 0, 0), thickness=1)
                image = cv2.putText(image, "0%", (image.shape[1] - 43, image.shape[0] - 75),
                                         cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(0, 0, 0), thickness=1)

            return (new_row, image)

    elif method[0] == 2:  # Si c'est mesh circulaire
        No_NA_Coos = np.array(Coos[deb:end + 1])
        No_NA_Coos = No_NA_Coos[np.all(No_NA_Coos != -1000, axis=1)]
        No_NA_Coos = No_NA_Coos.astype('float')

        M = cv2.moments(Arena)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        max_size = max(list(
            np.sqrt((Arena[:, :, 0] - cX) ** 2 + (Arena[:, :, 1] - cY) ** 2)))

        last_rad = math.sqrt((float(method[1]) * float(Vid.Scale[0]) ** 2) / math.pi)
        last_nb = 1

        list_rads = [last_rad]
        list_nb = [1]
        list_angles = [[0]]

        while last_rad < max_size:
            new_rad = ((math.sqrt(last_nb) + math.sqrt(method[2] ** 2)) / math.sqrt(
                last_nb)) * last_rad
            new_nb = int(round((math.sqrt(last_nb) + math.sqrt(method[2] ** 2)) ** 2))
            cur_nb = new_nb - last_nb

            list_nb.append(cur_nb)

            one_angle = (2 * math.pi) / cur_nb
            cur_angle = 0
            tmp_angles = [0]
            for angle in range(cur_nb):
                cur_angle += one_angle
                tmp_angles.append(cur_angle)

            list_angles.append(tmp_angles)
            list_rads.append(new_rad)

            last_rad = new_rad
            last_nb = new_nb

        # We summarise the position of the individual:
        Dists = list(np.sqrt((No_NA_Coos[:, 0] - cX) ** 2 + (No_NA_Coos[:, 1] - cY) ** 2))
        Circles = ([np.argmax(list_rads > dist) for dist in Dists])  # In which circle
        Angles = np.arctan2((No_NA_Coos[:, 1] - cY), (No_NA_Coos[:, 0] - cX))
        liste_angles_per_I = list(itemgetter(*Circles)(list_angles))
        Portions = ([np.argmax(liste_angles_per_I[idx] >= (angle + math.pi)) for idx, angle in
                     enumerate(Angles)])  # In which portion

        Pos = np.array(list(zip(Circles, Portions)))

        if not show:
            unique = np.unique(Pos, axis=0, return_counts=False)
        else:
            unique, count = np.unique(Pos, axis=0, return_counts=True)

        new_row.append(len(unique))  # Value
        new_row.append(len(unique) / sum(list_nb))  # Value divided by all possible cells
        new_row.append("Circular_mesh")  # Method
        new_row.append(method[1])  # Area
        new_row.append(method[2])  # Param_aspect

        if not show:
            return(new_row)
        else:
            colors=np.array([[255]*128 + [255]*128 + list(reversed(range(256))),[255]*128 + list(reversed(range(0,256,2)))+ [0]*256,list(reversed(range(0,256,2)))+[0]*128 +[0]*256], dtype=int).T
            image = cv2.circle(image, (cX, cY), int(last_rad), [int(c) for c in colors[0]], -1)
            for square in range(len(unique)):
                color = colors[int(round((count[square] / sum(count)) * (len(colors) - 1)))]
                if unique[square][0] == 0:
                    image = cv2.circle(image, (cX, cY), (int(list_rads[unique[square][0]])),
                                            color=[int(c) for c in color], thickness=-1)
                else:
                    diameters = [int(list_rads[unique[square][0]]), int(list_rads[unique[square][0] - 1])]
                    first_angle = 180 + ((list_angles[unique[square][0]][unique[square][1]]) * 180 / math.pi)
                    sec_angle = 180 + ((list_angles[unique[square][0]][unique[square][1] - 1]) * 180 / math.pi)

                    empty_img = np.zeros([image.shape[0], image.shape[1], 1], np.uint8)
                    empty_img = cv2.ellipse(empty_img, (cX, cY), (diameters[0], diameters[0]), 0,
                                            startAngle=first_angle + 1, endAngle=sec_angle - 1, color=255, thickness=1)
                    empty_img = cv2.ellipse(empty_img, (cX, cY), (diameters[1], diameters[1]), 0,
                                            startAngle=first_angle + 1, endAngle=sec_angle - 1, color=255, thickness=1)

                    pt1 = (int(cX + math.cos((first_angle) / 180 * math.pi) * (diameters[0] + 2)),
                           int(cY + math.sin(first_angle / 180 * math.pi) * (diameters[0] + 2)))
                    pt2 = (int(cX + math.cos((first_angle) / 180 * math.pi) * (diameters[1] - 2)),
                           int(cY + math.sin(first_angle / 180 * math.pi) * (diameters[1] - 2)))
                    empty_img = cv2.line(empty_img, pt1, pt2, 255, 1)  # We draw the limits

                    pt1 = (int(cX + math.cos((sec_angle) / 180 * math.pi) * (diameters[0] + 2)),
                           int(cY + math.sin(sec_angle / 180 * math.pi) * (diameters[0] + 2)))
                    pt2 = (int(cX + math.cos(sec_angle / 180 * math.pi) * (diameters[1] - 2)),
                           int(cY + math.sin(sec_angle / 180 * math.pi) * (diameters[1] - 2)))
                    empty_img = cv2.line(empty_img, pt1, pt2, 255, 1)  # We draw the limits
                    empty_img = cv2.rectangle(empty_img, (0, 0), (image.shape[1], image.shape[0]), color=255,
                                              thickness=1)  # If the shape is bigger than image

                    cnts, h = cv2.findContours(empty_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
                    cnts = [cnts[i] for i in range(len(cnts)) if h[0][i][3] >= 0]
                    image = cv2.drawContours(image, cnts, -1, [int(c) for c in color], -1)

            for circle in range(len(list_rads)):
                image = cv2.circle(image, (cX, cY), int(list_rads[circle]), (0, 0, 0), 2)
                if circle > 0:
                    for cur_angle in list_angles[circle]:
                        pt1 = (int(cX + math.cos(math.pi + cur_angle) * list_rads[circle - 1]),
                               int(cY + math.sin(math.pi + cur_angle) * list_rads[circle - 1]))
                        pt2 = (int(cX + math.cos(math.pi + cur_angle) * list_rads[circle]),
                               int(cY + math.sin(math.pi + cur_angle) * list_rads[circle]))
                        image = cv2.line(image, pt1, pt2, (0, 0, 0), 2)  # We draw the limits
            image = cv2.circle(image, (cX, cY), int(last_rad), (0, 0, 0), 2)

            image[(50): (image.shape[0] - 50), (image.shape[1] - 75):(image.shape[1])] = (150, 150, 150)

            for raw in range(image.shape[0] - 150):
                color = colors[int((raw / (image.shape[0] - 150)) * (len(colors) - 1))]
                image[image.shape[0] - 75 - raw, (image.shape[1] - 65):(image.shape[1] - 45)] = color

            image = cv2.putText(image, "100%", (image.shape[1] - 43, 75), cv2.FONT_HERSHEY_SIMPLEX,
                                     fontScale=0.4, color=(0, 0, 0), thickness=1)
            image = cv2.putText(image, "50%", (image.shape[1] - 43, int(image.shape[0] / 2)),
                                     cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(0, 0, 0), thickness=1)

            image = cv2.putText(image, "0%", (image.shape[1] - 43, image.shape[0] - 75),
                                     cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(0, 0, 0), thickness=1)

            return (new_row, image)


def calculate_dist_one_pt_Line(Ligne, Pt, Scale="NA", between_Pt_dist="NA", get_proj=False):
    '''Calculate and return the distance between one point and it's projection on a segment.
    Line: an array containing the coordinates of the two points defining the segment.
    Pt: The coordinates of the point.
    Scale: The video scale (to convert units to px).
    between_Pt_dist: the length of the segment (avoid recalculation if already done).
    get_proj= Boolean, if true also return the coordinates of the point projection on the segment.
    '''
    if between_Pt_dist == "NA":
        between_Pt_dist = math.sqrt((Ligne[1][0] - Ligne[0][0]) ** 2 + (Ligne[1][1] - Ligne[0][1]) ** 2)

    t = None
    dx = Ligne[0][0] - Ligne[1][0]
    dy = Ligne[0][1] - Ligne[1][1]
    prod = (float(Pt[0]) - Ligne[1][0]) * dx + (float(Pt[1]) - Ligne[1][1]) * dy
    if prod >= 0 and prod <= (dx * dx + dy * dy) and between_Pt_dist > 0:
        dist = abs((Ligne[1][0] - Ligne[0][0]) * (Ligne[0][1] - float(Pt[1])) - (Ligne[0][0] - float(Pt[0])) * (Ligne[1][1] - Ligne[0][1])) / between_Pt_dist
        if get_proj:
            if (Ligne[1][0] - Ligne[0][0])==0:
                t = [Ligne[1][0], Pt[1]]
            elif (Ligne[1][1] - Ligne[0][1])==0:
                t=[Pt[0], Ligne[1][1]]
            else:
                a=(Ligne[1][1] - Ligne[0][1])/(Ligne[1][0] - Ligne[0][0])
                b=Ligne[1][1]-(a*Ligne[1][0])
                slope_pt=-1/a
                bperp=-slope_pt*Pt[0]+Pt[1]
                t_x=(bperp-b)/(a-slope_pt)
                t=[t_x,slope_pt*t_x+bperp]

    else:
        dist_pt1 = math.sqrt((Ligne[0][0] - float(Pt[0])) ** 2 + (Ligne[0][1] - float(Pt[1])) ** 2)
        dist_pt2 = math.sqrt((Ligne[1][0] - float(Pt[0])) ** 2 + (Ligne[1][1] - float(Pt[1])) ** 2)
        if get_proj:
            t = [Ligne[0], Ligne[1]][[dist_pt1, dist_pt2].index(min(dist_pt1, dist_pt2))]
        dist = min(dist_pt1, dist_pt2)

    if Scale != "NA": dist = dist / Scale
    return (dist, t)


def change_NA(val):
    """If the value is 'NA', return np.nan, else return the original value as a float."""
    if val==-1000:
        val=np.nan
    else:
        val=float(val)
    return(val)

class speed_calculations:
    """Class containing various functions to extract the analyses results from the target's trajectories. This class
    is also used as a temporary container of the value of threshold speed (defined by user) and of the elements of
    interest used for the analyses of spatial repartition
    """

    def __init__(self, seuil_movement=0):
        self.seuil_movement=seuil_movement
        self.Areas=[]

    def calculate_nei(self, Pts_coos, ind, dist, Scale, Fr_rate, to_save=False):
        """Extract all inter-individual measurements.
        Pts_coos: Targets coordinates
        ind: target identifiant (number) we are interested in
        dist: the distance threshold to consider that two targets are in contact
        Scale: The video scale (to convert units to px).
        Fr_rate: The video frame rate (to convert frames to seconds)
        to_save: if True, return all the values for all targets, if false, return only a subsample of the results
        related to the ind target.
        """
        Nb_ind=len(Pts_coos)
        dist = float(dist) * Scale

        table_nb_frame=np.zeros([Nb_ind,Nb_ind])
        liste_nb_nei=[0]*Nb_ind
        liste_is_close = np.array([0]*Nb_ind)
        liste_min_dist_nei=[0]*Nb_ind
        liste_nb_frames=[len(Pts_coos[0])]*Nb_ind
        table_all_dists = np.zeros([Nb_ind, Nb_ind])
        if to_save : Save_all_dists=[]

        if to_save:
            table_is_close=np.zeros([Nb_ind,Nb_ind])
            table_is_contact=np.zeros([Nb_ind,Nb_ind])
            table_nb_contacts = np.zeros([Nb_ind, Nb_ind])
            list_events=[]


        for ligne in range(len(Pts_coos[0])):
            coos=[[change_NA(Pts_coos[i][ligne][0]),change_NA(Pts_coos[i][ligne][1])] for i in range(Nb_ind)]
            table_dists=cdist(coos, coos)
            scale=lambda x: x/Scale
            table_dists2=np.copy(table_dists)
            table_dists2=scale(table_dists2)

            if to_save: Save_all_dists.append(table_dists2)

            for row in range(Nb_ind):
                table_dists[row, row] = np.nan

            #All distances between inds
            if to_save:
                for row in range(Nb_ind):
                    table_is_close[row, row] = 0

                table_nb_frame[np.where(~np.isnan(table_dists))] = table_nb_frame[np.where(~np.isnan(table_dists))] + 1
                table_is_close[np.where(table_dists<dist)]=table_is_close[np.where(table_dists<dist)]+1
                if np.any(np.logical_and(table_dists < dist, table_is_contact == 0)):
                    table_nb_contacts[np.logical_and(table_dists < dist, table_is_contact == 0)]=table_nb_contacts[np.logical_and(table_dists < dist, table_is_contact == 0)]+1

                if np.any(np.logical_and(np.logical_or(table_dists >= dist, np.isnan(table_dists)), table_is_contact > 0)) or ((np.any(table_is_contact > 0) and ligne==(len(Pts_coos[0])-1))):
                    for row in range(len(table_is_contact)):
                        table_is_contact[row][row:len(table_is_contact)]=np.nan

                    if ligne<(len(Pts_coos[0])-1):
                        pos=np.where(np.logical_and(np.logical_or(table_dists >= dist, np.isnan(table_dists)),table_is_contact > 0))
                    else:
                        pos=np.where(table_is_contact > 0)

                    list_events=list_events+[[pos[0][i], pos[1][i], table_is_contact[pos[0][i], pos[1][i]]/Fr_rate, (ligne-table_is_contact[pos[0][i], pos[1][i]])/Fr_rate] for i in range(len(pos[0]))]

                table_is_contact[np.where(table_dists < dist)] = table_is_contact[np.where(table_dists < dist)] + 1
                table_is_contact[np.where(np.logical_or(table_dists >= dist,np.isnan(table_dists)))] = 0

            table_all_dists[np.where(~np.isnan(table_dists))]=np.add(table_all_dists[np.where(~np.isnan(table_dists))],table_dists[np.where(~np.isnan(table_dists))])
            # Close to at least one neighbor
            liste_is_close[np.any(table_dists<dist,0)]=liste_is_close[np.any(table_dists<dist,0)]+1
            #Number of neighbor
            liste_nb_nei=liste_nb_nei+(np.sum(table_dists < dist,0))
            #Shortest distance to a neighbor
            liste_min_dist_nei = [np.nansum([a, b]) for a, b in zip(liste_min_dist_nei, np.nanmin(table_dists,axis=0))]
            #Number of frames not lost
            liste_nb_frames=liste_nb_frames-np.all(np.isnan(table_dists),0)


        liste_nb_nei=np.divide(liste_nb_nei,liste_nb_frames)#Average number of neighbours
        liste_is_close=np.divide(liste_is_close,liste_nb_frames)#Prop of time close to at least one neighbourg
        liste_min_dist_nei=scale(np.divide(liste_min_dist_nei,liste_nb_frames))
        liste_all_dists = np.nansum(table_all_dists, axis=0)
        liste_all_dists=scale(np.divide(liste_all_dists,liste_nb_frames))

        if to_save:
            table_is_close=np.divide(table_is_close,table_nb_frame)#Prop of time close to this neighbor
            table_all_dists=scale(np.divide(table_all_dists,table_nb_frame))#Mean distances between individuals

        if not to_save:
            return(liste_nb_nei[ind],liste_is_close[ind],liste_min_dist_nei[ind],liste_all_dists[ind])
        else:
            return (liste_nb_nei, liste_is_close, liste_min_dist_nei, liste_all_dists, table_all_dists, table_is_close, table_nb_contacts, list_events, Save_all_dists)

    def calculate_mean_speed(self, parent,ind, in_move=False):
        """Calculate the average movement speed of the ind target.
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        in_move: if true, only consider speeds that are higher than the speed threshold defined by the user. If false, all the calculated speeds are considered.
        """
        speeds=self.get_all_speeds_ind(parent,ind,in_move)
        speeds=[S for S in speeds if S!="NA"]
        if len(speeds)>0:
            return(sum(speeds)/len(speeds))
        else:
            return("NA")


    def calculate_prop_move(self, parent,ind, return_vals=False):
        """Calculate the proportion of frame for which the target is moving.
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        """
        speeds=self.get_all_speeds_ind(parent,ind, in_move=False, with_NA=True)

        state=[int(val>self.seuil_movement) for val in speeds if val!="NA"]
        if len(state)>0:
            val_s= (sum(state) / len(state))
        else:
            val_s="NA"

        if not return_vals:
            return val_s
        else:
            states=[int(val>self.seuil_movement) if val!="NA" else "NA" for val in speeds]
            return(val_s,states)



    def get_all_speeds_ind(self, parent, ind, in_move=False, with_NA=False):
        """Calculate the speed of an individual for each frame.
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        in_move: if true, only consider speeds that are higher than the speed threshold defined by the user. If false, all the calculated speeds are considered.
        #With_NA: if true, missing speed is replaced by NA value, if false, missing speed is not returned
        """

        speeds = []
        speeds.append("NA")
        for ligne in range(len(parent.Coos[ind])):
            if ligne > 0 and parent.Coos[ind,ligne,0] != -1000 and parent.Coos[ind,ligne - 1,0] != -1000:
                try:
                    dist = math.sqrt((float(parent.Coos[ind,ligne,0]) - float(parent.Coos[ind,ligne - 1,0])) ** 2 + (float(parent.Coos[ind,ligne,1]) - float(parent.Coos[ind,ligne - 1,1])) ** 2)
                except:
                    pass
                speed = (dist / float(parent.Vid.Scale[0])) / (1 / parent.Vid.Frame_rate[1])
                if (in_move and speed > self.seuil_movement) or not in_move:
                    speeds.append(speed)
            elif ligne > 0 and (parent.Coos[ind,ligne,0] == -1000 or parent.Coos[ind,ligne - 1,0] == -1000) and with_NA:
                speeds.append("NA")
        return(speeds)

    def get_all_speeds_NAs(self, parent, ind, in_move=False):
        """Similar than get_all_speeds_ind function, but in that case, NA values are replaced by 0 (for graphical purpose only).
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        in_move: if true, only consider speeds that are higher than the speed threshold defined by the user. If false, all the calculated speeds are considered.
        """
        speeds = []
        for ligne in range(len(parent.Coos[ind])):
            if ligne > 0 and parent.Coos[ind,ligne,0] != -1000 and parent.Coos[ind,ligne - 1,0] != -1000:
                dist = math.sqrt((float(parent.Coos[ind,ligne,0]) - float(parent.Coos[ind,ligne - 1,0])) ** 2 + (float(parent.Coos[ind,ligne,1]) - float(parent.Coos[ind,ligne - 1,1])) ** 2)
                speed = (dist / float(parent.Vid.Scale[0])) / (1 / parent.Vid.Frame_rate[1])
                if (in_move and speed > self.seuil_movement) or not in_move:
                    speeds.append(speed)
            else:
                speeds.append(0)
        return(speeds)

    def calculate_lost(self, parent, ind):
        """Calculate the proportion of time an indiivdual is lost.
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        """
        copy=np.array(parent.Coos[ind])
        return(np.count_nonzero(copy[:,0]==-1000)/len(copy[:,0]))



    def calculate_dist(self, parent, ind, in_move=False, return_vals=False):
        """Calculate the distance traveled by the target (in px).
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        in_move: if true, only consider movements that are done with a speed higher than the speed threshold defined by the user. If false, all the calculated distances are considered.
        """
        if return_vals: dists = []
        Sdists=0
        nb_dists=0
        Smeander=0
        nb_Smeander=0
        last=[-1000,-1000]
        last_angle=-1000

        for ligne in range(len(parent.Coos[ind])):
            if ligne > 0 and parent.Coos[ind,ligne,0] != -1000:
                if parent.Coos[ind,ligne - 1,0] != -1000:
                    dist = (math.sqrt((float(parent.Coos[ind][ligne][0]) - float(parent.Coos[ind][ligne - 1][0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(parent.Coos[ind][ligne - 1][1])) ** 2))/ float(parent.Vid.Scale[0])
                    speed = (dist) / (1 / parent.Vid.Frame_rate[1])
                    last=parent.Coos[ind][ligne]

                    angle = math.atan2((parent.Coos[ind][ligne - 1][1] - parent.Coos[ind][ligne][1]), (parent.Coos[ind][ligne - 1][0] - parent.Coos[ind][ligne][0]))
                    angle = (angle*180)/math.pi

                    if (last_angle != -1000):
                        angle_diff = angle - last_angle

                        if angle_diff > 180: angle_diff -= 360
                        if angle_diff < -180: angle_diff += 360
                        angle_diff=abs(angle_diff)

                    if return_vals: dists.append(dist)
                    if (in_move and speed > self.seuil_movement) or not in_move:
                        Sdists+=dist
                        nb_dists+=1

                        if (last_angle != -1000 and dist>0):
                            Smeander += (angle_diff / dist)
                            nb_Smeander += 1

                        last_angle=angle
                    else:
                        last_angle=-1000

                elif last[0]!=-1000:
                    dist = (math.sqrt((float(parent.Coos[ind][ligne][0]) - float(last[0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(last[1])) ** 2))/ float(parent.Vid.Scale[0])
                    speed = (dist) / (1 / parent.Vid.Frame_rate[1])
                    last = parent.Coos[ind][ligne]
                    if return_vals: dists.append(dist)

                    if (in_move and speed > self.seuil_movement) or not in_move:
                        Sdists += dist
                        nb_dists += 1

                    last_angle=-1000

                else:
                    if return_vals: dists.append("NA")
                    last_angle = -1000

            elif return_vals:
                dists.append("NA")

        if nb_dists==0:
            Sdists="NA"

        if(nb_Smeander>0):
            meander_val=Smeander/nb_Smeander
        else:
            meander_val = "NA"

        if not return_vals:
            return (Sdists, meander_val)
        else:
            return(Sdists, dists, meander_val)

    def calculate_speed(self, parent, ind):
        """Calculate the speed of a target at the frame displayed by parent.
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        """
        if (parent.Scrollbar.active_pos*parent.Vid_Lecteur.one_every - parent.Vid.Cropped[1][0]) >= 0:
            coos = parent.Coos[ind,int(round(parent.Scrollbar.active_pos - int((parent.Vid.Cropped[1][0]/parent.Vid_Lecteur.one_every))))]
            prev_coos = parent.Coos[ind][int(round(parent.Scrollbar.active_pos - (parent.Vid.Cropped[1][0]/parent.Vid_Lecteur.one_every) - 1))]
            if coos[0] != -1000 and prev_coos[0] != -1000:
                dist = math.sqrt((float(coos[0]) - float(prev_coos[0])) ** 2 + (float(coos[1]) - float(prev_coos[1])) ** 2)
                return ((dist / float(parent.Vid.Scale[0])) / (1 / parent.Vid.Frame_rate[1]))
            else:
                return ("NA")
        else:
            return ("NA")


    def calculate_group_inside(self, Coos, Shape, Area, Vid):
        def cal_dist(x):
            if x[0]!=-1000:
                return (math.sqrt((int(float(x[0])) - Shape[1][0][0]) ** 2 + (int(float(x[1])) - Shape[1][0][1]) ** 2))/ float(Vid.Scale[0]) < Shape[2]
            else:
                return(False)

        def cal_dist_border(x):
            if x[0] != -1000:
                return self.calculate_distance_to_border_step1(x,shape=Shape)/ float(Vid.Scale[0]) < Shape[2]
            else:
                return(False)

        def cal_all_borders(x):
            if x[0] != -1000:
                res = cv2.pointPolygonTest(Area, (float(x[0]), float(x[1])),True) / float(Vid.Scale[0])
                if res>=0:
                    return res < Shape[2]
            else:
                return(False)

        def cal_in_shape(x):
            if x[0] != -1000:
                return cv2.pointPolygonTest(cnt[0],(int(float(x[0])), int(float(x[1]))),True) > 0
            else:
                return(False)

        isIn=[]
        if Shape[0]=="Point":
            for C_ind in Coos:
                isIn.append(list(map(cal_dist, C_ind)))

        elif Shape[0]=="Borders":
            for C_ind in Coos:
                isIn.append(list(map(cal_dist_border, C_ind)))

        elif Shape[0]=="All_borders":
            for C_ind in Coos:
                isIn.append(list(map(cal_all_borders, C_ind)))

        else:
            if len(Shape[1]) > 0:
                empty = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
                if Shape[0] == "Ellipse":
                    Function_draw_mask.Draw_elli(empty, [po[0] for po in Shape[1]], [po[1] for po in Shape[1]], 255,
                                                 thick=-1)
                elif Shape[0] == "Rectangle":
                    Function_draw_mask.Draw_rect(empty, [po[0] for po in Shape[1]], [po[1] for po in Shape[1]], 255,
                                                 thick=-1)
                elif Shape[0] == "Polygon":
                    Function_draw_mask.Draw_Poly(empty, [po[0] for po in Shape[1]], [po[1] for po in Shape[1]], 255,
                                                 thick=-1)
                cnt, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            else:
                cnt = []

            if len(cnt)>0:
                for C_ind in Coos:
                    isIn.append(list(map(cal_in_shape, C_ind)))
            else:
                for C_ind in Coos:
                    isIn.append(False)


        isIn = np.array(isIn)
        all = np.count_nonzero(isIn, 0)
        return (min(all), max(all), sum(all) / len(all))



    def calculate_dist_lat(self, parent, Point, ind, Dist, return_vals=False):
        """Extract the measurements relatives to the "Point" element of interest.
        parent: higher level class calling this function
        Point: coordinates of the point
        ind: individual of interest (ID number)
        Dist: Distance of interest around the point
        return_vals:if True, return all the distances for each frame
        """
        if return_vals: dists=[]

        last=[-1000, -1000, 0]#Last know position

        is_inside=0
        nb_inside=0
        Latency="NA"

        is_inside_abs=0

        last_in="NA" #Whether the target was already inside the perimeter
        Nb_entries=0#Number of time the target entered the area

        #Prop time lost
        Slost=0
        nb_lost=0

        #Prop time moving
        Smoving=0
        nb_moving=0

        #Distance to the point
        Sdists=0
        nb_dists=0

        # Distance traveled
        Sloc=0

        # Distance traveled while moving
        Sloc_move=0

        #Movement speed
        Sspeed=0
        nb_speed=0

        #Movement speed while moving
        Sspeed_move=0
        nb_speed_move=0

        #Meander
        last_angle=-1000
        last_angle_moving = -1000
        Smeander=0
        nb_Smeander=0

        #Meander en mouvement
        Smeander_move=0
        nb_Smeander_move=0

        for ligne in range(len(parent.Coos[ind])):
            was_in = last_in
            #If we don't know were teh taregt is but that it was inside the area last time
            if parent.Coos[ind,ligne,0] == -1000 and was_in==True:
                nb_lost+=1

            if parent.Coos[ind,ligne,0] != -1000:#If we now where the target is
                #We first determine whether the target is inside the perimeter
                dist = (math.sqrt((float(parent.Coos[ind,ligne,0]) - float(Point[0])) ** 2 + (float(parent.Coos[ind,ligne,1]) - float(Point[1])) ** 2)) / float(parent.Vid.Scale[0])
                if return_vals: dists.append(dist)#If we want to save all the detailed data
                Sdists+=dist#We sum the distances between the target and the point of interest
                nb_dists+=1
                if dist<=Dist:
                    #If the target is not lost
                    Slost+=1
                    nb_lost+=1

                    if last_in==False or last_in=="NA":
                        Nb_entries+=1#We count each time the target enters the area

                    last_in=True

                    is_inside+=1#We count the number of frame for which the target was seen inside
                    is_inside_abs+=1

                    if Latency=="NA":
                        Latency=ligne/parent.Vid.Frame_rate[1]#If it is the first time the target is seen inside, we save this time it

                else:
                    last_in = False#It is not inside the area

                nb_inside+=1#We count the total number of frames for which the target was visible

                if return_vals:
                    if parent.Coos[ind,ligne - 1,0] != -1000 and ligne>0 and dist <= Dist and was_in==True: #If we knew the last position of the target and that the target is and was inside the perimeter
                        #Number of frame for which we know whether the individual is moving or not
                        nb_moving += 1

                        #We first save the distance moved
                        dist_move = (math.sqrt((float(parent.Coos[ind][ligne][0]) - float(parent.Coos[ind][ligne - 1][0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(parent.Coos[ind][ligne - 1][1])) ** 2))/ float(parent.Vid.Scale[0])
                        speed = (dist_move) / (1 / parent.Vid.Frame_rate[1])

                        #We record the angle between last and current frame
                        angle = math.atan2((parent.Coos[ind][ligne - 1][1] - parent.Coos[ind][ligne][1]), (parent.Coos[ind][ligne - 1][0] - parent.Coos[ind][ligne][0]))
                        angle = (angle*180)/math.pi

                        #If we knew the last angle, we can calculate turning speed
                        if (last_angle != -1000):
                            angle_diff = angle - last_angle
                            if angle_diff > 180: angle_diff -= 360
                            if angle_diff < -180: angle_diff += 360
                            angle_diff_not_moving=abs(angle_diff)

                        if (last_angle_moving != -1000):
                            angle_diff = angle - last_angle_moving
                            if angle_diff > 180: angle_diff -= 360
                            if angle_diff < -180: angle_diff += 360
                            angle_diff_moving=abs(angle_diff)


                        #Count distance
                        Sloc += dist_move

                        # Count speed
                        Sspeed += speed
                        nb_speed += 1

                        #Count meander
                        if (last_angle != -1000 and dist_move>0):
                            Smeander += (angle_diff_not_moving / dist_move)
                            nb_Smeander += 1
                        last_angle=angle

                        #While moving
                        if (speed > self.seuil_movement):
                            Smoving +=1
                            Sloc_move+=dist_move
                            Sspeed_move += speed
                            nb_speed_move += 1
                            if (last_angle_moving != -1000 and dist_move > 0):
                                Smeander_move += (angle_diff_moving / dist_move)
                                nb_Smeander_move += 1
                            last_angle_moving=angle

                        else:
                            last_angle_moving = -1000

                    elif last[0] != -1000 and dist <= Dist and was_in==True:#Si il y a eu des valeurs de NA, on considère que l'individu a parcouru au moins la distance entre ces deux points
                        dist_move = (math.sqrt((float(parent.Coos[ind][ligne][0]) - float(last[0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(last[1])) ** 2)) / float(parent.Vid.Scale[0])
                        speed = (dist_move) / (1 / parent.Vid.Frame_rate[1])
                        Sloc += dist_move

                        is_inside_abs+=ligne - last[2]

                        if (speed > self.seuil_movement) :
                            Sloc_move += dist_move

                        last_angle = -1000
                        last_angle_moving = -1000

                    else:
                        last_angle=-1000
                        last_angle_moving = -1000

                last=list(parent.Coos[ind,ligne,:])+[ligne]#We save the last known coordinates

            else:
                last_angle=-1000
                last_angle_moving = -1000
                if return_vals:
                    dists.append("NA")

        if Sdists>0:
            Mean_dist=Sdists/nb_dists
            Prop_Time_in=is_inside/nb_inside
            Absolute_time_inside = is_inside_abs/parent.Vid.Frame_rate[1]
        else:
            Mean_dist = "NA"
            Prop_Time_in = "NA"
            Absolute_time_inside="NA"

        if nb_lost>0:
            Prop_Time_lost_in= 1- Slost/nb_lost
        else:
            Prop_Time_lost_in="NA"

        if nb_moving>0:
            Mean_time_moving_in = Smoving / nb_moving
        else:
            Mean_time_moving_in="NA"

        if nb_speed>0:
            Speed_in = Sspeed / nb_speed
        else:
            Speed_in = "NA"

        Distance_traveled_in=Sloc
        Distance_traveled_moving_in = Sloc_move


        if nb_speed_move>0:
            Speed_moving_in=Sspeed_move/nb_speed_move
        else:
            Speed_moving_in="NA"
        if nb_Smeander>0:
            Meander_in=Smeander/nb_Smeander
        else:
            Meander_in="NA"
        if nb_Smeander_move>0:
            Meander_moving_in = Smeander_move / nb_Smeander_move
        else:
            Meander_moving_in="NA"

        if not return_vals:
            return([Mean_dist, Latency, Prop_Time_in])
            #Average distance between the point and the target of interest, Latency before the distance between the point and the target is lower than Dist
        else:
            return ([Mean_dist, Latency, Prop_Time_in, Nb_entries,Prop_Time_lost_in,Mean_time_moving_in,Distance_traveled_in,Distance_traveled_moving_in,Speed_in,Speed_moving_in,Meander_in,Meander_moving_in, Absolute_time_inside, dists])

    def calculate_intersect(self, Vid, Coos, Points):
        """Count the number of times a target crosses a segment. Also record the latency to cross
        parent: higher level class calling this function
        Points: coordinates of the segment
        ind: individual of interest (ID number)
        """
        if len(Points)==2:#Avoid errors
            touched_border = False  # If a target stay more than 1 frame exactly on the segment
            Latency = "NA"
            nb_cross = 0
            nb_cross_TL_BR =0
            last=[-1000,-1000]
            dist_seg=math.sqrt((Points[0][0]-Points[1][0])**2 + (Points[0][1]-Points[1][1])**2)
            list_of_crosses=[]

            if dist_seg>0:#We verify that the two points defining the segment are not at the same place
                if abs(Points[1][0] - Points[0][0]) > abs(Points[1][1] - Points[0][1]):
                    vertical = True
                else:
                    vertical = False

                for ligne in range(len(Coos)):
                    if ligne > 0 and Coos[ligne,0] != -1000:
                        if Coos[ligne - 1,0] != -1000:
                            last = Coos[ligne]
                            dist_trav =math.sqrt((float(Coos[ligne,0]) - float(Coos[ligne - 1,0])) ** 2 + (float(Coos[ligne,1]) - float(Coos[ligne - 1,1])) ** 2)
                            if dist_trav>0:#Si l'individu est en mouvement
                                Pt1 = (float(Coos[ligne-1,0]), float(Coos[ligne-1,1]))
                                Pt2=(float(Coos[ligne,0]),float(Coos[ligne,1]))


                                is_inter=self.inter(Points[0], Pt1, Pt2)[0] != self.inter(Points[1], Pt1, Pt2)[0] and self.inter(Points[0], Points[1], Pt1)[0] != self.inter(Points[0], Points[1], Pt2)[0]
                                is_crossed=self.inter(Points[0], Pt1, Pt2)[1] != self.inter(Points[1], Pt1, Pt2)[1] and self.inter(Points[0], Points[1], Pt1)[1] != self.inter(Points[0], Points[1], Pt2)[1]


                                if is_crossed and not touched_border:
                                    #If there is a cross, we want to know if it is from left to right/top to bottom
                                    if (Points[1][0] - Points[0][0]) == 0:
                                        t = [Points[1][0], Pt1[1]]
                                    elif (Points[1][1] - Points[0][1]) == 0:
                                        t = [Pt1[0], Points[1][1]]
                                    else:
                                        a = (Points[1][1] - Points[0][1]) / (Points[1][0] - Points[0][0])
                                        b = Points[1][1] - (a * Points[1][0])
                                        slope_pt = -1 / a
                                        bperp = -slope_pt * Pt1[0] + Pt1[1]
                                        t_x = (bperp - b) / (a - slope_pt)
                                        t = [t_x, slope_pt * t_x + bperp]
                                    if vertical:
                                        if Pt1[1]<t[1]:
                                            nb_cross_TL_BR += 1
                                    else:
                                        if Pt1[0]<t[0]:
                                            nb_cross_TL_BR += 1

                                    nb_cross+=1
                                    list_of_crosses.append(ligne/Vid.Frame_rate[1])


                                    if Latency=="NA":
                                        Latency=ligne/Vid.Frame_rate[1]
                                    if is_crossed and not is_inter:
                                        touched_border = True
                                else:
                                    touched_border = False
                        elif last[0]!=-1000:
                            dist_trav = math.sqrt((float(Coos[ligne,0]) - float(last[0])) ** 2 + (float(Coos[ligne,1]) - float(last[1])) ** 2)
                            if dist_trav > 0:
                                Pt1 = (float(last[0]), float(last[1]))
                                Pt2 = (float(Coos[ligne,0]), float(Coos[ligne,1]))
                                is_inter = self.inter(Points[0], Pt1, Pt2)[0] != self.inter(Points[1], Pt1, Pt2)[0] and \
                                           self.inter(Points[0], Points[1], Pt1)[0] != \
                                           self.inter(Points[0], Points[1], Pt2)[0]
                                is_crossed = self.inter(Points[0], Pt1, Pt2)[1] != self.inter(Points[1], Pt1, Pt2)[1] and \
                                             self.inter(Points[0], Points[1], Pt1)[1] != \
                                             self.inter(Points[0], Points[1], Pt2)[1]
                                if is_crossed and not touched_border:

                                    #If there is a cross, we want to know if it is from left to right/top to bottom
                                    if (Points[1][0] - Points[0][0]) == 0:
                                        t = [Points[1][0], Pt1[1]]
                                    elif (Points[1][1] - Points[0][1]) == 0:
                                        t = [Pt1[0], Points[1][1]]
                                    else:
                                        a = (Points[1][1] - Points[0][1]) / (Points[1][0] - Points[0][0])
                                        b = Points[1][1] - (a * Points[1][0])
                                        slope_pt = -1 / a
                                        bperp = -slope_pt * Pt1[0] + Pt1[1]
                                        t_x = (bperp - b) / (a - slope_pt)
                                        t = [t_x, slope_pt * t_x + bperp]
                                    if vertical:
                                        if Pt1[1]<t[1]:
                                            nb_cross_TL_BR += 1
                                    else:
                                        if Pt1[0]<t[0]:
                                            nb_cross_TL_BR += 1

                                    nb_cross += 1
                                    list_of_crosses.append(ligne / Vid.Frame_rate[1])
                                    if Latency=="NA":
                                        Latency=ligne/Vid.Frame_rate[1]
                                    if is_crossed and not is_inter:
                                        touched_border = True
                                else:
                                    touched_border = False

            return(nb_cross, nb_cross_TL_BR, Latency, vertical, list_of_crosses)
        else:
            return ("NA", "NA", "NA", "NA", "NA")

    def inter(self, A, B, C):
        return ((C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0]),(C[1] - A[1]) * (B[0] - A[0]) >= (B[1] - A[1]) * (C[0] - A[0]))


    def calculate_dist_line(self, parent, Points, ind, return_vals=False):
        """Calculate the average distance between a target and a segment of interest.
        parent: higher level class calling this function
        Points: coordinates of the segment
        ind: individual of interest (ID number)
        """
        if len(Points)==2:
            Sdists=0
            nb=0
            if return_vals: dists=[]
            for ligne in range(len(parent.Coos[ind,:,0])):
                if parent.Coos[ind,ligne,0] != -1000:
                    dist,_=calculate_dist_one_pt_Line(Points, Pt=parent.Coos[ind,ligne],Scale=float(parent.Vid.Scale[0]))
                    if return_vals: dists.append(dist)
                    Sdists+=dist

                    nb+=1
                elif return_vals:
                    dists.append("NA")

            if Sdists>0:
                Mean_dist=Sdists/nb
            else:
                Mean_dist="NA"


            if not return_vals:
                return (Mean_dist)
            else:
                return (Mean_dist,dists)
        elif not return_vals:
            return("NA")
        elif return_vals:
            return ("NA",["NA"]*len(parent.Coos[ind])-1)

    def calculate_dist_border(self, parent, Area, ind, shape, return_vals=False):
        """Calculate the distance between the target and the border of the arena and average it.
        Also calculate the proportion of time the target spent at less than X px from the border (distance defined by user and stored in "shape")
        parent: higher level class calling this function
        Area: contour defining the arena (see opencv FindContours)
        ind: individual of interest (ID number)
        shape: the information relative to the border of interest
        """
        if return_vals: dists=[]

        is_inside=0
        nb_is_inside=0

        Sdists=0
        nb=0
        try:
            dist_limit=shape[2].get()
        except:
            dist_limit = shape[2]
        for ligne in range(len(parent.Coos[ind])):
            if parent.Coos[ind,ligne,0] != -1000:
                res=cv2.pointPolygonTest(Area, (float(parent.Coos[ind,ligne,0]), float(parent.Coos[ind,ligne,1])), True)
                if res>=0:
                    res=res/float(parent.Vid.Scale[0])
                    if return_vals:
                        dists.append(res)
                    Sdists+=res
                    nb+=1
                    if res <=dist_limit:
                        is_inside+=1
                    nb_is_inside+=1
                else:
                    if return_vals:
                        dists.append(0)
            elif return_vals:
                dists.append("NA")

        if Sdists>0:
            Mean_dist=Sdists/nb
            Prop_inside=is_inside/nb_is_inside
        else:
            Mean_dist="NA"
            Prop_inside="NA"
        if not return_vals:
            return (Mean_dist, Prop_inside)
        else:
            return (Mean_dist, Prop_inside, dists)


    def calculate_distance_to_border_step1(self, Pt, shape):
        possible_dists = []
        if Pt[0]!=-1000:
            for Points in shape[1]:
                possible_dists.append(calculate_dist_one_pt_Line(Points, Pt)[0])
        if len(possible_dists)>0:
            return(min(possible_dists))
        else:
            return("NA")

    def calculate_dist_sep_border(self, parent, shape, ind, return_vals=False):
        """Idem than calculate_dist_border, but with only a part of the borders (defined by user and stored in "shape")
        """
        if return_vals: dists=[]
        Sdists=0
        nb_dists=0
        is_inside=0
        nb_inside=0

        Latency="NA"
        try:
            limit=shape[2].get()
        except:
            limit = shape[2]
        for ligne in range(len(parent.Coos[ind])):
            # Is it possible to project the point?
            if parent.Coos[ind,ligne,0] != -1000:
                mini_dist=self.calculate_distance_to_border_step1(parent.Coos[ind,ligne],shape)/ float(parent.Vid.Scale[0])
                if mini_dist<=limit:
                    is_inside+=1
                    if Latency=="NA":
                        Latency=ligne/parent.Vid.Frame_rate[1]
                nb_inside+=1
                if return_vals: dists.append(mini_dist)
                Sdists+=mini_dist
                nb_dists+=1
            elif return_vals:
                dists.append("NA")

        if Sdists>0:
            Mean_dist=Sdists/nb_dists
            Prop_inside=is_inside/nb_inside
        else:
            Mean_dist="NA"
            Prop_inside="NA"
        if not return_vals:
            return (Mean_dist, Prop_inside, Latency)
        else:
            return (Mean_dist, Prop_inside, Latency,dists)

    def calculate_time_inside(self, parent, cnt, ind, return_vals=False):
        """Calculate the proportion of time a target spent in a given shape (cnt) and the latency to enter
        parent: higher level class calling this function
        cnt: contour defining the shape of interest (see opencv FindContours)
        ind: individual of interest (ID number)
        """
        Latency = "NA"
        if return_vals: dists=[]
        if len(cnt)>0:
            last = [-1000, -1000, 0]  # Last know position

            is_inside = 0
            nb_inside = 0
            is_inside_abs = 0

            last_in = "NA"  # Whether the target was already inside the perimeter
            Nb_entries = 0  # Number of time the target entered the area

            # Prop time lost
            Slost = 0
            nb_lost = 0

            # Prop time moving
            Smoving = 0
            nb_moving = 0

            # Distance traveled
            Sloc = 0

            # Distance traveled while moving
            Sloc_move = 0

            # Movement speed
            Sspeed = 0
            nb_speed = 0

            # Movement speed while moving
            Sspeed_move = 0
            nb_speed_move = 0

            # Meander
            last_angle = -1000
            last_angle_moving = -1000
            Smeander = 0
            nb_Smeander = 0

            # Meander en mouvement
            Smeander_move = 0
            nb_Smeander_move = 0

            nb_lignes=0

            for ligne in range(len(parent.Coos[ind])):
                was_in = last_in
                # If we don't know where the target is but that it was inside the area last time
                if parent.Coos[ind, ligne, 0] == -1000 and was_in == True:
                    nb_lost += 1
                if parent.Coos[ind][ligne][0] != -1000:
                    dist = cv2.pointPolygonTest(cnt[0], (int(float(parent.Coos[ind,ligne,0])), int(float(parent.Coos[ind,ligne,1]))),True)
                    dist=-dist/float(parent.Vid.Scale[0])
                    if return_vals: dists.append(dist)
                    if dist <= 0:
                        # If the target is not lost
                        Slost += 1
                        nb_lost += 1

                        if last_in == False or last_in == "NA":
                            Nb_entries += 1  # We count each time the target enters the area

                        last_in = True
                        is_inside += 1  # We count the number of frame for which the target was seen inside
                        is_inside_abs+=1


                        if Latency == "NA":
                            Latency = ligne / parent.Vid.Frame_rate[1]  # If it is the first time the target is seen inside, we save this time it

                    else:
                        last_in = False  # It is not inside the area

                    nb_inside += 1  # We count the total number of frames for which the target was visible

                    if return_vals:
                        if parent.Coos[ind, ligne - 1, 0] != -1000 and ligne > 0 and dist <= 0 and was_in == True:  # If we knew the last position of the target and that the target is and was inside the perimeter
                            # Number of frame for which we know whether the individual is moving or not
                            nb_moving += 1

                            # We first save the distance moved
                            dist_move = (math.sqrt((float(parent.Coos[ind][ligne][0]) - float(parent.Coos[ind][ligne - 1][0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(parent.Coos[ind][ligne - 1][1])) ** 2)) / float(parent.Vid.Scale[0])
                            speed = (dist_move) / (1 / parent.Vid.Frame_rate[1])

                            # We record the angle between last and current frame
                            angle = math.atan2((parent.Coos[ind][ligne - 1][1] - parent.Coos[ind][ligne][1]),
                                               (parent.Coos[ind][ligne - 1][0] - parent.Coos[ind][ligne][0]))
                            angle = (angle * 180) / math.pi

                            # If we knew the last angle, we can calculate turning speed
                            if (last_angle != -1000):
                                angle_diff = angle - last_angle
                                if angle_diff > 180: angle_diff -= 360
                                if angle_diff < -180: angle_diff += 360
                                angle_diff_not_moving = abs(angle_diff)

                            if (last_angle_moving != -1000):
                                angle_diff = angle - last_angle_moving
                                if angle_diff > 180: angle_diff -= 360
                                if angle_diff < -180: angle_diff += 360
                                angle_diff_moving = abs(angle_diff)

                            # Count distance
                            Sloc += dist_move

                            # Count speed
                            Sspeed += speed
                            nb_speed += 1

                            # Count meander
                            if (last_angle != -1000 and dist_move > 0):
                                Smeander += (angle_diff_not_moving / dist_move)
                                nb_Smeander += 1
                            last_angle=angle

                            # While moving
                            if (speed > self.seuil_movement):
                                Smoving += 1
                                Sloc_move += dist_move
                                Sspeed_move += speed
                                nb_speed_move += 1

                                if (last_angle_moving != -1000 and dist_move > 0):
                                    Smeander_move += (angle_diff_moving / dist_move)
                                    nb_Smeander_move += 1
                                last_angle_moving=angle

                            else:
                                last_angle_moving=-1000


                        elif last[0] != -1000 and dist <= 0 and was_in == True:  # Si il y a eu des valeurs de NA, on considère que l'individu a parcouru au moins la distance entre ces deux points
                            dist_move = (math.sqrt((float(parent.Coos[ind][ligne][0]) - float(last[0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(last[1])) ** 2)) / float(parent.Vid.Scale[0])
                            speed = (dist_move) / (1 / parent.Vid.Frame_rate[1])
                            Sloc += dist_move

                            is_inside_abs+=ligne - last[2]

                            if (speed > self.seuil_movement):
                                Sloc_move += dist_move

                            last_angle = -1000
                            last_angle_moving = -1000

                        else:
                            last_angle = -1000
                            last_angle_moving = -1000

                    last = parent.Coos[ind, ligne] + [ligne]  # We save the last known coordinates

                else:
                    last_angle=-1000
                    last_angle_moving = -1000
                    if return_vals:
                        dists.append("NA")

            if nb_inside > 0:
                Prop_inside = is_inside / nb_inside
                Absolute_time_inside = is_inside_abs/parent.Vid.Frame_rate[1]
            else:
                Prop_inside = "NA"
                Absolute_time_inside="NA"

            if nb_lost > 0:
                Prop_Time_lost_in = 1 - Slost / nb_lost
            else:
                Prop_Time_lost_in = "NA"

            if nb_moving > 0:
                Mean_time_moving_in = Smoving / nb_moving
            else:
                Mean_time_moving_in = "NA"

            if nb_speed > 0:
                Speed_in = Sspeed / nb_speed
            else:
                Speed_in = "NA"

            Distance_traveled_in = Sloc
            Distance_traveled_moving_in = Sloc_move

            if nb_speed_move > 0:
                Speed_moving_in = Sspeed_move / nb_speed_move
            else:
                Speed_moving_in = "NA"
            if nb_Smeander > 0:
                Meander_in = Smeander / nb_Smeander
            else:
                Meander_in = "NA"

            if nb_Smeander_move > 0:
                Meander_moving_in = Smeander_move / nb_Smeander_move
            else:
                Meander_moving_in = "NA"

        else:
            Prop_inside = "NA"
            Prop_Time_lost_in = "NA"
            Mean_time_moving_in = "NA"
            Speed_in = "NA"
            Speed_moving_in = "NA"
            Meander_in = "NA"
            Meander_moving_in = "NA"
            if return_vals: dists=["NA"]*len(parent.Coos[ind])-1

        if not return_vals:
            return (Prop_inside, Latency)
        else:
            return (Prop_inside, Latency, Nb_entries,Prop_Time_lost_in,Mean_time_moving_in,Distance_traveled_in,Distance_traveled_moving_in,Speed_in,Speed_moving_in,Meander_in,Meander_moving_in, Absolute_time_inside, dists)

    def calculate_all_inter_dists(self, Pts_coos, Scale):
        """Average the inter-individual distances found and extract its minimum and maximum values.
        Pts_coos: the targets coordinates
        Scale: The video scale (to convert units to px).
        """
        dists=[]
        for ligne in range(len(Pts_coos[0])):
            Pts=[Pt[ligne] for Pt in Pts_coos]
            dist=self.calculate_interind_dist(Pts, Scale)
            if dist!="NA":
                dists.append(dist)

        if len(dists)>0:
            Mean=sum(dists)/len(dists)
            Min = min(dists)
            Max = max(dists)
        else:
            Mean, Min, Max = "NA", "NA", "NA"
        return(Mean,Min,Max)

    def calculate_interind_dist(self, Pts, Scale, draw=False, img=None, thick=1):
        """Calculate all the inter-target distances and sum it for a given frame.
        Pts: coordinates of the targets at the frame of interest
        Scale: The video scale (to convert units to px).
        draw: Boolean, if true, draw on "img" the lines to link the different targets (for illustrative purpose only)
        img: if draw==True, draw the lines on this image
        thick: The thickness of the lines to be drawn if draw==True
        """

        is_NA=False
        new_img=np.copy(img)
        all_dists = 0
        all_Xs = 0
        all_Ys = 0
        nb_pairs = 0
        cmbn = itertools.combinations(range(len(Pts)), 2)

        for pair in cmbn:
            if (Pts[pair[0]][0]==-1000 or Pts[pair[1]][0]==-1000):
                is_NA=True
                break
            nb_pairs += 1
            X1 = float(Pts[pair[0]][0])
            Y1 = float(Pts[pair[0]][1])
            X2 = float(Pts[pair[1]][0])
            Y2 = float(Pts[pair[1]][1])
            dist = math.sqrt((X1 - X2) ** 2 + (Y1 - Y2) ** 2) / Scale
            if draw:
                new_img = cv2.line(new_img, (int(X1), int(Y1)),(int(X2), int(Y2)), (175, 0, 0), thick)
            all_dists = all_dists + dist
            all_Xs = all_Xs + X1 + X2
            all_Ys = all_Ys + Y1 + Y2

        if not is_NA:
            center=(int(all_Xs / (2 * nb_pairs)),int(all_Ys / (2 * nb_pairs)))
        else:
            center=["NA","NA"]
            all_dists="NA"
            new_img=img

        if draw:
            return(new_img,all_dists,center)
        else:
            return (all_dists)



    def Shape_characteristics(self, Shape, Vid, Area):
        Scale=Vid.Scale[0]
        if Shape[0]=="Point":
            Centroid=[Shape[1][0][0] / Scale, Shape[1][0][1] / Scale]
            Xmin=(Shape[1][0][0]  / Scale )- Shape[2]
            Xmax=(Shape[1][0][0] / Scale) + Shape[2]
            Ymin=(Shape[1][0][1]  / Scale) - Shape[2]
            Ymax=(Shape[1][0][1] / Scale) + Shape[2]
            Area=math.pi * (Shape[2]) **2
            Perimeter=math.pi * (Shape[2]) *2

            char = [Centroid[0],Centroid[1],Xmin,Xmax,Ymin,Ymax,Area,Perimeter]

        elif Shape[0]=="Line":
            Centroid=[((Shape[1][0][0]+Shape[1][1][0])/2)/ Scale,((Shape[1][0][1]+Shape[1][1][1])/2) / Scale]
            Xs=[Shape[1][0][0],Shape[1][1][0]]
            Ys = [Shape[1][0][1], Shape[1][1][1]]
            Xmin=(min(Xs)) / Scale
            Xmax=(max(Xs)) / Scale
            Ymin=(min(Ys)) / Scale
            Ymax=(max(Ys)) / Scale
            Area="NA"
            Perimeter=math.sqrt((Shape[1][0][0]-Shape[1][1][0])**2 + (Shape[1][0][1]-Shape[1][1][1])**2) / Scale

            char = [Centroid[0],Centroid[1],Xmin,Xmax,Ymin,Ymax,Area,Perimeter]

        else:
            Xs=[pt[0] for pt in Shape[1]]
            Ys=[pt[1] for pt in Shape[1]]

            mask = Function_draw_mask.draw_mask(Vid)
            Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            Arenas = Function_draw_mask.Organise_Ars(Arenas)
            Arena_pts = Arenas[Area]

            feasable, cnt, feasable_cleaned, cnt_cleaned = draw_shape(Vid,Arena_pts,Shape)

            if feasable:
                chars=self.Cnt_characteristics([cnt],Scale)
                if Shape[0] == "All_borders":
                    char=chars[0]
                    char[6]="NA"
                    char[7]="NA"
                elif Shape[0] == "Borders":
                    char=chars[0]
                    char[0]=np.mean([elem[0] for elem in chars])
                    char[1] = np.mean([elem[1] for elem in chars])
                    char[2] = np.min([elem[2] for elem in chars])
                    char[3] = np.max([elem[3] for elem in chars])
                    char[4] = np.min([elem[4] for elem in chars])
                    char[5] = np.max([elem[5] for elem in chars])
                    char[6]="NA"
                    char[7]="NA"

                else:
                    char=chars[0]
            else:
                char=["NA"]*8

        return (char + [Shape[1]])


    def Cnt_characteristics(self, cnts, Scale):
        results=[]
        for cnt in cnts:
            M = cv2.moments(cnt)
            Centroid = [(M["m10"] / M["m00"]) / Scale, (M["m01"] / M["m00"]) / Scale]
            Xmin = cnt[cnt[:, :, 0].argmin()][0][0] / Scale
            Xmax = cnt[cnt[:, :, 0].argmax()][0][0] / Scale
            Ymin = cnt[cnt[:, :, 1].argmin()][0][1] / Scale
            Ymax = cnt[cnt[:, :, 1].argmax()][0][1] / Scale

            Area = cv2.contourArea(cnt) * (1 / float(Scale)) ** 2
            Perimeter = cv2.arcLength(cnt, True) / Scale
            results.append([Centroid[0],Centroid[1],Xmin,Xmax,Ymin,Ymax,Area,Perimeter])
        return(results)




    def details_Point(self, Xs, Ys, Shape, Scale):
        Dist_to_point = np.sqrt(
            (Xs - Shape[1][0][0]) ** 2 + (Ys - Shape[1][0][1]) ** 2) / Scale
        Inside_circle = np.zeros(len(Dist_to_point))
        Inside_circle[np.where(Dist_to_point <= Shape[2])] = 1
        Inside_circle[np.where(np.isnan(Dist_to_point))] = np.nan
        return([Dist_to_point, Inside_circle])

    def details_All_borders(self, Xs, Ys, Shape, Cnt_Area, Scale):
        def PolyTest(X, Y):
            if np.isnan(X) or np.isnan(Y):
                return (np.nan)
            else:
                return (cv2.pointPolygonTest(Cnt_Area, (X, Y), True))

        Poly_vectorised = np.vectorize(PolyTest)
        Dist_to_border = Poly_vectorised(Xs, Ys) / Scale
        Inside_border = np.zeros(len(Dist_to_border))
        Inside_border[np.where(Dist_to_border <= Shape[2])] = 1
        Inside_border[np.where(np.isnan(Dist_to_border))] = np.nan
        return([Dist_to_border, Inside_border])

    def details_Borders(self, Xs, Ys, Shape, Scale):
        Dist_border = np.zeros([len(Shape[1]), len(Xs)])
        pos = 0
        for Seg in Shape[1]:
            Dist_border[pos, :] = self.Calculate_distance_Line(Seg, Xs, Ys) / Scale
            pos += 1
        Distances_borders = Dist_border.min(axis=0)
        Inside_border = np.zeros(len(Distances_borders))
        Inside_border[np.where(Distances_borders <= Shape[2])] = 1
        Inside_border[np.where(np.isnan(Distances_borders))] = np.nan
        return([Distances_borders, Inside_border])

    def details_shape(self, Xs, Ys, Shape, Scale, Vid, Arena):
        res_cnt, cnt, res_cnt_clean, cnt_clean=draw_shape(Vid, Arena, Shape)

        if res_cnt_clean:
            def PolyTest(X, Y):
                if np.isnan(X) or np.isnan(Y):
                    return (np.nan)
                else:
                    return (cv2.pointPolygonTest(cnt_clean, (X, Y), True))

            Poly_vectorised = np.vectorize(PolyTest)
            Dist_to_shape = Poly_vectorised(Xs, Ys) / Scale
            Inside = np.zeros(len(Dist_to_shape))
            Inside[np.where(Dist_to_shape >= 0)] = 1
            Inside[np.where(np.isnan(Dist_to_shape))] = np.nan
            return ([Dist_to_shape, Inside])
        else:
            return ([["NA"]*len(Xs),["NA"]*len(Ys)])


    def details_line(self, Xs, Ys, Shape, Scale):
        Dist_to_line = self.Calculate_distance_Line(Shape[1],Xs,Ys) / Scale
        return (Dist_to_line)


    def Calculate_distance_Line(self,Line, Xs, Ys):
        between_Pt_dist = math.sqrt((Line[1][0] - Line[0][0]) ** 2 + (Line[1][1] - Line[0][1]) ** 2)

        if between_Pt_dist > 0:
            dx = Line[0][0] - Line[1][0]
            dy = Line[0][1] - Line[1][1]
            Products = (Xs - Line[1][0]) * dx + (Ys - Line[1][1]) * dy

            dists_cond1 = abs((Line[1][0] - Line[0][0]) * (Line[0][1] - Ys) - (
                        Line[0][0] - Xs) * (Line[1][1] - Line[0][1])) / between_Pt_dist
            dist_pt1 = np.sqrt((Line[0][0] - Xs) ** 2 + (Line[0][1] - Ys) ** 2)
            dist_pt2 = np.sqrt((Line[1][0] - Xs) ** 2 + (Line[1][1] - Ys) ** 2)
            dists_cond2 = np.minimum(dist_pt1, dist_pt2)

            Dist_to_line = np.zeros(len(Xs))
            Dist_to_line[np.where((Products >= 0) & (Products <= (dx * dx + dy * dy)))] = dists_cond1[
                np.where((Products >= 0) & (Products <= (dx * dx + dy * dy)))]
            Dist_to_line[np.where(np.logical_not((Products >= 0) & (Products <= (dx * dx + dy * dy))))] = dists_cond2[
                np.where(np.logical_not((Products >= 0) & (Products <= (dx * dx + dy * dy))))]

            Dist_to_line = Dist_to_line

        else:
            Dist_to_line = np.array(len(Xs), np.nan)

        return(Dist_to_line)
