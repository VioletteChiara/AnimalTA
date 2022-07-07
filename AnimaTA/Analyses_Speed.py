import math
import cv2
import numpy as np
import itertools
from scipy.spatial.distance import cdist

"""This file contains a set of functions used to extract the analyses results from the target's trajectories"""

def calculate_dist_one_pt_Line(Ligne, Pt, Scale, between_Pt_dist="NA", get_proj=False):
    """Calculate and return the distance between one point and it's projection on a segment.
    Line: an array containing the coordinates of the two points defining the segment.
    Pt: The coordinates of the point.
    Scale: The video scale (to convert units to px).
    between_Pt_dist: the length of the segment (avoid recalculation if already done).
    get_proj= Boolean, if true also return the coordinates of the point projection on the segment.
    """

    if between_Pt_dist == "NA":
        between_Pt_dist = math.sqrt((Ligne[1][0] - Ligne[0][0]) ** 2 + (Ligne[1][1] - Ligne[0][1]) ** 2)
    t = None
    dx = Ligne[0][0] - Ligne[1][0]
    dy = Ligne[0][1] - Ligne[1][1]
    prod = (float(Pt[0]) - Ligne[1][0]) * dx + (float(Pt[1]) - Ligne[1][1]) * dy
    if prod >= 0 and prod <= (dx * dx + dy * dy) and between_Pt_dist > 0:
        dist = abs((Ligne[1][0] - Ligne[0][0]) * (Ligne[0][1] - float(Pt[1])) - (Ligne[0][0] - float(Pt[0])) * (
                    Ligne[1][1] - Ligne[0][1])) / between_Pt_dist
        if get_proj:
            if (Ligne[1][0] - Ligne[0][0])==0:
                t = [Ligne[1][0], Pt[1]]
            elif (Ligne[1][1] - Ligne[0][1])==0:
                t=[Pt[0], Ligne[1][1]]
            else:
                a=(Ligne[1][1] - Ligne[0][1])/(Ligne[1][0] - Ligne[0][0])
                b=Ligne[1][1]-(a*Ligne[1][0])
                slope_pt=-1/a
                bperp=-slope_pt*Pt[0]+Pt[1]
                t_x=(bperp-b)/(a-slope_pt)
                t=[t_x,slope_pt*t_x+bperp]

        dist = dist / Scale
    else:
        dist_pt1 = math.sqrt((Ligne[0][0] - float(Pt[0])) ** 2 + (Ligne[0][1] - float(Pt[1])) ** 2)
        dist_pt2 = math.sqrt((Ligne[1][0] - float(Pt[0])) ** 2 + (Ligne[1][1] - float(Pt[1])) ** 2)
        if get_proj:
            t = [Ligne[0], Ligne[1]][[dist_pt1, dist_pt2].index(min(dist_pt1, dist_pt2))]
        dist = min(dist_pt1, dist_pt2) / Scale

    return (dist, t)


def change_NA(val):
    """If the value is 'NA', return np.nan, else return the original value as a float."""
    if val=="NA":
        val=np.nan
    else:
        val=float(val)
    return(val)

