def makesettings(directory):
    """Makes a settings file for the experiment.
        Also creates a file listing the variables in this experiment, for reference.
        The directory variable is the root directory where the files will be saved."""
    import pandas as pd
    import os
    well_array = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
    array_well = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H"}
    startrow = input("What is the starting row letter?")
    stoprow = input("What is the ending row letter?")
    startwell = input("What is the starting well number?")
    stopwell = input("What is the ending well number?")
    frames = input("How many frames per well?")
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
            current_well = input("What is the variable (name) for well " + array_well[i] + str(j) + "? ")
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
    settings.to_csv(os.path.join(directory, "settings.csv"))
    variables = pd.DataFrame(list(variables.items()), columns=['Variable', 'Well'])
    variables.to_csv(os.path.join(directory, "variables.csv"))
    return settings


def organizer(directory, settings=None):
    """ This function organizes the files into a directory structure based on the settings provided.
        The directory variable is the root directory where the files are located.
        The settings variable, if provided, is a pandas dataframe that contains the settings for the experiment.
        If a settings variable is not provided, the function will look for a settings.csv file in the current directory.
        """
    import os
    import pandas as pd
    import shutil

    well_array = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
    if settings is None:
        settings = pd.read_csv(os.path.join(directory, "settings.csv"))
    directories = [d for d in entries if os.path.isdir(d)]
    if directories is not None:
        first_directory = directories[0]
        new_name = "Unsorted"
        os.rename(first_directory, new_name)
        print(f"Renamed '{first_directory}' to '{new_name}'")
    else:
        print("No directories found in the current directory.")
    """ For loops go through every well and frame of the experiment """
    for q in range(well_array[settings.iloc[0]['Start Row']], well_array[settings.iloc[0]['Stop Row']] + 1):
        wellcol = array_well[q]
        for x in range(int(settings.iloc[0]['Start Well']), int(settings.iloc[0]['Stop Well']) + 1):
            try:
                x_str = f"0{x}" if x < 10 else str(x)
                for y in range(int(settings.iloc[0]['Frames'])):
                    yy = str(y + 1)
                    """ This is the directory structure that will be created """
                    resorted_path = os.path.join(directory, "Resorted", wellcol + x_str, "s" + yy)
                    results_path = os.path.join(resorted_path, "results")
                    os.makedirs(resorted_path, exist_ok=True)
                    os.makedirs(results_path, exist_ok=True)
                    """ For every frame, go through every timepoint """
                    for z in range(int(settings.iloc[0]['Timepoints'])):
                        zz = str(z + 1)
                        origin = os.path.join(directory, "Unsorted", f"TimePoint_{zz}")
                        if not os.path.exists(origin):
                            print(f"Origin path does not exist: {origin}")
                            continue
                        """ For every timepoint, copy the files from the original directory to the new directory """
                        for w in range(1, int(settings.iloc[0]['Channels'])+1):
                            file_name = f"Campbell-K_{wellcol}{x_str}_s{yy}_w{w}.TIF"
                            origin_file = os.path.join(origin, file_name)
                            destination_file = os.path.join(resorted_path, file_name.replace(".TIF", f"_t{zz}.tif"))
                            print(f"Copying from {origin_file} to {destination_file}")
                            if os.path.exists(origin_file):
                                shutil.copy(origin_file, destination_file)
                            else:
                                print(f"File not found: {origin_file}")
            except Exception as error:
                print("An exception occurred:", type(error).__name__, error)
                continue


def stacker(directory, ij=None, settings=None):
    """This function simply assembles hyperstacks from the file structure established by the organizer fxn.
        The directory variable is the root directory where the files are located.
        The settings variable, if provided, is a pandas dataframe that contains the settings for the experiment.
        If a settings variable is not provided, the function will look for a settings.csv file in the current directory.
        """
    import os
    import pandas as pd
    well_array = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
    array_well = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H"}
    if settings is None:
        settings = pd.read_csv(os.path.join(directory, "settings.csv"))
    if ij is None:
        import imagej
        ij = imagej.init('sc.fiji:fiji', mode="headless")
    """ For loops go through every well and frame of the experiment """
    for q in range(well_array[settings.iloc[0]['Start Row']], well_array[settings.iloc[0]['Stop Row']] + 1):
        wellcol = array_well[q]
        print(wellcol)
        for x in range(int(settings.iloc[0]['Start Well']), int(settings.iloc[0]['Stop Well']) + 1):
            print(x)
            try:
                x_str = f"0{x}" if x < 10 else str(x)
                for y in range(int(settings.iloc[0]['Frames'])):
                    yy = y + 1
                    yy = str(yy)
                    source = os.path.join(directory, "Resorted", wellcol + x_str, "s" + yy)
                    """ This macro will create a hyperstack from the files in the source directory """
                    args = {"source": source, "channels": int(settings.iloc[0]['Channels']), }
                    ij.py.run_macro(StackMaster, args)

            except Exception as error:
                # handle the exception
                print("An exception occurred:", type(error).__name__)
                continue


def masker(directory, ij=None, correction=1, settings=None):
    import jpype
    import gc
    import numpy as np
    import os
    import pandas as pd
    well_array = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
    array_well = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H"}
    if settings is None:
        settings = pd.read_csv(os.path.join(directory, "settings.csv"))
    if ij is None:
        import imagej
        ij = imagej.init('sc.fiji:fiji', mode="headless")
    """ For loops go through every well and frame of the experiment """
    for q in range(well_array[settings.iloc[0]['Start Row']], well_array[settings.iloc[0]['Stop Row']] + 1):
        wellcol = array_well[q]
        print(wellcol)
        for x in range(int(settings.iloc[0]['Start Well']), int(settings.iloc[0]['Stop Well']) + 1):
            print(x)
            try:
                x_str = f"0{x}" if x < 10 else str(x)
                for y in range(int(settings.iloc[0]['Frames'])):
                    yy = y + 1
                    yy = str(yy)
                    source = os.path.join(directory, "Resorted", wellcol + x_str, "s" + yy)
                    print(f"Loading from {source}")
                    """ If correction is set to 1, the macro will run the correction script """
                    """ The correction script fixes x/y drift from the experiment """
                    if correction == 1:
                        args = {"source": source}
                        ij.py.run_macro(Corrections, args)
                        jpype.java.lang.Runtime.getRuntime().gc()
                        gc.collect()
                    """ Masker will run the ImageJ macro that creates the masks for the experiment """
                    args = {"source": source, "timepoints": int(settings.iloc[0]['Timepoints'])}
                    measurements = ij.py.run_macro(Masker, args)
                    """ measurements are the area of signal by timepoint """
                    w2measure = measurements.getOutput("w2measure")
                    w3measure = measurements.getOutput("w3measure")
                    w4measure = measurements.getOutput("w4measure")
                    w2measure = str(w2measure)
                    w3measure = str(w3measure)
                    w4measure = str(w4measure)
                    w2measure = w2measure.split(" ")
                    print(w2measure)
                    w3measure = w3measure.split(" ")
                    print(w3measure)
                    w4measure = w4measure.split(" ")
                    print(w4measure)
                    w2measure = np.array(w2measure)
                    w3measure = np.array(w3measure)
                    w4measure = np.array(w4measure)
                    results_dir = os.path.join(source, "results")
                    os.chdir(results_dir)
                    """ The following lines will save the measurements to a csv file """
                    np.savetxt("w2.csv", w2measure, delimiter=",", fmt='%s')
                    np.savetxt("w3.csv", w3measure, delimiter=",", fmt='%s')
                    np.savetxt("w4.csv", w4measure, delimiter=",", fmt='%s')

            except Exception as error:
                # handle the exception
                print("An exception occurred:", type(error).__name__)
                continue


def pather(directory, ij=None, settings=None):
    """ This function is a wrapper for the ImageJ macro that runs the tracking analysis.
        The directory variable is the root directory where the files are located.
        The ij variable is the ImageJ instance to use. Note: TrackMate is not available in headless mode.
        The settings variable, if provided, is a pandas dataframe that contains the settings for the experiment.
        If a settings variable is not provided, the function will look for a settings.csv file in the current directory.
        """
    import jpype
    import os
    import pandas as pd
    well_array = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
    array_well = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H"}
    if settings is None:
        settings = pd.read_csv(os.path.join(directory, "settings.csv"))
    if ij is None:
        import imagej
        """ TrackMate does seem to work now in headless mode, and you can try that if needed.
        I still think It's better to run this in interactive mode, so I set it to that by default. """
        ij = imagej.init('sc.fiji:fiji', mode="interactive")
    """ For loops go through every well and frame of the experiment """
    for q in range(well_array[settings.iloc[0]['Start Row']], well_array[settings.iloc[0]['Stop Row']] + 1):
        wellcol = array_well[q]
        print(wellcol)
        for x in range(int(settings.iloc[0]['Start Well']), int(settings.iloc[0]['Stop Well']) + 1):
            print(x)
            try:
                x_str = f"0{x}" if x < 10 else str(x)
                for y in range(int(settings.iloc[0]['Frames'])):
                    yy = y + 1
                    yy = str(yy)
                    source = os.path.join(directory, "Resorted", wellcol + x_str, "s" + yy, "results")
                    """ Individually load and run the tracking analysis for each mask """
                    """ I am not smart but I am lazy, so the hyperstacks are opened via Java (ie, IJ Macros)
                        However the TrackMate folks have their tutorial on scripting written out in Jython.
                        Thus, we have the frankly silly situation where we have 4 different lines to open, run, save,
                        and close the hyperstack. """
                    args = {"x": "w2-mask", "source": source}
                    ij.py.run_macro(opener, args)
                    ij.py.run_script("python", Tracking, args)
                    ij.py.run_script("python", TrackSaver, args)
                    ij.py.run_macro(closer)
                    args = {"x": "w3-mask", "source": source}
                    ij.py.run_macro(opener, args)
                    ij.py.run_script("python", Tracking, args)
                    ij.py.run_script("python", TrackSaver, args)
                    ij.py.run_macro(closer)
                    args = {"x": "w4-mask", "source": source}
                    ij.py.run_macro(opener, args)
                    ij.py.run_script("python", Tracking, args)
                    ij.py.run_script("python", TrackSaver, args)
                    ij.py.run_macro(closer)
                    jpype.java.lang.Runtime.getRuntime().gc()

            except Exception as error:
                # handle the exception
                print("An exception occurred:", type(error).__name__)
                continue


