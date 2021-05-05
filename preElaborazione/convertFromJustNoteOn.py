import mido

song = "error"

toAnalyze = "midi/%s.mid"%song

midi = mido.MidiFile(toAnalyze, clip=True)
print("Midi file:\n", midi, "\n")

newFile = mido.MidiFile()
newFile.ticks_per_beat = midi.ticks_per_beat

for track in midi.tracks:
	newTrack = mido.MidiTrack()
	for msg in track:
		if msg.type == "note_on" and msg.velocity == 0 :
			msg = mido.Message("note_off", note = msg.note, velocity = 110, time=msg.time)
		newTrack.append(msg)
	newFile.tracks.append(newTrack)

newFile.save(toAnalyze)


#TODO DA SISTEMARE I PATH CHE PROBABILMENTE SONO ROTTI



