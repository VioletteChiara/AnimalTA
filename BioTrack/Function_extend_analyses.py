import cv2
import numpy as np
import math
from scipy.interpolate import griddata



def cart2pol(x, y):
    theta = np.arctan2(y, x)
    rho = np.hypot(x, y)
    return theta, rho


def pol2cart(theta, rho):
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return x, y


def rotate_contour(cnt, angle, pts):
    pts=np.array(pts)

    M = cv2.moments(cnt)
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])

    cnt_norm = cnt - [cx, cy]
    coordinates = cnt_norm[:, 0, :]
    xs, ys = coordinates[:, 0], coordinates[:, 1]


    thetas, rhos = cart2pol(xs, ys)

    thetas = np.rad2deg(thetas)
    thetas = (thetas + angle) % 360
    thetas = np.deg2rad(thetas)

    xs, ys = pol2cart(thetas, rhos)

    cnt_norm[:, 0, 0] = xs
    cnt_norm[:, 0, 1] = ys

    cnt_rotated = cnt_norm + [cx, cy]
    cnt_rotated = cnt_rotated.astype(np.int32)

    #We do the same for the points:

    pts_norm=pts - [cx, cy]
    coordinates = pts_norm
    Ptxs, Ptys = coordinates[:, 0], coordinates[:, 1]
    thetas, rhos = cart2pol(Ptxs, Ptys)
    thetas = np.rad2deg(thetas)
    thetas = (thetas + angle) % 360
    thetas = np.deg2rad(thetas)

    Ptxs, Ptys = pol2cart(thetas, rhos)
    pts_norm[:, 0] = Ptxs
    pts_norm[:, 1] = Ptys
    pts_rotated = pts_norm + [cx, cy]


    return (cnt_rotated, pts_rotated)

def resize(cnt,centerO,centerA, val):
    cnt=cnt-centerO
    cnt[:, 0, 0]=cnt[:,0,0]*val[0]
    cnt[:, 0, 1] = cnt[:, 0, 1] * val[1]
    cnt=cnt+centerA
    cnt = cnt.astype(np.int32)
    return(cnt)

def resize_pt(cnt,centerO,centerA, val):
    cnt=cnt-centerO
    cnt[:, 0]=cnt[:, 0]*val[0]
    cnt[:, 1] = cnt[:, 1] * val[1]
    cnt=cnt+centerA
    cnt = cnt.astype(np.int32)
    return(cnt)


