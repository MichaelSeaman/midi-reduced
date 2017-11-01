#!/usr/bin/python

import sys
import os
import getopt
import subprocess
import csv
import glob
from pathlib import Path
from note_processing import *
from misc import prompt_yes_no

MIDI_INPUT_FILE = "testfiles/Test_midi_waldstein.mid"
RESOLUTION = 1e-2
PAUSE_LENGTH = 3

def main(argv):
    inputFiles, reduced_output_file, res, pause = parse_options(argv)
    notelist = []
    for i, midiInputFile in enumerate(inputFiles):
        print("Starting on file {}: {}".format(i+1, midiInputFile))
        # run midi to csv
        baseInputFilename, _ = os.path.splitext(os.path.basename(midiInputFile))
        csvFileName = baseInputFilename + ".csv"

        print("Creating midicsv file at ", csvFileName)
        if(os.path.exists(csvFileName)):
            print("WARNING: File already exists.")
            overwrite = prompt_yes_no("Overwrite it?", default="no")
            if not overwrite:
                print("Skipping over ", midiInputFile)
                continue


        os.system("midicsv {} {}".format(midiInputFile, csvFileName))

        # prepping midicsv data for processing
        with open(csvFileName, 'r', encoding="latin-1") as f:
            readCSV = csv.reader(f)
            rows = list(readCSV)
        os.remove(csvFileName)

        if not rows:
            print("\nError with file. Continuing on.\n")
            continue
        print("Processing notes with resolution of {}s".format(res))
        current_notelist = csv_to_notelist(rows, resolution=res)


        print("Prepending silence of {} seconds".format(pause))
        current_notelist = prepend_silence_to_notelist(current_notelist,
            t=pause, res=res)
        notelist = notelist + current_notelist

    notestring = notelist_to_notestring(notelist)
    with open(reduced_output_file, 'w', encoding="utf-8") as f:
        f.write(notestring)

    print("All done.")
    print("Output at", reduced_output_file)

def parse_options(argv):
    global MIDI_INPUT_FILE
    global PAUSE_LENGTH
    reduced_output_file = ""
    input_file_provided = False
    output_file_provided = False
    global RESOLUTION

    try:
        opts, args = getopt.getopt(argv, 'i:r:o:p:', ['input=', 'resolution=',
            'output=', 'pause='])
        for opt, arg in opts:
            if opt in ('-i','--input'):
                MIDI_INPUT_FILE = arg
                input_file_provided = True
            elif opt in ('-o','--output'):
                reduced_output_file = arg
                output_file_provided = True
            elif opt in ('-r','--resolution'):
                RESOLUTION = float(arg)
            elif opt in ('-p', '--pause'):
                PAUSE_LENGTH = int(arg)
    except getopt.GetoptError as e:
        print("No input provided")
        print(e)

    if(not input_file_provided):
        print("No input file provided. Defaulting to test case.")

    inputFiles = []
    isDir = False
    if(os.path.isdir(MIDI_INPUT_FILE)):
        isDir = True
        print("Directory inputted")
        for f in glob.glob(os.path.join(MIDI_INPUT_FILE, "*.mid")):
            inputFiles.append(f)
    else:
        inputFiles = [MIDI_INPUT_FILE]

    if(len(inputFiles) < 1):
        print("No '.mid' files found.")
        sys.exit(0)
    else:
        print("Found", len(inputFiles), "files.")

    if(not output_file_provided):
        if(isDir):
            dirname = os.path.dirname(MIDI_INPUT_FILE)
            baseInputFilename = os.path.basename(dirname)
        else:
            basename = os.path.basename(MIDI_INPUT_FILE)
            baseInputFilename, _ = os.path.splitext(basename)


        basename = os.path.basename(MIDI_INPUT_FILE)
        print(MIDI_INPUT_FILE)
        print(os.path.split(MIDI_INPUT_FILE))
        print(baseInputFilename)

        reduced_output_file = baseInputFilename + "_reduced.txt"
        print("Creating reduced file at ", reduced_output_file)
        Path(reduced_output_file).touch()

    return inputFiles, reduced_output_file, RESOLUTION, PAUSE_LENGTH

if __name__ == "__main__":
    main(sys.argv[1:])
