import cv2
import numpy as np
import math
from statistics import mean
from AnimalTA.A_General_tools import F_Ellipse


def draw_mask(Vid, thick=-1, color=255):
    """
    This function is used to draw a binary image from the arena's shapes. This binary image will be used as a mask.
    :param Vid: The video concerned, thick: the thickness of the shapes to be drawn (default=filled)
    :return: The binary image
    """

    liste_points=Vid.Mask[1]#Liste_points is a list of all the shapes used to draw the arenas.
    #Structure of liste_points:
    #[Shape1, Shape2,...]
    #With each Shape: [[X1,X2,X3,...], [Y1,Y2,Y3,...], Color_of_the_shape, Shape_type]
    #X and Y are the coordinates of the points used to draw the shape.
    #Shape_type can be: 1=Ellipse, 2=Rectangle, 3=Polygon
    #Color of the shape: (R,G,B)
    #
    image_to_save = np.zeros([Vid.shape[0], Vid.shape[1], 1], np.uint8)
    if len(liste_points)>0:
        for i in range(len(liste_points)):
            if len(liste_points[i][0]) > 0:
                if liste_points[i][3] == 1:
                    image_to_save, _ = Draw_elli(image_to_save, liste_points[i][0],
                                                           liste_points[i][1], color, -1)

                elif liste_points[i][3] == 2 and len(liste_points[i][0]) > 1:
                    image_to_save, _ = Draw_rect(image_to_save, liste_points[i][0],
                                                           liste_points[i][1], color, -1)

                elif liste_points[i][3] == 3 and len(liste_points[i][0]) > 1:
                    image_to_save, _ = Draw_Poly(image_to_save, liste_points[i][0],
                                                           liste_points[i][1], color, -1)
    else:
        #If the user did not define any arena, the whole image will be used.
        image_to_save.fill(color)
    return(image_to_save)


def Draw_rect(image, xs, ys, color=(255, 0, 0), thick=int(2)):
    """Function used to draw a rectangle from 2 to 4 points
    image:The image on the top of which the rectangle will be drawn.
    xs,ys: the coordinate sof the rectangle's corners
    color: the color to draw the rectangle.
    thick: How thick is the border of the rectangle.

    Return:
    The image with the shape drawn
    The coordinates of the points after modification
    """
    coos = []
    if len(xs) == 2:#If there are only two points, we calculate the position of the two missing ones (considering that the rectangle is perfectly horizontal.
        image=cv2.rectangle(image,(int(xs[0]),int(ys[0])),(int(xs[1]),int(ys[1])),color,thick)
        coos=[[int(xs[0]),int(ys[0])],[int(xs[1]),int(ys[0])],[int(xs[0]),int(ys[1])],[int(xs[1]),int(ys[1])]]

    elif len(xs) >2 and len(xs)<5: #If there are three points, we calculate where the fourth should be. If there are four, we reorganise them to avoid that segments cross
        pts=[]
        for i in range(len(xs)):
            pts.append([int(xs[i]),int(ys[i])])

        A=math.sqrt((pts[0][0]-pts[1][0])**2+(pts[0][1]-pts[1][1])**2)
        B=math.sqrt((pts[0][0]-pts[2][0])**2+(pts[0][1]-pts[2][1])**2)
        C=math.sqrt((pts[1][0] - pts[2][0]) ** 2 + (pts[1][1] - pts[2][1]) ** 2)
        Dists=np.array([A,B,C])
        Hypothenuse=np.min((np.where(Dists == np.max(Dists))))

        if Hypothenuse==0:
            if len(pts)<4:
                pts.append([int(pts[0][0] + pts[1][0]-pts[2][0]),int(pts[0][1] + pts[1][1]-pts[2][1])])
            pts=[pts[0],pts[3],pts[1],pts[2]]

        elif Hypothenuse==1:
            if len(pts) < 4:
                pts.append([int(pts[0][0] + pts[2][0]-pts[1][0]),int(pts[0][1] + pts[2][1]-pts[1][1])])
            pts=[pts[0],pts[3],pts[2],pts[1]]

        elif Hypothenuse==2:
            if len(pts) < 4:
                pts.append([int(pts[1][0] + pts[2][0]-pts[0][0]),int(pts[1][1] + pts[2][1]-pts[0][1])])
            pts=[pts[1],pts[3],pts[2],pts[0]]

        coos=pts

        pts = np.array(pts, np.int32)
        pts = pts.reshape((-1, 1, 2))
        if thick>0:
            image = cv2.polylines(image, [pts], True, color,thickness=thick)
        else:
            image= cv2.fillPoly(image, [pts], color)

    elif len(xs)>4:#If the user put more than 4 points, we change the shape to be a Polygon
        image, coos=Draw_Poly(image,xs,ys,color,thick)
    return (image, coos)


def Draw_Poly(image, xs, ys, color=(255, 0, 0), thick=int(2)):
    """Function used to draw a polygon
    image:The image on the top of which the polygon will be drawn.
    xs,ys: the coordinate sof the polygon's corners
    color: the color to draw the polygon.
    thick: How thick is the border of the polygon.

    Return:
    The image with the shape drawn
    The coordinates of the points after modification
    """

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
    """Function used to draw an ellipse
    image:The image on the top of which the ellipse will be drawn.
    xs,ys: the coordinates of the points used to draw the ellipse
    color: the color to draw the ellipse.
    thick: How thick is the border of the ellipse.

    Return:
    The image with the shape drawn
    The coordinates of the 4 points defining the ellipse
    """

    max_x = None
    min_x = None
    max_y = None
    min_y = None
    if len(xs) == 2:#If the user only give two points, we draw a circle with the two point as diameter
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
    """
    This function is used to give an order to the arenas, they will be counted from left to right and from top to bottom.
    :param Arenas: The list of the arenas.
    :return: The same list of Arenas but ordered
    """
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




def Touched_seg(Pt, Seg):
    """This function is used to determine if one point is touching a segment (with a 7px margin)"""
    length_seg=math.sqrt((Seg[1][0] - Seg[0][0]) ** 2 + (Seg[1][1] - Seg[0][1]) ** 2)
    if length_seg>0:
        dx = Seg[0][0] - Seg[1][0]
        dy = Seg[0][1] - Seg[1][1]
        prod = (Pt[0] - Seg[1][0]) * dx + (Pt[1] - Seg[1][1]) * dy
        if prod >= 0 and prod <= (dx * dx + dy * dy):
            return(7>=(abs((Seg[1][0] - Seg[0][0]) * (Seg[0][1] - Pt[1]) - (Seg[0][0] - Pt[0]) * (Seg[1][1] - Seg[0][1])) / length_seg))
        else:
            return(False)
    else:
        return (False)

def draw_line(img, pt1, pt2, color, thickness):
    #Function found at : https://stackoverflow.com/questions/73050416/how-to-draw-a-line-line-with-rectangular-corners-with-opencv-and-python
    #From: https://stackoverflow.com/users/13552470/ann-zen
    x1, y1, x2, y2 = *pt1, *pt2
    theta = np.pi - np.arctan2(y1 - y2, x1 - x2)
    dx = int(np.sin(theta) * thickness / 2)
    dy = int(np.cos(theta) * thickness / 2)
    pts = [
        [x1 + dx, y1 + dy],
        [x1 - dx, y1 - dy],
        [x2 - dx, y2 - dy],
        [x2 + dx, y2 + dy]
    ]
    cv2.fillPoly(img, [np.array(pts)], color)
    return img