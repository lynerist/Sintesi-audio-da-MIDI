#multi tracks in note on problem

import mido

midi = mido.MidiFile()
midi.ticks_per_beat = 92

track1 = mido.MidiTrack()

#track1.append(mido.Message("note_on", note = 40, velocity = 100, time = 0))
track1.append(mido.Message("note_on", note = 70, velocity = 30, time = 0))
#track1.append(mido.Message("note_on", note = 40, velocity = 80, time = 100))
track1.append(mido.Message("note_on", note = 70, velocity = 20, time = 200))
#track1.append(mido.Message("note_on", note = 40, velocity = 50, time = 100))
track1.append(mido.Message("note_on", note = 70, velocity = 10, time = 200))
#track1.append(mido.Message("note_on", note = 40, velocity = 0, time = 100))
track1.append(mido.Message("note_on", note = 70, velocity = 0, time = 200))

midi.tracks.append(track1)


track2 = mido.MidiTrack()

track2.append(mido.Message("note_on", note = 70, velocity = 100, time = 50))
track2.append(mido.Message("note_on", note = 70, velocity = 80, time = 50))
track2.append(mido.Message("note_on", note = 70, velocity = 50, time = 50))
track2.append(mido.Message("note_on", note = 70, velocity = 30, time = 50))
track2.append(mido.Message("note_on", note = 70, velocity = 0, time = 50))

midi.tracks.append(track2)

midi.save("midi/multiNoteOn.mid")