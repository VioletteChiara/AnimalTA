import os
from AnimalTA.A_General_tools import UserMessages, Small_info, Diverse_functions, Interface_extend
from tkinter import *
import pickle
import csv


root=Tk()

root.rowconfigure(index=0,weight=1)
root.rowconfigure(index=1,weight=1)
root.rowconfigure(index=2,weight=100)
root.rowconfigure(index=3,weight=1)
root.columnconfigure(index=0,weight=1)
root.config(width=800, height=600)
root.grid_propagate(False)


try:
    Dict_en = pickle.load(open("../Files/Translations/Dictionary_English.pkl", 'rb'))
except:
    Dict_en=dict()

All_languages=["English","Français","Español", "Galego"]#,"普通话"

Language=StringVar()
Language.set("English")


Saved_dict=Dict_en

def change_lan():
    global Saved_dict
    global all_words
    print(Language.get())
    try:
        Saved_dict = pickle.load(open("../Files/Translations/Dictionary_"+Language.get()+".pkl", 'rb'))
    except:
        Saved_dict = dict()
    load_directory()
    clean_dict()
    for key in all_words.keys():
        print(repr(all_words[key].get()))
        all_words[key].set(all_words[key].get().rstrip("\r\n"))

    show_dict()

count=0

Frame_lan=Frame(root)
Frame_lan.grid(row=0, column=0, columnspan=2, sticky="n")
for lan in All_languages:
    Radiobutton(Frame_lan, text=lan,variable=Language, value=lan, command=change_lan).grid(row=0, column=count)
    count+=1


def load_directory():
    global all_words
    all_words=dict()
    global infos_old
    infos_old=dict()
    all_directories = os.listdir("..")
    for directory in all_directories:
        if directory!=".idea" and directory!="Files" and directory!="Tests" and directory!="__pycache__":
            for root_files, dirs, files in os.walk("../"+directory):
                if not "__pycache__" in root_files:
                    for f in files:
                        if not "Auto_Translations" in f and not "UserMessages" in f:
                            if os.path.splitext(f)[1] == '.py':
                                fullpath = os.path.join(root_files, f)
                                with open(fullpath, 'r', errors="ignore") as fp:
                                    lines = fp.readlines()
                                    for row in lines:
                                        opening = 'Messages['  # String to search for
                                        if row.find(opening) != -1:
                                            begin=row[(row.find(opening))+len(opening)+1:]
                                            Word=begin[:(begin.find("]")-1)]
                                            if Word not in all_words and not "List_elem_" in Word and not "lem+" in Word:
                                                if Word in Saved_dict:
                                                    all_words[Word] = StringVar()
                                                    all_words[Word].set(Saved_dict[Word])
                                                elif Word in UserMessages.Mess[Language.get()]:
                                                    all_words[Word]=StringVar()
                                                    all_words[Word].set(UserMessages.Mess[Language.get()][Word])
                                                else:
                                                    all_words[Word] =StringVar()
                                                    all_words[Word].set(" ")

                                                if Word not in UserMessages.Mess[Language.get()]:
                                                    infos_old[Word] = "New"
                                                else:
                                                    infos_old[Word] = "Old"


    for Word in Diverse_functions.list_details_options:
        if Word+"_Details_exple" in Saved_dict:
            all_words[Word+"_Details_exple"] = StringVar()
            all_words[Word+"_Details_exple"].set(Saved_dict[Word+"_Details_exple"])
        elif Word+"_Details_exple" in UserMessages.Mess[Language.get()]:
            all_words[Word+"_Details_exple"] = StringVar()
            all_words[Word+"_Details_exple"].set(UserMessages.Mess[Language.get()][Word+"_Details_exple"])
        else:
            all_words[Word+"_Details_exple"] = StringVar()
            all_words[Word+"_Details_exple"].set(" ")

        if Word+"_Details_exple" not in UserMessages.Mess[Language.get()]:
            infos_old[Word+"_Details_exple"] = "New"
        else:
            infos_old[Word+"_Details_exple"] = "Old"

    list_of_elems = ["List_elem_Pt", "List_elem_Line", "List_elem_Bds_all", "List_elem_Bds", "List_elem_Ellipse",
                     "List_elem_Rectangle", "List_elem_Polygon"]

    for Word in Interface_extend.all_types+list_of_elems:
        if Word in Saved_dict:
            all_words[Word] = StringVar()
            all_words[Word].set(Saved_dict[Word])
        elif Word in UserMessages.Mess[Language.get()]:
            all_words[Word] = StringVar()
            all_words[Word].set(UserMessages.Mess[Language.get()][Word])
        else:
            all_words[Word] = StringVar()
            all_words[Word].set(" ")

        if Word not in UserMessages.Mess[Language.get()]:
            infos_old[Word] = "New"
        else:
            infos_old[Word] = "Old"





load_directory()

canvas=Canvas(root, width=600,height=300)
scroll=Scrollbar(root,orient=VERTICAL, command=canvas.yview)

canvas.config(yscrollcommand=scroll.set)
canvas.rowconfigure(0,weight=1)
canvas.columnconfigure(0,weight=1)

scroll.grid(row=2, column=1, sticky="ns")
canvas.grid(row=2,column=0, sticky="nsew")

