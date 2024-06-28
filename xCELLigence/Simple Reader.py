import pandas as pd
import os
from colorama import Fore
import matplotlib.pyplot as plt
import seaborn as sbn
import sys
import traceback

def populate(data,start, stop, wells, samples, datefinder):
    """ this function populates the data sheet with the raw data,
    start refers to the first timepoint sampled, stop the last timepoint"""

    """ graphdata is the formatted data table that we will generate graphs from """
    # print(start)
    # print(stop)
    graphdata = pd.DataFrame(columns=["Timepoint", "Impedence", "Condition", "Replicate", "Date"])
    """ replicates establishes the number of replicates for the loaded dataset """
    replicates = {}
    for y in wells:
        # print(y)
        # print(samples)
        """ is this a replicate? """
        if not graphdata.isin([samples[y]]).any().any():
            print("no replicate")
            replicates.update({samples[y]: 1})
        else:
            print("replicate")
            replicates.update({samples[y]: replicates[samples[y]] + 1})
        """ populate graphdata with this well """
        timer = start*15
        # print("about to start")
        for q in range(int(start), int(stop)):
            # print(q)
            try:
                normalized = data.iloc[q][y] - data.iloc[int(start)][y]
            except:
                normalized = data.iloc[q][y]
            row = pd.DataFrame(
                {"Timepoint": timer, "Impedence": normalized, "Condition": samples[y],
                 "Replicate": replicates[samples[y]], "Date": datefinder.iloc[9][1]}, index=[0])
            graphdata = pd.concat([graphdata, row])
            timer = timer + 15
    # print("done")
    graphdata.to_csv("log.csv")
    return graphdata

def sample_editor(option1,start,stop):
    option2 = "NULL"
    while option2 != "exit":


        files = []
        for (dirpath, dirnames, filenames) in os.walk(directory):
            files.extend(filenames)
            break
        for x in range(len(filenames)):
            print(filenames[x])
        print("Current files located in this directory.")
        filename = input("Please input an xCELLigence export file to start this project: ")
        try:
            data, samples, wells, datefinder = newsamples(filename)
            print("this data set has " + str(len(samples)) + " number of wells. They are named as followed: ")
            print(samples)
            option2 = input(f"is this the dataset you intended to upload, {Fore.BLUE}yes {Fore.WHITE}"
                            f" or {Fore.BLUE}no{Fore.WHITE}? ")
            if option2 == "yes":
                option3 = "NULL"
                workingdata = populate(data,0, len(data), wells, samples, datefinder)
                while option3 != "exit":
                    input("Here is a sample graph of the data. Please press Enter to view.")
                    grapher(workingdata, "preview")
                    if option1 == "new":
                        option3 = input(f"Would you like to adjust the x axis? {Fore.BLUE}yes {Fore.WHITE}"
                                        f" or {Fore.BLUE}no{Fore.WHITE}? ")
                        if option3 == "yes":
                            start = input("How many minutes forward to start?")
                            if not (int(start) / 15).is_integer():
                                print("please choose a number divisible by 15. Defaulting to 0.")
                                start = 0
                            elif int(start) / 15 >= 0 and int(start) / 15 <= len(data):
                                start = int(start) / 15
                            else:
                                print("you've chose a timepoint beyond the scope of the data, defaulting to zero.")
                                start = 0
                            stop = input("End at how many minutes?")
                            if not (int(stop) / 15).is_integer():
                                print("please choose a number divisible by 15. Defaulting to max.")
                                stop = len(data)
                            elif int(stop) / 15 <= len(data):
                                stop = int(stop) / 15
                            else:
                                print("you've chose a timepoint beyond the scope of the data, defaulting to max.")
                                stop = len(data)
                            print("passing data to form a new graph sheet")
                            workingdata = populate(data,start, stop, wells, samples, datefinder)

                        else:
                            option2 = "exit"
                            option3 = "exit"
                            break
                    else:
                        workingdata = populate(data,start,stop,wells,samples,datefinder)
                        input("Here is a sample graph of the data. Please press Enter to view.")
                        grapher(workingdata, "preview")
                        option2 = "exit"
                        option3 = "exit"
                        break

        except:
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            print("Selected dataset not suitable for upload. Is this an xCELLigence file?")
        continue
    return workingdata, start, stop