def serial_killing(directory, radmin = 5, radmax = 15, checkwiper = 0, settings = None):
    """ Purpose of this script:
     Natural Killer (NK) cells are a sub-type of immune cell important in the body's natural defence against cancer.
     This "cell-mediated" immunity is characterized by immune effector cells forming physical attachments with a target
     cell, eg a tumor cell, in order to direct cytolytic granules from the NK cell to kill the target cell.
     It is important to be able to compare conditions which increase or decrease an NK cell's ability to kill cancer cells.
     One of the metrics by which these NK cells can be judged is via serial killing, the ability for a single NK cell to
     kill multiple subsequent targets before dying or hitting "exhaustion"
     This script attempts to measure serial killing by taking real-time positional data of NK cells and apoptotic cells
     (dying cells) as acquired by microscopy.

     What this script does:
     This script reads tracking data generated by TrackMate for ImageJ. "tracks.csv" are tracks taken from images of
     NK cells. "atracks.csv", a-tracks are tracks taken from images of apoptotic cells. "bracks.csv", b-tracks are
     tracks taken from images of Hoechst dyed cells (all cells in an assay). A dead cell is a b-track that
     eventually overlaps with an a-track.
     Taking the x and y positions of a single NK cell along a time course, it compares those positions to dying cells.
     If an NK cell "scanned" (was one cell radii away) a cell sometime prior to it dying, it logs a potential kill
     Currently, this is a "first-come-first-served" process and assumes that if an NK cell is adhering to a cell
     and that cell dies sometime in the future, it was because of that NK cell.
     The script also accounts for the NK cells themselves dying. A "minimum radii" is set by this script to see if a
     dead cell overlaps with an NK track. Once the script has identified that a a/b-track is actually an NK cell,
     the script scrubs past and future kills that might be linked to that a/b-track.

     Defined variables:
     directory: the root directory where the files are located
     radmin: the minimum radii that defines a signal's distance from an NK cell. Anything less than this value is
     defined as the NK cell itself. Set to 5 pixels by default. This value should roughly match the radius of the
     NK cell nucleus.
     radmax: the maximum radii that defines a signal's distance from an NK cell. Anything greater than this value is
     considered too far from an NK cell to be considered a kill. This value should roughly match the diameter of the
     target cell.
     checkwiper: a flag to determine if multiple NK cells should be allowed to share a kill. By default,
     the first NK cell to make contact with a target cell track that eventually dies is the only NK cell
     that is awarded the kill. Setting this value to 1 allows every NK cell that made contact with a target
     cell prior to its death to be awarded a kill.
     settings: the file that determines the well dimensions for this experiment. By default it will look for
     a csv file in the provided directory, but can alternatively be supplied as a Pandas dataframe.
     """

    from typing import List
    import pandas as pd
    from QuadTree import Point, Rect, QuadTree
    import os
    import time

    """ Setup of the analysis sheet """
    analysis_sheet_summary = {"Sample": [], "No Kills": [], "One Kill": [], "Serial Kills": [], "Serial Ratio": []}
    analysis_sheet_summary = pd.DataFrame(analysis_sheet_summary)

    """ Load-bearing print command """
    print("Starting script....")
    """ First for loop sets the row and range of rows """
    well_array = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
    array_well = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H"}
    if settings is None:
        settings = pd.read_csv(os.path.join(directory, "settings.csv"))
    for q in range(well_array[settings.iloc[0]['Start Row']], well_array[settings.iloc[0]['Stop Row']] + 1):
        wellcol = array_well[q]
        for x in range(int(settings.iloc[0]['Start Well']), int(settings.iloc[0]['Stop Well']) + 1):
                x_str = f"0{x}" if x < 10 else str(x)
                for y in range(int(settings.iloc[0]['Frames'])):
                    yy = y + 1
                    yy = str(yy)
                    source = os.path.join(directory, "Resorted", wellcol + x_str, "s" + yy, "results")
                    os.chdir(source)
                    print(f"Loading from {source}")
                    try:
                        """Pandas gets really unhappy if you don't assign an object class to every column"""
                        spots = pd.read_csv("w2-mask_trackerv2-spots.csv", skiprows=[1, 2, 3],
                                            dtype={'LABEL': str, 'ID': str, 'TRACK_ID': float, 'QUALITY': float,
                                                   'POSITION_X': float, 'POSITION_Y': float, 'POSITION_Z': float,
                                                   'POSITION_T': float, 'FRAME': float, 'RADIUS': float,
                                                   'VISIBILITY': float,
                                                   'MANUAL_SPOT_COLOR': float, 'MEAN_INTENSITY_CH1': float,
                                                   'MEDIAN_INTENSITY_CH1': float, 'MIN_INTENSITY_CH1': float,
                                                   'MAX_INTENSITY_CH1': float, 'TOTAL_INTENSITY_CH1': float,
                                                   'STD_INTENSITY_CH1': float, 'MEAN_INTENSITY_CH2': float,
                                                   'MEDIAN_INTENSITY_CH2': float, 'MIN_INTENSITY_CH2': float,
                                                   'MAX_INTENSITY_CH2': float, 'TOTAL_INTENSITY_CH2': float,
                                                   'STD_INTENSITY_CH2': float, 'MEAN_INTENSITY_CH3': float,
                                                   'MEDIAN_INTENSITY_CH3': float, 'MIN_INTENSITY_CH3': float,
                                                   'MAX_INTENSITY_CH3': float, 'TOTAL_INTENSITY_CH3': float,
                                                   'STD_INTENSITY_CH3': float, 'MEAN_INTENSITY_CH4': float,
                                                   'MEDIAN_INTENSITY_CH4': float, 'MIN_INTENSITY_CH4': float,
                                                   'MAX_INTENSITY_CH4': float, 'TOTAL_INTENSITY_CH4': float,
                                                   'STD_INTENSITY_CH4': float, 'CONTRAST_CH1': float, 'SNR_CH1': float,
                                                   'CONTRAST_CH2': float, 'SNR_CH2': float, 'CONTRAST_CH3': float,
                                                   'SNR_CH3': float, 'CONTRAST_CH4': float, 'SNR_CH4': float})
                    except:
                        print("Error: correct csv file not found")
                        break
                    try:
                        aspots = pd.read_csv("w4-mask_trackerv2-spots.csv", skiprows=[1, 2, 3],
                                             dtype={'LABEL': str, 'ID': str, 'TRACK_ID': float, 'QUALITY': float,
                                                    'POSITION_X': float, 'POSITION_Y': float, 'POSITION_Z': float,
                                                    'POSITION_T': float, 'FRAME': float, 'RADIUS': float,
                                                    'VISIBILITY': float,
                                                    'MANUAL_SPOT_COLOR': float, 'MEAN_INTENSITY_CH1': float,
                                                    'MEDIAN_INTENSITY_CH1': float, 'MIN_INTENSITY_CH1': float,
                                                    'MAX_INTENSITY_CH1': float, 'TOTAL_INTENSITY_CH1': float,
                                                    'STD_INTENSITY_CH1': float, 'MEAN_INTENSITY_CH2': float,
                                                    'MEDIAN_INTENSITY_CH2': float, 'MIN_INTENSITY_CH2': float,
                                                    'MAX_INTENSITY_CH2': float, 'TOTAL_INTENSITY_CH2': float,
                                                    'STD_INTENSITY_CH2': float, 'MEAN_INTENSITY_CH3': float,
                                                    'MEDIAN_INTENSITY_CH3': float, 'MIN_INTENSITY_CH3': float,
                                                    'MAX_INTENSITY_CH3': float, 'TOTAL_INTENSITY_CH3': float,
                                                    'STD_INTENSITY_CH3': float, 'MEAN_INTENSITY_CH4': float,
                                                    'MEDIAN_INTENSITY_CH4': float, 'MIN_INTENSITY_CH4': float,
                                                    'MAX_INTENSITY_CH4': float, 'TOTAL_INTENSITY_CH4': float,
                                                    'STD_INTENSITY_CH4': float, 'CONTRAST_CH1': float, 'SNR_CH1': float,
                                                    'CONTRAST_CH2': float, 'SNR_CH2': float, 'CONTRAST_CH3': float,
                                                    'SNR_CH3': float, 'CONTRAST_CH4': float, 'SNR_CH4': float})
                    except:
                        print("Error: correct csv not found.")
                        break
                    try:
                        bspots = pd.read_csv("w3-mask_trackerv2-spots.csv", skiprows=[1, 2, 3],
                                             dtype={'LABEL': str, 'ID': str, 'TRACK_ID': float, 'QUALITY': float,
                                                    'POSITION_X': float, 'POSITION_Y': float, 'POSITION_Z': float,
                                                    'POSITION_T': float, 'FRAME': float, 'RADIUS': float,
                                                    'VISIBILITY': float,
                                                    'MANUAL_SPOT_COLOR': float, 'MEAN_INTENSITY_CH1': float,
                                                    'MEDIAN_INTENSITY_CH1': float, 'MIN_INTENSITY_CH1': float,
                                                    'MAX_INTENSITY_CH1': float, 'TOTAL_INTENSITY_CH1': float,
                                                    'STD_INTENSITY_CH1': float, 'MEAN_INTENSITY_CH2': float,
                                                    'MEDIAN_INTENSITY_CH2': float, 'MIN_INTENSITY_CH2': float,
                                                    'MAX_INTENSITY_CH2': float, 'TOTAL_INTENSITY_CH2': float,
                                                    'STD_INTENSITY_CH2': float, 'MEAN_INTENSITY_CH3': float,
                                                    'MEDIAN_INTENSITY_CH3': float, 'MIN_INTENSITY_CH3': float,
                                                    'MAX_INTENSITY_CH3': float, 'TOTAL_INTENSITY_CH3': float,
                                                    'STD_INTENSITY_CH3': float, 'MEAN_INTENSITY_CH4': float,
                                                    'MEDIAN_INTENSITY_CH4': float, 'MIN_INTENSITY_CH4': float,
                                                    'MAX_INTENSITY_CH4': float, 'TOTAL_INTENSITY_CH4': float,
                                                    'STD_INTENSITY_CH4': float, 'CONTRAST_CH1': float, 'SNR_CH1': float,
                                                    'CONTRAST_CH2': float, 'SNR_CH2': float, 'CONTRAST_CH3': float,
                                                    'SNR_CH3': float, 'CONTRAST_CH4': float, 'SNR_CH4': float})
                    except:
                        print("Error: correct csv not found.")
                        break

                    """ Reorder these by Track ID and time """
                    spots.sort_values(by=['TRACK_ID', 'FRAME'], inplace=True)
                    aspots.sort_values(by=['TRACK_ID', 'FRAME'], inplace=True)
                    bspots.sort_values(by=['TRACK_ID', 'FRAME'], inplace=True)

                    """ Create a bounding rectangle defined by image dimensions that will be used for creating search areas """
                    min_x = float(spots["POSITION_X"].min())
                    max_x = float(spots["POSITION_X"].max())
                    min_y = float(spots["POSITION_Y"].min())
                    max_y = float(spots["POSITION_Y"].max())
                    if min_x >= float(aspots["POSITION_X"].min()):
                        min_x = float(aspots["POSITION_X"].min())
                    if max_x <= float(aspots["POSITION_X"].max()):
                        max_x = float(aspots["POSITION_X"].max())
                    if min_y >= float(aspots["POSITION_Y"].min()):
                        min_y = float(aspots["POSITION_Y"].min())
                    if max_y <= float(aspots["POSITION_Y"].max()):
                        max_y = float(aspots["POSITION_Y"].max())
                    width = max_x - min_x
                    height = max_y - min_y

                    """ Create cspots, which will have all the apoptotic tracks to start, then splice b-tracks to the
                    start of each of them """
                    cspots = {"TRACK_ID": [], "POSITION_X": [], "POSITION_Y": [], "FRAME": []}
                    cspots = pd.DataFrame(cspots)
                    for targets in range(int(aspots["TRACK_ID"].max())):
                        a_narrow = aspots.loc[aspots['TRACK_ID'] == float(targets)]
                        a_narrow = a_narrow.loc[a_narrow["FRAME"] == a_narrow["FRAME"].min()]
                        cspots.loc[len(cspots.index)] = [a_narrow.iloc[0]["TRACK_ID"]
                            , a_narrow.iloc[0]["POSITION_X"]
                            , a_narrow.iloc[0]["POSITION_Y"]
                            , a_narrow.iloc[0]["FRAME"]
                                                         ]

                    """ for debugging track splicing: """
                    # print(cspots)

                    """ seed the quad tree with points """
                    apoints: List[Point] = [Point(float(cspots.iloc[row]["POSITION_X"])
                                                  , float(cspots.iloc[row]["POSITION_Y"])
                                                  , [int(cspots.iloc[row]["TRACK_ID"]), int(cspots.iloc[row]["FRAME"])]
                                                  ) for row in range(int(cspots["TRACK_ID"].count()))
                                            ]
                    domain = Rect((width + min_x) / 2, (height + min_y) / 2, width, height)
                    qtree = QuadTree(domain, 100)
                    for point in apoints:
                        qtree.insert(point)

                    """ Splice together b-tracks to apoptotic tracks by running every b-track against the quadtree """
                    bspots = bspots[["TRACK_ID", "POSITION_X", "POSITION_Y", "FRAME"]].copy()
                    for b_targets in range(int(bspots["TRACK_ID"].max())):
                        bmax = bspots["TRACK_ID"].max()
                        print("Splicing together target " + str(b_targets) + " from a max of " + str(bmax))
                        """ For every b-track, see if there is an intersecting apoptotic track
                        b_checker takes all of one track and looks backwards from the last frame to the first.
                        This should create target cell tracks that are end capped with an apoptotic event."""
                        b_checker = bspots.loc[bspots['TRACK_ID'] == float(b_targets)].copy()
                        b_checker.sort_values(by=['FRAME'], ascending=False, inplace=True)
                        """ If safety = 0 no b-track/a-track overlap has been found yet
                        If safety = 1 an overlap was found on the concurrent iteration of the for loop
                        If safety = 2 an overlap was found on this b-track in a previous iteration of the for loop """
                        safety = 0
                        for cc in range(int(b_checker.shape[0])):
                            """ hits is the array that the quadtree feeds """
                            hits = []
                            tar_x = float(b_checker.iloc[cc]["POSITION_X"])
                            tar_y = float(b_checker.iloc[cc]["POSITION_Y"])
                            center = (tar_x, tar_y)
                            """ Feed the hits array with """
                            qtree.query_radius(center, radmin, hits)
                            for l in hits:
                                if safety == 1:
                                    break
                                else:
                                    """ Because the b-tracks are sorted in descending order by timepoint, 
                                    this is the latest b-spot to overlap with this a-spot"""
                                    bpoint = Point(float(b_checker.iloc[cc]["POSITION_X"])
                                                   , float(b_checker.iloc[cc]["POSITION_Y"])
                                                   , [l.payload[0], l.payload[1]]
                                                   )
                                    qtree.insert(bpoint)
                                    safety = 1
                                    break
                            if safety == 2:
                                """ feed everything on this b-track upstream of the original connection"""
                                bpoint = Point(float(b_checker.iloc[cc]["POSITION_X"])
                                               , float(b_checker.iloc[cc]["POSITION_Y"])
                                               , [l.payload[0], l.payload[1]]
                                               )
                                qtree.insert(bpoint)
                                continue
                            elif safety == 1:
                                safety = safety + 1
                                continue
                            else:
                                continue

                    """ Create several DataFrames (and a list) that we will be adding to throughout the analysis """
                    analysis_sheet_simple = {"NK_ID": [], "Target Kills": [], "NK death as well?": []}
                    analysis_sheet_simple = pd.DataFrame(analysis_sheet_simple)
                    analysis_sheet_detailed = {"NK_ID": [], "Dead_Target_ID": [], "NK Frame": [],
                                               "Target Frame": []
                        , "NK_X": [], "NK_Y": [], "TAR_X": [], "TAR_Y": []}
                    analysis_sheet_detailed = pd.DataFrame(analysis_sheet_detailed)
                    deadNK = []
                    checker = []

                    x = int(spots["TRACK_ID"].max())

                    print(f"For this image set we are parsing {str(x)} NK cell tracks against {str(
                        int(cspots["TRACK_ID"].max()))} apoptotic cells")

                    """ Starting a new NK cell """
                    for z in range(x + 1):
                        print(f"Beginning NK cell {z} of {x}")
                        """ Reset the kill tally for this fresh NK cell to zero """
                        """ diditdie is a variable that tracks if an NK cell with a certain ID went apoptotic 
                        during the experiment """
                        kill_tally = 0
                        diditdie = 0
                        death = 0
                        """ wipe the checker for every cell? Ie, can multiple NK cells be awarded the same kill? """
                        if checkwiper == 1:
                           checker = []
                        working_NK = spots.loc[spots['TRACK_ID'] == float(z)]
                        working_NK = working_NK.reset_index()
                        spots_working_NK = len(working_NK)
                        """ Filter out especially short NK cell tracks """
                        if spots_working_NK <= 4:
                           continue
                        """ debug line """
                        # print(spots_working_NK)
                        for a in range(spots_working_NK):
                            """ Begin checking every point in the timecourse of our apoptotic cell against
                            one point in our selected NK cell's path """
                            hits = []
                            aa = int(a)
                            safety = 0
                            # print(aa)
                            if death == 1:
                                break
                            NK_x = float(working_NK.iloc[aa]["POSITION_X"])
                            NK_y = float(working_NK.iloc[aa]["POSITION_Y"])
                            center = (NK_x, NK_y)
                            qtree.query_radius(center, radmax, hits)
                            for l in hits:
                                for r in deadNK:
                                    if r == int(l.payload[0]):
                                        safety = 1
                                        break
                                for p in checker:
                                    if p == int(l.payload[0]):
                                        safety = 1
                                        continue
                                checker.append(int(l.payload[0]))
                                if int(l.payload[1]) == working_NK.iloc[aa]["FRAME"] and abs(
                                       l.x - NK_x) <= radmin and abs(NK_y - l.y) <= radmin:
                                    deadNK.append(int(l.payload[0]))
                                    diditdie = 1
                                    death = 1
                                    break
                                elif safety == 1 or int(l.payload[1]) <= working_NK.iloc[aa]["FRAME"]:
                                  break
                                else:
                                    kill_tally = kill_tally + 1
                                    print(f"Kill {kill_tally} for this NK cell")
                                    analysis_sheet_detailed.loc[len(analysis_sheet_detailed.index)] = [z,
                                                                                                       int(l.payload[0]),
                                                                                                       working_NK.iloc[
                                                                                                           aa]["FRAME"],
                                                                                                           int(l.payload[
                                                                                                                   1]),
                                                                                                       NK_x, NK_y, l.x,
                                                                                                       l.y
                                                                                                       ]

                        analysis_sheet_simple.loc[len(analysis_sheet_simple.index)] = [z, kill_tally, diditdie]

                    """ Remove dead NK cells from the kill tallies for this frame """
                    # for s in deadNK:
                    #    analysis_sheet_detailed = analysis_sheet_detailed.loc[
                    #    analysis_sheet_detailed["Dead_Target_ID"] != s]

                    """" Save the analysis sheets for this frame """
                    analysis_sheet_detailed.to_csv("track_comparison_detailed.csv")
                    analysis_sheet_simple.to_csv("track_comparison_simple.csv")


