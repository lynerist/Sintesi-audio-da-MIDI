import os
import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write

fs = 44.1 #kHz

MS_15 = int(fs * 15) #campioni in 15ms
MS_50 = int(fs * 50) #campioni in 50ms

instrumentName = "frenchHorn"
outputPath = f"instruments/{instrumentName}"

#outputAudioPath = f"{outputPath}/audioTest"
#os.mkdir(outputAudioPath)

times = []

for fileName in os.listdir(outputPath):
	if fileName == "info.txt" or fileName == "audioTest": continue

	note = np.array(read(f"{outputPath}/{fileName}")[1])

	for index, sample in enumerate([l + r for [l, r] in note[MS_50:]]):
		if not sample:
			endOfAttack = index + MS_50
			break

	for index, sample in enumerate([l + r for [l, r] in note[::-1][MS_50:]]):
		if not sample:
			startOfRelease = index + MS_50
			break
	
	times.append((endOfAttack, startOfRelease))
	#write(f"{outputAudioPath}/{fileName}",44100, np.concatenate((note[:endOfAttack], note[-startOfRelease:])))

infoFile = open(f"{outputPath}/info.txt", "a")
infoFile.write("\n" + " ".join(f"{ea},{sr}" for ea, sr in times))


