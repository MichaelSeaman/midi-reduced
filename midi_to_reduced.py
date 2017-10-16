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
    for midiInputFile in inputFiles:
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

        print("Processing notes with resolution of {}s".format(res))
        current_notelist = csv_to_notelist(rows, resolution=res)
        print("Prepending silence")
        current_notelist = prepend_silence_to_notelist(current_notelist,
            t=pause, res=res)
        notelist = notelist + current_notelist

    print(notelist)
    notestring = notelist_to_notestring(notelist)
    with open(reduced_output_file, 'w', encoding="utf-8") as f:
        f.write(notestring)

    print("All done.")

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
    if(os.path.isdir(MIDI_INPUT_FILE)):
        print("Directory inputted")
        for f in glob.glob(os.path.join(MIDI_INPUT_FILE, "*.mid")):
            inputFiles.append(f)
    else:
        inputFiles = [MIDI_INPUT_FILE]

    if(len(inputFiles) < 1):
        print("No files found.")
        sys.exit(0)
    else:
        print("Using file(s) ", inputFiles)

    if(not output_file_provided):
        baseInputFilename, _ = os.path.splitext(os.path.basename(MIDI_INPUT_FILE))
        reduced_output_file = baseInputFilename + "_reduced.txt"
        print("Creating reduced file at ", reduced_output_file)
        Path(reduced_output_file).touch()

    return inputFiles, reduced_output_file, RESOLUTION, PAUSE_LENGTH

if __name__ == "__main__":
    main(sys.argv[1:])