def mito_sampler(directory, settings = None):
    """This function takes the results of the serial killing analysis and samples the mitochondria intensity
        of the NK cells before and after they kill a target cell. It does this by looking at the NK cell ID and
        the NK cell frame in the analysis sheet, then looking for the apoptotic cell ID and the apoptotic cell frame.
        It then looks for the NK cell ID in the spots file, and takes the channel 2 (mitochondria) intensity at the
        NK cell frame and the apoptotic cell frame. Finally, it puts these values into a new dataframe with the NK cell ID
        and before/after tags. It does this for every NK cell in the analysis sheet.
        The directory variable is the root directory where the files are located.
        The settings variable, if provided, is a pandas dataframe that contains the settings for the experiment.
        If a settings variable is not provided, the function will look for a settings.csv file in the current directory."""

    import pandas as pd
    from QuadTree import Point, Rect, QuadTree
    import os
    import time

    """ First for loop sets the row and range of rows """
    well_array = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
    array_well = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H"}
    if settings is None:
        settings = pd.read_csv(os.path.join(directory, "settings.csv"))
    for q in range(well_array[settings.iloc[0]['Start Row']], well_array[settings.iloc[0]['Stop Row']] + 1):
        wellcol = array_well[q]
        for x in range(int(settings.iloc[0]['Start Well']), int(settings.iloc[0]['Stop Well']) + 1):
                x_str = f"0{x}" if x < 10 else str(x)
                for y in range(int(settings.iloc[0]['Frames'])):
                    yy = y + 1
                    yy = str(yy)
                    source = os.path.join(directory, "Resorted", wellcol + x_str, "s" + yy, "results")
                    os.chdir(source)
                    print(f"Loading from {source}")
                    try:
                        NK_killers = pd.read_csv("track_comparison_detailed.csv")
                    except:
                        print(f"Error: track analysis in sample {wellcol+x_str}/s{yy} not found")
                        break
                    try:
                        """Pandas gets really unhappy if you don't assign an object class to every column"""
                        spots = pd.read_csv("w2-mask_trackerv2-spots.csv", skiprows=[1, 2, 3],
                                            dtype={'LABEL': str, 'ID': str, 'TRACK_ID': float, 'QUALITY': float,
                                                   'POSITION_X': float, 'POSITION_Y': float, 'POSITION_Z': float,
                                                   'POSITION_T': float, 'FRAME': float, 'RADIUS': float,
                                                   'VISIBILITY': float,
                                                   'MANUAL_SPOT_COLOR': float, 'MEAN_INTENSITY_CH1': float,
                                                   'MEDIAN_INTENSITY_CH1': float, 'MIN_INTENSITY_CH1': float,
                                                   'MAX_INTENSITY_CH1': float, 'TOTAL_INTENSITY_CH1': float,
                                                   'STD_INTENSITY_CH1': float, 'MEAN_INTENSITY_CH2': float,
                                                   'MEDIAN_INTENSITY_CH2': float, 'MIN_INTENSITY_CH2': float,
                                                   'MAX_INTENSITY_CH2': float, 'TOTAL_INTENSITY_CH2': float,
                                                   'STD_INTENSITY_CH2': float, 'MEAN_INTENSITY_CH3': float,
                                                   'MEDIAN_INTENSITY_CH3': float, 'MIN_INTENSITY_CH3': float,
                                                   'MAX_INTENSITY_CH3': float, 'TOTAL_INTENSITY_CH3': float,
                                                   'STD_INTENSITY_CH3': float, 'MEAN_INTENSITY_CH4': float,
                                                   'MEDIAN_INTENSITY_CH4': float, 'MIN_INTENSITY_CH4': float,
                                                   'MAX_INTENSITY_CH4': float, 'TOTAL_INTENSITY_CH4': float,
                                                   'STD_INTENSITY_CH4': float, 'CONTRAST_CH1': float, 'SNR_CH1': float,
                                                   'CONTRAST_CH2': float, 'SNR_CH2': float, 'CONTRAST_CH3': float,
                                                   'SNR_CH3': float, 'CONTRAST_CH4': float, 'SNR_CH4': float})
                    except:
                        print(f"Error: Spot file from sample {wellcol+x_str}/s{yy} not found")
                        print("You should not be seeing this error unless something got moved.")
                        break

                    """ Look for the NK cell tracks in the analysis sheet, take the NK cell ID and the NK cell frame.
                    Then look for the apoptotic cell ID and the apoptotic cell frame. Look for the NK cell ID in the
                    spots file, and take the channel 2 (mitochondria) intensity at the NK cell frame and the apoptotic
                    cell frame. Finally, put these values into a new dataframe with the NK cell ID and before/after
                    tags. Do this for every NK cell in the analysis sheet. """
                    analysis_sheet_mito = {"NK_ID": [], "Before": [], "After": []}
                    analysis_sheet_mito = pd.DataFrame(analysis_sheet_mito)
                    for i in range(len(NK_killers)):
                        NK_ID = NK_killers.iloc[i]["NK_ID"]
                        NK_frame = NK_killers.iloc[i]["NK Frame"]
                        target_frame = NK_killers.iloc[i]["Target Frame"]
                        try:
                            """ Take the NK cell spots that equal the NK cell ID being queried"""
                            print(f"Processing NK cell {NK_ID} from sample {wellcol+x_str}/s{yy}")
                            working_NK = spots.loc[spots['TRACK_ID'] == float(NK_ID)]
                            # print(working_NK)
                            """ Take the frame the NK cell engaged the target cell"""
                            engaged_NK = working_NK.loc[working_NK['FRAME'] == float(NK_frame)]
                            # print(working_NK)
                            working_target = working_NK.loc[working_NK['FRAME'] == float(target_frame)]
                            # print(working_target)
                            analysis_sheet_mito.loc[len(analysis_sheet_mito.index)] = [NK_ID,
                                                                                       engaged_NK.iloc[0][
                                                                                           "TOTAL_INTENSITY_CH2"],
                                                                                       working_target.iloc[0][
                                                                                           "TOTAL_INTENSITY_CH2"]]
                        except:
                            print(f"Error: sample {wellcol+x_str}/s{yy} does not have this track")
                            continue
                    analysis_sheet_mito.to_csv("mito_analysis.csv")


