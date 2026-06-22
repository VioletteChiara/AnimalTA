import math
import time
from skimage import draw
import cv2
import numpy as np
import itertools
from scipy.spatial.distance import cdist
from AnimalTA.A_General_tools import Function_draw_arenas
from operator import itemgetter

"""This file contains a set of functions used to extract the analyses results from the target's trajectories"""


def draw_shape(Vid, Arena, Shape):
    Xss = [pt[0] for pt in Shape[1]]
    Yss = [pt[1] for pt in Shape[1]]

    empty = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
    if Shape[0] == "Rectangle":
        empty, _ = Function_draw_arenas.Draw_rect(empty, Xss, Yss, color=(255, 0, 0), thick=-1)
    elif Shape[0] == "Polygon":
        empty, _ = Function_draw_arenas.Draw_Poly(empty, Xss, Yss, color=(255, 0, 0), thick=-1)
    elif Shape[0] == "Ellipse":
        empty, _ = Function_draw_arenas.Draw_elli(empty, Xss, Yss, color=(255, 0, 0), thick=-1)
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

    mask_glob = Function_draw_arenas.draw_mask(Vid)
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

def calculate_exploration(method, Vid, Coos, deb, end, Arena, show=False, image=None, subsample=False, only_vals=False, load_frame=None, return_cell=False):
    new_row=[]

    if not load_frame is None:
        Load_bar, ID_pos, Nb_to_do  =load_frame

    if subsample:
        if len(Coos[deb:end + 1])>25000:
            step=len(Coos[deb:end + 1])//25000
            Coos=Coos[deb:end + 1][::step].copy()

    # Exploration:
    if method[0] == 0:  # Si c'est method moderne
        radius = math.sqrt((float(method[1])) / math.pi)
        empty = np.zeros((Vid.shape[0], Vid.shape[1], 1), np.uint8)
        last_pt = [-1000, -1000]
        if not only_vals:
            if radius > 0:
                pt_done=0
                nb_pt=len(Coos[deb:end + 1])
                for pt in Coos[deb:end + 1]:
                    if not load_frame is None:
                        Load_bar.show_load(ID_pos / Nb_to_do + ((pt_done/nb_pt) * (1 / Nb_to_do)))
                    if pt[0] != -1000 and last_pt[0] != -1000 and not np.isnan(pt[0]) and not np.isnan(last_pt[0]):
                        cv2.line(empty, (int(float(last_pt[0])), int(float(last_pt[1]))),
                                 (int(float(pt[0])), int(float(pt[1]))), (255),
                                 max(1, int(radius * 2 * float(Vid.Scale[0]))))
                    elif pt[0] != -1000 and not np.isnan(pt[0]):
                        cv2.circle(empty, (int(float(pt[0])), int(float(pt[1]))),
                                   int(radius * float(Vid.Scale[0])), (255), -1)
                    last_pt = pt
                    pt_done+=1


            mask_glob = Function_draw_arenas.draw_mask(Vid)
            mask = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
            mask = cv2.drawContours(mask, [Arena], -1, (255), -1)
            mask = cv2.bitwise_and(mask, mask_glob)
            empty = cv2.bitwise_and(mask, empty)

            new_row.append(np.sum(empty > [0]) * (1 / float(Vid.Scale[0]) ** 2))  # We want to save the total surface explored (independantly of the size of the arena)
            new_row.append(len(np.where(empty > [0])[0]) / len(np.where(mask == [255])[0]))  # Now relative to the arena area
            new_row.append("Modern")  # Method
            new_row.append(method[1])  # Area
            new_row.append("NA")  # Param_aspect

            to_return=[new_row]
            if show:
                to_return.append(empty)
            if return_cell:
                to_return.append(None)

            return(to_return)

        else:
            empty = np.zeros((Vid.shape[0], Vid.shape[1], 1), np.int64)

            pt_done = 0
            nb_pt = len(Coos[deb:end + 1])
            for pt in Coos[deb:end + 1]:
                if not load_frame is None:
                    Load_bar.show_load(ID_pos / Nb_to_do + ((pt_done / nb_pt) * (1 / Nb_to_do)))
                if pt[0] != "NA":
                    xx, yy = draw.disk((int(pt[0]), int(pt[1])),
                                       radius=int(radius * float(Vid.Scale[0])),
                                       shape=[empty.shape[1], empty.shape[0], 1])
                    empty[yy, xx] += 1
                pt_done+=1

            to_return = [None, empty, None]
            if return_cell:
                to_return.append(None)

            return (to_return)

    elif method[0] == 1:  # Si c'est mesh carré
        No_NA_Coos = np.array(Coos[deb:end + 1])
        No_NA_Coos[np.all(No_NA_Coos == -1000, axis=1)]=np.nan
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

        NA_XYs = np.array(list(zip(Xs, Ys)))
        XYs = NA_XYs[~np.isnan(NA_XYs).any(axis=1)]
        XYs=np.int32(XYs)

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
            to_return = [new_row]
            if return_cell:
                to_return.append([NA_XYs,(nb_squares_v * nb_squares_h)])

            return(to_return)

        elif not only_vals:
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

            image = cv2.copyMakeBorder(image, 0, 0, 0, 75, cv2.BORDER_CONSTANT, value=[255, 255, 255])

            image[(50): (image.shape[0] - 50), (image.shape[1] - 75):(image.shape[1])] = (150, 150, 150)

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

            to_return = [new_row, image]
            if return_cell:
                to_return.append([NA_XYs,(nb_squares_v * nb_squares_h)])
            return (to_return)

        elif only_vals:
            empty=np.zeros([image.shape[0],image.shape[1],1], np.int64)

            square_done = 0
            nb_square = len(range(len(unique)))
            for square in range(len(unique)):
                if not load_frame is None:
                    Load_bar.show_load(ID_pos / Nb_to_do + ((square_done / nb_square) * (1 / Nb_to_do)))
                value = count[square]

                empty[int(min(Arena[:, :, 1]) - decal_y + unique[square][1] * (largeur)):
                    int(min(Arena[:, :, 1]) - decal_y + (unique[square][1] + 1) * (
                        largeur)), int(min(Arena[:, :, 0]) - decal_x + unique[square][0] * (largeur)):
                      int(min(Arena[:, :, 0]) - decal_x + (unique[square][0] + 1) * (largeur))]=value
                square_done+=1



            to_return = [new_row, empty, (int(round(nb_squares_v*largeur)/2),int(round(nb_squares_h*largeur)/2))]
            if return_cell:
                to_return.append([NA_XYs,(nb_squares_v * nb_squares_h)])

            return (to_return)

    elif method[0] == 2:  # Si c'est mesh circulaire
        No_NA_Coos = np.array(Coos[deb:end + 1])
        No_NA_Coos[np.all(No_NA_Coos == -1000, axis=1)]=np.nan
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
        Circles = ([np.argmax(list_rads > dist) if not np.isnan(dist) else np.nan for dist in Dists])  # In which circle
        Angles = np.arctan2((No_NA_Coos[:, 1] - cY), (No_NA_Coos[:, 0] - cX))
        liste_angles_per_I = [list_angles[int(c)] if not np.isnan(c) else np.nan for c in Circles]
        Portions = [
            np.argmax(liste_angles_per_I[idx] >= (angle + math.pi)) if not np.isnan(liste_angles_per_I[idx]).any() else np.nan
            for idx, angle in enumerate(Angles)
        ]

        NA_Pos = np.array(list(zip(Circles, Portions)))
        Pos = NA_Pos[~np.isnan(NA_Pos).any(axis=1)]
        Pos=np.int32(Pos)


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
            to_return = [new_row]
            if return_cell:
                to_return.append([NA_Pos,(sum(list_nb))])

            return (to_return)

        elif not only_vals:
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

            image = cv2.copyMakeBorder(image, 0, 0, 0, 75, cv2.BORDER_CONSTANT, value=[255,255,255])

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

            to_return = [new_row, image]
            if return_cell:
                to_return.append([NA_Pos,(sum(list_nb))])

            return (to_return)

        elif only_vals:
            empty = np.zeros([image.shape[0], image.shape[1], 1], np.int64)

            square_done = 0
            nb_square = len(range(len(unique)))
            for square in range(len(unique)):
                if not load_frame is None:
                    Load_bar.show_load(ID_pos / Nb_to_do + ((square_done / nb_square) * (1 / Nb_to_do)))
                value = count[square]
                if unique[square][0] == 0:
                    xx, yy = draw.disk((int(cX) , int(cY)),
                                       radius=int(list_rads[unique[square][0]]),
                                       shape=[empty.shape[1], empty.shape[0], 1])
                    empty[yy, xx] =value

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

                    mask = np.zeros([image.shape[0], image.shape[1], 1], np.uint8)
                    mask = cv2.drawContours(mask, cnts, -1, 255, -1)
                    empty[mask == 255]=value
                square_done+=1

            to_return = [new_row, empty, (int(cX) , int(cY))]
            if return_cell:
                to_return.append([NA_Pos,(sum(list_nb))])
            return (to_return)