frame_show = Frame(canvas, width=600)
frame_show.grid(row=0, column=0, sticky="nsew")
frame_show.columnconfigure(index=0, weight=1)
frame_show.columnconfigure(index=1, weight=10)




def clean_dict():
    for key in all_words.keys():
            all_Texts_entries[key][0].grid_forget()
            all_Texts_entries[key][1].grid_forget()

all_Texts_entries=dict()
def show_dict(pattern=None):
    count_empty = 0
    count_full = len(all_words)+1
    global all_Texts_entries

    for key in all_words.keys():
        if (pattern is None and (all_words[key].get().isspace() or all_words[key].get()=="")) or (not pattern is None and pattern in key):
            l=Label(frame_show,text=key)
            l.grid(row=count_empty, column=0, sticky="n")
            try:
                Small_info.small_info(elem=l, parent=root, message=Dict_en[key])
            except:
                pass
            e=Text(frame_show, height=3, background="mistyrose")
            e.grid(row=count_empty, column=1, sticky="nsew")

            all_Texts_entries[key]=[l,e]
            count_empty+=1

        else:
            l=Label(frame_show,text=key)
            l.grid(row=count_full, column=0, sticky="n")
            try:
                Small_info.small_info(elem=l, parent=root, message=Dict_en[key])
            except:
                pass
            e=Text(frame_show, height=3)
            e.insert(END, all_words[key].get())
            e.grid(row=count_full, column=1, sticky="nsew")
            all_Texts_entries[key] = [l, e]
            count_full-=1

show_dict()

def reorg_dict(pattern=None, by_key=True):
    count_empty = 0
    count_full = len(all_words) - 1
    global all_Texts_entries

    if by_key:
        for key in all_words.keys():
            if ((pattern is None or pattern=="") and (all_words[key].get().isspace() or all_words[key].get()=="")) or (not (pattern is None or pattern=="") and pattern in key):
                print(key)
                all_Texts_entries[key][0].grid_forget()
                all_Texts_entries[key][0].grid(row=count_empty, column=0, sticky="n")

                all_Texts_entries[key][1].grid_forget()
                all_Texts_entries[key][1].grid(row=count_empty, column=1, sticky="nsew")

                count_empty += 1
            else:
                all_Texts_entries[key][0].grid_forget()
                all_Texts_entries[key][0].grid(row=count_full, column=0, sticky="n")

                all_Texts_entries[key][1].grid_forget()
                all_Texts_entries[key][1].grid(row=count_full, column=1, sticky="nsew")

                count_full -= 1
    else:
        for key in all_words.keys():
            if ((pattern is None or pattern == "") and (all_words[key].get().isspace() or all_words[key].get() == "")) or (
                    not (pattern is None or pattern == "") and pattern in all_words[key].get()):
                print(key)
                all_Texts_entries[key][0].grid_forget()
                all_Texts_entries[key][0].grid(row=count_empty, column=0, sticky="n")

                all_Texts_entries[key][1].grid_forget()
                all_Texts_entries[key][1].grid(row=count_empty, column=1, sticky="nsew")

                count_empty += 1
            else:
                all_Texts_entries[key][0].grid_forget()
                all_Texts_entries[key][0].grid(row=count_full, column=0, sticky="n")

                all_Texts_entries[key][1].grid_forget()
                all_Texts_entries[key][1].grid(row=count_full, column=1, sticky="nsew")

                count_full -= 1

frame_show.update_idletasks()
canvas_window = canvas.create_window((0, 0), window=frame_show, anchor="nw")

canvas.config(scrollregion=canvas.bbox("all"))

def resize_frame(event):
    canvas.itemconfig(canvas_window, width=event.width)

canvas.bind("<Configure>", resize_frame)

def save():
    filehandler = open("../Files/Translations/Dictionary_"+Language.get()+".pkl", 'wb')
    new_dict=dict()
    for key, item in all_Texts_entries.items():
        new_dict[key]=str(item[1].get("1.0", "end-1c").replace("\\n", "\n"))

    pickle.dump(new_dict, filehandler)

def build_csv():
    with open("../Files/Translations/Dictionary_"+Language.get()+".csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["key","English equivalent", "value", "data present","novelty"])  # optional header
        new_dict = {key: str(item[1].get("1.0", "end-1c").replace("\\n", "\n")) for key, item in all_Texts_entries.items()}
        for key, value in new_dict.items():
            if value=="":
                is_empty="Missing"
            else:
                is_empty="OK"
            writer.writerow([key, Dict_en[key], value, is_empty, infos_old[key]])



Button(root, text="Save",command=save).grid(row=3, column=0)
Button(root, text="Build_csv",command=build_csv).grid(row=3, column=1)

def busca(arg):
    reorg_dict(Busca.get())

def busca_in(arg):
    reorg_dict(Busca2.get(), by_key=False)

Frame_search=Frame(root)
Frame_search.grid(row=1,columnspan=2,column=0)

Label(Frame_search, text="Search in keys:").grid(row=1, column=0)
Busca=Entry(Frame_search)
Busca.grid(row=1, column=1)
Busca.bind("<Key>", busca)

Label(Frame_search, text="Search in description:").grid(row=1, column=2)
Busca2=Entry(Frame_search)
Busca2.grid(row=1, column=3)
Busca2.bind("<Key>", busca_in)
root.mainloop()