def mover(origin, destination, file_string, settings=None):
    import os
    import shutil
    # Get the current working directory
    for x in range(2, 6):
        for y in range(1, 5):
            shutil.copy(os.path.join(origin, f"D0{x}\\s{y}\\01_Merge.tif"),
                        os.path.join(destination, f"D0{x}\\s{y}\\01_Merge.tif"))


def stitcher(directory, ij=None, settings=None, args=None):
    import jpype
    import gc
    import os
    import pandas as pd
    import shutil
    well_array = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
    array_well = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H"}
    if os.path.exists(os.path.join(directory, "Combination")):
        pass
    else:
        os.makedirs(os.path.join(directory, "Combination"))
    if settings is None:
        settings = pd.read_csv(os.path.join(directory, "settings.csv"))
    if args is None:
        """Assumes a square grid of tiles, so the x and y values are the same. If this is not the case, there will
        be an error, and you will need to manually input the x and y values by providing them in the args variable"""
        args = {"source": directory, "destination": os.path.join(directory, "Combination"),
                "x": str(int(settings.iloc[0]['Frames']) / 2),
                "y": str(int(settings.iloc[0]['Frames']) / 2)}
    if ij is None:
        import imagej
        ij = imagej.init('sc.fiji:fiji', mode='interactive')
    for q in range(well_array[settings.iloc[0]['Start Row']], well_array[settings.iloc[0]['Stop Row']] + 1):
        wellcol = array_well[q]
        for x in range(int(settings.iloc[0]['Start Well']), int(settings.iloc[0]['Stop Well']) + 1):
            x_str = f"0{x}" if x < 10 else str(x)
            print(f"Processing well {wellcol + x_str}")
            for y in range(int(settings.iloc[0]['Frames'])):
                yy = y + 1
                yy = str(yy)
                fileloc = os.path.join(directory, "Resorted", wellcol + x_str, "s" + yy)
                shutil.copy(os.path.join(fileloc, "01_Merge.tif"),
                            os.path.join(directory, f"s0{yy}.tif"))
            logget = ij.py.run_macro(Stitcher, args)
            print(logget.getOutput("returner"))
            jpype.java.lang.Runtime.getRuntime().gc()
            gc.collect()
            shutil.move(os.path.join(directory, "Stitched.tif"),
                        os.path.join(directory, "Resorted", wellcol + x_str, "Stitched.tif"))
            for y in range(int(settings.iloc[0]['Frames'])):
                yy = y + 1
                yy = str(yy)
                try:
                    os.unlink(os.path.join(directory, "s0" + yy + ".tif"))
                except Exception as e:
                    print(f'Failed to delete {os.path.join(directory, "s0" + yy + ".tif")}. Reason: {e}')


