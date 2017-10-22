#!/usr/bin/env python

# Code made possible by shoogle's midicsv-process
# https://github.com/shoogle/midicsv-process


import sys
from midi import *

def csv_to_notelist(rows, resolution):
    '''
    Takes a nested list corresponding to split csv file and returns a 'notelist'
    in the following format [<displacement from last note>, <pitch>, <duration]
    with all time measurements are made with integers in units of resolution
    times seconds.
    '''
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
        elif rowType == "Note_on_c":
            pitch    = int(cells[4])
            velocity = int(cells[5])
            noteEvents.append(NoteEvent(track, tick, pitch, velocity, i))
        elif rowType == "Note_off_c":
            pitch    = int(cells[4])
            velocity = 0
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

    return notelist

def notelist_to_MIDI_event_list(notelist, res):
    '''
    Converts notelist into midi event list by splitting each note into its
    respective on/off messages.
    '''
    resolution_multiplier = res * 1000
    event_list = []

    last_note_on = 0
    for i, cells in enumerate(notelist):
        note_on_relative = int(cells[0]) * resolution_multiplier
        note_on = last_note_on + note_on_relative
        last_note_on = note_on
        pitch = int(cells[1])
        duration = int(cells[2]) * resolution_multiplier

        noteEvent_on = NoteEvent(track=2, tick=note_on, pitch=pitch, velocity=100)
        noteEvent_off = NoteEvent(track=2, tick=note_on+duration, pitch=pitch,
            velocity=0)
        event_list.append(noteEvent_on)
        event_list.append(noteEvent_off)

    return sorted(event_list)

def notelist_to_notestring(notelist):
    '''
    Takes a notelist object [<displacement from last note>, <pitch>, <duration]
    and casts it (and returns it) as a unicode string
    '''
    strlist = []
    for note in notelist:
        strlist.append("".join([
            chr( min(cell, 63583) + 160) for cell in note]))
    notestring = ",".join(strlist)
    return notestring

def notestring_to_notelist(notestring):
    '''
    Takes a notelist object in unicode string form and casts it (and returns it)
    in integer list form: [<displacement from last note>, <pitch>, <duration]
    '''
    note_list_uni = notestring.split(",")
    notelist = []
    for note in note_list_uni:
        row = [ord(cell) - 160 for cell in note ]
        if(len(row) != 3):
            row = row + [0,0,0]
            row = row[:3]
        notelist.append(row)
    return notelist

def prepend_silence_to_notestring(notestring, t, res):
    '''
    Adds a silence of length t (in seconds) at the beginning of a notestring
    '''
    notelist = notestring_to_notelist(notestring)
    notelist = prepend_silence_to_notelist(notelist, t=t, res=res)
    return notelist_to_notestring(notelist)

def prepend_silence_to_notelist(notelist, t, res):
    '''
    Adds a silence of length t (in seconds) at the beginning of a notelist
    '''
    ticks_to_add = int(t / res)
    notelist[0][0] += ticks_to_add
    return notelist
