import pydub
import os
import sys

instrumentName = "frenchHorn"
outputPath = f"instruments/{instrumentName}"

lowestNote = 38
duplicatedOffset = 0 #per correggere il raddoppio delle note
duplicatedNotes = []

for fileName in os.listdir("samplesExtractor"):
	instrument = pydub.AudioSegment.from_file("samplesExtractor/"+fileName, "flac")
	notes = pydub.silence.detect_nonsilent(instrument, silence_thresh=-65, min_silence_len=500 )
	print(notes)
	
if not os.path.exists(outputPath):
	os.mkdir(outputPath)

for i, note in enumerate(notes):
	if i+lowestNote in duplicatedNotes:
		duplicatedOffset += 1
		continue

	singleNote = instrument[note[0]:note[1]]

	startNote = pydub.silence.detect_leading_silence(singleNote)

	singleNote[startNote:].fade_out(400).export(f"{outputPath}/{i+lowestNote-duplicatedOffset}.wav", "wav")

loop = "loopable" if (len(sys.argv)>1) else "not loopable"
	
infoFile = open(f"{outputPath}/info.txt", "a")
infoFile.write(f"{lowestNote} {lowestNote + len(notes) -1 -duplicatedOffset}\n{loop}")
infoFile.close()
