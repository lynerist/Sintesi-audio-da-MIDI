import mido
from functions import *

song 		= "evangelion"
instrument 	= "trumpet"

try:
	instrument = Instrument(instrument) 
except FileNotFoundError as e :
	print(e)
	exit()

midi = MidiInterface(mido.MidiFile(f"midi/{song}.mid", clip=True))
duration = midi.duration


# genero un file audio vuoto lungo quanto il file midi (+500 per non troncare alla fine)
audio = AudioSegment.silent(midi.length*1000 + 500)

# il clock nella traccia
countTicks = 0

# Dizionario per salvarmi il tick di inizio dei note on per poi associarli ai note off relativi
noteOnCollection = dict()

# Per visualizzare l'elaborazione nel tempo
loading = 0

# cache dove salvo le note già suonate per non ricercarle
cacheAudioSamples = dict()

# Scorro ogni messaggio
for msg in midi.allTracks:
	#Ignoro tutti gli altri messaggi per ora
	if msg.type == "note_on":
		countTicks += msg.time	# Clock		
		noteOnCollection[msg.note] = Note(msg.note, countTicks, msg.velocity)

	elif msg.type == "note_off":
		countTicks += msg.time	# Clock

		#recupero la nota
		note = noteOnCollection[msg.note]

		if note.note in cacheAudioSamples.keys(): 
			audioNote = cacheAudioSamples[note.note]
		else:
			#controllo se sono fuori range  (Da sistemare)
			if int(msg.note) < int(instrument.rangeNotes[0]) or int(msg.note) > int(instrument.rangeNotes[1]):
				audioNote = AudioSegment.from_file(instrument.path + instrument.rangeNotes[int(msg.note) > int(instrument.rangeNotes[1])] + "." + instrument.extension)
				audioNote = pitchChange(audioNote, (int(msg.note) - int(instrument.rangeNotes[int(msg.note) > int(instrument.rangeNotes[1])])))
			else:	
				offset = 0
				while not "%d.%s"%(note.note - offset, instrument.extension) in instrument.notes:
					offset += 1
				audioNote = AudioSegment.from_file("%s%d.%s"%(instrument.path, note.note - offset, instrument.extension))
				audioNote = pitchChange(audioNote, offset)

			cacheAudioSamples[note.note] = audioNote				

		#calcolato sulla velocity è un valore negativo nel range [-18, 0] che viene usato per applicare una riduzione massima di 18dB
		volume = (note.velocity/127)*18 - 18


		#durata della nota midi
		noteLength = duration(countTicks-note.startTime)
		#scrivo il campione (prima adatto la durata del campione)
		
		audio = audio.overlay(adjustLength(audioNote, noteLength) + volume, duration(note.startTime) * 1000)

		currentLoading = countTicks/midi.totalTicks*100
		if (currentLoading) - loading > 1:
			print("%.2f %%"%(currentLoading))
			loading = (currentLoading)
			
#Se non esiste creo la directory dove collezionare gli output
if not os.path.exists("outputAudio"):
	os.mkdir("outputAudio")

audio.export(f"outputAudio/{song}-{instrument.name}.wav", "wav")

			
			
