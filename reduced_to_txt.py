import sys
import os
import getopt
import subprocess
import csv
from note_processing import *
from midi import *
import midi_static_data

REDUCED_INPUT_FILE = "testfiles/Test_midi_waldstein_reduced.txt"
INPUT_FILE_PROVIDED = False
RESOLUTION = 1e-2
NOTE_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
OCTAVE_LEN = 12

def main(argv):
    reduced_input_file, input_file_provided, res, output_file = parse_options(argv)

    # Read CSV
    with open(reduced_input_file, 'r', encoding="utf-8") as f:
        raw = f.read()

    notelist = notestring_to_notelist(raw)
    title, _ = os.path.splitext(os.path.basename(reduced_input_file))
    
    if(output_file):
        out_title = output_file
    else:
        if(title[-8:] == "_reduced"):
            out_title = title[:-8] + ".txt"
        else:
            out_title = title + "_readable.txt"

    with open(out_title, 'w') as f:
        for note in notelist:
            f.write(print_note(note) + "\n")

    print("Created output at ", out_title)
    print("All done.")

def print_note(note, delim=', '):
    # Returns a human readable form of a note, which is a length 3 list of ints
    t = str(note[0])
    name = midi_note_name(note[1])
    dur = str(note[2])
    return delim.join([t, name, dur])


def midi_note_name(midi_pitch):
    octave = midi_pitch // OCTAVE_LEN
    mod_pitch = midi_pitch % OCTAVE_LEN
    return NOTE_NAMES[mod_pitch] + str(octave)


def parse_options(argv):
    global REDUCED_INPUT_FILE
    global INPUT_FILE_PROVIDED
    global RESOLUTION
    output_file=''

    try:
        opts, args = getopt.getopt(argv, 'i:r:o:', ['input=', 'resolution=',
            'output='])
        for opt, arg in opts:
            if opt in ('-i','--input'):
                REDUCED_INPUT_FILE = arg
                INPUT_FILE_PROVIDED = True
            elif opt in ('-o', '--output'):
                output_file = arg
            elif opt in ('-r','--resolution'):
                RESOLUTION = float(arg)
    except getopt.GetoptError as e:
        print("No input provided")
        print(e)

    if(not INPUT_FILE_PROVIDED):
        print("No input file provided. Defaulting to test case.")
    print("Using input reduced file: ", REDUCED_INPUT_FILE)
    if(not os.path.exists(REDUCED_INPUT_FILE)):
        print("File not found")
        sys.exit(0)
    return REDUCED_INPUT_FILE, INPUT_FILE_PROVIDED, RESOLUTION, output_file


if __name__ == "__main__":
    main(sys.argv[1:])