def calculate_explored(method, Vid, Coos, Arena, sub_load):
    Explored_values_cumulative=[]
    Explored_values_binary = []
    # Exploration:
    radius = math.sqrt((float(method[1])) / math.pi)
    last_pt = [-1000, -1000]
    cumulated_values = np.zeros((Vid.shape[0], Vid.shape[1], 1), np.float64)

    mask_glob = Function_draw_arenas.draw_mask(Vid)
    mask = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
    mask = cv2.drawContours(mask, [Arena], -1, (255), -1)
    mask = cv2.bitwise_and(mask, mask_glob)
    done=0
    if radius > 0:
        for pt in Coos:
            if pt[0]>-1 and not np.isnan(pt[0]):
                if not sub_load is None:
                    sub_load.show_load(done/len(Coos))
                where_to_look = np.zeros((Vid.shape[0], Vid.shape[1], 1), np.uint8)
                cv2.circle(where_to_look, (int(float(pt[0])), int(float(pt[1]))),int(radius * float(Vid.Scale[0])), (255), -1)
                where_to_look = cv2.bitwise_and(mask, where_to_look)
                Explored_values_cumulative.append(np.mean(cumulated_values[where_to_look == 255]))
                if np.count_nonzero(where_to_look == 255)>0:
                    Explored_values_binary.append(np.count_nonzero(cumulated_values[where_to_look == 255] > 0)/np.count_nonzero(where_to_look == 255))
                else:
                    Explored_values_binary.append(np.nan)
            else:
                Explored_values_cumulative.append(np.nan)
                Explored_values_binary.append(np.nan)



            empty = np.zeros((Vid.shape[0], Vid.shape[1], 1), np.uint8)
            if pt[0] != -1000 and last_pt[0] != -1000 and not np.isnan(pt[0]) and not np.isnan(last_pt[0]):
                cv2.line(empty, (int(float(last_pt[0])), int(float(last_pt[1]))),
                         (int(float(pt[0])), int(float(pt[1]))), (255),
                         max(1, int(radius * 2 * float(Vid.Scale[0]))))
                cv2.circle(empty, (int(float(last_pt[0])), int(float(last_pt[1]))),
                           int(radius * float(Vid.Scale[0])), (0), -1)
            if pt[0] != -1000 and not np.isnan(pt[0]):
                cv2.circle(empty, (int(float(pt[0])), int(float(pt[1]))),
                           int(radius * float(Vid.Scale[0])), (255), -1)

            done += 1

            last_pt = pt
            cumulated_values[empty==255] += 1/Vid.Frame_rate[1]

    return (Explored_values_cumulative, Explored_values_binary)




