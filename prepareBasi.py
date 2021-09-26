from functions import *
import soundfile as sf

numeroBasi = 10

for n in range(1, numeroBasi+1):
	base = sf.read(f"basi/base_{n}.wav" if n>9 else f"basi/base_0{n}.wav")[0]
	
	#la rendo mono
	if base.ndim > 1: 
		base = np.asarray([r + l for [l, r] in base])

	#normalizzo
	base = normalize(base, -17)
	sf.write(f"outputAudio/base_{n}.wav" if n>9 else f"outputAudio/base_0{n}.wav",base, FS)
	print(n)

# base = sf.read(f"basi/base_07.wav")[0]
# if base.ndim > 1: 
# 	base = np.asarray([r + l for [l, r] in base])
# sf.write(f"outputAudio/base_07Mono.wav",base, FS)