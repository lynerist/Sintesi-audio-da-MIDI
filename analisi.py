import mido
import pydub
from functions import MidiInterface
import sys

song = "x_files"
trackNumber = 0
if len(sys.argv) > 1:
	trackNumber = int(sys.argv[1])

midi = MidiInterface(mido.MidiFile("midi/%s.mid"%song, clip=True))

print("Midi file:\n", midi, "\n")

print("Tracks:")
for track in midi.midi.tracks:
	print(track)
print()


print("Messages of track %d:"%trackNumber)
for msg in midi.track(trackNumber):
 	print(msg)