def deprecated_trackloader(source, radmin):
    import os
    import pandas as pd
    os.chdir(source)
    try:
        """Pandas gets really unhappy if you don't assign an object class to every column"""
        spots = pd.read_csv("w2_trackerv2-spots.csv", skiprows=[1, 2, 3],
                            dtype={'LABEL': str, 'ID': str, 'TRACK_ID': float, 'QUALITY': float,
                                   'POSITION_X': float, 'POSITION_Y': float, 'POSITION_Z': float,
                                   'POSITION_T': float, 'FRAME': float, 'RADIUS': float, 'VISIBILITY': float,
                                   'MANUAL_SPOT_COLOR': float, 'MEAN_INTENSITY_CH1': float,
                                   'MEDIAN_INTENSITY_CH1': float, 'MIN_INTENSITY_CH1': float,
                                   'MAX_INTENSITY_CH1': float, 'TOTAL_INTENSITY_CH1': float,
                                   'STD_INTENSITY_CH1': float, 'MEAN_INTENSITY_CH2': float,
                                   'MEDIAN_INTENSITY_CH2': float, 'MIN_INTENSITY_CH2': float,
                                   'MAX_INTENSITY_CH2': float, 'TOTAL_INTENSITY_CH2': float,
                                   'STD_INTENSITY_CH2': float, 'MEAN_INTENSITY_CH3': float,
                                   'MEDIAN_INTENSITY_CH3': float, 'MIN_INTENSITY_CH3': float,
                                   'MAX_INTENSITY_CH3': float, 'TOTAL_INTENSITY_CH3': float,
                                   'STD_INTENSITY_CH3': float, 'MEAN_INTENSITY_CH4': float,
                                   'MEDIAN_INTENSITY_CH4': float, 'MIN_INTENSITY_CH4': float,
                                   'MAX_INTENSITY_CH4': float, 'TOTAL_INTENSITY_CH4': float,
                                   'STD_INTENSITY_CH4': float, 'CONTRAST_CH1': float, 'SNR_CH1': float,
                                   'CONTRAST_CH2': float, 'SNR_CH2': float, 'CONTRAST_CH3': float,
                                   'SNR_CH3': float, 'CONTRAST_CH4': float, 'SNR_CH4': float})
        spots.sort_values(by=['TRACK_ID', 'FRAME'], inplace=True)
    except:
        print("Error: correct csv file for NK cell paths not found")
        spots = None

    try:
        aspots = pd.read_csv("w4-mask_trackerv2-spots.csv", skiprows=[1, 2, 3],
                             dtype={'LABEL': str, 'ID': str, 'TRACK_ID': float, 'QUALITY': float,
                                    'POSITION_X': float, 'POSITION_Y': float, 'POSITION_Z': float,
                                    'POSITION_T': float, 'FRAME': float, 'RADIUS': float, 'VISIBILITY': float,
                                    'MANUAL_SPOT_COLOR': float, 'MEAN_INTENSITY_CH1': float,
                                    'MEDIAN_INTENSITY_CH1': float, 'MIN_INTENSITY_CH1': float,
                                    'MAX_INTENSITY_CH1': float, 'TOTAL_INTENSITY_CH1': float,
                                    'STD_INTENSITY_CH1': float, 'MEAN_INTENSITY_CH2': float,
                                    'MEDIAN_INTENSITY_CH2': float, 'MIN_INTENSITY_CH2': float,
                                    'MAX_INTENSITY_CH2': float, 'TOTAL_INTENSITY_CH2': float,
                                    'STD_INTENSITY_CH2': float, 'MEAN_INTENSITY_CH3': float,
                                    'MEDIAN_INTENSITY_CH3': float, 'MIN_INTENSITY_CH3': float,
                                    'MAX_INTENSITY_CH3': float, 'TOTAL_INTENSITY_CH3': float,
                                    'STD_INTENSITY_CH3': float, 'MEAN_INTENSITY_CH4': float,
                                    'MEDIAN_INTENSITY_CH4': float, 'MIN_INTENSITY_CH4': float,
                                    'MAX_INTENSITY_CH4': float, 'TOTAL_INTENSITY_CH4': float,
                                    'STD_INTENSITY_CH4': float, 'CONTRAST_CH1': float, 'SNR_CH1': float,
                                    'CONTRAST_CH2': float, 'SNR_CH2': float, 'CONTRAST_CH3': float,
                                    'SNR_CH3': float, 'CONTRAST_CH4': float, 'SNR_CH4': float})
        aspots.sort_values(by=['TRACK_ID', 'FRAME'], inplace=True)
    except:
        print("Error: correct csv file for apoptotic cells not found.")
        aspots = None

    try:
        bspots = pd.read_csv("w3-mask_trackerv2-spots.csv", skiprows=[1, 2, 3],
                             dtype={'LABEL': str, 'ID': str, 'TRACK_ID': float, 'QUALITY': float,
                                    'POSITION_X': float, 'POSITION_Y': float, 'POSITION_Z': float,
                                    'POSITION_T': float, 'FRAME': float, 'RADIUS': float, 'VISIBILITY': float,
                                    'MANUAL_SPOT_COLOR': float, 'MEAN_INTENSITY_CH1': float,
                                    'MEDIAN_INTENSITY_CH1': float, 'MIN_INTENSITY_CH1': float,
                                    'MAX_INTENSITY_CH1': float, 'TOTAL_INTENSITY_CH1': float,
                                    'STD_INTENSITY_CH1': float, 'MEAN_INTENSITY_CH2': float,
                                    'MEDIAN_INTENSITY_CH2': float, 'MIN_INTENSITY_CH2': float,
                                    'MAX_INTENSITY_CH2': float, 'TOTAL_INTENSITY_CH2': float,
                                    'STD_INTENSITY_CH2': float, 'MEAN_INTENSITY_CH3': float,
                                    'MEDIAN_INTENSITY_CH3': float, 'MIN_INTENSITY_CH3': float,
                                    'MAX_INTENSITY_CH3': float, 'TOTAL_INTENSITY_CH3': float,
                                    'STD_INTENSITY_CH3': float, 'MEAN_INTENSITY_CH4': float,
                                    'MEDIAN_INTENSITY_CH4': float, 'MIN_INTENSITY_CH4': float,
                                    'MAX_INTENSITY_CH4': float, 'TOTAL_INTENSITY_CH4': float,
                                    'STD_INTENSITY_CH4': float, 'CONTRAST_CH1': float, 'SNR_CH1': float,
                                    'CONTRAST_CH2': float, 'SNR_CH2': float, 'CONTRAST_CH3': float,
                                    'SNR_CH3': float, 'CONTRAST_CH4': float, 'SNR_CH4': float})
        bspots.sort_values(by=['TRACK_ID', 'FRAME'], inplace=True)

    except:
        print("Error: correct csv file for all cell paths not found.")
        bspots = None
    cspots, qtree = tracker_part1(spots, aspots, bspots, radmin)
    return spots, cspots, qtree


