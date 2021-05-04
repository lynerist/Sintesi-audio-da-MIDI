import mido

song = "star_wars"
toAnalyze = "midi/%s.mid"%song
newSongName = "midi/new-%s.mid"%song

trackToSave = [0,1,2,3,4]
velocities = dict()



midi = mido.MidiFile(toAnalyze, clip=True)
print("Midi file:\n", midi, "\n")

newFile = mido.MidiFile()
newFile.filename = newSongName

newFile.ticks_per_beat = midi.ticks_per_beat

for index, track in enumerate(midi.tracks):
	if index in trackToSave:
		if index in velocities.keys():
			traccia = mido.MidiTrack()
			traccia.name = track.name
			for msg in track:
				if msg.type == "note_on" or msg.type == "note_off":
					msg = mido.Message(msg.type, note = msg.note, velocity = velocities[index], time=msg.time)
				traccia.append(msg)
			newFile.tracks.append(traccia)
		else:
			newFile.tracks.append(track)

newFile.save(newSongName)

print("Midi file:\n", newFile, "\n")