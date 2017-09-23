#!/usr/bin/python

import sys
import os
import getopt
import subprocess
import csv
from csv_processing import csv_to_notelist

MIDI_INPUT_FILE = "testfiles/Test_midi_waldstein.mid"
INPUT_FILE_PROVIDED = False
RESOLUTION = 1e-3

def main(argv):
    global MIDI_INPUT_FILE
    global INPUT_FILE_PROVIDED
    global RESOLUTION

    try:
        opts, args = getopt.getopt(argv, 'i:r:', ['input=', 'resolution='])
        for opt, arg in opts:
            if opt in ('-i','--input'):
                MIDI_INPUT_FILE = arg
                INPUT_FILE_PROVIDED = True
            elif opt in ('-r','--resolution'):
                RESOLUTION = float(arg)
    except getopt.GetoptError as e:
        print("No input provided")
        print(e)

    if(not INPUT_FILE_PROVIDED):
        print("No input file provided. Defaulting to test case.")
    print("Using input midi file: ", MIDI_INPUT_FILE)
    if(not os.path.exists(MIDI_INPUT_FILE)):
        print("File not found")
        sys.exit(0)

    # run midi to csv
    midiInputFileName, _ = os.path.splitext(os.path.basename(MIDI_INPUT_FILE))
    csvFileName = midiInputFileName + ".csv"

    print("Creating midicsv file at ", csvFileName)
    os.system("midicsv {} {}".format(MIDI_INPUT_FILE, csvFileName))

    # prepping midicsv data for processing
    with open(csvFileName, 'r', encoding="latin-1") as f:
        readCSV = csv.reader(f)
        rows = list(readCSV)
    os.remove(csvFileName)

    notelist = csv_to_notelist(rows, resolution=RESOLUTION)

    reducedFileName = midiInputFileName + "_reduced.csv"
    print("Creating reduced file at ", reducedFileName)
    with open(reducedFileName, 'w') as f:
        writeCSV = csv.writer(f)
        writeCSV.writerows(notelist)

    print("All done.")


if __name__ == "__main__":
    main(sys.argv[1:])
