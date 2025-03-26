import os
import pandas as pd
import shutil
import os
import csv
import numpy as np
from colorama import Fore
import imagej
import scyjava
import gc

""" Some basic settings that generally don't need to be changed from run to run..."""
""" For ImageJ... """
""" Set the path to your Fiji installation """
FIJI = 'C:\\Users\\Coolacanth\\Desktop\\Lab Stuff\\Fiji.app'
""" Things get silly if this is not set """
scyjava.config.add_option('-Xmx10g')
""" For tracking... """
""" Set external kill radius """
radmax = 20
""" Set internal kill radius """
radmin = 3
""" Can more than one NK cell be attributed as killing a single target cell? 0 = no, 1 = yes 
if no, the first NK cell to reach the target cell will be the only one to kill it """
checkwiper = 0
""" Some arrays that make automation between wells in a 96-well plate easier """
well_array = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
array_well = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H"}
""" Set the target file for experiment specific settings """
target_file = "settings.csv"
found = False

""" Interactive portion of the script """
directory = input("Where are we working today, chief? ")
os.chdir(directory)
""" Check for settings file """
for file in os.listdir('.'):
    if file == target_file:
        settings = pd.read_csv(file)
        variables = pd.read_csv("variables.csv")
        found = True
        break
""" If settings file is not found, create one """
if not found:
    startrow = input("What is the starting row letter?")
    stoprow = input("What is the ending row letter?")
    startwell = input("What is the starting well number?")
    stopwell = input("What is the ending well number?")
    frames = input("How many frames per well?")
    settings = pd.DataFrame(columns=["Well", "Variable", "Frame"])
    varnum = input("How many variables are in this experiment?")
    varnum = int(varnum)
    variables = {}
    for i in range(int(varnum)):
        varname = input("What is the name of variable " + str(i + 1) + "?")
        variables[varname] = []
    startwell = int(startwell)
    stopwell = int(stopwell)
    frames = int(frames)
    for i in range(well_array[startrow], well_array[stoprow] + 1):
        for j in range(startwell, stopwell + 1):
            current_well = input("What is the variable for well " + array_well[i] + str(j) + "? ")
            variables[current_well].append(array_well[i] + str(j))
    timepoints = input("How many timepoints in this experiment?")
    timepoints = int(timepoints)
    settings = {
        'Start Row': [startrow],
        'Stop Row': [stoprow],
        'Start Well': [startwell],
        'Stop Well': [stopwell],
        'Frames': [frames],
        'Timepoints': [timepoints]
    }
    settings = pd.DataFrame(settings)
    settings.to_csv("settings.csv")
    variables = pd.DataFrame(list(variables.items()), columns=['Variable', 'Well'])
    variables.to_csv("variables.csv")

if not os.path.exists("Resorted"):
    from filetools import organizer
    organizer(settings,directory)
    print(Fore.GREEN + "Files have been reorganized. Ready to import into ImageJ." + Fore.RESET)

resorted_check = os.path.join(directory, "Resorted", str(settings.iloc[0]["Start Row"]) + "0" + str(settings.iloc[0]["Start Well"]), "s1")
os.chdir(resorted_check)
if not os.path.exists("01_Merge.tif"):
    from filetools import stacker, StackMaster
    ij = imagej.init(FIJI, mode="interactive")
    stacker(settings, directory)
    print(Fore.GREEN + "Stacks have been created. Ready to mask." + Fore.RESET)
os.chdir(directory)
option1 = input(f"Please select an option:{Fore.BLUE} \n1. Run Masking and Make Stacks \n2. Create Pathing for Masks"
                f" \n3. Run Kill Tracking for Paths \n4. Gimmee the whole 9 yards... {Fore.RESET}")
