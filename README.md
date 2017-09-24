# midi-reduced
2 way translation from midi to a reduced midi form

### Reduced midi form
For use as a condensed musical file form, made to be easily readable by a
character based RNN.

Notes are seperated by commas, and each note takes the form
```
<time since last note><note number><duration>,
```
All time is measured in a resolution not specified in the file (Default 1
  millisecond). All numeric values are stored with unicode characters, starting
  at UTF-8 Dec# 160.

### Usage
To convert a midi file into reduced form:
```
python3 midi_to_reduced.py -i <INPUT_MIDI_FILE> -r <RESOLUTION>

Example:

python3 midi_to_reduced.py -i moonlight_sonata.mid -r .001
```

### Dependencies

This tool requires the ever helpful [midicsv](http://www.fourmilab.ch/webtools/midicsv/) and is written in Python3

## Authors

* **Michael Seaman** - *Initial work* - [Michael Seaman](https://github.com/MichaelSeaman)


## Acknowledgments

* Thanks to [shoogle's midi-csv process](https://github.com/shoogle/midicsv-process) for some code inspiration for the midi module
