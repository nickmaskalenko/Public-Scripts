def organizer(settings, directory):
    import os
    import pandas as pd
    import shutil

    well_array = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
    array_well = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H"}
    entries = os.listdir('.')
    directories = [d for d in entries if os.path.isdir(d)]
    if directories:
        first_directory = directories[0]
        new_name = "Unsorted"
        os.rename(first_directory, new_name)
        print(f"Renamed '{first_directory}' to '{new_name}'")
    else:
        print("No directories found in the current directory.")
    for q in range(well_array[settings.iloc[0]['Start Row']], well_array[settings.iloc[0]['Stop Row']] + 1):
        wellcol = array_well[q]
        print(wellcol)
        for x in range(int(settings.iloc[0]['Start Well']), int(settings.iloc[0]['Stop Well']) + 1):
            print(x)
            try:
                x_str = f"0{x}" if x < 10 else str(x)
                for y in range(int(settings.iloc[0]['Frames'])):
                    yy = str(y + 1)
                    resorted_path = os.path.join(directory, "Resorted", wellcol + x_str, "s" + yy)
                    results_path = os.path.join(resorted_path, "results")
                    os.makedirs(resorted_path)
                    os.makedirs(results_path)
                    for z in range(int(settings.iloc[0]['Timepoints'])):
                        zz = str(z + 1).zfill(2)
                        origin = os.path.join(directory, "Unsorted", f"Timepoint_{zz}")
                        for w in range(1, 5):  # Assuming 4 channels as per original code
                            file_name = f"Campbell-K_{wellcol}{x_str}_s{yy}_w{w}.tif"
                            shutil.copy(os.path.join(origin, file_name),
                                        os.path.join(resorted_path, file_name.replace(".tif", f"_t{zz}.tif")))
            except Exception as error:
                print("An exception occurred:", type(error).__name__)
                continue


def stacker(settings, directory):
    well_array = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
    array_well = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H"}
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
                    args = {"source": source}
                    ij.py.run_macro(StackMaster, args)

            except Exception as error:
                # handle the exception
                print("An exception occurred:", type(error).__name__)
                continue


def masker_settings():
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


def masker(ij, args):
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


def pather(ij, source):
    import jpype
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