def change_NA(val):
    """If the value is 'NA', return np.nan, else return the original value as a float."""
    if val==-1000:
        val=np.nan
    else:
        val=float(val)
    return(val)

def calculate_nei(Pts_coos, ind, dist, Scale, Fr_rate, to_save=False):
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
    scale = lambda x: x / Scale

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

def calculate_speed(parent, ind):
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

def calculate_group_inside( Coos, Shape, Area, Vid):
    def cal_dist(x):
        if x[0]!=-1000:
            return (math.sqrt((int(float(x[0])) - Shape[1][0][0]) ** 2 + (int(float(x[1])) - Shape[1][0][1]) ** 2))/ float(Vid.Scale[0]) < Shape[2]
        else:
            return(False)

    def cal_dist_border(x):
        if x[0] != -1000:
            return calculate_distance_to_border_step1(x,shape=Shape)/ float(Vid.Scale[0]) < Shape[2]
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
                Function_draw_arenas.Draw_elli(empty, [po[0] for po in Shape[1]], [po[1] for po in Shape[1]], 255,
                                             thick=-1)
            elif Shape[0] == "Rectangle":
                Function_draw_arenas.Draw_rect(empty, [po[0] for po in Shape[1]], [po[1] for po in Shape[1]], 255,
                                             thick=-1)
            elif Shape[0] == "Polygon":
                Function_draw_arenas.Draw_Poly(empty, [po[0] for po in Shape[1]], [po[1] for po in Shape[1]], 255,
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

def calculate_intersect( Vid, Coos, Points):
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


                            is_inter=inter(Points[0], Pt1, Pt2)[0] != inter(Points[1], Pt1, Pt2)[0] and inter(Points[0], Points[1], Pt1)[0] != inter(Points[0], Points[1], Pt2)[0]
                            is_crossed=inter(Points[0], Pt1, Pt2)[1] != inter(Points[1], Pt1, Pt2)[1] and inter(Points[0], Points[1], Pt1)[1] != inter(Points[0], Points[1], Pt2)[1]

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
                            is_inter = inter(Points[0], Pt1, Pt2)[0] != inter(Points[1], Pt1, Pt2)[0] and \
                                       inter(Points[0], Points[1], Pt1)[0] != \
                                       inter(Points[0], Points[1], Pt2)[0]
                            is_crossed = inter(Points[0], Pt1, Pt2)[1] != inter(Points[1], Pt1, Pt2)[1] and \
                                         inter(Points[0], Points[1], Pt1)[1] != \
                                         inter(Points[0], Points[1], Pt2)[1]
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

def inter(A, B, C):
    return ((C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0]),(C[1] - A[1]) * (B[0] - A[0]) >= (B[1] - A[1]) * (C[0] - A[0]))


