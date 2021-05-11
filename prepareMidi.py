import mido
import os

song = "He_is_a_Pirate"

midi = mido.MidiFile(f"midi/{song}.mid", clip=True)
print("Midi file:\n", midi, "\n")

newFile = mido.MidiFile(ticks_per_beat = midi.ticks_per_beat)


for track in midi.tracks:
	noteAlreadyOn = dict()

	newTrack = mido.MidiTrack()
	newTrack.name = track.name

	offsetByNotMeta = 0

	for msg in track:
		if msg.type == "note_on":
			if msg.velocity == 0:
				msg = mido.Message("note_off", note = msg.note, time=msg.time+offsetByNotMeta, channel = msg.channel)
			elif noteAlreadyOn.get(msg.note):
				newTrack.append(mido.Message("note_off", note = msg.note, time=msg.time+offsetByNotMeta, channel = msg.channel))
				newTrack.append(mido.Message("note_on", note = msg.note, velocity = msg.velocity, time = 0, channel = msg.channel))
			else:
				newTrack.append(mido.Message("note_on", note = msg.note, time=msg.time+offsetByNotMeta, channel = msg.channel, velocity = msg.velocity))


			noteAlreadyOn[msg.note] = True	
								
		if msg.type == "note_off":
			noteAlreadyOn[msg.note] = False
			newTrack.append(mido.Message("note_off", note = msg.note, time=msg.time+offsetByNotMeta, channel = msg.channel))

		
		if not msg.is_meta and msg.type not in ["note_on", "note_off"]:
			offsetByNotMeta += msg.time
		else:
			offsetByNotMeta = 0
		
	newFile.tracks.append(newTrack)

#Se non esiste creo la directory dove collezionare i backups dei file midi
if not os.path.exists("backups"):
	os.mkdir("backups")

print(newFile, "\n")

from functions import MidiInterface

m = MidiInterface(midi)
n = MidiInterface(newFile)


print(midi.length, m.totalTicks)
print(newFile.length, n.totalTicks)

midi.save(f"backups/{song}.mid")
newFile.save(f"midi/{song}.mid")