def deprecated_tracker_part1(spots, aspots, bspots, radmin):
    from QuadTree import Point, Rect, QuadTree
    """ Quadtree script derived from Christian Hill's walkthrough on his blog, 
    Learning Scientific Programming with Python; not necessary for the tracking script 
    but speeds the whole thing up considerably """
    import pandas as pd
    print("beginning tracking")
    min_x = float(spots["POSITION_X"].min())
    max_x = float(spots["POSITION_X"].max())
    min_y = float(spots["POSITION_Y"].min())
    max_y = float(spots["POSITION_Y"].max())
    if min_x >= float(aspots["POSITION_X"].min()):
        min_x = float(aspots["POSITION_X"].min())
    if max_x <= float(aspots["POSITION_X"].max()):
        max_x = float(aspots["POSITION_X"].max())
    if min_y >= float(aspots["POSITION_Y"].min()):
        min_y = float(aspots["POSITION_Y"].min())
    if max_y <= float(aspots["POSITION_Y"].max()):
        max_y = float(aspots["POSITION_Y"].max())
    width = max_x - min_x
    height = max_y - min_y
    print("starting to make cspots")
    # print(aspots)
    """ Create cspots, which will have all the apoptotic tracks to start, then splice b-tracks to the
    start of each of them """
    cspots = pd.DataFrame(columns=["TRACK_ID", "POSITION_X", "POSITION_Y", "FRAME"])
    for targets in range(int(aspots["TRACK_ID"].max())):
        print(targets)
        a_narrow = aspots.loc[aspots['TRACK_ID'] == float(targets)]
        a_narrow = a_narrow.loc[a_narrow["FRAME"] == a_narrow["FRAME"].min()]
        cspots.loc[len(cspots.index)] = [a_narrow.iloc[0]["TRACK_ID"]
            , a_narrow.iloc[0]["POSITION_X"]
            , a_narrow.iloc[0]["POSITION_Y"]
            , a_narrow.iloc[0]["FRAME"]
                                         ]

    """ for debugging track splicing: """
    # print(cspots)

    """ seed the quad tree with points """
    apoints: List[Point] = [Point(float(cspots.iloc[row]["POSITION_X"])
                                  , float(cspots.iloc[row]["POSITION_Y"])
                                  , [int(cspots.iloc[row]["TRACK_ID"]), int(cspots.iloc[row]["FRAME"])]
                                  ) for row in range(int(cspots["TRACK_ID"].count()))
                            ]
    domain = Rect((width + min_x) / 2, (height + min_y) / 2, width, height)
    qtree = QuadTree(domain, 100)
    for point in apoints:
        qtree.insert(point)

    """ Splice together b-tracks to apoptotic tracks by running every b-track against the quadtree """
    print("beginning splicing")
    bspots = bspots[["TRACK_ID", "POSITION_X", "POSITION_Y", "FRAME"]].copy()
    if isinstance(bspots, pd.DataFrame):
        print("bspots is a dataframe")
    else:
        print("bspots is not a dataframe")
    for b_targets in range(int(bspots["TRACK_ID"].max())):
        bmax = bspots["TRACK_ID"].max()
        print("Splicing together target " + str(b_targets) + " from a max of " + str(bmax))
        """ For every b-track, see if there is an intersecting apoptotic track
        b_checker takes all of one track and looks backwards from the last frame to the first """
        b_checker = bspots.loc[bspots['TRACK_ID'] == float(b_targets)].copy()
        b_checker.sort_values(by=['FRAME'], ascending=False, inplace=True)
        """ If safety = 0 no b-track/a-track overlap has been found yet
        If safety = 1 an overlap was found on the concurrent iteration of the for loop
        If safety = 2 an overlap was found on this b-track in a previous iteration of the for loop """
        safety = 0
        for cc in range(int(b_checker.shape[0])):
            """ hits is the array that the quadtree feeds """
            hits = []
            tar_x = float(b_checker.iloc[cc]["POSITION_X"])
            tar_y = float(b_checker.iloc[cc]["POSITION_Y"])
            center = (tar_x, tar_y)
            """ Feed the hits array with """
            qtree.query_radius(center, radmin, hits)
            for l in hits:
                if safety == 1:
                    break
                else:
                    bpoint = Point(float(b_checker.iloc[cc]["POSITION_X"])
                                   , float(b_checker.iloc[cc]["POSITION_Y"])
                                   , [l.payload[0], l.payload[1]]
                                   )
                    qtree.insert(bpoint)
                    safety = 1
                    break
            if safety == 2:
                bpoint = Point(float(b_checker.iloc[cc]["POSITION_X"])
                               , float(b_checker.iloc[cc]["POSITION_Y"])
                               , [l.payload[0], l.payload[1]]
                               )
                qtree.insert(bpoint)
                continue
            elif safety == 1:
                safety = safety + 1
                continue
            else:
                continue
    return cspots, qtree


def deprecated_tracker_part2(spots, cspots, qtree, analysis_sheet_summary, radmin, radmax, checkwiper, currow, curwell,
                      curframe):
    from QuadTree import Point, Rect, QuadTree
    import pandas as pd
    # Create several DataFrames (and a list) that we will be adding to throughout the analysis
    analysis_sheet_simple = pd.DataFrame(columns=["NK_ID", "Target Kills", "NK death as well?"])
    analysis_sheet_detailed = pd.DataFrame(
        columns=["NK_ID", "Dead_Target_ID", "NK Frame", "Target Frame", "NK_X", "NK_Y", "TAR_X",
                 "TAR_Y"])
    analysis_sheet_revised = pd.DataFrame(columns=["NK_ID", "Target Kills"])
    deadNK = []
    # Defining some starting variables. Each NK cell is assigned an ID from zero up,
    # x takes the highest value.
    x = int(spots["TRACK_ID"].max())
    # print(x)
    print("For this image set we are parsing " + str(x) + " NK cell tracks against " + str(
        int(cspots["TRACK_ID"].max())) + " apoptotic cells")
    print("beginning kill tracking")
    # for-loop goes through every NK cell ID
    checker = []
    for z in range(x + 1):
        print(f"Beginning NK cell {z} of {x}")
        # Starting a new NK cell
        # print("Calculating kills for NK cell number " + str(z))
        # Reset the kill tally for this fresh NK cell to zero
        # diditdie is a variable that tracks if an NK cell with a certain ID went apoptotic during the experiment
        kill_tally = 0
        diditdie = 0
        death = 0
        # wipe the checker for every cell? Ie, can multiple NK cells be awarded the same kill?
        if checkwiper == 1:
            checker = []
        working_NK = spots.loc[spots['TRACK_ID'] == float(z)]
        working_NK = working_NK.reset_index()
        spots_working_NK = len(working_NK)
        # spots_working_NK = spots_working_NK-1
        # print(spots_working_NK)

        for a in range(spots_working_NK):
            # Begin checking every point in the timecourse of our apoptotic cell against
            # one point in our selected NK cell's path
            hits = []
            aa = int(a)
            safety = 0
            # print(aa)
            if death == 1:
                # This death check ensures NK cells can't be awarded kills after they die
                break
            NK_x = float(working_NK.iloc[aa]["POSITION_X"])
            NK_y = float(working_NK.iloc[aa]["POSITION_Y"])
            center = (NK_x, NK_y)
            qtree.query_radius(center, radmax, hits)
            for l in hits:
                for r in deadNK:
                    if r == int(l.payload[0]):
                        safety = 1
                        break
                for p in checker:
                    if p == int(l.payload[0]):
                        safety = 1
                        continue
                checker.append(int(l.payload[0]))
                if int(l.payload[1]) == working_NK.iloc[aa]["FRAME"] and abs(l.x - NK_x) <= radmin and abs(
                        l.y - NK_y) <= radmin:
                    deadNK.append(int(l.payload[0]))
                    print("Dead NK cell")
                    diditdie = 1
                    death = 1
                    break
                elif safety == 1 or int(l.payload[1]) <= working_NK.iloc[aa]["FRAME"]:
                    break
                else:
                    kill_tally = kill_tally + 1
                    print(f"Kill {kill_tally} for this NK cell")
                    analysis_sheet_detailed.loc[len(analysis_sheet_detailed.index)] = [z, int(l.payload[0]),
                                                                                       working_NK.iloc[aa]["FRAME"],
                                                                                       int(l.payload[1]), NK_x, NK_y,
                                                                                       l.x, l.y
                                                                                       ]
        analysis_sheet_simple.loc[len(analysis_sheet_simple.index)] = [z, kill_tally, diditdie]
        # Remove dead NK cells from the kill tallies
        for s in deadNK:
            analysis_sheet_detailed = analysis_sheet_detailed.loc[analysis_sheet_detailed["Dead_Target_ID"] != s]

        # Make a new simple analysis sheet (called revised) that is the same format as the simple analysis sheet,
        # but has properly deducted the dead NK cells from the tallies
        try:
            for t in range(int(analysis_sheet_detailed["NK_ID"].max()) + 1):
                df1 = analysis_sheet_detailed.loc[analysis_sheet_detailed["NK_ID"] == t]
                df2 = df1["NK_ID"].count()
                analysis_sheet_revised.loc[len(analysis_sheet_revised.index)] = [t, df2]
                whoops = 0
        except:
            print("No kills recorded. Is this a bug test?")
            whoops = 1
        finally:
            """Export all the data to csv files"""
            analysis_sheet_detailed.to_csv("track_comparison_detailed.csv")
            analysis_sheet_revised.to_csv("track_comparison_revised.csv")
            analysis_sheet_simple.to_csv("track_comparison_simple.csv")
            zerokills = float(len(analysis_sheet_simple[analysis_sheet_simple["Target Kills"] == 0]))
            onekill = float(len(analysis_sheet_revised[analysis_sheet_revised["Target Kills"] == 1]))
            serialkills = float(len(analysis_sheet_revised[analysis_sheet_revised["Target Kills"] >= 1]))
            # zerokills = analysis_sheet_simple.loc[analysis_sheet_simple["Target Kills"] == 0]
            # onekill = analysis_sheet_revised.loc[analysis_sheet_revised["Target Kills"] == 1]
            # serialkills = analysis_sheet_revised.loc[analysis_sheet_revised["Target Kills"] >= 1]
            try:
                serialratio = serialkills / onekill
            except:
                serialratio = 0
            sample = str(currow) + str(curwell) + "\\s" + str(curframe)
            analysis_sheet_summary.loc[len(analysis_sheet_summary.index)] = [sample, zerokills, onekill, serialkills
                , serialratio]
    return analysis_sheet_summary


