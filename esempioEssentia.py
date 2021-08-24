modelName = 'networks/msd-musicnn-1.pb'
input_layer = 'model/Placeholder'
output_layer = 'model/Sigmoid'
msd_labels = ['rock','pop','alternative','indie','electronic','female vocalists','dance','00s','alternative rock','jazz','beautiful','metal','chillout','male vocalists','classic rock','soul','indie rock','Mellow','electronica','80s','folk','90s','chill','instrumental','punk','oldies','blues','hard rock','ambient','acoustic','experimental','female vocalist','guitar','Hip-Hop','70s','party','country','easy listening','sexy','catchy','funk','electro','heavy metal','Progressive rock','60s','rnb','indie pop','sad','House','happy']



#########################################################################################################



# analysis parameters
sampleRate = 16000
frameSize=512
hopSize=256

# mel bands parameters
numberBands=96
weighting='linear'
warpingFormula='slaneyMel'
normalize='unit_tri'

# model parameters
patchSize = 187



#########################################################################################################



from essentia.streaming import *
from essentia import Pool, run

filename = "outputAudio/evangelion-harpsichord.wav"

# Algorithms for mel-spectrogram computation
audio = MonoLoader(filename=filename, sampleRate=sampleRate)

fc = FrameCutter(frameSize=frameSize, hopSize=hopSize)

w = Windowing(normalized=False)

spec = Spectrum()

mel = MelBands(numberBands=numberBands, sampleRate=sampleRate,
               highFrequencyBound=sampleRate // 2, 
               inputSize=frameSize // 2 + 1,
               weighting=weighting, normalize=normalize,
               warpingFormula=warpingFormula)

# Algorithms for logarithmic compression of mel-spectrograms
shift = UnaryOperator(shift=1, scale=10000)

comp = UnaryOperator(type='log10')

# This algorithm cuts the mel-spectrograms into patches
# according to the model's input size and stores them in a data
# type compatible with TensorFlow
vtt = VectorRealToTensor(shape=[1, 1, patchSize, numberBands])

# Auxiliar algorithm to store tensors into pools
ttp = TensorToPool(namespace=input_layer)

# The core TensorFlow wrapper algorithm operates on pools
# to accept a variable number of inputs and outputs
tfp = TensorflowPredict(graphFilename=modelName,
                        inputs=[input_layer],
                        outputs=[output_layer])

# Algorithms to retrieve the predictions from the wrapper
ptt = PoolToTensor(namespace=output_layer)

ttv = TensorToVectorReal()

# Another pool to store output predictions
pool = Pool()



#########################################################################################################



audio.audio    >>  fc.signal
fc.frame       >>  w.frame
w.frame        >>  spec.frame
spec.spectrum  >>  mel.spectrum
mel.bands      >>  shift.array
shift.array    >>  comp.array
comp.array     >>  vtt.frame
vtt.tensor     >>  ttp.tensor
ttp.pool       >>  tfp.poolIn
tfp.poolOut    >>  ptt.pool
ptt.tensor     >>  ttv.tensor
ttv.frame      >>  (pool, output_layer)

# Store mel-spectrograms to reuse them later in this tutorial
comp.array     >>  (pool, "melbands")



#######################################################################################################



from time import time

start_time = time()

run(audio)

print('Prediction time: {:.2f}s'.format(time() - start_time))




#######################################################################################################



import numpy as np

print('Most predominant tags:')
for i, l  in enumerate(np.mean(pool[output_layer],
                       axis=0).argsort()[-3:][::-1], 1):
    print('{}: {}'.format(i, msd_labels[l]))



#######################################################################################################



import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = [12, 20]

f, ax = plt.subplots()
ax.matshow(pool[output_layer].T, aspect=1.5)
_ = plt.yticks(np.arange(50), msd_labels, fontsize=11)



#######################################################################################################



import essentia.standard as es

predict = es.TensorflowPredict(graphFilename=modelName,
                               inputs=[input_layer],
                               outputs=[output_layer])

in_pool = Pool()



#######################################################################################################



bands = pool['melbands']
discard = bands.shape[0] % patchSize  # Would not fit into the patch.

bands = np.reshape(bands[:-discard,:], [-1, patchSize, numberBands])
batch = np.expand_dims(bands, 2)

in_pool.set('model/Placeholder', batch)

out_pool = predict(in_pool)

print('Most predominant tags:')
for i, l in enumerate(np.mean(out_pool[output_layer].squeeze(),
                       axis=0).argsort()[-3:][::-1], 1):
    print('{}: {}'.format(i, msd_labels[l]))




    