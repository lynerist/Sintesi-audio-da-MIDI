import mido
from functions import *
import soundfile as sf

def synthesize(song, instrument, base = ""):

	try:
		instrument = Instrument(instrument)
	except FileNotFoundError as e :
		print(e)
		exit()

	midi = MidiInterface(mido.MidiFile(f"midi/{song}.mid", clip=True))
	duration = midi.duration

	#verifico se esiste una base:
	if base != "":
		audio = sf.read(f"basi/{base}")[0]
		if audio.ndim > 1:
			audio = np.asarray([r + l for [l, r] in audio])
		audio = audio/2
	else:
		# genero un file audio vuoto lungo quanto il file midi (+1500 per non troncare alla fine)
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

				#calcolato sulla velocity è un valore negativo nel range [-18, 0] che viene usato per applicare una riduzione massima di 18dB
				volume = (note.velocity/127)*18 - 18

			
				#durata della nota midi
				noteLength = duration(countTicks-note.startTime)

				#scrivo il campione (prima adatto la durata del campione)
				
				endAttack = instrument.endOfAttackStartOfRelease[msg.note][0]
				startRelease = instrument.endOfAttackStartOfRelease[msg.note][1]


				adjustedLengthNote = adjustLength(audioNote, noteLength, instrument.loopable, endAttack, startRelease)

				offset = int(duration(note.startTime) * FS) 

				#print(len(adjustedLengthNote), len(audio[offset:offset + len(adjustedLengthNote)]))

				# Verificare se è giusto

				#np.add(audio[offset:offset + len(adjustedLengthNote)], adjustedLengthNote)
				
				# divido la nota per questo fattore per conferire dinamica al pezzo.
				dynamicFactor = 25 - (note.velocity/127)*24
				
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

	#audio = audio/2 #Prevent clipping

	sf.write(f"outputAudio/{song}-{instrument.name}.wav",audio, FS)


if __name__ == "__main__":

	song 		= "melodia_01"
	instrument 	= "saw"
	base 		= "base_01.wav"

	#frenchhorn-panflute-harpsichord-trumpet-violin
	synthesize(song, instrument, base)