def deprecated_masker_settings():
    option1 = "NULL"
    while option1 != "exit":
        print("At some point this will be interactive. For now, please"
              " input the threshold values for each channel.")
        w2 = input("Channel 2 (red) Threshold: ")
        w3 = input("Channel 3 (blue) Threshold: ")
        w4 = input("Channel 4 (green) Threshold: ")
        option1 = "exit"
    w2 = int(w2)
    w3 = int(w3)
    w4 = int(w4)
    return w2, w3, w4


def deprecated_auto_masker_settings(directory, ij=None, settings=None):
    """This function sets the thresholds for the masks based on the settings provided.
        The directory variable is the root directory where the files are located.
        The ij variable is the ImageJ instance, if provided. Otherwise, it will boot FIJI.
        The settings variable, if provided, is a pandas dataframe that contains the settings for the experiment.
        If a settings variable is not provided, the function will look for a settings.csv file in the current directory.
        """
    if ij is None:
        import imagej
        ij = imagej.init('sc.fiji:fiji', headless=False)
    if settings is None:
        import os
        import pandas as pd
        settings = pd.read_csv(os.path.join(directory, "settings.csv"))
        wellquery = []
    for channel in range(2, int(settings.iloc[0]['Channels'])):
        well = input(f"Please input the threshold values for channel {channel}: ")

    return settings


def deprecated_masker(ij=None, args=None):
    import jpype
    import gc

    ij.py.run_macro(Corrections, args)
    jpype.java.lang.Runtime.getRuntime().gc()
    gc.collect()
    measurements = ij.py.run_macro(Masker, args)
    w2measure = measurements.getOutput("w2measure")
    w3measure = measurements.getOutput("w3measure")
    w4measure = measurements.getOutput("w4measure")
    w2measure = str(w2measure)
    w3measure = str(w3measure)
    w4measure = str(w4measure)
    w2measure = w2measure.split(" ")
    print(w2measure)
    w3measure = w3measure.split(" ")
    print(w3measure)
    w4measure = w4measure.split(" ")
    print(w4measure)
    return w2measure, w3measure, w4measure


AutoThresher = """
#@String source
#@output String w1
#@output String w2
#@output String w3
#@output String w4
open(source + "01_Merge.tif");
run("Split Channels");
selectWindow("C1-01_Merge.tif");
run("Auto Threshold", "method=Default white");
w1 = getThrehold(bottomValue);
selectWindow("C2-01_Merge.tif");
run("Auto Threshold", "method=Default white");
w2 = getThrehold(bottomValue);
selectWindow("C3-01_Merge.tif");
run("Auto Threshold", "method=Default white");
w3 = getThrehold(bottomValue);
selectWindow("C4-01_Merge.tif");
run("Auto Threshold", "method=Default white");
w4 = getThrehold(bottomValue);
close("*");
"""

StackMaster = """
#@String source
#@Integer channels
// Supports up to 5 channels and tries to make a logical color assignment
for (i = 1; i <= channels; i++) {
    File.openSequence(source, " filter=_w" + i);
    saveAs("Tiff", source + "/w"+i+".tif");
if channels == 3: {
    run("Merge Channels...", "c2=w3.tif c3=w2.tif c4=w1 create");
}
else if channels == 4: {
    run("Merge Channels...", "c1=w2.tif c2=w4.tif c3=w3.tif c4=w1.tif create");
}
else if channels == 5: {
    run("Merge Channels...", "c1=w2.tif c2=w4.tif c3=w3.tif c4=w1.tif c5=w5.tif create");
}
saveAs("Tiff", source + "/01_Merge.tif");
close("*");
"""

Stitcher = """
#@String source
#@String destination
#@String x
#@String y
#@Integer channels
#@Integer frames
#@output String returner
for (i = 1; i <= frames; i++) {
    open(source + "/s0"+i+".tif");
    selectWindow("s0"+i+".tif");
    run("Re-order Hyperstack ...", "channels=[Channels (c)] slices=[Frames (t)] frames=[Slices (z)]");
    saveAs("Tiff", source + "/s0"+i+".tif");
    getDimensions(width1, height1, channels1, slices1, frames1);
    print("Frames: " + frames1);
    close();
}
run("Grid/Collection stitching", "type=[Grid: row-by-row] order=[Right & Down                ] grid_size_x="+x+" grid_size_y="+y+" tile_overlap=10 first_file_index_i=1 directory="+source+" file_names=s{ii}.tif output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap use_virtual_input_images computation_parameters=[Save memory (but be slower)] image_output=[Write to disk] output_directory="+destination);
for (i = 1; i <= channels; i++) {
    File.openSequence(destination, "virtual filter=c"+i);
    rename("c"+i);
}
if channels == 3: {
    run("Merge Channels...", "c2=c2 c3=c3 c4=c4");
}
else if channels == 4: {
    run("Merge Channels...", "c1=c1 c2=c2 c3=c3 c4=c3 create");
}
else if channels == 5: {
    run("Merge Channels...", "c1=c1 c2=c2 c3=c3 c4=c4 c5=c5create");
}
saveAs("Tiff", source + "/Stitched.tif");
getDimensions(width2, height2, channels2, slices2, frames2);
if (width1 != width2 || height1 != height2) {
    returner = "Successful stitching";
} else {
    returner = "Stitching failed";
}
"""

Corrections = """
#@String source
//Open the Composite for this well/frame
open(source + "/01_Merge.tif");
run("Re-order Hyperstack ...", "channels=[Channels (c)] slices=[Frames (t)] frames=[Slices (z)]");
run("Correct 3D drift", "channel=4 correct sub_pixel only=0 lowest=1 highest=1 max_shift_x=50 max_shift_y=50 max_shift_z=10");
selectWindow("registered time points");
saveAs("Tiff", source + "/results/corrected-merge.tif");
close("*");
run("Collect Garbage");
"""

Masker = """
#@String source
#@Integer timepoints
#@output String w2measure
#@output String w3measure
#@output String w4measure
//open(source + "/01_Merge.tif");
open(source + "/results/corrected-merge.tif");
//Make Masks for data analysis
selectWindow("corrected-merge.tif");
run("Duplicate...", "duplicate");
selectWindow("corrected-merge-1.tif");
run("Split Channels");
selectWindow("C4-corrected-merge-1.tif");
saveAs("Tiff", source + "/results/w1.tif");
close();
selectWindow("C2-corrected-merge-1.tif");
run("Subtract Background...", "rolling=10 stack");
run("Auto Threshold", "method=RenyiEntropy white stack");
saveAs("Tiff", source + "/results/w2-mask.tif");
//Analyize the NK cells
w2measure = "";
selectWindow("w2-mask.tif");
for (t =1; t<=timepoints; t++) {
    run("Create Selection");
    area = getValue("Area");
    w2measure = w2measure + area + " ";
    run("Next Slice [>]");
};
selectWindow("w2-mask.tif");
close();
//End Analyze NK cells
selectWindow("C3-corrected-merge-1.tif");
run("Subtract Background...", "rolling=50 stack");
run("Auto Threshold", "method=RenyiEntropy white stack");
saveAs("Tiff", source + "/results/w3-mask.tif");
//Analyize all cells
w3measure = "";
selectWindow("w3-mask.tif");
for (t =1; t<=timepoints; t++) {
    run("Create Selection");
    area = getValue("Area");
    w3measure = w3measure + area + " ";
    //run("Measure");
    run("Next Slice [>]");
};
//selectWindow("Results");
//saveAs("Results", source + "w3-masks.csv");
//close("Results");
selectWindow("w3-mask.tif");
close();
run("Collect Garbage");
//End Analyize all cells
selectWindow("C2-corrected-merge-1.tif");
run("Auto Threshold", "method=RenyiEntropy white stack");
setOption("BlackBackground", true);
run("Convert to Mask", "method=Default background=Dark black");
saveAs("Tiff", source + "/results/w4-mask.tif");
//Analyize apoptotic cells
w4measure = "";
selectWindow("w4-mask.tif");
for (t =1; t<=timepoints; t++) {
    run("Create Selection");
    area = getValue("Area");
    w4measure = w4measure + area + " ";
    //run("Measure");
    run("Next Slice [>]");
};

//selectWindow("Results");
//saveAs("Results", source + "w2-masks.csv");
//close("Results");
selectWindow("w4-mask.tif");
close();
//selectWindow("C5-corrected-merge-1.tif");
//saveAs("Tiff", source + "/results/w5.tif");
//close();
run("Collect Garbage");
//End analyize apoptotic cells
run("Collect Garbage");
close("*");
run("Collect Garbage");
"""

macro = """
#@Integer timepoints
@output String w2measure
var w2measure = newArray(97);
for (t =1; t<timepoints; t++) {
    w2measure[t] = t;
};
"""

opener = """
#@String x
#@String source
open(source + "/" + x + ".tif");

"""

opener2 = """
#@String x
#@String source
open(source + "/" + x + ".tif");
open(source + "/w5.tif");
run("8-bit");
run("Merge Channels...", "c1="+x+".tif c5=w5.tif create");
rename("w2-mask.tif");

"""

