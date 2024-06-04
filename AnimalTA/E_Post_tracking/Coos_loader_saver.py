import os
import csv
import numpy as np
from tkinter import *
from AnimalTA.A_General_tools import Class_loading_Frame
import time

def load_coos(Vid, TMP=False, location=None):
    # Importation of the coordinates associated with the current video
    if Vid.User_Name == Vid.Name:
        file_name = Vid.Name
        point_pos = file_name.rfind(".")
        if file_name[point_pos:].lower()!=".avi":#Old versions of AnimalTA did not allow to rename or duplicate the videos, the name of the video was the file name without the ".avi" extension
            file_name = Vid.User_Name
        else:
            file_name = file_name[:point_pos]
    else:
        file_name = Vid.User_Name

    if not TMP:
        file_tracked_not_corr = os.path.join(Vid.Folder, "coordinates", file_name + "_Coordinates.csv")
        file_tracked_corr = os.path.join(Vid.Folder, "corrected_coordinates", file_name + "_Corrected.csv")
    else:
        file_tracked_corr = os.path.join(Vid.Folder, "TMP_portion", file_name + "_TMP_portion_Coordinates.csv")

    if os.path.isfile(file_tracked_corr):
        path = file_tracked_corr
    else:
        path = file_tracked_not_corr



    if Vid.Track[1][8]:
        return load_fixed(Vid, path, location)
    else:
        return load_variable(Vid, path)





def save(Vid, Coos, TMP=False, location=None):
    # Save the coordinates associated with the current video
    if Vid.User_Name == Vid.Name:
        file_name = Vid.Name
        point_pos = file_name.rfind(".")
        if file_name[point_pos:].lower()!=".avi":#Old versions of AnimalTA did not allow to rename or duplicate the videos, the name of the video was the file name without the ".avi" extension
            file_name = Vid.User_Name
        else:
            file_name = file_name[:point_pos]
    else:
        file_name = Vid.User_Name

    if not TMP:
        if not os.path.isdir(os.path.join(Vid.Folder, "corrected_coordinates")):
            os.makedirs(os.path.join(Vid.Folder, "corrected_coordinates"))
        path = os.path.join(Vid.Folder, "corrected_coordinates", file_name + "_Corrected.csv")
    else:
        if not os.path.isdir(os.path.join(Vid.Folder, "TMP_portion")):
            os.makedirs(os.path.join(Vid.Folder , "TMP_portion"))
        path = os.path.join(Vid.Folder, "TMP_portion", file_name + "_TMP_portion_Coordinates.csv")

    if os.path.isfile(path):
        path = path

    if Vid.Track[1][8]:
        save_fixed(Vid, Coos, path, location)
    else:
        save_variable(Vid, Coos, path)