class speed_calculations:
    """Class containing various functions to extract the analyses results from the target's trajectories. This class
    is also used as a temporary container of the value of threshold speed (defined by user) and of the elements of
    interest used for the analyses of spatial repartition
    """

    def __init__(self, seuil_movement=0):
        self.seuil_movement=seuil_movement
        self.Areas=[]

    def calculate_nei(self, Pts_coos, ind, dist, Scale, Fr_rate, to_save=False):
        """Extract all inter-individual measurements.
        Pts_coos: Targets coordinates
        ind: target identifiant (number) we are interested in
        dist: the distance threshold to consider that two targets are in contact
        Scale: The video scale (to convert units to px).
        Fr_rate: The video frame rate (to convert frames to seconds)
        to_save: if True, return all the values for all targets, if false, return only a subsample of the results
        related to the ind target.
        """


        Nb_ind=len(Pts_coos)
        dist = float(dist) * Scale

        table_nb_frame=np.zeros([Nb_ind,Nb_ind])
        liste_nb_nei=[0]*Nb_ind
        liste_is_close = np.array([0]*Nb_ind)
        liste_min_dist_nei=[0]*Nb_ind
        liste_nb_frames=[len(Pts_coos[0])]*Nb_ind
        table_all_dists = np.zeros([Nb_ind, Nb_ind])

        if to_save:
            table_is_close=np.zeros([Nb_ind,Nb_ind])
            table_is_contact=np.zeros([Nb_ind,Nb_ind])
            table_nb_contacts = np.zeros([Nb_ind, Nb_ind])
            list_events=[]


        for ligne in range(len(Pts_coos[0])):
            coos=[[change_NA(Pts_coos[i][ligne][0]),change_NA(Pts_coos[i][ligne][1])] for i in range(Nb_ind)]
            table_dists=cdist(coos, coos)

            for row in range(Nb_ind):
                table_dists[row, row] = np.nan

            #All distances between inds
            if to_save:
                for row in range(Nb_ind):
                    table_is_close[row, row] = 0

                table_nb_frame[np.where(~np.isnan(table_dists))] = table_nb_frame[np.where(~np.isnan(table_dists))] + 1
                table_is_close[np.where(table_dists<dist)]=table_is_close[np.where(table_dists<dist)]+1
                if np.any(np.logical_and(table_dists < dist, table_is_contact == 0)):
                    table_nb_contacts[np.logical_and(table_dists < dist, table_is_contact == 0)]=table_nb_contacts[np.logical_and(table_dists < dist, table_is_contact == 0)]+1

                if np.any(np.logical_and(table_dists >= dist, table_is_contact > 0)):
                    for row in range(len(table_is_contact)):
                        table_is_contact[row][row:len(table_is_contact)]=np.nan

                    pos=np.where(np.logical_and(table_dists >= dist, table_is_contact > 0))
                    list_events=list_events+[[pos[0][i], pos[1][i], table_is_contact[pos[0][i], pos[1][i]]/Fr_rate, (ligne-table_is_contact[pos[0][i], pos[1][i]])/Fr_rate] for i in range(len(pos[0]))]

                table_is_contact[np.where(table_dists < dist)] = table_is_contact[np.where(table_dists < dist)] + 1
                table_is_contact[np.where(table_dists >= dist)] = 0

            table_all_dists[np.where(~np.isnan(table_dists))]=np.add(table_all_dists[np.where(~np.isnan(table_dists))],table_dists[np.where(~np.isnan(table_dists))])
            # Close to at least one neighbor
            liste_is_close[np.any(table_dists<dist,0)]=liste_is_close[np.any(table_dists<dist,0)]+1
            #Number of neighbor
            liste_nb_nei=liste_nb_nei+(np.sum(table_dists < dist,0))
            #Shortest distance to a neighbor
            liste_min_dist_nei = [np.nansum([a, b]) for a, b in zip(liste_min_dist_nei, np.nanmin(table_dists,axis=0))]
            #Number of frames not lost
            liste_nb_frames=liste_nb_frames-np.all(np.isnan(table_dists),0)


        liste_nb_nei=np.divide(liste_nb_nei,liste_nb_frames)#Average number of neighbours
        liste_is_close=np.divide(liste_is_close,liste_nb_frames)#Prop of time close to at least one neighbourg
        liste_min_dist_nei=np.divide(liste_min_dist_nei,liste_nb_frames)
        liste_all_dists = np.nansum(table_all_dists, axis=0)
        liste_all_dists=np.divide(liste_all_dists,liste_nb_frames)

        if to_save:
            table_is_close=np.divide(table_is_close,table_nb_frame)#Prop of time close to this neighbor
            table_all_dists=np.divide(table_all_dists,table_nb_frame)#Mean distances between individuals

        if not to_save:
            return(liste_nb_nei[ind],liste_is_close[ind],liste_min_dist_nei[ind],liste_all_dists[ind])
        else:
            return (liste_nb_nei, liste_is_close, liste_min_dist_nei, liste_all_dists, table_all_dists, table_is_close, table_nb_contacts, list_events)

    def calculate_mean_speed(self, parent,ind, in_move=False):
        """Calculate the average movement speed of the ind target.
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        in_move: if true, only consider speeds that are higher than the speed threshold defined by the user. If false, all the calculated speeds are considered.
        """
        speeds=self.get_all_speeds_ind(parent,ind,in_move)
        if len(speeds)>0:
            return(sum(speeds)/len(speeds))
        else:
            return("NA")

    def calculate_prop_move(self, parent,ind):
        """Calculate the proportion of frame for which the target is moving.
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        """
        speeds=self.get_all_speeds_ind(parent,ind,False)
        state=[int(val>self.seuil_movement) for val in speeds]
        if len(speeds)>0:
            return (sum(state) / len(state))
        else:
            return("NA")


    def get_all_speeds_ind(self, parent, ind, in_move=False):
        """Calculate the speed of an individual for each frame.
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        in_move: if true, only consider speeds that are higher than the speed threshold defined by the user. If false, all the calculated speeds are considered.
        """
        speeds = []
        for ligne in range(len(parent.Coos[ind])):
            if ligne > 0 and parent.Coos[ind][ligne][0] != "NA" and parent.Coos[ind][ligne - 1][0] != "NA":
                dist = math.sqrt((float(parent.Coos[ind][ligne][0]) - float(parent.Coos[ind][ligne - 1][0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(parent.Coos[ind][ligne - 1][1])) ** 2)
                speed = (dist / float(parent.Vid.Scale[0])) / (1 / parent.Vid.Frame_rate[1])
                if (in_move and speed > self.seuil_movement) or not in_move:
                    speeds.append(speed)
        return(speeds)

    def get_all_speeds_NAs(self, parent, ind, in_move=False):
        """Similar than get_all_speeds_ind function, but in that case, NA values are replaced by 0 (for graphical purpose only).
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        in_move: if true, only consider speeds that are higher than the speed threshold defined by the user. If false, all the calculated speeds are considered.
        """
        speeds = []
        for ligne in range(len(parent.Coos[ind])):
            if ligne > 0 and parent.Coos[ind][ligne][0] != "NA" and parent.Coos[ind][ligne - 1][0] != "NA":
                dist = math.sqrt((float(parent.Coos[ind][ligne][0]) - float(parent.Coos[ind][ligne - 1][0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(parent.Coos[ind][ligne - 1][1])) ** 2)
                speed = (dist / float(parent.Vid.Scale[0])) / (1 / parent.Vid.Frame_rate[1])
                if (in_move and speed > self.seuil_movement) or not in_move:
                    speeds.append(speed)
            else:
                speeds.append(0)
        return(speeds)

    def calculate_lost(self, parent, ind):
        """Calculate the proportion of time an indiivdual is lost.
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        """
        loca = []
        for ligne in range(len(parent.Coos[ind])):
            if parent.Coos[ind][ligne][0] != "NA" :
                loca.append(0)
            else:
                loca.append(1)
        return(sum(loca)/len(loca))

    def calculate_dist(self, parent, ind, in_move=False):
        """Calculate the distance traveled by the target (in px).
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        in_move: if true, only consider movements that are done with a speed higher than the speed threshold defined by the user. If false, all the calculated distances are considered.
        """
        dists = []
        last=["NA","NA"]
        for ligne in range(len(parent.Coos[ind])):
            if ligne > 0 and parent.Coos[ind][ligne][0] != "NA":
                if parent.Coos[ind][ligne - 1][0] != "NA":
                    dist = (math.sqrt((float(parent.Coos[ind][ligne][0]) - float(parent.Coos[ind][ligne - 1][0])) ** 2 + (
                                float(parent.Coos[ind][ligne][1]) - float(parent.Coos[ind][ligne - 1][1])) ** 2))/ float(parent.Vid.Scale[0])
                    speed = (dist) / (1 / parent.Vid.Frame_rate[1])
                    last=parent.Coos[ind][ligne]
                    if (in_move and speed > self.seuil_movement) or not in_move:
                        dists.append(dist)
                elif last[0]!="NA":
                    dist = (math.sqrt((float(parent.Coos[ind][ligne][0]) - float(last[0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(last[1])) ** 2))/ float(parent.Vid.Scale[0])
                    speed = (dist) / (1 / parent.Vid.Frame_rate[1])
                    last = parent.Coos[ind][ligne]
                    if (in_move and speed > self.seuil_movement) or not in_move:
                        dists.append(dist)
        if len(dists)>0:
            return (sum(dists))
        else:
            return ("NA")

    def calculate_speed(self, parent, ind):
        """Calculate the speed of a target at the frame displayed by parent.
        parent: higher level class calling this function
        ind: individual of interest (ID number)
        """
        if (parent.Scrollbar.active_pos*parent.Vid_Lecteur.one_every - parent.Vid.Cropped[1][0]) >= 0:
            coos = parent.Coos["Ind"+str(ind)][int(round(parent.Scrollbar.active_pos - int((parent.Vid.Cropped[1][0]/parent.Vid_Lecteur.one_every))))]
            prev_coos = parent.Coos["Ind"+str(ind)][int(round(parent.Scrollbar.active_pos - (parent.Vid.Cropped[1][0]/parent.Vid_Lecteur.one_every) - 1))]
            if coos[0] != "NA" and prev_coos[0] != "NA":
                dist = math.sqrt((float(coos[0]) - float(prev_coos[0])) ** 2 + (float(coos[1]) - float(prev_coos[1])) ** 2)
                return ((dist / float(parent.Vid.Scale[0])) / (1 / parent.Vid.Frame_rate[1]))
            else:
                return ("NA")
        else:
            return ("NA")

    def calculate_dist_lat(self, parent, Point, ind, Dist):
        """Extract the measurements relatives to the "Point" element of interest.
        parent: higher level class calling this function
        Point: coordinates of the point
        ind: individual of interest (ID number)
        Dist: Distance of interest around the point
        """

        dists=[]
        is_inside=[]
        Latency="NA"
        for ligne in range(len(parent.Coos[ind])):
            if parent.Coos[ind][ligne][0] != "NA":
                dist = (math.sqrt((float(parent.Coos[ind][ligne][0]) - float(Point[0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(Point[1])) ** 2)) / float(parent.Vid.Scale[0])
                dists.append(dist)
                if dist<=Dist:
                    is_inside.append(1)
                    if Latency=="NA":
                        Latency=ligne/parent.Vid.Frame_rate[1]
                else:
                    is_inside.append(0)

        if len(dists)>0:
            Mean_dist=sum(dists)/len(dists)
            Prop_Time=sum(is_inside)/len(is_inside)
        else:
            Mean_dist="NA"
            Prop_Time="NA"

        return([Mean_dist, Latency, Prop_Time])
        #Average distance between the point and the target of interest, Latency before the distance between the point and the target is lower than Dist

    def calculate_intersect(self, parent, Points, ind):
        """Count the number of times a target crosses a segment. Also record the latency to cross
        parent: higher level class calling this function
        Points: coordinates of the segment
        ind: individual of interest (ID number)
        """

        if len(Points)==2:#Avoid errors
            touched_border = False  # If a taregt stay more than 1 frame exactly on the segment
            Latency = "NA"
            nb_cross = 0
            last="NA"
            dist_seg=math.sqrt((Points[0][0]-Points[1][0])**2 + (Points[0][1]-Points[1][1])**2)
            if dist_seg>0:#We verify that the two points defining the segment are not at the same place
                for ligne in range(len(parent.Coos[ind])):
                    if ligne > 0 and parent.Coos[ind][ligne][0] != "NA":
                        if parent.Coos[ind][ligne - 1][0] != "NA":
                            last = parent.Coos[ind][ligne]
                            dist_trav =math.sqrt((float(parent.Coos[ind][ligne][0]) - float(parent.Coos[ind][ligne - 1][0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(parent.Coos[ind][ligne - 1][1])) ** 2)
                            if dist_trav>0:#Si l'individu est en mouvement
                                Pt1 = (float(parent.Coos[ind][ligne-1][0]), float(parent.Coos[ind][ligne-1][1]))
                                Pt2=(float(parent.Coos[ind][ligne][0]),float(parent.Coos[ind][ligne][1]))
                                is_inter=self.inter(Points[0], Pt1, Pt2)[0] != self.inter(Points[1], Pt1, Pt2)[0] and self.inter(Points[0], Points[1], Pt1)[0] != self.inter(Points[0], Points[1], Pt2)[0]
                                is_crossed=self.inter(Points[0], Pt1, Pt2)[1] != self.inter(Points[1], Pt1, Pt2)[1] and self.inter(Points[0], Points[1], Pt1)[1] != self.inter(Points[0], Points[1], Pt2)[1]
                                if is_crossed and not touched_border:
                                    nb_cross+=1
                                    if Latency=="NA":
                                        Latency=ligne/parent.Vid.Frame_rate[1]
                                    if is_crossed and not is_inter:
                                        touched_border = True
                                else:
                                    touched_border = False
                        elif last!="NA":
                            dist_trav = math.sqrt((float(parent.Coos[ind][ligne][0]) - float(last[0])) ** 2 + (float(parent.Coos[ind][ligne][1]) - float(last[1])) ** 2)
                            if dist_trav > 0:
                                Pt1 = (float(last[0]), float(last[1]))
                                Pt2 = (float(parent.Coos[ind][ligne][0]), float(parent.Coos[ind][ligne][1]))
                                is_inter = self.inter(Points[0], Pt1, Pt2)[0] != self.inter(Points[1], Pt1, Pt2)[0] and \
                                           self.inter(Points[0], Points[1], Pt1)[0] != \
                                           self.inter(Points[0], Points[1], Pt2)[0]
                                is_crossed = self.inter(Points[0], Pt1, Pt2)[1] != self.inter(Points[1], Pt1, Pt2)[1] and \
                                             self.inter(Points[0], Points[1], Pt1)[1] != \
                                             self.inter(Points[0], Points[1], Pt2)[1]
                                if is_crossed and not touched_border:
                                    nb_cross += 1
                                    if Latency=="NA":
                                        Latency=ligne/parent.Vid.Frame_rate[1]
                                    if is_crossed and not is_inter:
                                        touched_border = True
                                else:
                                    touched_border = False

            return(nb_cross, Latency)
        else:
            return ("NA", "NA")


    def inter(self, A, B, C):
        return ((C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0]),(C[1] - A[1]) * (B[0] - A[0]) >= (B[1] - A[1]) * (C[0] - A[0]))


    def calculate_dist_line(self, parent, Points, ind):
        """Calculate the average distance between a target and a segment of interest.
        parent: higher level class calling this function
        Points: coordinates of the segment
        ind: individual of interest (ID number)
        """
        if len(Points)==2:
            between_Pt_dist = math.sqrt((Points[1][0] - Points[0][0]) ** 2 + (Points[1][1] - Points[0][1]) ** 2)
            dists=[]
            for ligne in range(len(parent.Coos[ind])):
                if parent.Coos[ind][ligne][0] != "NA":
                    dist,_=calculate_dist_one_pt_Line(Points, Pt=parent.Coos[ind][ligne],between_Pt_dist=between_Pt_dist, Scale=float(parent.Vid.Scale[0]))
                    dists.append(dist)

            if len(dists)>0:
                Mean_dist=sum(dists)/len(dists)
            else:
                Mean_dist="NA"

            return (Mean_dist)
        else:
            return("NA")

    def calculate_dist_border(self, parent, Area, ind, shape):
        """Calculate the distance between the target and the border of the arena and average it.
        Also calculate the proportion of time the target spent at less than X px from the border (distance defined by user and stored in "shape")
        parent: higher level class calling this function
        Area: contour defining the arena (see opencv FindContours)
        ind: individual of interest (ID number)
        shape: the information relative to the border of interest
        """
        dists=[]
        is_inside=[]
        try:
            dist_limit=shape[2].get()
        except:
            dist_limit = shape[2]
        for ligne in range(len(parent.Coos[ind])):
            if parent.Coos[ind][ligne][0] != "NA":
                res=cv2.pointPolygonTest(Area, (float(parent.Coos[ind][ligne][0]), float(parent.Coos[ind][ligne][1])), True)
                if res>=0:
                    res=res/float(parent.Vid.Scale[0])
                    dists.append(res)
                    if res <=dist_limit:
                        is_inside.append(1)
                    else:
                        is_inside.append(0)

        if len(dists)>0:
            Mean_dist=sum(dists)/len(dists)
            Prop_inside=sum(is_inside)/len(is_inside)
        else:
            Mean_dist="NA"
            Prop_inside="NA"

        return (Mean_dist, Prop_inside)


    def calculate_dist_sep_border(self, parent, shape, ind):
        """Idem than calculate_dist_border, but with only a part of the borders (defined by user and stored in "shape")
        """
        dists=[]
        is_inside=[]
        Latency="NA"
        try:
            limit=shape[2].get()
        except:
            limit = shape[2]
        for ligne in range(len(parent.Coos[ind])):
            # Is it possible to project the point?
            possible_dists = []
            if parent.Coos[ind][ligne][0] != "NA":
                for Points in shape[1]:
                    dx = Points[0][0] - Points[1][0]
                    dy = Points[0][1] - Points[1][1]
                    prod = (float(parent.Coos[ind][ligne][0]) - Points[1][0]) * dx + (
                                float(parent.Coos[ind][ligne][1]) - Points[1][1]) * dy
                    if prod >= 0 and prod <= (dx * dx + dy * dy) :
                        dist_perp = abs((Points[1][0] - Points[0][0]) * (Points[0][1] - float(parent.Coos[ind][ligne][1])) - (
                                    Points[0][0] - float(parent.Coos[ind][ligne][0])) * (
                                               Points[1][1] - Points[0][1])) / math.sqrt((Points[1][0] - Points[0][0]) ** 2 + (Points[1][1] - Points[0][1]) ** 2)

                        dist_pt1 = math.sqrt((Points[0][0] - float(parent.Coos[ind][ligne][0])) ** 2 + (
                                    Points[0][1] - float(parent.Coos[ind][ligne][1])) ** 2)
                        dist_pt2 = math.sqrt((Points[1][0] - float(parent.Coos[ind][ligne][0])) ** 2 + (
                                    Points[1][1] - float(parent.Coos[ind][ligne][1])) ** 2)
                        dist = min(dist_pt1, dist_pt2, dist_perp) / float(parent.Vid.Scale[0])
                        possible_dists.append(dist)

            if len(possible_dists)>0:
                mini_dist=min(possible_dists)
                if mini_dist<=limit:
                    is_inside.append(1)
                    if Latency=="NA":
                        Latency=ligne/parent.Vid.Frame_rate[1]
                else:
                    is_inside.append(0)
                dists.append(mini_dist)

        if len(dists)>0:
            Mean_dist=sum(dists)/len(dists)
            Prop_inside=sum(is_inside)/len(is_inside)
        else:
            Mean_dist="NA"
            Prop_inside="NA"

        return (Mean_dist, Prop_inside, Latency)




    def calculate_time_inside(self, parent, cnt, ind):
        """Calculate the proportion of time a target spent in a given shape (cnt) and the latency to enter
        parent: higher level class calling this function
        cnt: contour defining the shape of interest (see opencv FindContours)
        ind: individual of interest (ID number)
        """
        Latency = "NA"
        if len(cnt)>0:
            is_inside = []
            for ligne in range(len(parent.Coos[ind])):
                if parent.Coos[ind][ligne][0] != "NA":
                    res = cv2.pointPolygonTest(cnt[0], (int(parent.Coos[ind][ligne][0]), int(parent.Coos[ind][ligne][1])),True)
                    if res >= 0:
                        is_inside.append(1)
                        if Latency=="NA":
                            Latency=ligne/parent.Vid.Frame_rate[1]
                    else:
                        is_inside.append(0)

            if len(is_inside) > 0:
                Prop_inside = sum(is_inside) / len(is_inside)
            else:
                Prop_inside = "NA"
        else:
            Prop_inside = "NA"

        return (Prop_inside, Latency)

    def calculate_all_inter_dists(self, Pts_coos, Scale):
        """Average the inter-individual distances found and extract its minimum and maximum values.
        Pts_coos: the targets coordinates
        Scale: The video scale (to convert units to px).
        """
        dists=[]
        for ligne in range(len(Pts_coos[0])):
            Pts=[Pt[ligne] for Pt in Pts_coos]
            dist=self.calculate_interind_dist(Pts, Scale)
            if dist!="NA":
                dists.append(dist)

        if len(dists)>0:
            Mean=sum(dists)/len(dists)
            Min = min(dists)
            Max = max(dists)
        else:
            Mean, Min, Max = "NA", "NA", "NA"
        return(Mean,Min,Max)

    def calculate_interind_dist(self, Pts, Scale, draw=False, img=None, thick=1):
        """Calculate all the inter-target distances and sum it for a given frame.
        Pts: coordinates of the targets at the frame of interest
        Scale: The video scale (to convert units to px).
        draw: Boolean, if true, draw on "img" the lines to link the different targets (for illustrative purpose only)
        img: if draw==True, draw the lines on this image
        thick: The thickness of the lines to be drawn if draw==True
        """

        is_NA=False
        new_img=np.copy(img)
        all_dists = 0
        all_Xs = 0
        all_Ys = 0
        nb_pairs = 0
        cmbn = itertools.combinations(range(len(Pts)), 2)

        for pair in cmbn:
            if (Pts[pair[0]][0]=="NA" or Pts[pair[1]][0]=="NA"):
                is_NA=True
                break
            nb_pairs += 1
            X1 = float(Pts[pair[0]][0])
            Y1 = float(Pts[pair[0]][1])
            X2 = float(Pts[pair[1]][0])
            Y2 = float(Pts[pair[1]][1])
            dist = math.sqrt((X1 - X2) ** 2 + (Y1 - Y2) ** 2) / Scale
            if draw:
                new_img = cv2.line(new_img, (int(X1), int(Y1)),(int(X2), int(Y2)), (175, 0, 0), thick)
            all_dists = all_dists + dist
            all_Xs = all_Xs + X1 + X2
            all_Ys = all_Ys + Y1 + Y2

        if not is_NA:
            center=(int(all_Xs / (2 * nb_pairs)),int(all_Ys / (2 * nb_pairs)))
        else:
            center=["NA","NA"]
            all_dists="NA"
            new_img=img

        if draw:
            return(new_img,all_dists,center)
        else:
            return (all_dists)