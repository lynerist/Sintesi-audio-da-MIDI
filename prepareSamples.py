import pydub
import os



instrumentName = "frenchHorn"
outputPath = f"instruments/{instrumentName}"

lowestNote = 38
duplicatedOffset = 0 #per correggere il raddoppio delle note
duplicatedNotes = []

for fileName in os.listdir("samplesExtractor"):
	instrument = pydub.AudioSegment.from_file("samplesExtractor/"+fileName, "flac")
	notes = pydub.silence.detect_nonsilent(instrument, silence_thresh=-60 )
	print(notes)
	
if not os.path.exists(outputPath):
	os.mkdir(outputPath)

for i, note in enumerate(notes):
	if i+lowestNote in duplicatedNotes:
		duplicatedOffset += 1
		continue

	singleNote = instrument[note[0]:note[1]]

	singleNote.fade_out(650).export(f"{outputPath}/{i+lowestNote-duplicatedOffset}.wav", "wav")

rangeFile = open(f"{outputPath}/range.txt", "a")
rangeFile.write(f"{lowestNote} {lowestNote + len(notes) -1 -duplicatedOffset}\nwav")
rangeFile.close()

# TODO scrivere file range in qualche modo