def calculate_distance_to_border_step1( Pt, shape):
    possible_dists = []
    if Pt[0]!=-1000:
        for Points in shape[1]:
            possible_dists.append(Calculate_distance_Line(Points, np.array([Pt[0]]), np.array([Pt[1]]))[0])
    if len(possible_dists)>0:
        return(min(possible_dists))
    else:
        return("NA")


def calculate_all_inter_dists(Pts_coos, Scale):
    """Average the inter-individual distances found and extract its minimum and maximum values.
    Pts_coos: the targets coordinates
    Scale: The video scale (to convert units to px).
    """
    dists=[]
    for ligne in range(len(Pts_coos[0])):
        Pts=[Pt[ligne] for Pt in Pts_coos]
        dist=calculate_interind_dist(Pts, Scale)
        if dist!="NA":
            dists.append(dist)

    if len(dists)>0:
        Mean=sum(dists)/len(dists)
        Min = min(dists)
        Max = max(dists)
    else:
        Mean, Min, Max = "NA", "NA", "NA"
    return(Mean,Min,Max)

def calculate_interind_dist(Pts, Scale, draw=False, img=None, thick=1, Xadd=None,Yadd=None,ratio=None):
    """Calculate all the inter-target distances and sum it for a given frame.
    Pts: coordinates of the targets at the frame of interest
    Scale: The video scale (to convert units to px).
    draw: Boolean, if true, draw on "img" the lines to link the different targets (for illustrative purpose only)
    img: if draw==True, draw the lines on this image
    thick: The thickness of the lines to be drawn if draw==True
    """

    is_NA=False
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
            cv2.line(img, (int((X1+Xadd)/ratio), int((Y1+Yadd)/ratio)),(int((X2+Xadd)/ratio), int((Y2+Yadd)/ratio)), (175, 0, 0), thick)


        all_dists = all_dists + dist
        all_Xs = all_Xs + X1 + X2
        all_Ys = all_Ys + Y1 + Y2

    if not is_NA:
        center=(int(all_Xs / (2 * nb_pairs)),int(all_Ys / (2 * nb_pairs)))
    else:
        center=["NA","NA"]
        all_dists="NA"
        img=img

    if draw:
        return(all_dists,center)
    else:
        return (all_dists)


