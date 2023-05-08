import numpy as np
import cv2
import math

def correct(curr_img, ref_img,or_pts,corr_pts, ratio, selected=None, scale=1):
    ref_img2=np.copy(ref_img)
    curr_img2 = np.copy(curr_img)
    schem=np.zeros_like(ref_img2)
    schem.fill(255)
    id = 0
    for pt in or_pts:
        if selected != None and selected[1] == id:
            cv2.circle(ref_img2, (int(pt[0]), int(pt[1])), max([1,int(ratio*3)]) ,(255,0,0),-1)
        else:
            cv2.circle(ref_img2, (int(pt[0]), int(pt[1])), max([1, int(ratio * 3)]), (150, 0, 0), -1)
        id+=1

    id=0
    dists=[]
    for pt in corr_pts:
        if selected != None and selected[1]==id:
            cv2.circle(schem, (int(pt[0]), int(pt[1])), max([1,int(ratio*3)]) ,(0,0,0),-1)
        else:
            cv2.circle(schem, (int(pt[0]), int(pt[1])), max([1,int(ratio*3)]) ,(150,150,150),-1)

        if selected != None and selected[1]!=id:
            dists.append([id,math.sqrt((pt[0]-corr_pts[selected[1]][0])**2 + (pt[1]-corr_pts[selected[1]][1])**2)])
        id+=1

    dists.sort(key = lambda x: x[1])
    for pt_id in range(min([3,len(dists)])):
        pt=corr_pts[dists[pt_id][0]]
        dist=dists[pt_id][1]

        cv2.line(schem, (int(pt[0]), int(pt[1])), (int(corr_pts[selected[1]][0]),int(corr_pts[selected[1]][1])), (150, 0, 0), max([1, int(ratio * 1)]))
        #Create empty image to put text
        empty=np.zeros((schem.shape[0],schem.shape[1],1), np.uint8)
        #Where the text shoudl appear
        center=[int((pt[0]+corr_pts[selected[1]][0])/2),int((pt[1]+corr_pts[selected[1]][1])/2)]
        center_b = center.copy()
        #Which angle?
        dims, baseline = cv2.getTextSize(str(round(dist/scale,3)), cv2.FONT_HERSHEY_SIMPLEX, max([0.5,ratio*0.5]), max([1,int(ratio*0.75)]))
        center_b[0]=int(center[0]-dims[0]/2)

        if pt[0]>corr_pts[selected[1]][0]:
            angle=-math.asin((pt[1]-corr_pts[selected[1]][1])/dist)*180/math.pi
            center_b[1] = int(center[1] - dims[1] / 2)
        else:
            angle = math.asin((pt[1] - corr_pts[selected[1]][1]) / dist) * 180 / math.pi
            center_b[1] = int(center[1] + dims[1] / 2)


        empty=cv2.putText(empty, str(round(dist/scale,3)), center_b, cv2.FONT_HERSHEY_SIMPLEX, max([0.5,ratio*0.5]), 255, max([1,int(ratio*0.75)]))

        # Rotate the text
        M = cv2.getRotationMatrix2D(center, angle, 1)
        empty = cv2.warpAffine(empty, M, (empty.shape[1], empty.shape[0]))
        text_cnts, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        schem=cv2.drawContours(schem, text_cnts, -1, ((150,0,0)), -1)

    """
    size_grid=min([int((ref_img2.shape[1]/scale)/10),int((ref_img2.shape[0]/scale)/10)])

    for l in range(0,int(ref_img2.shape[1]/scale),size_grid):
        cv2.line(schem, [int(l*scale),0],[int(l*scale),ref_img2.shape[0]],  (50, 50, 50), max([1,int(ratio*1)]))
    for l in range(0,int(ref_img2.shape[0]/scale),size_grid):
        cv2.line(schem, [0,int(l*scale)],[ref_img2.shape[1],int(l*scale)],  (50, 50, 50), max([1,int(ratio*1)]))
    """

    curr_img2=transform(curr_img2,or_pts,corr_pts)

    frame_out1 = cv2.hconcat([ref_img2, schem])
    frame_out2 = np.zeros_like(frame_out1)
    frame_out2[ 0:ref_img2.shape[0] ,int(ref_img2.shape[1]/2):int(ref_img2.shape[1]/2)+ref_img2.shape[1]]=curr_img2
    frame_out = cv2.vconcat([frame_out1, frame_out2])

    return(frame_out)


def transform(img,or_pts,corr_pts):
    if len(or_pts)>=4 and len(or_pts)==len(corr_pts):
        or_pts = np.float32(or_pts)
        corr_pts = np.float32(corr_pts)
        M, mask = cv2.findHomography(or_pts, corr_pts)
        img_t = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))
        return(img_t)
    else:
        return(img)