class Classifier:
	def __init__(self, model, input_layer, output_layer, filename):
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

		self.model = model
		# Algorithms for mel-spectrogram computation
		self.audio = MonoLoader(filename=filename, sampleRate=sampleRate)

		self.fc = FrameCutter(frameSize=frameSize, hopSize=hopSize)

		self.w = Windowing(normalized=False)

		self.spec = Spectrum()

		self.mel = MelBands(numberBands=numberBands, sampleRate=sampleRate,
							highFrequencyBound=sampleRate // 2, 
							inputSize=frameSize // 2 + 1,
							weighting=weighting, normalize=normalize,
							warpingFormula=warpingFormula)


		# Algorithms for logarithmic compression of mel-spectrograms
		self.shift = UnaryOperator(shift=1, scale=10000)

		self.comp = UnaryOperator(type='log10')

		# This algorithm cuts the mel-spectrograms into patches
		# according to the model's input size and stores them in a data
		# type compatible with TensorFlow
		self.vtt = VectorRealToTensor(shape=[1, 1, patchSize, numberBands])


		# Auxiliar algorithm to store tensors into pools
		self.ttp = TensorToPool(namespace=input_layer)

		# The core TensorFlow wrapper algorithm operates on pools
		# to accept a variable number of inputs and outputs
		self.tfp = TensorflowPredict(graphFilename=model,
                        			 inputs=[input_layer],
                        			 outputs=[output_layer])

		# Algorithms to retrieve the predictions from the wrapper
		self.ptt = PoolToTensor(namespace=output_layer)

		self.ttv = TensorToVectorReal()

		# Another pool to store output predictions
		self.pool = Pool()

	def link(self):
		self.audio.audio    >>  self.fc.signal
		self.fc.frame       >>  self.w.frame
		self.w.frame        >>  self.spec.frame
		self.spec.spectrum  >>  self.mel.spectrum
		self.mel.bands      >>  self.shift.array
		self.shift.array    >>  self.comp.array
		self.comp.array     >>  self.vtt.frame
		self.vtt.tensor     >>  self.ttp.tensor
		self.ttp.pool       >>  self.tfp.poolIn
		self.tfp.poolOut    >>  self.ptt.pool
		self.ptt.tensor     >>  self.ttv.tensor
		self.ttv.frame      >>  (self.pool, output_layer)

		# Store mel-spectrograms to reuse them later in this tutorial
		self.comp.array     >>  (self.pool, "melbands")