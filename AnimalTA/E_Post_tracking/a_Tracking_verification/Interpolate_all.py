from AnimalTA.E_Post_tracking import Coos_loader_saver as CoosLS



def interpolate_all(Vid):
    Coos, who_is_here = CoosLS.load_coos(Vid)
    Blancs = []
    for col in range(len(Coos)):
        Blancs.append([])
        pdt_blanc = False
        for raw in range(len(Coos[col])):
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


