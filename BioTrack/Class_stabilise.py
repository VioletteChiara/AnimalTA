from tkinter import filedialog
import numpy as np
import cv2
import os

resume_values=[]
def find_best_position(Prem_Im,frame,show):
    prev_gray=cv2.cvtColor(Prem_Im,cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h = prev_gray.shape[0]
    w = prev_gray.shape[1]

    prev_pts = cv2.goodFeaturesToTrack(prev_gray,
                                       maxCorners=200,
                                       qualityLevel=0.01,
                                       minDistance=30,
                                       blockSize=3)

    curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)

    # Sanity check
    assert prev_pts.shape == curr_pts.shape

    # Filter only valid points
    idx = np.where(status == 1)[0]
    prev_pts = prev_pts[idx]
    curr_pts = curr_pts[idx]

    # Find transformation matrix
    m, _ = cv2.estimateAffinePartial2D(prev_pts, curr_pts)  # will only work with OpenCV-3 or less

    # Extract traslation
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

    # Fix border artifacts
    #frame_stabilized = fixBorder(frame_stabilized)

    if show:
        frame_out = cv2.hconcat([frame, frame_stabilized])
        cv2.putText(frame_out,"Original", (25,75), cv2.FONT_HERSHEY_PLAIN, 5, (255,255,255), 20)
        cv2.putText(frame_out, "Original", (25, 75), cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 0), 8)

        cv2.putText(frame_out, "Stabilised", (w+25, 75), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 20)
        cv2.putText(frame_out, "Stabilised", (w+25, 75), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,0), 8)

        # Store transformation
        return(frame_out)
    else:
        return (frame_stabilized)

def fixBorder(frame):
  s = frame.shape
  # Scale the image 4% without moving the center
  T = cv2.getRotationMatrix2D((s[1]/2, s[0]/2), 0, 1.04)
  frame = cv2.warpAffine(frame, T, (s[1], s[0]))
  return frame