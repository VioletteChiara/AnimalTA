from AnimalTA.E_Post_tracking import Coos_loader_saver as CoosLS



def interpolate_all(Vid):
    Coos = CoosLS.load_coos(Vid)
    Blancs = []
    try:  # Old versions of AnimalTA did not had the possibility to have a variable number of targets, this is to avoid compatibility problems
        if Vid.Track[1][8]:
            fixed = True
        else:
            fixed = False
    except:
        Vid.Track[1].append(False)
        fixed = True


    for col in range(len(Coos)):
        Blancs.append([])
        pdt_blanc = False

        if not fixed:
            mask = Coos[col,:,0] < -1  # only this part is loaded
            if mask.any():
                first = mask.argmin()
                last = len(mask) - 1 - mask[::-1].argmin()
            else:
                first = last = None

            if first is None:
                first=0
                last=len(Coos[col])-1
        else:
            first = 0
            last = len(Coos[col]) - 1

        for raw in range(first, last+1):
            if Coos[col][raw][0] == -1000:
                if pdt_blanc == False:
                    Deb = raw
                    pdt_blanc = True
            else:
                if pdt_blanc:
                    Blancs[col].append((Deb, raw))
                    pdt_blanc = False
            if raw == (len(Coos[col]) - 1) and pdt_blanc:
                Blancs[col].append((int(Deb), int(raw)))
                pdt_blanc = False

    for col in range(len(Coos)):
        for correct in Blancs[col]:
            nb_raws = int(correct[1] - correct[0])
            if correct[0] != 0 and correct[1] != (len(Coos[col]) - 1):
                for raw in range(correct[0], correct[1] + 1):
                    Coos[col][raw][0] = Coos[col][correct[0] - 1][0] + (
                                (Coos[col][correct[1]][0] - Coos[col][correct[0] - 1][0]) * (
                                    (raw - correct[0]) / nb_raws))
                    Coos[col][raw][1] = Coos[col][correct[0] - 1][1] + (
                                (Coos[col][correct[1]][1] - Coos[col][correct[0] - 1][1]) * (
                                    (raw - correct[0]) / nb_raws))

            elif correct[0] == 0 and correct[1] != (len(Coos[col]) - 1):
                for raw in range(correct[0], correct[1] + 1):
                    Coos[col][raw][0] = Coos[col][correct[1]][0]
                    Coos[col][raw][1] = Coos[col][correct[1]][1]

            elif correct[0] != 0 and correct[1] == (len(Coos[col]) - 1):
                for raw in range(correct[0], correct[1] + 1):
                    Coos[col][raw][0] = Coos[col][correct[0] - 1][0]
                    Coos[col][raw][1] = Coos[col][correct[0] - 1][1]

    # Save the new cooridnates in a specific folder (corrected_coordinates)
    CoosLS.save(Vid, Coos)
    # If there was a temporary file used, we delete it


