import multiprocessing
import cv2
import decord
from AnimalTA.A_General_tools import Function_draw_arenas as Dr, UserMessages, Message_simple_question as MsgBox
from AnimalTA.D_Tracking_process import Function_prepare_images_multi, Function_assign_cnts_multi, security_settings_track, Treat_simgle_image
import numpy as np
import os
from tkinter import *
import threading
import pickle
import time
from multiprocessing import Lock

'''
To improve the speed of the tracking, we will separate the work in 2 threads.
1. Image loading, and modifications (stabilization, light correction, greyscale...) until contours are get
2. Target assignment and data recording
'''


def Do_tracking(parent, Vid, folder, type, portion=False, prev_row=None, arena_interest=None, head_tail=False, ref_frame=None):
    '''This is the main tracking function of the program.
    parent=container (main window)
    Vid=current video
    portion= True if it is a rerun of the tracking over a short part of the video (for corrections)
    prev_row=If portion is True, this correspond to the last known coordinates of the targets.
    '''
    # Language importation
    Language = StringVar()
    f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
    Language.set(f.read())
    f.close()
    Messages = UserMessages.Mess[Language.get()]

    Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
    with open(Param_file, 'rb') as fp:
        Params = pickle.load(fp)
        use_Kalman=Params["Use_Kalman"]


    # Where coordinates will be saved, if the folder did not exists, it is created.
    if Vid.User_Name == Vid.Name:
        file_name = Vid.Name
        point_pos = file_name.rfind(".")
        if file_name[point_pos:].lower()!=".avi":
            file_name = Vid.User_Name
        else:
            file_name = file_name[:point_pos]
    else:
        file_name = Vid.User_Name

    if not portion:
        if not os.path.isdir(os.path.join(folder,"coordinates")):
            os.makedirs(os.path.join(folder, "coordinates"))
    else:
        if not os.path.isdir(os.path.join(folder,"TMP_portion")):
            os.makedirs(os.path.join(folder,"TMP_portion"))

    if portion:
        To_save = os.path.join(folder, "TMP_portion", file_name + "_TMP_portion_Coordinates.csv")
    else:
        To_save = os.path.join(folder, "Coordinates", file_name + "_Coordinates.csv")

    # if the user choose to reduce the frame rate.
    one_every = Vid.Frame_rate[0] / Vid.Frame_rate[1]

    start = Vid.Cropped[1][0]  # Video beginning (after crop)
    end = Vid.Cropped[1][1]  # Video end (after crop)

    security_settings_track.init()
    security_settings_track.activate_protection=False
    security_settings_track.activate_super_protection=False

    if ref_frame is None:
        First_frame = start
    else:
        First_frame = ref_frame

    Which_part_first=0
    if Vid.Cropped[0]:
        if len(Vid.Fusion) > 1:  # If the video results from concatenated videos
            Which_part_first = [index for index, Fu_inf in enumerate(Vid.Fusion) if Fu_inf[0] <= First_frame][-1]

    security_settings_track.activate_protection=False
    security_settings_track.activate_super_protection=False


    if Vid.type=="Video":
        capture = decord.VideoReader(Vid.Fusion[Which_part_first][1])  # Open video
        capture.seek(0)
        Prem_image_to_show = capture[First_frame - Vid.Fusion[Which_part_first][0]].asnumpy()  # Take the first image
        del capture
    else:
        Prem_image_to_show = cv2.imread(os.path.join(Vid.Fusion[Which_part_first][1], Vid.img_list[First_frame - Vid.Fusion[Which_part_first][0]]))

    if type=="fixed":
        mask, or_bright, Arenas, Prem_image_to_show = Treat_simgle_image.Prepare_Vid(Vid, Prem_image_to_show, type, portion=portion, arena_interest=arena_interest)
    elif type=="variable":
        mask, or_bright, Arenas, Main_Arenas_image, Main_Arenas_Bimage, Prem_image_to_show = Treat_simgle_image.Prepare_Vid(Vid,
                                                                                                        Prem_image_to_show,
                                                                                                        type,
                                                                                                        portion=portion,
                                                                                                        arena_interest=arena_interest)

    nb_cpu_extract_treat=min(15,(multiprocessing.cpu_count() -1))

    Nb_images_processed=multiprocessing.Value("i",0)

    #Creation of the process to treat images
    Locks_cnts = [Lock() for i in range(nb_cpu_extract_treat)]

    Processes = []
    #A end process associate the contours
    chunk_size=25

    all_frames=np.arange(start, end + one_every, one_every)
    Images_to_treat = [
        [i, all_frames[val: val + chunk_size].tolist()]
        for i, val in enumerate(range(0, len(all_frames), chunk_size))
    ]
    Queue_frames=multiprocessing.Queue()
    for t in Images_to_treat:
        Queue_frames.put(t)

    #We create one queue per cpu (-1 as one cpu will be in charge of the tracking itself)
    Queues_cnt=multiprocessing.Queue(maxsize=100)

    if type=="fixed":
        Processes.append(multiprocessing.Process(target=Function_assign_cnts_multi.Treat_cnts_fixed, args=(Queues_cnt, Nb_images_processed, Vid, Arenas, start, end, prev_row, To_save, portion, one_every, use_Kalman, head_tail)))
    elif type == "variable":
        keep_entrance = Params["Keep_entrance"]
        manager = multiprocessing.Manager()
        ID_kepts = manager.list([manager.list(sublist) for sublist in [[] for _ in Arenas]])
        Processes.append(multiprocessing.Process(target=Function_assign_cnts_multi.Treat_cnts_variable, args=(Queues_cnt, Nb_images_processed,Vid, Arenas, Main_Arenas_image, Main_Arenas_Bimage, start, end, ID_kepts, prev_row, To_save, portion, one_every, not keep_entrance, use_Kalman, head_tail)))


    #A maximum of process treat the images
    for process_ID in range(nb_cpu_extract_treat):
        Processes.append(multiprocessing.Process(target=Function_prepare_images_multi.Image_modif, args=(Queues_cnt, Queue_frames, Vid, Prem_image_to_show, mask, or_bright, process_ID, Locks_cnts[process_ID])))

    to_add = parent.loading_state.cget("text")
    parent.loading_state.config(text=to_add)


    def launcher():
        for p in range(len(Processes)):
            Processes[p].start()
            with Nb_images_processed.get_lock():
                if p>0 and Nb_images_processed.value >= (Vid.Cropped[1][1] / one_every - Vid.Cropped[1][0] / one_every) - (chunk_size*2):
                    print("broke")
                    break


    threading.Thread(target=launcher, daemon=True).start()

    while not any(p.is_alive() for p in Processes):
        time.sleep(0.01)

    while len([p for p in Processes if p.is_alive()])>0:
        time.sleep(0.25)
        with Nb_images_processed.get_lock():  # Acquire lock to safely modify the shared value
            parent.timer=(Nb_images_processed.value)/(Vid.Cropped[1][1]/one_every-Vid.Cropped[1][0]/one_every)
            parent.show_load()


    parent.timer = 1
    parent.show_load()



    if security_settings_track.stop_threads:
        if type=="fixed":
            return (False)
        elif type=="variable":
            return (False,0)
    else:
        if type == "fixed":
            return (True)
        elif type=="variable":
            ID_kepts_toret = [list(sublist) for sublist in ID_kepts]
            print(ID_kepts_toret)
            return (True,list(ID_kepts_toret))


def urgent_close(Vid):
    security_settings_track.stop_threads = True

