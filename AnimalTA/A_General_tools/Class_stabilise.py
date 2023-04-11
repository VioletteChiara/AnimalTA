from tkinter import *
import os
import numpy as np
import cv2
from AnimalTA.A_General_tools import UserMessages
from PIL import ImageFont, ImageDraw, Image


""" These functions are based on the work of members of the learnopencv team.
https://github.com/spmallick/learnopencv/blob/master/VideoStabilization/video_stabilization.py"""


#Import language
f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
Language=f.read()
f.close()
Messages = UserMessages.Mess[Language]


def find_pts(Vid, Prem_Im, minDistance=30,  blockSize=3, quality=0.05,maxCorners=200):
    '''
    This function looks for points of interest to be tracked (on the first frame of the video).
    Vid=Video of interest
    Prem_Im=the image used to stabilise (the first of the video)
    '''
    if len(Prem_Im.shape)>2:
        prev_gray=cv2.cvtColor(Prem_Im,cv2.COLOR_BGR2GRAY)
    else:
        prev_gray = Prem_Im.copy()

    found=False
    while not found and quality >= 0.001:
        prev_pts = cv2.goodFeaturesToTrack(prev_gray,
                                           maxCorners=maxCorners,
                                           qualityLevel=quality,
                                           minDistance=minDistance,
                                           blockSize=blockSize)
        quality = quality - 0.001

        if len(prev_pts) > 10:
            found = True

    return(prev_pts)



def find_best_position(Vid, Prem_Im, frame, show, scale=1, prev_pts=None):
    '''
    This function calculate the optival flow between the points of interest of the first image (see find_pts function) and the point of interest of a frame of interest (frame).
    Vid=Video of interest
    Prem_Im=First image
    frame=current image
    show: if True, the function return the image for the "Check stabilization" panel (a composition of the original frame, current frame and stabilised frame). If False, it returns only the stabilised image.
    scale: if show==True, scale is used to write some titles on the frame at an appropiate size
    '''

    try:
        if prev_pts==None:#If the points of interest were not defined yet, we look for them
            prev_pts=find_pts(Vid,Prem_Im,Vid.Stab[2][0],Vid.Stab[2][1],Vid.Stab[2][2],Vid.Stab[2][3])
    except:
        pass


    if len(Prem_Im.shape)>2:#If mandatory, we convert to grayscale the first image
        prev_gray=cv2.cvtColor(Prem_Im,cv2.COLOR_BGR2GRAY)
    else:
        prev_gray = Prem_Im.copy()

    curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)#Convert to grayscale the current image
    h = prev_gray.shape[0]
    w = prev_gray.shape[1]

    if len(prev_pts)>1:#If there are emought points to stabilise, we apply the stabilisation
        choose_pts=prev_pts.copy()

        curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)#Calculate optical flow

        assert choose_pts.shape == curr_pts.shape

        # Filter only valid points
        idx = np.where(status == 1)[0]
        choose_pts = choose_pts[idx]
        curr_pts = curr_pts[idx]

        if len(choose_pts)>1:
            # Find transformation matrix
            m, _ = cv2.estimateAffinePartial2D(choose_pts, curr_pts)  # will only work with OpenCV-3 or less

            # Extract translation
            dx = -m[0, 2]
            dy = -m[1, 2]

            # Extract rotation angle
            da = -np.arctan2(m[1, 0], m[0, 0])

            # Reconstruct transformation matrix accordingly to new values
            m = np.zeros((2, 3), np.float32)
            m[0, 0] = np.cos(da)
            m[0, 1] = -np.sin(da)
            m[1, 0] = np.sin(da)
            m[1, 1] = np.cos(da)
            m[0, 2] = dx
            m[1, 2] = dy

            # Apply affine wrapping to the given frame
            frame_stabilized = cv2.warpAffine(frame, m, (w, h))

        else:
            frame_stabilized = frame
    else:
        frame_stabilized=frame

    if show:#If we want to see the result as an image composition
        fontpath = os.path.join(".","simsun.ttc")
        decal=10
        if scale<10:
            font = ImageFont.truetype(fontpath, max(1, int(scale * 30)))
            stroke_width=max(1, int(scale * 2))
        else:
            font = ImageFont.truetype(fontpath, 1)
            stroke_width = 1
        first_im = np.copy(Prem_Im)

        cnt=0
        Messages_S=[Messages["Stab3"],Messages["Stab4"],Messages["Stab5"]]

        first_im = Image.fromarray(first_im)
        draw = ImageDraw.Draw(first_im)
        draw.text((max(1, int(scale * decal)) , max(1, int(scale * decal))) , Messages_S[cnt], font=font,fill=(255, 255, 255, 0),stroke_width=stroke_width)
        draw.text((max(1,int(scale*decal)), max(1,int(scale*decal))), Messages_S[cnt], font=font, fill=(0,0,0,0))

        first_im = np.array(first_im)

        cnt = 1
        frame = Image.fromarray(frame)
        draw = ImageDraw.Draw(frame)
        draw.text((max(1, int(scale * decal)) , max(1, int(scale * decal))) , Messages_S[cnt], font=font,fill=(255, 255, 255, 0),stroke_width=stroke_width)
        draw.text((max(1,int(scale*decal)), max(1,int(scale*decal))), Messages_S[cnt], font=font, fill=(0,0,0,0))
        frame = np.array(frame)

        cnt = 2
        frame_stabilized = Image.fromarray(frame_stabilized)
        draw = ImageDraw.Draw(frame_stabilized)
        draw.text((max(1, int(scale * decal)) , max(1, int(scale * decal))) , Messages_S[cnt], font=font,fill=(255, 255, 255, 0),stroke_width=stroke_width)
        draw.text((max(1,int(scale*decal)), max(1,int(scale*decal))), Messages_S[cnt], font=font, fill=(0,0,0,0))
        frame_stabilized = np.array(frame_stabilized)

        #Draw the points of interest
        for pt in range(len(prev_pts)):
            cv2.circle(first_im, (int(prev_pts[pt][0][0]), int(prev_pts[pt][0][1])), max(1,int(scale*2)), (255,0,0), -1)
            cv2.putText(first_im,str(pt),(int(prev_pts[pt][0][0])+max(1,int(scale*3)), int(prev_pts[pt][0][1])-max(1,int(scale*3))),cv2.FONT_HERSHEY_PLAIN,max(1,scale*1),(255,0,0),max(1,int(scale*1.5)))

        for pt in range(len(curr_pts)):
            cv2.circle(frame, (int(curr_pts[pt][0][0]), int(curr_pts[pt][0][1])), max(1,int(scale*2)), (100,255,100), -1)
            cv2.putText(frame, str(pt), (int(curr_pts[pt][0][0])+max(1,int(scale*3)), int(curr_pts[pt][0][1])-max(1,int(scale*3))), cv2.FONT_HERSHEY_PLAIN, max(1,scale*1), (100, 255, 100),max(1,int(scale*1.5)))


        #Concatenate the three images
        frame_out1 = cv2.hconcat([frame, frame_stabilized])
        frame_out2 = cv2.hconcat([first_im, np.zeros_like(first_im)])
        frame_out = cv2.vconcat([frame_out2, frame_out1])

        # Store transformation
        return(frame_out)
    else:
        return (frame_stabilized)
