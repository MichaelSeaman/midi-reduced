#!/usr/bin/env python

# Code made possible by shoogle's midicsv-process
# https://github.com/shoogle/midicsv-process


import sys
from midi import *

def csv_to_notelist(rows, resolution):
    tempoMap   = TempoMap()
    notes      = []
    noteEvents = []
    onTicks    = []
    resolution_multiplier = 1e-3 / resolution

    # Reading midi events
    for i, cells in enumerate(rows):
        track = int(cells[0])
        tick = int(cells[1])
        rowType = cells[2].strip()
        if rowType == "Header":
            tpqn = int(cells[5]) # set tickcells per quarter note
            tempoMap.tpqn = tpqn
            nTracks = int(cells[4]) + 1
        elif rowType == "Tempo":
            tempo = int(cells[3])
            tempoMap.addTempo(tick, tempo)
        elif rowType in ("Note_on_c","Note_off_c"):
            pitch    = int(cells[4])
            velocity = int(cells[5])
            noteEvents.append(NoteEvent(track, tick, pitch, velocity, i))

    # Create notes by pairing noteOn and NoteOff events
    for i, noteEvent_on in enumerate(noteEvents):
        if noteEvent_on.velocity ==0:
            continue
        for noteEvent_off in noteEvents[i:]:
            if (noteEvent_off.velocity != 0 or
            noteEvent_off.track != noteEvent_on.track or
            noteEvent_off.pitch != noteEvent_on.pitch):
                continue
            note = Note(noteEvent_on, noteEvent_off)
            notes.append(note)
            onTicks.append(note.tick)
            break

    # sort notes by onTick
    notes = [x for (y,x) in sorted(zip(onTicks, notes))]
    onTicks.sort()
    notelist = []

    # creating notelist
    for note in notes:
        notelist.append([int(note.onTimeMillis(tempoMap) * resolution_multiplier + .5),
        int(note.pitch), int(note.durationMillis(tempoMap) * resolution_multiplier + .5)])

    # changing first entry to only record delta t
    last_note_on = 0
    for note in notelist:
        curr_note_on = note[0]
        temp = note[0]
        note[0] = curr_note_on - last_note_on
        last_note_on = temp

    strlist = []
    for note in notelist:
        strlist.append("".join([
            chr( min(cell, 63583) + 160) for cell in note]))

    notestring = ",".join(strlist)
    return notestring

def csv_to_note_event_list(rows, resolution):
    resolution_multiplier = resolution * 1000
    event_list = []

    last_note_on = 0
    for i, cells in enumerate(rows):
        note_on_relative = int(cells[0]) * resolution_multiplier
        note_on = last_note_on + note_on_relative
        last_note_on = note_on
        pitch = int(cells[1])
        duration = int(cells[2])

        noteEvent_on = NoteEvent(track=2, tick=note_on, pitch=pitch, velocity=100)
        noteEvent_off = NoteEvent(track=2, tick=note_on+duration, pitch=pitch,
            velocity=0)
        event_list.append(noteEvent_on)
        event_list.append(noteEvent_off)

    return sorted(event_list)

def preprocesses_raw_unicode_notes(raw):
    note_list_uni = raw.split(",")
    out = []
    for note in note_list_uni:
        row = [ord(cell) - 160 for cell in note ]
        if(len(row) != 3):
            row = row + [0,0,0]
            row = row[:3]
        out.append(row)

    return out
