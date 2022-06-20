import cv2
import numpy as np
import math
from statistics import mean
from BioTrack import F_Ellipse



def draw_mask(Vid):
    liste_points=Vid.Mask[1]
    image_to_save = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
    if len(liste_points)>0:
        for i in range(len(liste_points)):
            if len(liste_points[i][0]) > 0:
                if liste_points[i][3] == 1:
                    image_to_save, _ = Draw_elli(image_to_save, liste_points[i][0],
                                                           liste_points[i][1], 255, -1)

                elif liste_points[i][3] == 2 and len(liste_points[i][0]) > 1:
                    image_to_save, _ = Draw_rect(image_to_save, liste_points[i][0],
                                                           liste_points[i][1], 255, -1)

                elif liste_points[i][3] == 3 and len(liste_points[i][0]) > 1:
                    image_to_save, _ = Draw_Poly(image_to_save, liste_points[i][0],
                                                           liste_points[i][1], 255, -1)
    else:
        image_to_save.fill(255)


    return(image_to_save)



def Draw_rect(image, xs, ys, color=(255, 0, 0), thick=int(2)):
    coos = []
    if len(xs) == 2:
        image=cv2.rectangle(image,(int(xs[0]),int(ys[0])),(int(xs[1]),int(ys[1])),color,thick)
        coos=[[int(xs[0]),int(ys[0])],[int(xs[1]),int(ys[0])],[int(xs[0]),int(ys[1])],[int(xs[1]),int(ys[1])]]
    elif len(xs) >2 and len(xs)<5:
        pts=[]
        for i in range(len(xs)):
            pts.append([int(xs[i]),int(ys[i])])

        A=math.sqrt((pts[0][0]-pts[1][0])**2+(pts[0][1]-pts[1][1])**2)
        B=math.sqrt((pts[0][0]-pts[2][0])**2+(pts[0][1]-pts[2][1])**2)
        C=math.sqrt((pts[1][0] - pts[2][0]) ** 2 + (pts[1][1] - pts[2][1]) ** 2)
        Dists=np.array([A,B,C])
        Hypothenuse=np.min((np.where(Dists == np.max(Dists))))

        if Hypothenuse==0:
            pts.append([int(pts[0][0] + pts[1][0]-pts[2][0]),int(pts[0][1] + pts[1][1]-pts[2][1])])
            pts=[pts[0],pts[3],pts[1],pts[2]]

        elif Hypothenuse==1:
            pts.append([int(pts[0][0] + pts[2][0]-pts[1][0]),int(pts[0][1] + pts[2][1]-pts[1][1])])
            pts=[pts[0],pts[3],pts[2],pts[1]]

        elif Hypothenuse==2:
            pts.append([int(pts[1][0] + pts[2][0]-pts[0][0]),int(pts[1][1] + pts[2][1]-pts[0][1])])
            pts=[pts[1],pts[3],pts[2],pts[0]]

        coos=pts

        pts = np.array(pts, np.int32)
        pts = pts.reshape((-1, 1, 2))
        if thick>0:
            image = cv2.polylines(image, [pts], True, color,thickness=thick)
        else:
            image= cv2.fillPoly(image, [pts], color)

    elif len(xs)>4:
        image, _=Draw_Poly(image,xs,ys,color,thick)

    return (image, coos)


def Draw_Poly(image, xs, ys, color=(255, 0, 0), thick=int(2)):
    pts=[]
    for i in range(len(xs)):
        pts.append([int(xs[i]),int(ys[i])])

    pts = np.array(pts, np.int32)
    pts = pts.reshape((-1, 1, 2))

    if thick>0:
        image = cv2.polylines(image, [pts], True, color,thickness=thick)
    else:
        image= cv2.fillPoly(image, [pts], color)

    return (image, pts)