def load_variable(Vid, path):
    one_every=Vid.Frame_rate[0] / Vid.Frame_rate[1]
    newWindow = Toplevel()
    load_frame = Class_loading_Frame.Loading(newWindow)  # Progression bar
    load_frame.grid()

    with open(path, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        or_table = list(csv_reader)

    who_is_here = [[] for x in range(int((Vid.Cropped[1][1] - Vid.Cropped[1][0]) / one_every) + 1)]
    if len(or_table)==1:
        Coos=np.full((1,(int((Vid.Cropped[1][1] - Vid.Cropped[1][0])/one_every) + 1),2),-1000, dtype=float)

    else:
        Coos = np.full((len(Vid.Identities),(int((Vid.Cropped[1][1] - Vid.Cropped[1][0])/one_every) + 1),2),-1000, dtype=float)
        or_table = np.asarray(or_table)
        or_table[or_table=="NA"]=-1000

        count = 0
        for Ind in Vid.Identities:
            load_frame.show_load(count / len(Vid.Identities))
            subset = or_table[np.where((np.array(or_table[:, 2]) == str(Ind[0])) & (np.array(or_table[:, 3]) == str(Ind[1])))]
            if len(subset)<=0:
                subset = or_table[np.where((np.array(or_table[:, 2]) == str(Ind[0])) & (np.array(or_table[:, 3]) == str(Ind[1][3:])))]

            if len(subset)>0:
                time = subset[:, 0].astype('float')
                time = time.astype('int32')
                time=time-round(Vid.Cropped[1][0]/one_every)
                T_Coos = subset[:, 4:6]
                Coos[count, time, :] = T_Coos
                for im in time:
                    who_is_here[im] = who_is_here[im] + [count]
            count += 1



    load_frame.destroy()
    newWindow.destroy()
    return(Coos, who_is_here)


def load_fixed(Vid, path, location=None):
    if location==None:
        frame = Toplevel()
    else:
        frame=location
    load_frame = Class_loading_Frame.Loading(frame)  # Progression bar
    load_frame.grid()
    load_frame.show_load(0)
    load_frame.grab_set()

    or_table=[]
    with open(path, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        count=0
        for row in csv_reader:
            or_table.append(row)
            if count % 1000 == 0:
                load_frame.show_load((count/Vid.Frame_nb[1])/3)
            count+=1

    or_table = np.array(or_table)
    Coos = np.full((len(Vid.Identities), len(or_table)-1, 2), -1000,dtype=float)
    or_table = np.asarray(or_table)
    or_table[or_table == "NA"] = -1000
    count=0
    for Ind in range(len(Vid.Identities)):
        load_frame.show_load(1/3 + (count / len(Vid.Identities))*2/3)
        Coos[Ind] = or_table[1:,2*Ind+2:2*Ind+4]
        count+=1


    load_frame.destroy()
    if location==None:
        frame.destroy()

    load_frame.grab_release()

    return (Coos, [list(range(len(Vid.Identities)))]*len(Coos[0,:,0]))

def save_fixed(Vid, Coos, path, location=None):
    if location == None:
        frame = Toplevel()
    else:
        frame = location
    load_frame = Class_loading_Frame.Loading(frame)  # Progression bar
    load_frame.grid()
    load_frame.show_load(0)


    one_every=Vid.Frame_rate[0] / Vid.Frame_rate[1]
    General_Coos=np.zeros([Coos.shape[1]+1,Coos.shape[2]*Coos.shape[0]+2], dtype="object")

    liste_times=range(0, Coos.shape[1])
    General_Coos[1:,0]=liste_times[0:len(General_Coos[1:,0])]

    tmp=np.array(General_Coos[1:, 0]/Vid.Frame_rate[1], dtype="float")
    General_Coos[1:, 1]=np.around(tmp,2)

    General_Coos[0,:]=["Frame","Time"]+[Col+"_Arena"+str(ind[0])+"_"+str(ind[1]) for ind in Vid.Identities for Col in ["X","Y"]]
    Coos = Coos.astype(dtype=object)
    Coos[Coos==-1000]="NA"
    for Ind in range(Coos.shape[0]):
        load_frame.show_load(((Ind+1)/(Coos.shape[0]+1))*1/3)
        General_Coos[1:,Ind*2+2:Ind*2+2+2]=Coos[Ind]

    with open(path, 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        for rows in range(300,len(General_Coos)+300,300):
            writer.writerows(General_Coos[range(rows-300, min([len(General_Coos),rows]))])
            load_frame.show_load(1/3 + ((rows) / Vid.Frame_nb[1])*2/3)

    #np.savetxt(path, General_Coos, delimiter=';', encoding="utf-8", fmt='%s')
    load_frame.destroy()

    if location == None:
        frame.destroy()


def save_variable(Vid, Coos, path):
    one_every = Vid.Frame_rate[0] / Vid.Frame_rate[1]
    Pos=np.where(Coos[:,:,0]!=-1000)
    new_Coos=Coos[Pos[0],Pos[1],:]
    Ars=[Vid.Identities[P][0] for P in Pos[0]]
    Inds = [Vid.Identities[P][1] for P in Pos[0]]
    new_Coos=np.vstack((Pos[1]+round(Vid.Cropped[1][0]/one_every),(Pos[1]+round(Vid.Cropped[1][0])/one_every)/Vid.Frame_rate[1], Ars, Inds, new_Coos[:,0], new_Coos[:,1])).T
    new_Coos=new_Coos[new_Coos[:,0].astype(float).argsort(),:]
    first_row = ["Frame", "Time", "Arena", "Ind", "X", "Y"]
    new_Coos=np.vstack([first_row, new_Coos])
    np.savetxt(path, new_Coos, delimiter=';', encoding="utf-8", fmt='%s')