if option1 == "1":
    from filetools import masker_settings
    if ij not in locals():
        ij = imagej.init(FIJI, mode="interactive")
    w2, w3, w4 = masker_settings(settings, directory)
    print(Fore.GREEN + "Mask thresholds have been set. Ready to make masks." + Fore.RESET)
    from filetools import masker, Masker, Corrections
    for q in range(well_array[settings.iloc[0]['Start Row']], well_array[settings.iloc[0]['Stop Row']] + 1):
        wellcol = array_well[q]
        print(wellcol)
        for x in range(int(settings.iloc[0]['Start Well']), int(settings.iloc[0]['Stop Well']) + 1):
            print(x)
            try:
                x_str = f"0{x}" if x < 10 else str(x)
                for y in range(int(settings.iloc[0]['Frames'])):
                    gc.collect()
                    yy = y + 1
                    yy = str(yy)
                    source = os.path.join(directory, "Resorted", wellcol + x_str,"s" + yy)
                    args = {"source": source, "w2":w2, "w3": w3,
                            "w4": w4, "timepoints": int(settings.iloc[0]['Timepoints'])}
                    print(args["source"])
                    w2measure, w3measure, w4measure = masker(ij, args)
                    w2measure = np.array(w2measure)
                    w3measure = np.array(w3measure)
                    w4measure = np.array(w4measure)
                    results_dir = os.path.join(source, "results")
                    os.chdir(results_dir)
                    np.savetxt("w2.csv", w2measure, delimiter=",", fmt='%s')
                    np.savetxt("w3.csv", w3measure, delimiter=",", fmt='%s')
                    np.savetxt("w4.csv", w4measure, delimiter=",", fmt='%s')
                    os.chdir(directory)

            except Exception as error:
                # handle the exception
                print("An exception occurred:", type(error).__name__)
                continue
    print(Fore.GREEN + "Masks have been created. Ready to make path cells." + Fore.RESET)

elif option1 == "2":
    ij = imagej.init(FIJI, mode="interactive")
    from filetools import pather, opener, closer, Tracking, TrackSaver
    for q in range(well_array[settings.iloc[0]['Start Row']], well_array[settings.iloc[0]['Stop Row']] + 1):
        wellcol = array_well[q]
        print(wellcol)
        for x in range(int(settings.iloc[0]['Start Well']), int(settings.iloc[0]['Stop Well']) + 1):
            print(x)
            try:
                x_str = f"0{x}" if x < 10 else str(x)
                for y in range(int(settings.iloc[0]['Frames'])):
                    gc.collect()
                    yy = y + 1
                    yy = str(yy)
                    source = os.path.join(directory, "Resorted", wellcol + x_str,"s" + yy, "results")
                    pather(ij, source)

            except Exception as error:
                # handle the exception
                print("An exception occurred:", type(error).__name__)
                continue
    print(Fore.GREEN + "Masks have been created. Ready to make path cells." + Fore.RESET)

elif option1 == "3":
    from filetools import trackloader, tracker_part2

    analysis_sheet_summary = pd.DataFrame(columns=["Sample", "No Kills", "One Kill", "Serial Kills", "Serial Ratio"])
    for q in range(well_array[settings.iloc[0]['Start Row']], well_array[settings.iloc[0]['Stop Row']] + 1):
        wellcol = array_well[q]
        print(wellcol)
        for x in range(int(settings.iloc[0]['Start Well']), int(settings.iloc[0]['Stop Well']) + 1):
            print(x)
            try:
                x_str = f"0{x}" if x < 10 else str(x)
                for y in range(int(settings.iloc[0]['Frames'])):
                    gc.collect()
                    yy = y + 1
                    yy = str(yy)
                    source = os.path.join(directory, "Resorted", wellcol + x_str,"s" + yy, "results")
                    os.chdir(source)
                    spots, cspots, qtree = trackloader(source, radmin)
                    print("Tracking files have been loaded")
                    analysis_sheet_summary = tracker_part2(spots, cspots, qtree, analysis_sheet_summary,
                                                           radmin, radmax, checkwiper, wellcol, x_str, yy)
            except Exception as error:
                # handle the exception
                print("An exception occurred:", type(error).__name__)
                continue
    os.chdir(directory)
    analysis_sheet_summary.to_csv("Tracking_Summary.csv")
    print(Fore.GREEN + "Path script executed" + Fore.RESET)

elif option1 == "4":
    print("Not available yet.")
