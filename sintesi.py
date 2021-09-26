import mido
from functions import *
import soundfile as sf

NORMALIZATION = -20

def synthesize(song, instrument, base = "", saveTreeVolumes = False):

	try:
		instrument = Instrument(instrument)
	except FileNotFoundError as e :
		print(e)
		exit()

	midi = MidiInterface(mido.MidiFile(f"midi/{song}.mid"))
	duration = midi.duration
	
	# genero un file audio vuoto lungo quanto il file midi (+ 1s per non troncare alla fine)
	audio = np.zeros(int((midi.length + 1) * FS), dtype=int) 


	# cache dove salvo le note già suonate per non ricercarle
	cacheAudioSamples = dict()

	#per ogni traccia applico il procedimento. 
	for index, track in enumerate(midi.tracks):
		print(f"\ntrack {index +1}/{midi.ntracks} - ", end = " ")

		# il clock nella traccia
		countTicks = 0


		# Dizionario per salvarmi il tick di inizio dei note on per poi associarli ai note off relativi
		noteOnCollection = dict()

		# Per visualizzare l'elaborazione nel tempo
		loading = 0

		# Scorro ogni messaggio
		for msg in track:
			if msg.type == "note_on" or msg.type == "note_off":
				countTicks += msg.time	# Clock		

			if msg.type == "note_on":
				noteOnCollection[msg.note] = Note(msg.note, countTicks, msg.velocity)
				

			elif msg.type == "note_off":
				#recupero la nota
				note = noteOnCollection[msg.note]

				if note.note in cacheAudioSamples.keys(): 
					audioNote = cacheAudioSamples[note.note]
				else:
					minDistance 	= 127
					minDistanceNote = 0
					for sampleNote in instrument.notes:
						distance = abs(sampleNote - note.note)
						if distance < minDistance:
							minDistance, minDistanceNote = distance, sampleNote
						else:
							break
					audioNote = sf.read(f"{instrument.path}{minDistanceNote}.wav")[0]

					#rendo mono
					if audioNote.ndim > 1:
						audioNote = np.asarray([r + l for [l, r] in audioNote])

					#aggiusto il pitch				
					audioNote = pitchChange(audioNote, note.note - minDistanceNote)

					cacheAudioSamples[note.note] = audioNote
					instrument.endOfAttackStartOfRelease[note.note] = instrument.endOfAttackStartOfRelease[minDistanceNote]				

			
				#durata della nota midi
				noteLength = duration(countTicks-note.startTime)

				#scrivo il campione (prima adatto la durata del campione)
				
				endAttack = instrument.endOfAttackStartOfRelease[msg.note][0]
				startRelease = instrument.endOfAttackStartOfRelease[msg.note][1]


				adjustedLengthNote = adjustLength(audioNote, noteLength, instrument.loopable, endAttack, startRelease)

				offset = int(duration(note.startTime) * FS) 

				# divido la nota per questo fattore per conferire dinamica al pezzo.
				dynamicFactor = 5 - (note.velocity/127)*4
				
				try:
					audio = np.concatenate((audio[:offset], np.add(audio[offset:min(offset + len(adjustedLengthNote), len(audio))], adjustedLengthNote / dynamicFactor), audio[offset + len(adjustedLengthNote):]))
				except:
					print("bug at message %s\n"%msg)
					continue

			currentLoading = countTicks/midi.totalTicks*100
			if (currentLoading) - loading > 10:
				print("%.1f %%"%(currentLoading), end = " ", flush=True)
				loading = (currentLoading)
				
	#Se non esiste creo la directory dove collezionare gli output
	if not os.path.exists("outputAudio"):
		os.mkdir("outputAudio")
	print()

	output = [normalize(audio, -10, True)]

	#verifico se esiste una base:
	if base != "":
		base = sf.read(f"basi/{base}")[0]
		
		#la rendo mono
		if base.ndim > 1: 
			base = np.asarray([r + l for [l, r] in base])
						
		#per evitare out of range allungo l'audio
		if len(base) > len(audio): 
			audio = np.concatenate((audio, np.zeros(int(len(base) - len(audio) + 10), dtype=int)))
					
		#normalizzo
		base = normalize(base, NORMALIZATION)
		audioNormalized = normalize(audio, NORMALIZATION, True)

		if saveTreeVolumes:
			audioNormalizedDown = normalize(audio, NORMALIZATION -5, True)
			audioNormalizedUp = normalize(audio, NORMALIZATION +5, True)

		for i, c in enumerate(base):
			audioNormalized[i] += c
			if saveTreeVolumes:
				audioNormalizedDown[i] += c
				audioNormalizedUp[i] += c

		output.append(audioNormalized)
		if saveTreeVolumes:
			output.append(audioNormalizedDown)
			output.append(audioNormalizedUp)

	appendix = ["-TrackOnly","","-Down","-Up" ]
	for i, audio in enumerate(output):
		if i == 0: continue
		sf.write(f"outputAudio/{song}-{instrument.name}{appendix[i]}.wav",audio, FS)


if __name__ == "__main__":

	song 		= "melodia_08"
	instrument 	= "piano"
	base 		= "base_08.wav"

	#stessa canzone a volumi diversi -20 -15 -10

	instruments = ["frenchhorn","harpsichord","panflute", "piano", "saw", "trumpet","violin"]

	# for instrument in instruments:
	# 	print(instrument, end="")
	# 	synthesize(song, instrument, base, emphasis)
	# 	print()


	numSongs = 8

	for instrument in instruments:
		print(instrument, end="")
		for s in range(1, numSongs+1):
			song = f"melodia_0{s}"
			base = f"base_0{s}.wav"
			synthesize(song, instrument, base, True)
			print()


