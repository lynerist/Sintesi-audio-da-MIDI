import mido
import os

song = "multiNoteOn"

midi = mido.MidiFile(f"midi/{song}.mid", clip=True)
print("Midi file:\n", midi, "\n")

newFile = mido.MidiFile()
newFile.ticks_per_beat = midi.ticks_per_beat

noteAlreadyOn = dict()

for track in midi.tracks:
	newTrack = mido.MidiTrack()
	newTrack.name = track.name
	for msg in track:
		if msg.type == "note_on":
			if msg.velocity == 0:
				msg = mido.Message("note_off", note = msg.note, time=msg.time)
			elif noteAlreadyOn.get(msg.note):
				newTrack.append(mido.Message("note_off", note = msg.note, time=msg.time))
				newTrack.append(mido.Message("note_on", note = msg.note, velocity = msg.velocity, time = 0))
			else:
				newTrack.append(msg)
			noteAlreadyOn[msg.note] = True	

								
		if msg.type == "note_off":
			noteAlreadyOn[msg.note] = False
			newTrack.append(msg)

	newFile.tracks.append(newTrack)

#Se non esiste creo la directory dove collezionare i backups dei file midi
if not os.path.exists("backups"):
	os.mkdir("backups")

midi.save(f"backups/{song}.mid")
newFile.save(f"midi/{song}.mid")


#TODO file di pre elaborazione


