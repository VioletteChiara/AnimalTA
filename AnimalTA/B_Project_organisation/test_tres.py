import pickle
import cv2
from AnimalTA.A_General_tools import Function_draw_mask as Dr
import numpy as np

def test_fn():
    file_to_open="F:/Neophobia_MAZE_SAMPLE_copy.ata"
    with open(file_to_open, 'rb') as fp:
        data_to_load = pickle.load(fp)
        project_name=(data_to_load["Project_name"])
        folder = data_to_load["Folder"]
        liste_of_videos = data_to_load["Videos"]
        file_to_save = file_to_open

    for V in liste_of_videos:
        img=Dr.draw_mask(V)
        Arenas_or, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        Arenas = []  # We now remoce the too small arenas (<5px)
        for A in Arenas_or:
            if cv2.contourArea(A) > 5:
                Arenas.append(A)
        Arenas = Dr.Organise_Ars(Arenas)

        if len(Arenas)>0:
            biggest=["NA",0]
            count=0
            for A in Arenas:
                size=cv2.contourArea(A)
                if size>biggest[1]:
                    biggest=[count,size]
                count+=1

        if len(V.Identities)>1:
            V.Identities=[V.Identities[biggest[0]]]
            V.Identities[0][0]=0
            V.Track[1][6]=[1]
            V.Analyses = [V.Analyses[0], [[]], V.Analyses[2], V.Analyses[3], V.Analyses[4]]

    data_to_save = dict(Project_name=project_name, Folder=folder,
                        Videos=liste_of_videos)


    with open("F:/Neophobia_MAZE_SAMPLE_copy_1Ar.ata", 'wb') as fp:
        pickle.dump(data_to_save, fp)
    print("saved")