def newsamples(filename):
    """ Pull the sample names and attempt to pick out cell types """
    categories = pd.read_excel(filename, sheet_name=2)
    """ For every well in the dataset, establish a condition and add their information to graphdata """
    datefinder = pd.read_excel(filename, sheet_name=0)
    """ uniques is the conditions present in the experiment """
    uniques = []
    """ samples assigns a well to a condition """
    samples = {}
    """ wells is the wells present in the experiment """
    wells = []
    """ for loop populates the samples dictionary """
    for x in range(len(categories)):
        if categories.iloc[x]["Cell-Type"] in uniques and categories.iloc[x]["Compound Name"] in uniques:
            print("replicate detected")
        elif categories.iloc[x]["Cell-Type"] in uniques and categories.iloc[x]["Compound Name"] not in uniques:
            uniques.append(categories.iloc[x]["Compound Name"])
        elif categories.iloc[x]["Cell-Type"] not in uniques and categories.iloc[x]["Compound Name"] in uniques:
            uniques.append(categories.iloc[x]["Cell-Type"])
        elif categories.iloc[x]["Cell-Type"] not in uniques and categories.iloc[x]["Compound Name"] not in uniques:
            uniques.append(categories.iloc[x]["Compound Name"])
            uniques.append(categories.iloc[x]["Cell-Type"])
        samples[categories.iloc[x]["Well ID"]] = str(categories.iloc[x]["Compound Name"]) + " " + str(
            categories.iloc[x]["Cell-Type"])
        wells.append(categories.iloc[x]["Well ID"])
    """ load the well graph sheet of the dataset """
    data = pd.read_excel(filename, sheet_name=5)
    """ drop the rows that display the tiny useless graphs present on this sheet, reset index to the well numbers """
    for x in range(52):
        data = data.drop([x])
    data.columns = data.loc[52]
    data = data.drop([52])
    return data, samples, wells, datefinder


def grapher(graphdata, gtype):
    plt.figure()
    if gtype == "preview":
        sbn.lineplot(data=graphdata, x="Timepoint", y="Impedence", hue="Condition", palette="colorblind", errorbar=None)
        plt.show()
    elif gtype == "single":
        print("to be added")
    elif gtype == "wholedata":
        print("to be added")
    else:
        print("input not among selected options. How did you get here?")

start = 0
stop = 9999
""" USER INTERFACE STARTS HERE """
directory = input(f"Where are we working today, chief? {Fore.BLUE}(Input desired directory): {Fore.WHITE}")
os.chdir(directory)
""" Ask the user if they'd like to setup a new dataset or load a pre-existing graph """
option1 = "Null"
option2 = "Null"
option3 = "Null"
while option1 != "exit":
    option1 = input(f"are we uploading a {Fore.BLUE}new {Fore.WHITE}project or "
                    f"modifying an {Fore.BLUE}old {Fore.WHITE}project with new data? ")
    if option1 == "new":
        projectname = input("Select a name for this new project: ")
        workingdata, start, stop = sample_editor(option1,start,stop)
        print(f"saving current project as {Fore.BLUE}project-" + projectname + ".csv{Fore.WHITE} in current directory")
        workingdata.to_csv("project-" + projectname + ".csv")
        metadata = pd.DataFrame({"Start":start,"Stop":stop},index=[0])
        metadata.to_csv("meta-project-" + projectname + ".csv")

    elif option1 == "old":
        files = []
        for (dirpath, dirnames, filenames) in os.walk(directory):
            files.extend(filenames)
            break
        for x in range(len(filenames)):
            if not filenames[x].find("project"):
                print(filenames[x])
        print("Current projects located in this directory.")
        projectname = input("Please type the name of the project you want to open: ")

        try:
            metadata = pd.read_csv("meta-" + projectname)
            workingproject = pd.read_csv(projectname)
            option4 = "NULL"
            while option4 != "exit":
                option4 = input(f"Do you want to {Fore.BLUE}add{Fore.WHITE} data to this project, "
                                f"{Fore.BLUE}view{Fore.WHITE} the current project, or {Fore.BLUE}modify{Fore.WHITE}"
                                f" the current project?")
                if option4 == "add":
                    start = metadata.iloc[0]["Start"]
                    stop = metadata.iloc[0]["Stop"]
                    workingdata, start, stop = sample_editor(option1,start,stop)
                    option5 = input(f"would you like to include this data into the project? {Fore.BLUE}yes{Fore.WHITE}"
                                    f" or {Fore.BLUE}no{Fore.WHITE}? ")
                    if option5 == "yes":
                        workingproject = pd.concat([workingproject,workingdata])
                        print("okay, adding to and saving project")
                        workingproject.to_csv(projectname)
                    else:
                        print("okay, ignoring that data...")
                elif option4 == "view":
                    grapher(workingproject,"preview")
                elif option4 == "modify":
                    # ADD THIS FUNCTIONALITY
                    print("I haven't added this to the script yet")
        except:
            print("Error. Did you upload the wrong type of file for this project?")

    else:
        option1 = input(f"ERROR: please choose either {Fore.BLUE}new {Fore.WHITE}or {Fore.BLUE}old{Fore.WHITE}: ")
