import sys
import os
import getopt
import subprocess
import csv
from csv_processing import csv_to_note_event_list
from midi import *

REDUCED_INPUT_FILE = "testfiles/Test_midi_waldstein_reduced.csv"
INPUT_FILE_PROVIDED = False
RESOLUTION = 1e-3
MIDI_HEADER_TEMPLATE_FILE = "midi_header.csv"
MIDI_FOOTER_TEMPLATE_FILE = "midi_footer.csv"

def main(argv):
    global REDUCED_INPUT_FILE
    global INPUT_FILE_PROVIDED
    global RESOLUTION

    try:
        opts, args = getopt.getopt(argv, 'i:r:', ['input=', 'resolution='])
        for opt, arg in opts:
            if opt in ('-i','--input'):
                REDUCED_INPUT_FILE = arg
                INPUT_FILE_PROVIDED = True
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

    # Read CSV
    with open(REDUCED_INPUT_FILE, 'r', encoding="latin-1") as f:
        readCSV = csv.reader(f)
        rows = list(readCSV)

    # Re-order notelist to list of note events
    note_event_list = csv_to_note_event_list(rows, RESOLUTION)

    # Find tick of last event
    last_tick = int(note_event_list[-1].tick)

    # Creating the CSV rows
    # Store the preamble
        # Write title, last tick
    out_rows = []
    title, _ = os.path.splitext(os.path.basename(REDUCED_INPUT_FILE))

    with open(MIDI_HEADER_TEMPLATE_FILE, 'r') as f:
        raw = f.read()
        preamble = raw.format(title=title, last_tick=last_tick)

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
    with open(MIDI_FOOTER_TEMPLATE_FILE, 'r') as f:
        raw = f.read()
        postamble = raw.format(title=title, last_tick=last_tick)

    # Write to file
    temp_csv_file_name = title + "_temp.csv"

    with open(temp_csv_file_name, 'w') as f:
        f.write(preamble)
        writeCSV = csv.writer(f)
        writeCSV.writerows(out_rows)
        f.write(postamble)

    # next, run csv to midi

    print("All done.")


if __name__ == "__main__":
    main(sys.argv[1:])
