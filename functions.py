import mido
import os
from pydub import AudioSegment
import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write

FS = 44100	

#cambia il pitch specificando il numero di semitoni
def pitchChange(sound, change):
	"""
		adjuste the pitch by change semitones
	"""
	semitoneDistance = 2 ** (1/12)
	#TODO guardare numpy interp1


	speed = (semitoneDistance**change)
	newAudio = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * speed)})
	return newAudio.set_frame_rate(sound.frame_rate)


def pitchChangeNp(sound:np.array, change):
	if change == 0: return sound

	semitoneDistance = 2 ** (1/12)
	speed = (semitoneDistance**change)
	
	oldSpeed = np.arange(0, len(sound)/FS, 1/FS)
	newSpeed = np.arange(0, len(sound)/(FS * speed), 1/(FS * speed))[:len(sound)]
	
	#print(len(oldSpeed), len(newSpeed), len(sound), "speed: ", speed)

	return fadeOut(np.interp(oldSpeed, newSpeed, sound), 2000)

def adjustLengthNp(note:np.array, durationDesired, loopable, endOfAttack, startOfRelease):
	samplesInNote = len(note)
	samplesDesired = int(durationDesired * FS)
	halfNote = int(samplesInNote/2)

	#Se è troppo corta restituisco crossfade di attacco più rilascio
	if samplesDesired < endOfAttack + startOfRelease:
		return crossfade(note[:endOfAttack], note[-startOfRelease:])

	if samplesInNote > samplesDesired:
		halfSamplesToTrim = int((samplesInNote - samplesDesired)/2)

		endFirstHalfIndex = halfNote - halfSamplesToTrim

		startSecondHalfIndex =  halfNote + halfSamplesToTrim
		


		#print(minSampleEndStart, minSampleStartEnd)

		return crossfade(note[:endFirstHalfIndex], note[startSecondHalfIndex:])

	
	return note
			



def adjustLength(sound:AudioSegment, durationDesired, loopable):
	#TODO ping pong
	#TODO attacco 12/15 ms
	attack = 15
	#TODO rilascio 30/40 ms + fade out
	release = 40
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
		adjusted = sound[:max(half-toTrim/2, attack)]

		#second half
		adjusted = adjusted.append(sound[max(half+int(toTrim/2), release):], crossfade)


	elif loopable:
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

		#I use the excess to crossfade the start and the end
		excess = len(middle) - toAdd

		#first part + middle
		adjusted = start.append(middle, min(excess/2, len(start)))
		#first part + middle + end
		adjusted = adjusted.append(end, min(excess/2, len(end)))	
	else:
		adjusted = sound
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
		self.tracks = midi.tracks
		self.ntracks = len(midi.tracks)

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
		self.note = int(note)
		self.startTime = countTicks
		self.velocity = velocity 

class Instrument:
	"""
		interface to the audio samples of the instrument

		info file contains:
			minNote maxNote
			loopable/not loopable
			attack and realeases samples
		
	"""
	def __init__(self, instrument):
		self.name = instrument
		self.path = f"instruments/{self.name}/"
		self.loopable = False

		#leggo il range di note disponibili per lo strumento scelto
		try:
			infoFile = open(self.path + "info.txt", "r")
			self.rangeNotes = tuple(infoFile.readline().split())
			self.notes = [int(x[:-4]) for x in os.listdir(self.path) if len(x) < 8]
			self.notes.sort()
			self.loopable = infoFile.readline() == "loopable"
			self.endOfAttackStartOfRelease = dict()
			attacksAndReleases = [ [int(x) for x in ar.split(",")] for ar in infoFile.readline().split()]
			for index, note in enumerate(self.notes):
				self.endOfAttackStartOfRelease[note] = attacksAndReleases[index]
		except FileNotFoundError :
			raise FileNotFoundError("Info file missing in instrument directory!\n")
			
		
def crossfade(first, second, crossfadeSamples = 500):
	"""
		len specifies crossfade in samples
	"""

	fadeOut = np.multiply(first[-crossfadeSamples:], np.array([(x/crossfadeSamples)**0.5 for x in range(crossfadeSamples, 0, -1)])) 
	fadeIn  = np.multiply(second[:crossfadeSamples], np.array([(x/crossfadeSamples)**0.5 for x in range(0, crossfadeSamples,  1)])) 

	return np.concatenate((first[:-crossfadeSamples], np.add(fadeOut, fadeIn), second[crossfadeSamples:]))

def fadeIn(audio, fadeInSamples = 500):
	fadeIn  = np.multiply(audio[:fadeInSamples], np.array([(x/fadeInSamples)**0.5 for x in range(0, fadeInSamples,  1)])) 
	return np.concatenate((fadeIn, audio[fadeInSamples:]))

def fadeOut(audio, fadeOutSamples = 500):
	fadeOut = np.multiply(audio[-fadeOutSamples:], np.array([(x/fadeOutSamples)**0.5 for x in range(fadeOutSamples, 0, -1)])) 
	return np.concatenate((audio[:-fadeOutSamples], fadeOut))


# if __name__ == "__main__":
# 	a = np.array([0.2, 0.4, 0.5, 0.4, 0.2, 0])
# 	b = np.array([0.5, 0.6, 0.9, 0.7, 0.5, 0.3, 0.1, 0])

# 	print(crossfade(a, b, 4))