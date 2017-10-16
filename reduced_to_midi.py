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

def main(argv):
    reduced_input_file, input_file_provided, res, output_file = parse_options(argv)

    # Read CSV
    with open(reduced_input_file, 'r', encoding="utf-8") as f:
        raw = f.read()

    notelist = notestring_to_notelist(raw)
    title, _ = os.path.splitext(os.path.basename(reduced_input_file))
    preamble, out_rows, postamble = notelist_to_csv_parts(notelist, res=res,
        title=title)

    # Write to file
    temp_csv_file_name = title + "_temp.csv"
    write_to_csv(temp_csv_file_name, preamble, out_rows, postamble)

    # next, run csv to midi
    if(output_file):
        out_title = output_file
    else:
        if(title[-8:] == "_reduced"):
            out_title = title[:-8] + ".mid"
        else:
            out_title = title + ".mid"

    print("Creating midicsv file at ", out_title)
    os.system("csvmidi {} {}".format(temp_csv_file_name, out_title))
    os.remove(temp_csv_file_name)

    print("All done.")

def notelist_to_csv_parts(notelist, res, title='Default'):
    # Re-order notelist to list of note events
    note_event_list = notelist_to_MIDI_event_list(notelist, res=res)

    # Find tick of last event
    last_tick = int(note_event_list[-1].tick)

    # Creating the CSV rows
    # Store the preamble
        # Write title, last tick
    out_rows = []

    preamble = midi_static_data.MIDI_HEADER
    preamble = preamble.format(title=title, last_tick=last_tick)

    # Write all note events
    for note_event in note_event_list:
        # Sample row: 2, 171300, Note_on_c, 0, 50, 0
        tick = int(note_event.tick)
        pitch = int(note_event.pitch)
        vel = int(note_event.velocity)
        out_rows.append([note_event.track, " " + str(tick),
        " Note_on_c", " 0", " " + str(pitch), " " + str(vel)])

    # Store the footer
        # Again, last tick and title
    postamble = midi_static_data.MIDI_FOOTER
    postamble = postamble.format(title=title, last_tick=last_tick)

    return preamble, out_rows, postamble

def write_to_csv(filename, preamble, out_rows, postamble):
    with open(filename, 'w') as f:
        f.write(preamble)
        writeCSV = csv.writer(f)
        writeCSV.writerows(out_rows)
        f.write(postamble)

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
