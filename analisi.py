import mido
import pydub
from functions import MidiInterface
import sys

song = "evangelion"
trackNumber = ""
if len(sys.argv) > 1:
	trackNumber = sys.argv[1]

midi = MidiInterface(mido.MidiFile("midi/%s.mid"%song, clip=True))

print("Midi file:\n", midi, "\n")
print(f"Length {midi.length}") #questa è sbagliata

print("Tracks:")
for track in midi.midi.tracks:
	print(track)
print()


if len(sys.argv) > 2:
	for track in midi.tracks:
		print(track)
		for i, msg in enumerate(track):
			print(msg)
			if i == int(sys.argv[2]):
				break
		print()
elif trackNumber == "a":
	print("message from all tracks")
	for msg in midi.allTracks:
		print(msg)	
elif len(sys.argv) > 1:
	print("Messages of track %s:"%trackNumber)
	for msg in midi.track(int(trackNumber)):
		print(msg)
