#!/usr/bin/env python

# Code made possible by shoogle's midicsv-process
# https://github.com/shoogle/midicsv-process

# File contains python classes for midi objects

class NoteEvent:
    def __init__(self, track=0, tick=0, pitch=64, velocity=127, rowNumber=0):
        self.track    = track
        self.tick     = tick
        self.pitch    = pitch
        self.velocity = velocity
        self.rowNumber = rowNumber

class Note:
    noteLetters  = ["C","C","D","D","E","F","F","G","G","A","A","B"]
    sharps       = [ "","#", "","#", "", "","#", "","#", "","#", ""]

    def __init__(self, noteEvent_on, noteEvent_off):
        self.track    = noteEvent_on.track
        self.tick     = noteEvent_on.tick
        self.pitch    = noteEvent_on.pitch
        self.velocity = noteEvent_on.velocity
        self.duration = noteEvent_off.tick - noteEvent_on.tick
        self.noteEvent_on = noteEvent_on
        self.noteEvent_off = noteEvent_off

    def __lt__(self, other):
        return (self.tick < other.tick)

    def onTimeMillis(self, tempoMap):
        return tempoMap.millisAtTick(self.tick)

    def durationMillis(self, tempoMap):
        return tempoMap.millisAtTick(self.tick + self.duration) - self.onTimeMillis(tempoMap)

    def octave(self):
        return (self.pitch // 12) - 1

    def letter(self):
        return self.noteLetters[self.pitch % 12]

    def sharp(self):
        return self.sharps[self.pitch % 12]

    def fullNote(self):
        return "%s%s" % (self.letter(), self.sharp())

    def fullNoteOctave(self):
        return "%s%s%s" % (self.letter(), self.octave(), self.sharp())

    def toString(self, tempoMap):
        return "%s,%s,%s,%s,%s,%s,%s" % (\
            self.tick,
            self.onTimeMillis(tempoMap),
            self.duration,
            self.durationMillis(tempoMap),
            self.pitch,
            self.velocity,
            self.track)


class TempoEvent:
    def __init__(self, tick=0, millis=0, tempo=500000):
        self.tick = tick
        self.millis = millis
        self.tempo  = tempo

class TempoMap:
    tpqn = 480 # ticks per quarter note
    tmap = []

    def __init__(self, tpqn=480, tmap=[]):
        self.tpqn = tpqn
        self.tmap = tmap

    def addTempo(self, tick, tempo):
        tempoEvent = TempoEvent()
        tempoEvent.tick = tick
        tempoEvent.tempo = tempo
        tempoEvent.millis = self.millisAtTick(tick)
        self.tmap.append(tempoEvent)

    def tempoEventAtTick(self, tick):
        savedTempoEvent = TempoEvent()
        for tempoEvent in self.tmap:
            if tempoEvent.tick > tick:
                break
            savedTempoEvent = tempoEvent
        return savedTempoEvent

    def millisAtTick(self, tick):
        tempoEvent = self.tempoEventAtTick(tick)
        return tempoEvent.millis + ((tick - tempoEvent.tick)*tempoEvent.tempo)/(self.tpqn*1000)