def Draw_elli(image, xs, ys, color=(255, 0, 0), thick=2):

    max_x = None
    min_x = None
    max_y = None
    min_y = None
    if len(xs) == 2:
        mid_x = (xs[0] + xs[1]) / 2
        mid_y = (ys[0] + ys[1]) / 2
        radius = math.sqrt((xs[0] - xs[1]) ** 2 + (ys[0] - ys[1]) ** 2) / 2
        max_x = (mid_x + radius, mid_y)
        min_x = (mid_x - radius, mid_y)
        max_y = (mid_x, mid_y + radius)
        min_y = (mid_x, mid_y - radius)
        image = cv2.circle(image, (int(mid_x), int(mid_y)), int(radius), color, thick)

    elif len(xs) == 3:
        dist_01 = math.sqrt((xs[0] - xs[1]) ** 2 + (ys[0] - ys[1]) ** 2)
        dist_02 = math.sqrt((xs[0] - xs[2]) ** 2 + (ys[0] - ys[2]) ** 2)
        dist_12 = math.sqrt((xs[1] - xs[2]) ** 2 + (ys[1] - ys[2]) ** 2)

        if dist_01 >= max([dist_02, dist_12]):
            radius_min = math.sqrt((xs[0] - xs[1]) ** 2 + (ys[0] - ys[1]) ** 2) / 2
            mid_x = (xs[0] + xs[1]) / 2
            mid_y = (ys[0] + ys[1]) / 2
            radius_max = math.sqrt((xs[2] - mid_x) ** 2 + (ys[2] - mid_y) ** 2)


        elif dist_02 >= max([dist_01, dist_12]):
            radius_min = math.sqrt((xs[0] - xs[2]) ** 2 + (ys[0] - ys[2]) ** 2) / 2
            mid_x = (xs[0] + xs[2]) / 2
            mid_y = (ys[0] + ys[2]) / 2
            radius_max = math.sqrt((xs[1] - mid_x) ** 2 + (ys[1] - mid_y) ** 2)

        else:
            radius_min = math.sqrt((xs[1] - xs[2]) ** 2 + (ys[1] - ys[2]) ** 2) / 2
            mid_x = (xs[1] + xs[2]) / 2
            mid_y = (ys[1] + ys[2]) / 2
            radius_max = math.sqrt((xs[0] - mid_x) ** 2 + (ys[0] - mid_y) ** 2)

        max_x = (mid_x + radius_min, mid_y)
        min_x = (mid_x - radius_min, mid_y)
        max_y = (mid_x, mid_y + radius_max)
        min_y = (mid_x, mid_y - radius_max)
        image = cv2.ellipse(image, (int(mid_x), int(mid_y)), (int(radius_min), int(radius_max)), 0, 0, 360, color,
                            thick)

    elif len(xs) == 4:
        mid_x = mean([max(xs),min(xs)])
        mid_y = mean([max(ys),min(ys)])
        radius_min = (max(xs) - min(xs)) / 2
        radius_max = (max(ys) - min(ys)) / 2
        max_x = (mid_x + radius_min, mid_y)
        min_x = (mid_x - radius_min, mid_y)
        max_y = (mid_x, mid_y + radius_max)
        min_y = (mid_x, mid_y - radius_max)
        image = cv2.ellipse(image, (int(mid_x), int(mid_y)), (int(radius_min), int(radius_max)), 0, 0, 360, color,
                            thick)

    elif len(xs) > 4:
        lsqe = F_Ellipse.LSqEllipse()
        lsqe.fit(np.array([xs, ys]))
        center, width, height, phi = lsqe.parameters()
        phi = float(phi)*180/math.pi
        max_x = (center[0] + width, center[1])
        min_x = (center[0] - width, center[1])
        max_y = (center[0], center[1] + height)
        min_y = (center[0], center[1] - height)
        image = cv2.ellipse(image, (int(center[0]), int(center[1])), (int(width), int(height)), phi, 0, 360,
                            color, thick)

    return (image, [max_x, min_x, max_y, min_y])

def Organise_Ars(Arenas):
    heights = []
    centers = []
    ID = 0
    for Ar in Arenas:
        x, y, w, h = cv2.boundingRect(Ar)
        heights.append(h)
        centers.append([ID, y + (h / 2), x + (w / 2)])
        ID += 1

    rows = []
    centers = np.array(centers, dtype=int)
    while len(centers) > 0:
        first_row = np.where(((min(centers[:, 1]) - max(heights) / 2) < np.array(centers[:, 1])) & (
                np.array(centers[:, 1]) < (min(centers[:, 1]) + max(heights) / 2)))
        cur_row = centers[first_row]
        cur_row = cur_row[cur_row[:, 2].argsort()][:, 0]
        rows = rows + list(cur_row)
        centers = np.delete(centers, first_row, axis=0)
        heights = np.delete(heights, first_row)
    return [Arenas[place] for place in rows]
