import psutil


def init():
    #To ensure we won't has a memory leak
    global stop_threads
    global capture
    global activate_protection

    #Using this as a global variables keeper
    global ID_kepts

def check_memory_overload():
    '''Some problems of memory leak were encountered with decord, these problems have been fixed but this is a security to control potential loss of memory.'''
    if psutil.virtual_memory()._asdict()["percent"] > 99.8:#Too much memory of the computer is used, we trigger a security that will stop immediatly the program
        return 1
    elif psutil.virtual_memory()._asdict()["percent"] > 95: #The computer is reaching it's limit, it could come from a memory leak of decord, we add a security that will limity decord's memory leaks
        return 0
    else:
        return -1 #The memory usage is back to normal, we remove previous security as it slow down the rocess a bit

