
from tkinter import filedialog
import numpy as np
import cv2
import os

resume_values=[]
def find_best_position(Prem_Im,frame, range_stab, square):
    resume_values = []
    Prem_Im_comp = Prem_Im
    frame_comp=frame
    frame=frame[square[0]:square[2],square[1]:square[3]]
    Prem_Im=Prem_Im[square[0]:square[2], square[1]:square[3]]

    for i in range(-int(Prem_Im.shape[0] / range_stab), int(Prem_Im.shape[0] / range_stab)):
        for j in range(-int(Prem_Im.shape[1] / range_stab), int(Prem_Im.shape[1] / range_stab)):
            if i >= 0 and j >= 0:
                IMG0_RESIZE = Prem_Im[0:(Prem_Im.shape[0] - i),
                              0:(Prem_Im.shape[1] - j)]
                TMP_IMG = frame[i:(frame.shape[0]),
                          j:(frame.shape[1])]

            elif i < 0 and j >= 0:
                IMG0_RESIZE = Prem_Im[-i:(Prem_Im.shape[0]),
                              0:(Prem_Im.shape[1] - j)]
                TMP_IMG = frame[0:(frame.shape[0] + i),
                          j:(frame.shape[1])]

            elif i >= 0 and j < 0:
                IMG0_RESIZE = Prem_Im[0:(Prem_Im.shape[0] - i),
                              -j:(Prem_Im.shape[1])]
                TMP_IMG = frame[i:(frame.shape[0]),
                          0:(frame.shape[1] + j)]

            elif i < 0 and j < 0:
                IMG0_RESIZE = Prem_Im[-i:(Prem_Im.shape[0]),
                              -j:(Prem_Im.shape[1])]
                TMP_IMG = frame[0:(frame.shape[0] + i),
                          0:(frame.shape[1] + j)]

            resume_values.append((i, j, cv2.mean(cv2.subtract(IMG0_RESIZE, TMP_IMG)^2)[0]))


    resume_values.sort(key=lambda tup: tup[2])

    i = resume_values[0][0]
    j = resume_values[0][1]

    if i >= 0 and j >= 0:
        TMP_IMG = frame_comp[i:(frame_comp.shape[0]),
                  j:(frame_comp.shape[1])]

    elif i < 0 and j >= 0:
        TMP_IMG = frame_comp[0:(frame_comp.shape[0] + i),
                  j:(frame_comp.shape[1])]

    elif i >= 0 and j < 0:
        TMP_IMG = frame_comp[i:(frame_comp.shape[0]),
                  0:(frame_comp.shape[1] + j)]

    elif i < 0 and j < 0:
        TMP_IMG = frame_comp[0:(frame_comp.shape[0] + i),
                  0:(frame_comp.shape[1] + j)]

    if(TMP_IMG.shape[0]<Prem_Im_comp.shape[0]):
        Diff=Prem_Im_comp.shape[0]-TMP_IMG.shape[0]
        a_ajou=np.zeros(TMP_IMG.shape, TMP_IMG.dtype)
        a_ajou=a_ajou[0:Diff,0:TMP_IMG.shape[1]]

        if i > 0:
            TMP_IMG = np.concatenate((TMP_IMG,a_ajou), axis=0)
        else:
            TMP_IMG = np.concatenate((a_ajou,TMP_IMG), axis=0)


    if(TMP_IMG.shape[1]<Prem_Im_comp.shape[1]):
        Diff=Prem_Im_comp.shape[1]-TMP_IMG.shape[1]
        a_ajou=np.zeros(TMP_IMG.shape, TMP_IMG.dtype)
        a_ajou=a_ajou[0:TMP_IMG.shape[0],0:Diff]
        if j>0:
            TMP_IMG = np.concatenate((TMP_IMG,a_ajou), axis=1)
        else:
            TMP_IMG = np.concatenate((a_ajou, TMP_IMG), axis=1)


    return (TMP_IMG, [i,j])

