import mido
from functions import *

song 		= "He_is_a_Pirate"
instrument 	= "frenchHorn"

try:
	instrument = Instrument(instrument)
except FileNotFoundError as e :
	print(e)
	exit()

midi = MidiInterface(mido.MidiFile(f"midi/{song}.mid", clip=True))
duration = midi.duration

#TODO essentia / madmom

# genero un file audio vuoto lungo quanto il file midi (+500 per non troncare alla fine)
audio = AudioSegment.silent(midi.length*1000 + 500)


# cache dove salvo le note già suonate per non ricercarle
cacheAudioSamples = dict()

#per ogni traccia applico il procedimento. 
for index, track in enumerate(midi.tracks):
	print(f"\ntrack {index +1}/{midi.ntracks} - ", end = " ")

	# il clock nella traccia
	countTicks = 0

	#TODO note off stoppa ogni nota del channel

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
				audioNote = AudioSegment.from_file(f"{instrument.path}{minDistanceNote}.{instrument.extension}")
				audioNote = pitchChange(audioNote, note.note - minDistanceNote)

				cacheAudioSamples[note.note] = audioNote				

			#calcolato sulla velocity è un valore negativo nel range [-18, 0] che viene usato per applicare una riduzione massima di 18dB
			volume = (note.velocity/127)*18 - 18

			#durata della nota midi
			noteLength = duration(countTicks-note.startTime)
			#scrivo il campione (prima adatto la durata del campione)
			
			audio = audio.overlay(adjustLength(audioNote, noteLength) + volume, duration(note.startTime) * 1000)


		currentLoading = countTicks/midi.totalTicks*100
		if (currentLoading) - loading > 10:
			print("%.1f %%"%(currentLoading), end = " ", flush=True)
			loading = (currentLoading)
			
#Se non esiste creo la directory dove collezionare gli output
if not os.path.exists("outputAudio"):
	os.mkdir("outputAudio")

audio.export(f"outputAudio/{song}-{instrument.name}.wav", "wav")

			
			
