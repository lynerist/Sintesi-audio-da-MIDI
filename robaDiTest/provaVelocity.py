import mido
import pydub
from functions import *

audio = pydub.AudioSegment.silent(20000)
instrument = "violin"
instrumentPath = "instruments/" + instrument + "/"

audioNote = pydub.AudioSegment.from_file(instrumentPath + "74.wav")
noteLength = 1.00

pydub.effects

for i in range(0,9):
	variation = -(i+1)*3
	audio = audio.overlay(adjustLength(audioNote, noteLength) + variation, i*2000)


audio.export("testVelocity.wav", "wav")