def Shape_characteristics(Shape, Vid, Area):
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

        Arenas = Function_draw_arenas.get_arenas(Vid)
        Arena_pts = Arenas[Area]

        feasable, cnt, feasable_cleaned, cnt_cleaned = draw_shape(Vid,Arena_pts,Shape)

        if feasable:
            chars=Cnt_characteristics([cnt],Scale)
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


def Cnt_characteristics(cnts, Scale):
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


def correct_Inside(Inside, deb, end):
    # If an individual was lost outside and found outside: was outside during this time
    Losts_deb = np.where(np.diff((np.isnan(Inside[deb:end + 1]).astype(int))) == 1)[0]
    Losts_ends = np.where(np.diff((np.isnan(Inside[deb:end + 1]).astype(int))) == -1)[0]

    Inside_fixed=Inside.copy()

    if len(Losts_deb) > 0 or len(Losts_ends) > 0:
        if not len(Losts_ends) == 0 and (
                (len(Losts_ends) > 0 and len(Losts_deb) == 0) or Losts_ends[0] <
                Losts_deb[0]):
            Inside_fixed[deb:end + 1][0:Losts_ends[0] + 1] = Inside_fixed[deb:end + 1][Losts_ends[0] + 1]
            Losts_ends = np.delete(Losts_ends, 0, None)

        if not len(Losts_deb) == 0 and (
                (len(Losts_ends) == 0 and len(Losts_deb) > 0) or Losts_ends[
            len(Losts_ends) - 1] < Losts_deb[len(Losts_deb) - 1]):
            Inside_fixed[deb:end + 1][(Losts_deb[len(Losts_deb) - 1]):(len(Inside_fixed[deb:end + 1]))] = \
                Inside_fixed[deb:end + 1][Losts_deb[len(Losts_deb) - 1]]
            Losts_deb = np.delete(Losts_deb, len(Losts_deb) - 1, None)

    for event_lost in range(len(Losts_deb)):
        if Inside_fixed[deb:end + 1][Losts_deb[event_lost]] == 1 and Inside_fixed[deb:end + 1][
            Losts_ends[event_lost] + 1] == 1:
            Inside_fixed[deb:end + 1][Losts_deb[event_lost]:Losts_ends[event_lost] + 1] = 1
        elif Inside_fixed[deb:end + 1][Losts_deb[event_lost]] == 0 and Inside_fixed[deb:end + 1][
            Losts_ends[event_lost] + 1] == 0:
            Inside_fixed[deb:end + 1][Losts_deb[event_lost]:Losts_ends[event_lost] + 1] = 0

    return(Inside_fixed)

def details_Point(Xs, Ys, Shape, Scale):
    Dist_to_point = np.sqrt(
        (Xs - Shape[1][0][0]) ** 2 + (Ys - Shape[1][0][1]) ** 2) / Scale
    Inside_circle = np.zeros(len(Dist_to_point))
    Inside_circle[np.where(Dist_to_point <= Shape[2])] = 1
    Inside_circle[np.where(np.isnan(Dist_to_point))] = np.nan
    return([Dist_to_point, Inside_circle])

def details_All_borders(Xs, Ys, Shape, Cnt_Area, Scale):
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

def details_Borders(Xs, Ys, Shape, Scale):
    Dist_border = np.zeros([len(Shape[1]), len(Xs)])
    pos = 0
    for Seg in Shape[1]:
        Dist_border[pos, :] = Calculate_distance_Line(Seg, Xs, Ys) / Scale
        pos += 1
    Distances_borders = Dist_border.min(axis=0)
    Inside_border = np.zeros(len(Distances_borders))
    Inside_border[np.where(Distances_borders <= Shape[2])] = 1
    Inside_border[np.where(np.isnan(Distances_borders))] = np.nan
    return([Distances_borders, Inside_border])

def details_shape(Xs, Ys, Shape, Scale, Vid, Arena):
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

def details_line(Xs, Ys, Shape, Scale):
    Dist_to_line = Calculate_distance_Line(Shape[1],Xs,Ys) / Scale
    return (Dist_to_line)

