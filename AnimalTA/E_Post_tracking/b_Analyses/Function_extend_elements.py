import cv2
import numpy as np
import math
from scipy.interpolate import griddata

"""The functions bellow are used to transfer elements of interest defined by user in one arena to other arenas."""


def cart2pol(x, y):
    """Convert cartesian coordinates to polar ones"""
    theta = np.arctan2(y, x)
    rho = np.hypot(x, y)
    return theta, rho


def pol2cart(theta, rho):
    """Convert polar coordinates to cartesian ones"""
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return x, y


def rotate_contour(cnt, angle, pts):
    """
    :param cnt: The contour to be rotated
    :param angle: The angle of rotation
    :param pts: The points of the elements of interest that must be rotated in the same way as the contour
    :return: contour and points rotated
    """
    pts=np.array(pts)

    #Rotation of the contour
    M = cv2.moments(cnt)
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])

    #First contour is placed in coordinates 0,0
    cnt_norm = cnt - [cx, cy]
    coordinates = cnt_norm[:, 0, :]
    xs, ys = coordinates[:, 0], coordinates[:, 1]
    thetas, rhos = cart2pol(xs, ys)

    #Then it is rotated
    thetas = np.rad2deg(thetas)
    thetas = (thetas + angle) % 360
    thetas = np.deg2rad(thetas)

    xs, ys = pol2cart(thetas, rhos)

    cnt_norm[:, 0, 0] = xs
    cnt_norm[:, 0, 1] = ys

    #Then placed back in its original position
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
    #This function is used to resize the contour
    #cnt=contour of interest
    #center0=the center of the contour (X,Y coordinates)
    #centerA=where we wants the contour to be after the transformation (X,Y coordinates)
    cnt=cnt-centerO
    cnt[:, 0, 0]=cnt[:,0,0]*val[0]
    cnt[:, 0, 1] = cnt[:, 0, 1] * val[1]
    cnt=cnt+centerA
    cnt = cnt.astype(np.int32)
    return(cnt)

def resize_pt(pts,centerO,centerA, val):
    #This function is used to change the position of the points by resizing the grid in which they are
    #cnt=points
    #center0=the center of the contour (X,Y coordinates)
    #centerA=where we wants the contour to be after the transformation (X,Y coordinates)
    pts=pts-centerO
    pts[:, 0]=pts[:, 0]*val[0]
    pts[:, 1] = pts[:, 1] * val[1]
    pts=pts+centerA
    pts = pts.astype(np.int32)
    return(pts)

def calculate_shapes_diff(shape1,shape2):
    empty1 = np.zeros([max(np.max(shape1[:, :, 1]), np.max(shape2[:, :, 1])) + 10,
                       max(np.max(shape1[:, :, 0]), np.max(shape2[:, :, 0])) + 10, 1], np.uint8)
    empty2 = np.copy(empty1)
    cv2.drawContours(empty1, [shape1], -1, 255, -1)
    cv2.drawContours(empty2, [shape2], -1, 255, -1)

    Difference = cv2.bitwise_xor(empty1, empty2)
    Val_no_rot = np.sum(Difference == 255) / ((cv2.contourArea(shape1) + cv2.contourArea(shape2)) / 2)
    return (Val_no_rot)

