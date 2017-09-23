# midi-reduced
2 way translation from midi to a reduced midi form

### Reduced midi form
For use as a condensed musical file form, made to be easily readable by a
character based RNN.

Notes are seperated by new lines, and each line takes the form
```
<time since last note>,<note number>,<duration>
```
All time is measured in a resolution of milliseconds
