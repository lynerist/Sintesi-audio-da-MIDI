import os
import numpy as np
import soundfile as sf
from functions import crossfade

fs = 44.1 #kHz

MS_15 = int(fs * 15) #campioni in 15ms
MS_50 = int(fs * 50) #campioni in 50ms
MS_100 = int(fs * 100) #campioni in 50ms


instrumentName = "frenchHorn"
outputPath = f"instruments/{instrumentName}"

outputAudioPath = f"{outputPath}/audioTest"
#os.mkdir(outputAudioPath)

times = []
outputAudio = np.array([])

for fileName in os.listdir(outputPath):
	if fileName == "info.txt" or fileName == "audioTest": continue

	
	note = sf.read(f"{outputPath}/{fileName}")[0]
	
	if note.ndim > 1:
		note = np.asarray([r + l for [l, r] in note])


	for index, sample in enumerate(note[MS_100:]):
		if abs(sample) < 1/100:
			endOfAttack = index + MS_100
			break

	for index, sample in enumerate(note[::-1][MS_100:]):
		if abs(sample) < 1/100:
			startOfRelease = index + MS_100
			break
	
	times.append((endOfAttack, startOfRelease))
	outputAudio = np.concatenate((outputAudio, np.zeros(11025),crossfade(note[:endOfAttack], note[-startOfRelease:]), np.zeros(11025)))

sf.write(f"{outputAudioPath}/output.wav", outputAudio, 44100)

infoFile = open(f"{outputPath}/info.txt", "a")
infoFile.write("\n" + " ".join(f"{ea},{sr}" for ea, sr in times))


