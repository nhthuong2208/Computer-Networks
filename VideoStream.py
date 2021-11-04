class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		self.Cache = self.cache()

		try:
			self.file = open(filename, 'rb')
		except:
			raise IOError
		self.frameNum = 0
		
	# def nextFrame(self):
	# 	"""Get next frame."""
	# 	data = self.file.read(5) # Get the framelength from the first 5 bits
	# 	if data: 
	# 		framelength = int(data)
							
	# 		# Read the current frame
	# 		data = self.file.read(framelength)
	# 		self.frameNum += 1
	# 	return data
	
	def nextFrame(self):
		self.frameNum += 1
		if self.frameNum >= self.get_length():
			self.frameNum = self.get_length()
		return self.Cache[self.frameNum - 1]

	def cache(self):
		s = []
		file = open(self.filename, 'rb')
		while True:
			data = file.read(5)
			if data:
				frameLength = int(data)

				#Read the current frame
				data = file.read(frameLength)
				s.append(data)
			else:
				break
		return s
		
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum

	def set_frameNbr(self, number):
		self.frameNum = number
		if self.frameNum < 0:
			self.frameNum = 0
		elif self.frameNum >= self.get_length():
			self.frameNum = self.get_length() - 1

	def get_length(self):
		return len(self.Cache)
	
	