def match_shapes(cnt1,cnt2, pts):
    Is_ellipse_c1 = False
    Is_ellipse_c2 = False
    is_square2=False
    is_square1 = False
    #We first check that both areas have the same number of points:
    list_of_pts1 = []
    list_of_pts2=[]

    if len(cnt2) > 4:
        minEllpise2=cv2.fitEllipse(cnt2)
        Ell_Poly = cv2.ellipse2Poly((int(minEllpise2[0][0]), int(minEllpise2[0][1])), (int(minEllpise2[1][0] / 2), int(minEllpise2[1][1] / 2)),int(minEllpise2[2]), 0, 360, 5)
        Ell_Poly=Ell_Poly.reshape((Ell_Poly.shape[0], 1, Ell_Poly.shape[1]))
        similarity = cv2.matchShapes(Ell_Poly, cnt2, 1,0)
        if similarity<0.003:
            Is_ellipse_c2=True

    if len(cnt1) > 4:
        minEllpise1=cv2.fitEllipse(cnt1)
        Ell_Poly = cv2.ellipse2Poly((int(minEllpise1[0][0]), int(minEllpise1[0][1])), (int(minEllpise1[1][0] / 2), int(minEllpise1[1][1] / 2)),int(minEllpise1[2]), 0, 360, 5)
        Ell_Poly=Ell_Poly.reshape((Ell_Poly.shape[0], 1, Ell_Poly.shape[1]))
        similarity = cv2.matchShapes(Ell_Poly, cnt1, 1,0)
        if similarity<0.003:
            Is_ellipse_c1=True

    approx1 = cv2.approxPolyDP(cnt1, 0.002 * cv2.arcLength(cnt1, True), True)
    for pt in approx1:
        list_of_pts1.append((int(round(pt[0][0])), int(round(pt[0][1]))))

    approx2 = cv2.approxPolyDP(cnt2, 0.002 * cv2.arcLength(cnt2, True), True)
    for pt in approx2:
        list_of_pts2.append((int(round(pt[0][0])), int(round(pt[0][1]))))


    if len(list_of_pts1)==len(list_of_pts2) or (Is_ellipse_c1 and Is_ellipse_c2):
        if Is_ellipse_c1:
            min_rect1 = cv2.minAreaRect(cnt1)
            min_rect2 = cv2.minAreaRect(cnt2)
        else:
            min_rect1=cv2.minAreaRect(approx1)#( center (x,y), (width, height), angle of rotation )
            min_rect2=cv2.minAreaRect(approx2)

        #On veut savoir si l'arène est verticale ou horizontale
        min_rect1=list(min_rect1)
        min_rect2 = list(min_rect2)

        min_rect1[1]=list(min_rect1[1])
        min_rect2[1] = list(min_rect2[1])

        if 0.95 < min_rect2[1][0] / min_rect2[1][1] < 1.05:
            is_square2=True

        if 0.95 < min_rect1[1][0] / min_rect1[1][1] < 1.05:
            is_square1=True


        if not is_square1 and not is_square2:
            if min_rect1[1][0]<min_rect1[1][1]:
                min_rect1[2]=min_rect1[2]+90
                min_rect1[1][0],min_rect1[1][1]=min_rect1[1][1],min_rect1[1][0]

            if min_rect2[1][0]<min_rect2[1][1]:
                min_rect2[2]=min_rect2[2]+90
                min_rect2[1][0], min_rect2[1][1] = min_rect2[1][1], min_rect2[1][0]


        center1=[0,0]
        M=cv2.moments(approx1)
        center1[0] = int(M["m10"] / M["m00"])
        center1[1] = int(M["m01"] / M["m00"])

        center2=[0,0]
        M=cv2.moments(approx2)
        center2[0] = int(M["m10"] / M["m00"])
        center2[1] = int(M["m01"] / M["m00"])


        approx2, pts=rotate_contour(approx2, -min_rect2[2], pts=pts)

        #We calculate the size difference between the two arenas:
        resize_val=(min_rect1[1][0]/min_rect2[1][0],min_rect1[1][1]/min_rect2[1][1])
        approx2=resize(approx2,center2,center1,resize_val)
        pts = resize_pt(np.array(pts),center2,center1,resize_val)

        # If it is a square or a circle, we keep the original orientation
        if not (Is_ellipse_c2 and is_square2) and not (Is_ellipse_c1 and is_square1):
            approx2, pts = rotate_contour(approx2, 360 + min_rect1[2], pts=pts)
        else:
            approx2, pts = rotate_contour(approx2, min_rect2[2], pts=pts)

        # We update the points position:
        list_of_pts2=[]
        for pt in approx2:
            list_of_pts2.append((int(round(pt[0][0])), int(round(pt[0][1]))))

        #We check which is the first point
        list_dists = []
        for pt2 in list_of_pts2:
            list_dists.append(math.sqrt((list_of_pts1[0][0] - pt2[0]) ** 2 + (list_of_pts1[0][1] - pt2[1]) ** 2))
        list_of_pts1=np.flip(list_of_pts1,1)

        first_point = list_dists.index(min(list_dists))
        list_of_pts2 = list_of_pts2[first_point:len(list_of_pts2)] + list_of_pts2[0:(first_point)]
        list_of_pts2=np.flip(list_of_pts2,1)

        if not Is_ellipse_c1:
            size=max(np.amax(list_of_pts2),np.amax(list_of_pts1))

            grid_x, grid_y = np.mgrid[0:size, 0:size]
            grid_z = griddata(list_of_pts2,list_of_pts1 , (grid_x, grid_y), method='cubic')
            map_x = np.append([], [ar[:, 1] for ar in grid_z]).reshape(size,size)
            map_y = np.append([], [ar[:, 0] for ar in grid_z]).reshape(size,size)
            map_x_32 = map_x.astype('float32')
            map_y_32 = map_y.astype('float32')


        new_pts=[]
        for pt in pts:
            try:
                X=int(float(map_x_32[pt[1],pt[0]]))
                Y=int(float(map_y_32[pt[1],pt[0]]))
                new_pts.append([X,Y])
            except Exception as e:
                print(e)
                new_pts.append([pt[0],pt[1]])

        return(True, new_pts)
    else:
        return (False, None)
        print("Not the same number of points")


'''
img1=cv2.imread("E:/Post-doc/TRacking_software/test_arenas1.png")
img1=cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
cnt1,_=cv2.findContours(img1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
img2 = cv2.imread("E:/Post-doc/TRacking_software/test_arenas5.png")
img2=cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
cnt2,_=cv2.findContours(img2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

print(match_shapes(cnt1[0],cnt2[0], [(150,150),(200,200)]))
'''