import cv2
import os

def convert_to_avi(parent, file, folder):
    """Function to convert videos toward .avi. The new .avi file will be stored in the project folder with the same name as the previous one."""
    file_name=os.path.basename(file)
    point_pos=file_name.rfind(".")
    if not os.path.isdir(os.path.join(folder,str("converted_vids"))):#Create a new directory if was not existing
        os.makedirs(os.path.join(folder,str("converted_vids")))
    new_file= os.path.join(folder, "converted_vids", file_name[:point_pos]+".avi")

    try:
        cap = cv2.VideoCapture(file)
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        frame_rate=int(cap.get(cv2.CAP_PROP_FPS))
        size = (frame_width, frame_height)

        result = cv2.VideoWriter(new_file,cv2.VideoWriter_fourcc(*'XVID'), frame_rate, size)
        nb_fr=0
        start=0
        end=cap.get(cv2.CAP_PROP_FRAME_COUNT)
        while(cap.isOpened()):
            if nb_fr%25==0:
                parent.timer = (nb_fr - start) / (end - start - 1)
                parent.show_load()
            ret, frame = cap.read()
            if ret==True:
                result.write(frame)
                nb_fr+=1
            else:
                break

        cap.release()
        result.release()
        cv2.destroyAllWindows()
        return(new_file)

    except:
        if os.path.isfile(new_file):
            os.remove(new_file)