def Calculate_distance_Line(Line, Xs, Ys, get_proj=False):
    between_Pt_dist = math.sqrt((Line[1][0] - Line[0][0]) ** 2 + (Line[1][1] - Line[0][1]) ** 2)

    if get_proj:
        projs = np.full((len(Xs), 2), np.nan)  # Store projection points as NaN initially


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

        if get_proj:
            # For each point, calculate the projection on the line
            for i in range(len(Xs)):
                # Calculate the vector from the point to the first point of the line (Line[0])
                Px = Xs[i] - Line[0][0]
                Py = Ys[i] - Line[0][1]

                # Calculate the projection scalar (dot product of P and L divided by the squared length of L)
                projection_scalar = (Px * dx + Py * dy) / (dx ** 2 + dy ** 2)
                projection_scalar = max(-1, min(projection_scalar, 0))

                # Calculate the projection point on the line
                proj_x = Line[0][0] + projection_scalar * dx
                proj_y = Line[0][1] + projection_scalar * dy

                # Store the projection point
                projs[i] = [proj_x, proj_y]

    else:
        Dist_to_line = np.array(len(Xs), np.nan)
        projs=np.array(len(Xs), np.nan)

    if get_proj:
        return Dist_to_line, projs

    return(Dist_to_line)

def separate_0s_1s_durations_nan(State, frame_rate, corr_threshold, return_details=False):
    arr_clean=State.copy()
    arr_clean = np.array(arr_clean, dtype=float)  # Ensure floats to allow NaN
    arr_clean[np.isnan(arr_clean)]=5

    # Find change indices (including NaNs)
    change_indices = np.where(np.diff(arr_clean) != 0)[0] + 1
    indices = np.concatenate(([0], change_indices, [len(arr_clean)-1]))
    durations = np.diff(indices)
    durations = durations/frame_rate

    #We first fill the small groups of 0s or 1s
    for seq in [idx for idx, dur in enumerate(durations) if dur<corr_threshold]:
        if seq==0:

            arr_clean[indices[seq]:indices[seq + 1]] = arr_clean[indices[seq+1]]
        else:
            arr_clean[indices[seq]:indices[seq+1]]=arr_clean[indices[seq]-1]

    arr_clean[arr_clean==5]=np.nan



    #Then we redo the identification of sequences
    change_indices = np.where(np.diff(arr_clean) != 0)[0] + 1
    indices = np.concatenate(([0], change_indices, [len(arr_clean)]))
    durations = np.diff(indices)
    durations = durations/frame_rate


    frac_state = arr_clean[indices[:-1]]
    prev_state = np.concatenate([np.array([np.nan]), arr_clean[indices[1:-1] - 1]])  # Convert to NumPy array
    next_state = np.concatenate([arr_clean[indices[1:-1]], np.array([np.nan])])  # Convert to NumPy array


    # Filter valid 0s and 1s only
    begin_zeros=indices[:-1][frac_state == 0]
    begin_zeros=begin_zeros/frame_rate
    zeros_dur = durations[frac_state == 0]
    zeros_1cens = np.isnan(prev_state[
                               frac_state == 0])  # Indexing works since prev_state is a NumPy array
    zeros_2cens = np.isnan(next_state[
                               frac_state == 0])  # Indexing works since next_state is a NumPy array
    zeros_combined_cens = np.logical_or(zeros_1cens, zeros_2cens)
    zeros = np.column_stack((begin_zeros, zeros_dur, zeros_combined_cens)).tolist()


    begin_ones = indices[:-1][frac_state == 1]
    begin_ones=begin_ones/frame_rate
    ones_dur = durations[frac_state == 1]
    ones_1cens = np.isnan(prev_state[
                              frac_state == 1])  # Indexing works since prev_state is a NumPy array
    ones_2cens = np.isnan(next_state[
                              frac_state == 1])  # Indexing works since next_state is a NumPy array
    ones_combined_cens = np.logical_or(ones_1cens, ones_2cens)
    ones = np.column_stack((begin_ones, ones_dur, ones_combined_cens)).tolist()

    if return_details:
        return zeros, ones, np.mean(zeros_dur), np.mean(ones_dur), arr_clean
    else:
        return zeros, ones, np.mean(zeros_dur), np.mean(ones_dur),