def match_shapes(cnt1,cnt2, pts):
    """This function perform all the transformations to allow to duplicates the elements of interest from one arena to another one."""
    #cnt1 is the contour of the first arena
    #cnt2 is the contour of the second arena
    #pts are the elements of interest to be copied from the first to the second arena
    Is_ellipse_c1 = False
    Is_ellipse_c2 = False
    is_square2=False
    is_square1 = False

    list_of_pts1 = []
    list_of_pts2=[]

    # We first check if the contours are circular/ellipsoids
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


    #We then make an approximation of the two arena's shapes
    approx1 = cv2.approxPolyDP(cnt1, 0.025 * cv2.arcLength(cnt1, True), True)
    for pt in approx1:
        list_of_pts1.append((int(round(pt[0][0])), int(round(pt[0][1]))))

    approx2 = cv2.approxPolyDP(cnt2, 0.025 * cv2.arcLength(cnt2, True), True)
    for pt in approx2:
        list_of_pts2.append((int(round(pt[0][0])), int(round(pt[0][1]))))


    #If the two shapes have the same number of points or if both ar circual/ellipsoid
    if len(list_of_pts1)==len(list_of_pts2) or (Is_ellipse_c1 and Is_ellipse_c2):
        print("Same nb")
        if Is_ellipse_c1:
            min_rect1 = cv2.minAreaRect(cnt1)
            min_rect2 = cv2.minAreaRect(cnt2)
        else:
            min_rect1=cv2.minAreaRect(approx1)#(center (x,y), (width, height), angle of rotation )
            min_rect2=cv2.minAreaRect(approx2)

        #We want to determine wether the arena is vertical or horizontal
        min_rect1=list(min_rect1)
        min_rect2 = list(min_rect2)

        min_rect1[1]= list(min_rect1[1])
        min_rect2[1] = list(min_rect2[1])

        #We first check that it is not a square (if it is the case, we will not apply rotation according to the width/heigh)
        if 0.95 < min_rect2[1][0] / min_rect2[1][1] < 1.05:
            is_square2=True

        if 0.95 < min_rect1[1][0] / min_rect1[1][1] < 1.05:
            is_square1=True


        if not is_square1 or not is_square2:
            if min_rect1[1][0]<min_rect1[1][1]:
                min_rect1[2]=min_rect1[2]+90
                min_rect1[1][0],min_rect1[1][1]=min_rect1[1][1],min_rect1[1][0]

            if min_rect2[1][0]<min_rect2[1][1]:
                min_rect2[2]=min_rect2[2]+90
                min_rect2[1][0], min_rect2[1][1] = min_rect2[1][1], min_rect2[1][0]


        min_rect1[2] = min_rect1[2] % 360
        if min_rect1[2] < -90:# We want to aply the smallest possible rotation
            min_rect1[2] = min_rect1[2] + 180
        elif min_rect1[2] > 90:# We want to aply the smallest possible rotation
            min_rect1[2] = min_rect1[2] - 180


        min_rect2[2]=min_rect2[2]%360
        if min_rect2[2] < -90:# We want to aply the smallest possible rotation
            min_rect2[2] = min_rect2[2] + 180
        elif min_rect2[2] > 90:# We want to aply the smallest possible rotation
            min_rect2[2] = min_rect2[2] - 180

        center1=[0,0]
        M=cv2.moments(approx1)
        center1[0] = int(M["m10"] / M["m00"])
        center1[1] = int(M["m01"] / M["m00"])

        center2=[0,0]
        M=cv2.moments(approx2)
        center2[0] = int(M["m10"] / M["m00"])
        center2[1] = int(M["m01"] / M["m00"])


        # We put the shape horizontaly to change its size
        approx2, pts=rotate_contour(approx2, -min_rect2[2], pts=pts)

        empty1 = np.zeros([max(np.max(approx1[:, :, 1]), np.max(approx2[:, :, 1])) + 10,
                           max(np.max(approx1[:, :, 0]), np.max(approx2[:, :, 0])) + 10, 3], np.uint8)

        #We calculate the size difference between the two arenas:
        resize_val=(min_rect1[1][0]/min_rect2[1][0],min_rect1[1][1]/min_rect2[1][1])
        approx2=resize(approx2,center2,center1,resize_val)


        print(approx2)
        print("AAAA")
        empty1 = cv2.drawContours(empty1, [approx2], -1, (0, 255, 0), 3)
        empty1 = cv2.drawContours(empty1, [approx1], -1, (255, 0, 0), 3)
        cv2.imshow("W", empty1)
        cv2.waitKey()
        cv2.waitKey()
        cv2.waitKey()
        cv2.waitKey("Q")


        pts = resize_pt(np.array(pts),center2,center1,resize_val)

        # If it is a square or a circle, we keep the original orientation
        if not (Is_ellipse_c2 or is_square2) or not (Is_ellipse_c1 or is_square1):
            # We check what is the best: to make a 180deg rotation or not (i.e., if we have a rectangle, it is better to not rotate than to do a 180deg rotation)
            approx1B, _ = rotate_contour(approx1, 180, pts=pts)
            Val_no_rot = calculate_shapes_diff(approx1, approx2)
            Val_rot = calculate_shapes_diff(approx1B, approx2)

            # If there is no big difference between the two, we don't rotate:
            if (Val_no_rot - Val_rot) >= 0.1:
                if min_rect1[2] < 0:
                    min_rect1[2] = min_rect1[2] + 180
                else:
                    min_rect1[2] = min_rect1[2] - 180

            approx2, pts = rotate_contour(approx2, min_rect1[2] , pts=pts)
        else:
            approx2, pts = rotate_contour(approx2, min_rect2[2], pts=pts)


        # We update the points position:
        list_of_pts2=[]
        for pt in approx2:
            list_of_pts2.append((int(round(pt[0][0])), int(round(pt[0][1]))))

        #We check which is the first point of each shapes
        list_dists = []
        for pt1 in list_of_pts1:
            list_dists.append(math.sqrt((0-pt1[0]) ** 2 + (0 - pt1[1]) ** 2))
        first_point = list_dists.index(min(list_dists))
        list_of_pts1 = list_of_pts1[first_point:len(list_of_pts1)] + list_of_pts1[0:(first_point)]

        list_dists=[]
        for pt2 in list_of_pts2:
            list_dists.append(math.sqrt((0-pt2[0]) ** 2 + (0 - pt2[1]) ** 2))
        first_point = list_dists.index(min(list_dists))
        list_of_pts2 = list_of_pts2[first_point:len(list_of_pts2)] + list_of_pts2[0:(first_point)]

        #We calculate the deformation matrix
        new_pts = []
        if not Is_ellipse_c1:
            size=max(np.amax(list_of_pts2),np.amax(list_of_pts1))
            grid_x, grid_y = np.mgrid[0:size, 0:size]
            grid_z = griddata(np.flip(list_of_pts2),np.flip(list_of_pts1) , (grid_x, grid_y), method='linear')
            map_x = np.append([], [ar[:, 1] for ar in grid_z]).reshape(size,size)
            map_y = np.append([], [ar[:, 0] for ar in grid_z]).reshape(size,size)
            map_x_32 = map_x.astype('float32')
            map_y_32 = map_y.astype('float32')

            #Finally, we apply the transformation of the points according to the shape deformation
            for pt in pts:
                try:
                    X=int(float(map_x_32[pt[1],pt[0]]))
                    Y=int(float(map_y_32[pt[1],pt[0]]))
                    new_pts.append([X,Y])
                except Exception as e:
                    print(e)
                    new_pts.append([pt[0], pt[1]])

        else :
            new_pts=[[pt[0],pt[1]] for pt in pts]

        return(True, new_pts)
    else:
        return (False, None)

'''
img1=cv2.imread("E:/Post-doc/TRacking_software/test_arenas1.png")
img1=cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
cnt1,_=cv2.findContours(img1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
img2 = cv2.imread("E:/Post-doc/TRacking_software/test_arenas5.png")
img2=cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
cnt2,_=cv2.findContours(img2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

print(match_shapes(cnt1[0],cnt2[0], [(150,150),(200,200)]))
'''