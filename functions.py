import mido
from os import listdir
from pydub import AudioSegment


#cambia il pitch specificando il numero di semitoni
def pitchChange(sound, change):
	"""
		adjuste the pitch by change semitones
	"""
	semitoneDistance = 2 ** (1/12)

	speed = (semitoneDistance**change)
	newAudio = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * speed)})
	return newAudio.set_frame_rate(sound.frame_rate)

def adjustLength(sound:AudioSegment, durationDesired):
	"""
		Adjust from the center cutting the samples or looping them
	"""
	#half in ms
	half = sound.duration_seconds * 1000 / 2

	#cut samples from the center
	if sound.duration_seconds>durationDesired:
		#per compensare il crossfade
		toTrim = (sound.duration_seconds - durationDesired) * 1000 
		
		#at most 400ms but I try to crossfade all the two parts when they are too short 
		crossfade = int(durationDesired * 1000)%400

		#It will be trimmed by the crossfade
		toTrim -= crossfade 

		#first half
		adjusted = sound[:half-toTrim/2]
		#second half
		adjusted = adjusted.append(sound[half+toTrim/2:], crossfade)
		
	else:
		toAdd = (durationDesired - sound.duration_seconds) * 1000
		widthOfLoop = sound.duration_seconds * 1000 / 4
		toLoop = sound[half-widthOfLoop:half+widthOfLoop]
		
		start =  sound[:half]
		end = sound[half:]


		internalCrossfade = 300
		excess = len(toLoop) - toAdd % (len(toLoop) - internalCrossfade)

		#I search an internalCrossfade that leaves an excess of 1 s that I can use to crossfade the start and the end. (To minimize jumps of the sound)
		#The internalCrossfade must prevent excess too long for the length of the start and the end of the sound.
		while (excess < 1200 or excess/2 > len(start) or excess/2 > len(end)):
			internalCrossfade-=5
			#I predict the excess
			excess = len(toLoop) - toAdd % (len(toLoop) - internalCrossfade)

			#safety condition
			if internalCrossfade < 0 : 
				internalCrossfade = 300 
				break

		#I initialize the middle with the single part to loop
		middle = toLoop
		while len(middle) < toAdd:
			middle = middle.append(toLoop, internalCrossfade)

		print(min(excess/2, len(start)))

		#I use the excess to crossfade the start and the end
		excess = len(middle) - toAdd

		print(min(excess/2, len(start)))

		#first part + middle
		adjusted = start.append(middle, min(excess/2, len(start)))
		#first part + middle + end
		adjusted = adjusted.append(end, min(excess/2, len(end)))	
	

	return adjusted



class MidiInterface:
	def __init__(self, midi:mido.MidiFile):
		self.midi = midi
		self.ticks_per_beat = midi.ticks_per_beat
		self.length = midi.length
		self.totalTicks = 0
		self.bpm = 0
		
		#merge all tracks
		self.allTracks = mido.merge_tracks(midi.tracks)

		for msg in self.allTracks:
			if not msg.is_meta:
				self.totalTicks += msg.time

		#calculate bpm of the file 
		self.bpm = (self.totalTicks / self.ticks_per_beat / self.length) * 60
		#tempo is microseconds per beat
		self._time = (1000000 * 60) / self.bpm 

	def duration(self, ticks):
		"""
			return the duration of the given ticks in the current midi file
		"""
		return mido.tick2second(ticks, self.ticks_per_beat, self._time)

	def track(self, index:int):
		"""
			return the track specified by index
		"""
		return self.midi.tracks[index]
	
	def __str__ (self):
		return self.midi.__str__()

class Note:
	def __init__ (self, note, countTicks, velocity):
		self.note = note
		self.startTime = countTicks
		self.velocity = velocity 

class Instrument:
	"""
		interface to the audio samples of the instrument
	"""
	def __init__(self, instrument):
		self.name = instrument
		self.path = "instruments/%s/"%self.name
		self.extension = ""

		#leggo il range di note disponibili per lo strumento scelto
		try:
			rangeFile = open(self.path + "range.txt", "r")
			self.rangeNotes = tuple(rangeFile.readline().split())
			self.extension = rangeFile.readline()
			self.notes = listdir(self.path)
		except FileNotFoundError :
			raise FileNotFoundError("Range file missing in instrument directory!\n")
			
		