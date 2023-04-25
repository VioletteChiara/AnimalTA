import cv2
import threading
import decord

class Video_Loader():
    def __init__(self, Vid, File, is_crop=True, **kwargs):
        self.Vid=Vid#Which video of the project (can be different from the previous one in case of concatenated videos)
        self.is_crop=is_crop#Should we crop the video
        self.load_video(File)#Which video to load


    def __len__(self):
        return self.calculate_len()

    def __del__(self):
        del self.capture
        del self

    def __getitem__(self, i):
        if self.which_reader=="decord":
            im=self.capture[i].asnumpy()
            if self.is_crop and self.Vid.Cropped_sp[0]:
                im=im[self.Vid.Cropped_sp[1][0]:self.Vid.Cropped_sp[1][2], self.Vid.Cropped_sp[1][1]:self.Vid.Cropped_sp[1][3]]
            self.capture.seek(0)

            return im
        else:
            try:
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, i)
                res, frame = self.capture.read()
                frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                if self.is_crop and self.Vid.Cropped_sp[0]:
                    frame = frame[self.Vid.Cropped_sp[1][0]:self.Vid.Cropped_sp[1][2],self.Vid.Cropped_sp[1][1]:self.Vid.Cropped_sp[1][3]]
                return (frame)
            except: #If the reader changed in the middle
                return self[i]

    def calculate_len(self):
        if self.which_reader=="decord":
            L=len(self.capture)
            self.capture.seek(0)
            return L
        else:
            return int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))


    def load_video(self, File):
        self.which_reader = "cv2"
        self.capture = cv2.VideoCapture(File)
        Thread_load_vid =threading.Thread(target=self.load_decord_thread ,args=[File])
        Thread_load_vid.start()

    def load_decord_thread(self ,File):
        self.tmp_capture = decord.VideoReader(File)
        del self.capture
        self.which_reader ="decord"
        self.capture = self.tmp_capture
        del self.tmp_capture

        # if the video was not concatenated, we recalculate its real length (opencv is not precise in this task, so we correct this value using the decord library)
        # For concatenated videos, this step has been done at the moment of the concatenation
        if len(self.Vid.Fusion) < 2:
            self.Vid.Frame_nb[0] = len(self.capture)
            self.capture.seek(0)
            self.Vid.Frame_nb[1] = self.Vid.Frame_nb[0] /  int(round(round(self.Vid.Frame_rate[0], 2) / self.Vid.Frame_rate[1]))
            if not self.Vid.Cropped[0]:
                self.Vid.Cropped[1][1] = self.Vid.Frame_nb[0] - 1