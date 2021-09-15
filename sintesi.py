import mido
from functions import *
import soundfile as sf

def synthesize(song, instrument, base = "", emphasis = 0):

	try:
		instrument = Instrument(instrument)
	except FileNotFoundError as e :
		print(e)
		exit()

	midi = MidiInterface(mido.MidiFile(f"midi/{song}.mid"))
	duration = midi.duration
	
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

	#verifico se esiste una base:
	if base != "":
		base = sf.read(f"basi/{base}")[0]
		
		#la rendo mono
		if base.ndim > 1: 
			base = np.asarray([r + l for [l, r] in base])
				
		#adatto il volume allo strumento
		#calcolo loundess rms(escludo sotto 70 dB) le porto a -20 dB
		#al ^2,  media, r sqrt
		#divido in finestre, elimino quelle con quasi silenzio
		#unisco tutto di nuovo e calcolo rms 
		#rendo mono la base
		
		base = normalize(base, -20)
		audio = normalize(audio, [-20, -15, -10][emphasis])

		#per evitare out of range rendo l'audio finale il più lungo dei due
		if len(base) > len(audio): 
			audio, base = base, audio
		for i, c in enumerate(base):
			audio[i] += c

	sf.write(f"outputAudio/{song}-{instrument.name}.wav",audio, FS)


if __name__ == "__main__":

	song 		= "melodia_06"
	instrument 	= "piano"
	base 		= "base_06.wav"
	emphasis	=  0 # 0 / 1 / 2

	#frenchhorn-panflute-harpsichord-trumpet-violin-saw

	#stessa canzone a volumi diversi -20 -15 -10

	instruments = ["frenchhorn","harpsichord","panflute", "piano", "saw", "trumpet","violin"]

	for instrument in instruments:
		print(instrument, end="")
		synthesize(song, instrument, base, emphasis)
		print()