def trackloader(source, radmin):
    import os
    import pandas as pd
    os.chdir(source)
    try:
        """Pandas gets really unhappy if you don't assign an object class to every column"""
        spots = pd.read_csv("w2-mask_tracker-spots.csv", skiprows=[1, 2, 3],
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
        aspots = pd.read_csv("w4-mask_tracker-spots.csv", skiprows=[1, 2, 3],
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
        bspots = pd.read_csv("w3-mask_tracker-spots.csv", skiprows=[1, 2, 3],
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


def tracker_part1(spots, aspots, bspots, radmin):
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

def tracker_part2(spots, cspots, qtree, analysis_sheet_summary, radmin, radmax, checkwiper, currow, curwell, curframe):
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
File.openSequence(source, " filter=_w1");
saveAs("Tiff", source + "/w1.tif");
File.openSequence(source, " filter=_w2");
saveAs("Tiff", source + "/w2.tif");
File.openSequence(source, " filter=_w3");
saveAs("Tiff", source + "/w3.tif");
File.openSequence(source, " filter=_w4");
saveAs("Tiff", source + "/w4.tif");
run("Merge Channels...", "c1=w2.tif c2=w4.tif c3=w3.tif c4=w1.tif create");
saveAs("Tiff", source + "/01_Merge.tif");
close("*");
"""

Corrections = """
#@String source
#@Integer timepoints
#@Integer w2
#@Integer w3
#@Integer w4
//Open the Composite for this well/frame
open(source + "/01_Merge.tif");
//Set the Brightness and Contrast for the image, then paste it back together
//These values should be constant and set experiment-to-experiment
run("Split Channels");
selectWindow("C1-01_Merge.tif");
run("Enhance Contrast", "saturated=0.35");
setMinAndMax(122, 309);
selectWindow("C2-01_Merge.tif");
run("Enhance Contrast", "saturated=0 .35");
setMinAndMax(431, 2614);
selectWindow("C3-01_Merge.tif");
run("Enhance Contrast", "saturated=0.35");
setMinAndMax(846, 2614);
selectWindow("C4-01_Merge.tif");
run("Enhance Contrast", "saturated=0.35");
setMinAndMax(364, 3500);
run("Merge Channels...", "c1=C1-01_Merge.tif c2=C2-01_Merge.tif c3=C3-01_Merge.tif c4=C4-01_Merge.tif create");
//Fix the drifting camera
run("Re-order Hyperstack ...", "channels=[Channels (c)] slices=[Frames (t)] frames=[Slices (z)]");
run("Correct 3D drift", "channel=4 correct sub_pixel only=0 lowest=1 highest=1 max_shift_x=50 max_shift_y=50 max_shift_z=10");
selectWindow("registered time points");
saveAs("Tiff", source + "/results/corrected-merge.tif");
close("01_Merge.tif");
run("Collect Garbage");
"""

Masker = """
#@String source
#@Integer timepoints
#@Integer w2
#@Integer w3
#@Integer w4
#@output String w2measure
#@output String w3measure
#@output String w4measure
//Make Masks for data analysis
selectWindow("corrected-merge.tif");
run("Duplicate...", "duplicate");
selectWindow("corrected-merge-1.tif");
run("Split Channels");
selectWindow("C1-corrected-merge-1.tif");
run("Subtract Background...", "rolling=50 stack");
setThreshold(w2, 65535, "raw");
setOption("BlackBackground", true);
run("Convert to Mask", "method=Default background=Dark black");
saveAs("Tiff", source + "/results/w2-mask.tif");
//Analyize the NK cells
w2measure = "";
selectWindow("w2-mask.tif");
for (t =1; t<=timepoints; t++) {
    run("Create Selection");
    area = getValue("Area");
    w2measure = w2measure + area + " ";
    //run("Measure");
    run("Next Slice [>]");
};
//selectWindow("Results");
//saveAs("Results", source + "/results/w2-masks.csv");
//close("Results");
selectWindow("w2-mask.tif");
close();
//End Analyze NK cells
selectWindow("C3-corrected-merge-1.tif");
run("Subtract Background...", "rolling=50 stack");
setThreshold(w3, 65535, "raw");
setOption("BlackBackground", true);
run("Convert to Mask", "method=Default background=Dark black");
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
//saveAs("Results", source + "w2-masks.csv");
//close("Results");
selectWindow("w3-mask.tif");
close();
run("Collect Garbage");
//End Analyize all cells
selectWindow("C2-corrected-merge-1.tif");
run("Subtract Background...", "rolling=50 stack");
setThreshold(w4, 65535, "raw");
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
run("Collect Garbage");
//End analyize apoptotic cells
selectWindow("C4-corrected-merge-1.tif");
close();
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
open(source + "/" + "w3" + ".tif");
"""

""" Why is ImageJ so bad at garbage collection? """

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

""" Using TrackMate's template script for tracking and saving tracks """

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

if x == "w2-mask":
    rad = 6.0
    qual = 90.
elif x == "w3-mask":
    rad = 5.0
    qual = 5.
elif x == "w4-mask":
    rad = 5.0
    qual = 5.

# We have to do the following to avoid errors with UTF8 chars generated in 
# TrackMate that will mess with our Fiji Jython.
reload(sys)
sys.setdefaultencoding('utf-8')

# Get currently selected image
imp = WindowManager.getCurrentImage()
# imp = IJ.openImage('D:/HTSF images 07102024/Resorted/B02/s1/results/w1.tif')
# imp.show()


#----------------------------
# Create the model object now
#----------------------------

# Some of the parameters we configure below need to have
# a reference to the model at creation. So we create an
# empty model now.

model = Model()

# Send all messages to ImageJ log window.
model.setLogger(Logger.IJ_LOGGER)



#------------------------
# Prepare settings object
#------------------------

settings = Settings(imp)

# Configure detector - We use the Strings for the keys
settings.detectorFactory = LogDetectorFactory()
settings.detectorSettings = {
    'DO_SUBPIXEL_LOCALIZATION' : True,
    'RADIUS' : rad,
    'TARGET_CHANNEL' : 1,
    'THRESHOLD' : qual,
    'DO_MEDIAN_FILTERING' : True,
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

# Add ALL the feature analyzers known to TrackMate. They will 
# yield numerical features for the results, such as speed, mean intensity etc.
settings.addAllAnalyzers()

# Configure track filters - We want to get rid of the two immobile spots at
# the bottom right of the image. Track displacement must be above 10 pixels.

# if x == "w2-mask":
filter2 = FeatureFilter('TRACK_DURATION', 3, True)
settings.addTrackFilter(filter2)
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

