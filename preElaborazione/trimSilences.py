import pydub
import os
from pydub import AudioSegment


instrument = "harpsichord"

instrumentPath = "instruments/%s/"%instrument
trimmedPath = "instruments/%sTrimmed"%instrument

#Se non esiste creo la directory
if not os.path.exists(trimmedPath):
	os.mkdir(trimmedPath)


#leggo il range di note disponibili
try:
	rangeNotes = tuple(open(instrumentPath + "info.txt", "r").readline().split())
except Exception as e:
	rangeNotes = e
	exit()

#"""		PER TRIMMARE TUTTE LE NOTE
for note in range(int(rangeNotes[0]), int(rangeNotes[1])+1):
	try:
		audioNote = pydub.AudioSegment.from_file("%s/%s.wav"%(instrumentPath,note))
		print(note, " - ", end = "")
		print("duration:", audioNote.duration_seconds, end=" -> ")
		
		startTrim = pydub.silence.detect_leading_silence(audioNote)
		if audioNote.duration_seconds > 6:
			endTrim = pydub.silence.detect_leading_silence(audioNote.reverse(), -45)
		else:
			endTrim = pydub.silence.detect_leading_silence(audioNote.reverse(), -60)

		duration = len(audioNote)
		trimmed = audioNote[startTrim:duration-endTrim].fade_out(600)

		print(trimmed.duration_seconds)
		trimmed.export("%s/%d.wav"%(trimmedPath, note), "wav")

	except Exception as e:
		print(e)
		continue