closer = """
run("Collect Garbage");
close("*");
run("Collect Garbage");
run("Collect Garbage");
run("Collect Garbage");
run("Collect Garbage");
run("Collect Garbage");
run("Collect Garbage");
run("Collect Garbage");
run("Collect Garbage");
run("Collect Garbage");
run("Collect Garbage");
"""

Tracking = """ 
#@String x
#@String source
import sys
import os
import csv
os.chdir(source)
from ij import IJ
from ij import WindowManager
from java.io import File

from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import LogDetectorFactory
from fiji.plugin.trackmate.tracking.jaqaman import SparseLAPTrackerFactory
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettingsIO
from fiji.plugin.trackmate.gui.displaysettings.DisplaySettings import TrackMateObject
from fiji.plugin.trackmate.features.track import TrackIndexAnalyzer
from fiji.plugin.trackmate.io import TmXmlReader
from fiji.plugin.trackmate.io import TmXmlWriter
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettings
from fiji.plugin.trackmate.visualization.table import TrackTableView
from fiji.plugin.trackmate.visualization.table import AllSpotsTableView

# We have to do the following to avoid errors with UTF8 chars generated in 
# TrackMate that will mess with our Fiji Jython.
reload(sys)
sys.setdefaultencoding('utf-8')

# Get currently selected image
imp = WindowManager.getCurrentImage()
# imp = IJ.openImage('D:/HTSF images 07102024/Resorted/B02/s1/results/w1.tif')
# imp.show()


# Some of the parameters we configure below need to have
# a reference to the model at creation. So we create an
# empty model now.

model = Model()

# Send all messages to ImageJ log window.
model.setLogger(Logger.IJ_LOGGER)

settings = Settings(imp)

# Channel specific parameters for spot detection
if x == "w2-mask":
    rad = 7.0
    qual = 2.0
elif x == "w3-mask":
    rad = 13.0
    qual = 2.0
elif x == "w4-mask":
    rad = 8.0
    qual = 0.7

# Configure detector - We use the Strings for the keys
settings.detectorFactory = LogDetectorFactory()
settings.detectorSettings = {
    'DO_SUBPIXEL_LOCALIZATION' : False,
    'RADIUS' : rad,
    'TARGET_CHANNEL' : 1,
    'THRESHOLD' : qual,
    'DO_MEDIAN_FILTERING' : False,
}  

if x == "w2":
    filter1 = FeatureFilter('MIN_INTENSITY_CH1', 28, True)
    filter3 = FeatureFilter('MEDIAN_INTENSITY_CH1', 12000, True)
    settings.addSpotFilter(filter1)
    settings.addSpotFilter(filter3)

# Configure tracker - We want to allow merges and fusions
settings.trackerFactory = SparseLAPTrackerFactory()
settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
settings.trackerSettings['MAX_FRAME_GAP'] = 2
settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = False
settings.trackerSettings['ALLOW_TRACK_MERGING'] = False
settings.trackerSettings['LINKING_MAX_DISTANCE'] = 60.0
if x == "w3-mask":
    # The targets should not be moving
    settings.trackerSettings['LINKING_MAX_DISTANCE'] = 15.0
if x == "w4-mask":
    # Apoptotic tracks should not be really moving
    settings.trackerSettings['LINKING_MAX_DISTANCE'] = 15.0
settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = 15.0

# Add ALL the feature analyzers known to TrackMate. They will 
# yield numerical features for the results, such as speed, mean intensity etc.
settings.addAllAnalyzers()

# Configure track filters - We want to get rid of the two immobile spots at
# the bottom right of the image. Track displacement must be above 10 pixels.

# if x == "w2-mask":
# filter2 = FeatureFilter('TRACK_DURATION', 3, True)
# settings.addTrackFilter(filter2)
#-------------------
# Instantiate plugin
#-------------------

trackmate = TrackMate(model, settings)

#--------
# Process
#--------

ok = trackmate.checkInput()
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))

ok = trackmate.process()
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))


#----------------
# Display results
#----------------

# A selection.
selectionModel = SelectionModel( model )

# Read the default display settings.
ds = DisplaySettingsIO.readUserDefault()
# Color by tracks.
ds.setTrackColorBy( TrackMateObject.TRACKS, TrackIndexAnalyzer.TRACK_INDEX )
ds.setSpotColorBy( TrackMateObject.TRACKS, TrackIndexAnalyzer.TRACK_INDEX )

displayer =  HyperStackDisplayer( model, selectionModel, imp, ds )
displayer.render()
displayer.refresh()

# Echo results with the logger we set at start:
# model.getLogger().log( str( model ) )


outFile = File(source +"/"+ x +"_trackerv2.xml")   #  usr__savePathFile is a user-inputted variable from the command line
writer = TmXmlWriter(outFile)
writer.appendSettings(settings)
writer.appendModel(model)
writer.writeToFile()
"""

TrackSaver = """
#@String x
#@String source
from fiji.plugin.trackmate.visualization.hyperstack import HyperStackDisplayer
from fiji.plugin.trackmate.io import TmXmlReader
from fiji.plugin.trackmate.io import TmXmlWriter
from fiji.plugin.trackmate.io import CSVExporter
from fiji.plugin.trackmate.visualization.table import TrackTableView
from fiji.plugin.trackmate.action import ExportTracksToXML
from fiji.plugin.trackmate import Logger
from java.io import File
import sys
import os

# We have to do the following to avoid errors with UTF8 chars generated in 
# TrackMate that will mess with our Fiji Jython.
reload(sys)
sys.setdefaultencoding('utf-8')


# This script demonstrates several ways by which TrackMate data
# can be exported to files. Mainly: 1/ to a TrackMate XML file,
# 2/ & 3/ to CSV files, 4/ to a simplified XML file, for linear tracks.


#----------------------------------
# Loading an example tracking data.
#----------------------------------

# For this script to work, you need to edit the path to the XML below.
# It can be any TrackMate file, that we will re-export in the second
# part of the script.

# Put here the path to the TrackMate file you want to load
filename = x + '_trackerv2.xml'
input_filename = os.path.join(source, filename)
input_file = File( input_filename )

# We have to feed a logger to the reader.
logger = Logger.IJ_LOGGER

reader = TmXmlReader( input_file )
if not reader.isReadingOk():
    sys.exit( reader.getErrorMessage() )

# Load the model.
model = reader.getModel()
# Load the image and tracking settings.
imp = reader.readImage()
settings = reader.readSettings(imp)
# Load the display settings.
ds = reader.getDisplaySettings()
log = reader.getLog()

#-------------------------------
# 1/ Resave to a TrackMate file.
#-------------------------------

# The following will generate a TrackMate XML file.
# This is the file type you will be able to load with
# the GUI, using the command 'Plugins > Tracking > Load a TrackMate file'
# in Fiji.

target_xml_filename = input_filename.replace( '.xml', '-resaved.xml' )
target_xml_file = File( target_xml_filename )
writer = TmXmlWriter( target_xml_file, logger )

# Append content. Only the model is mandatory.
writer.appendLog( log )
writer.appendModel( model )
writer.appendSettings( settings )
writer.appendDisplaySettings( ds )

# We want TrackMate to show the view config panel when 
# reopening this file.
writer.appendGUIState( 'ConfigureViews' )

# Actually write the file.
writer.writeToFile()



#-------------------------------------------------------
# 2/ Export spots data to a CSV file in a headless mode.
#-------------------------------------------------------

# This will export a CSV table containing the spots data. The table will
# include all spot features, their ID, the track they belong to, name etc.
# But it will not include the edge and track features. Also if you have
# splitting and merging events in your data, the content of the CSV file
# will not be enough to reconstruct the tracks. 

# Nonetheless, the advantage of using this snippet, with the 'CSVExporter'
# is that it can work in headless mode. It does not depend on Fiji GUI
# being launched. So you can use it a 'headless' script, called from the 
# command line. See this page for more information:
# https://imagej.net/scripting/headless

out_file_csv = input_filename.replace( '.xml', '.csv' )
only_visible = True # Export only visible tracks
# If you set this flag to False, it will include all the spots,
# the ones not in tracks, and the ones not visible.
CSVExporter.exportSpots( out_file_csv, model, only_visible )



#----------------------------------------------------
# 3/ Export spots, edges and track data to CSV files.
#----------------------------------------------------

# The following uses the tables that are displayed in the TrackMate
# GUI. As a consequence the snippet cannot be used in 'headless' mode.
# If you launch the script from the Fiji script editor, we won't
# have a problem.

# Spot table. Will contain only the spots that are in visible tracks.
spot_table = TrackTableView.createSpotTable( model, ds )
spot_table_csv_file = File( input_filename.replace( '.xml', '-spots.csv' ) )
spot_table.exportToCsv( spot_table_csv_file )

# Edge table.
edge_table = TrackTableView.createEdgeTable( model, ds )
edge_table_csv_file = File( input_filename.replace( '.xml', '-edges.csv' ) )
edge_table.exportToCsv( edge_table_csv_file )

# Track table.
track_table = TrackTableView.createTrackTable( model, ds )
track_table_csv_file = File( input_filename.replace( '.xml', '-tracks.csv' ) )
track_table.exportToCsv( track_table_csv_file )
"""
