#from _typeshed import SupportsLessThan
from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os
from time import time
import datetime

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:

	SWITCH = -1
	INIT = 0
	READY = 1
	PLAYING = 2
	state = SWITCH
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3
	SKIP = 4
	
	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)

		self.breakpoint = 0
		self.listfilm = filename
		self.index = -1
		self.played = 0
		self.removed = 0
		self.paused = 0

		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		self.index_frame = 0

	def delayfunc(self, x):
		start = time()
		while True:
			end = time()
			if (float(end - start) > float(x)):
				break
		
	# THIS GUI IS JUST FOR REFERENCE ONLY, STUDENTS HAVE TO CREATE THEIR OWN GUI 	
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)

		# Create Back button
		self.back = Button(self.master, width=20, padx=3, pady=3)
		self.back["text"] = "Back"
		self.back["command"] = lambda: self.pass_time(-2)
		self.back.grid(row=5, column=0, padx=2, pady=2)

		# Create Forward button
		self.forward = Button(self.master, width=20, padx=3, pady=3)
		self.forward["text"] = "Forward"
		self.forward["command"] = lambda: self.pass_time(2)
		self.forward.grid(row=5, column=1, padx=2, pady=2)

		self.start_time=Label(self.master,text=str(datetime.timedelta(seconds=0)))
		self.start_time.grid(row=4,column=0,sticky='ew')
		self.end_time=Label(self.master,text=str(datetime.timedelta(seconds=0)))
		self.end_time.grid(row=4,column=3,sticky='ew')

		# Create Select film button
		self.choose = Button(self.master, width=20, padx=3, pady=3)
		self.choose["text"] = "Select film"
		self.choose["command"] = self.nextfilm
		self.choose.grid(row=5, column=3, padx=2, pady=2)

		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 

	def nextfilm(self):
		if self.state != self.PLAYING:
			if self.played == 0:
				self.delayfunc(float(0.1))
				self.playMovie()
				print(self.sessionId)
			
			if self.played == 1:
				self.breakpoint = 1
				self.played = 0
				print(self.sessionId)
				if self.teardownAcked == 0:
					print(self.sessionId)
					self.delayfunc(float(0.1))
					self.exitClient()
					print('Teardown')
				print(self.sessionId)
				self.delayfunc(float(1))
				self.connectToServer()
				print(self.sessionId)
				self.breakpoint = 0

			self.index += 1
			if self.index == len(self.listfilm):
				self.index = 0
			self.fileName = self.listfilm[self.index]
			self.state = self.INIT
			self.choose["text"] = "File: " + str(self.fileName)

	def pass_time(self, time):
		self.index_frame = int(float(self.my_slider.get())*20) + time*20
		print('self.index_frame', self.index_frame)

		if self.index_frame < 0:
			self.index_frame = 0

		if self.state == self.PLAYING:
			self.pauseMovie()
			self.delayfunc(float(0.05))
			self.sendRtspRequest(self.SKIP)
			self.delayfunc(float(0.05))
			self.playMovie()
			self.delayfunc(float(0.05))
	
	def setupMovie(self):
		"""Setup button handler."""
		if self.state == self.INIT:
			self.delayfunc(float(0.5))
			self.removed = 0
			self.sendRtspRequest(self.SETUP)
			self.teardownAcked = 0
	#TODO
	
	def exitClient(self):
		"""Teardown button handler."""
		self.sendRtspRequest(self.TEARDOWN)
		print("Video data rate: " + str(self.rate) + "bytes/s")
		
	#TODO

	def pauseMovie(self):
		"""Pause button handler."""
		if self.state == self.PLAYING:
			self.sendRtspRequest(self.PAUSE)
			self.paused = 1
	#TODO
	
	def playMovie(self):
		"""Play button handler."""
		if self.state == self.READY:
			
			# Create new Thread to listen for RTP packets
			# threading.Thread(target = self.listenRtp).start()
			# self.playEvent = threading.Event()
			# self.playEvent.clear()
			self.sendRtspRequest(self.PLAY)
	#TODO

	def listenRtp(self):		
		"""Listen for RTP packets."""
		#TODO
		while True:
			self.playEvent.wait(0.01)
			if self.playEvent.isSet():
				break

			if self.teardownAcked == 1:
				print("Listen")
				if self.removed == 0:
					print("Listen")
					os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT)
					self.removed = 1
					self.sessionId = 0
				self.rtpSocket.close()
				break
			else:

				try:
					print("LISTENING...")
					data = self.rtpSocket.recv(20480)
					if data:
						rtpPacket = RtpPacket()
						rtpPacket.decode(data)
						self.rate = len(data)*20

						self.frameNbr = rtpPacket.seqNum()
						self.my_slider.set(self.frameNbr*0.05)
						self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
						self.slider_label['text'] = str(datetime.timedelta(seconds = self.my_slider.get()))

						# currFrameNbr = rtpPacket.seqNum()
						# print("Current Seq Num: " + str(currFrameNbr))
						
						# # Discard the late packet
						# if currFrameNbr > self.frameNbr:
						# 	self.frameNbr = currFrameNbr
						# 	self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
				except:
					self.loss += 1
					break
					
					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
	#TODO
		cacheName = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		file = open(cacheName, "wb")
		file.write(data)
		file.close()

		return cacheName
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
	#TODO
		photo = ImageTk.PhotoImage(Image.open(imageFile))
		self.label.configure(image = photo, height = 288)
		self.label.image = photo
		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
	#TODO
		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.rtspSocket.connect((self.serverAddr, self.serverPort))
		except:
			tkinter.messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' % self.serverAddr)
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	
		#-------------
		# TO COMPLETE
		#-------------
		
		if requestCode == self.SKIP and self.state != self.INIT:
			self.rtspSeq += 1

			# Write the RTSP request to be sent.
			request = 'SKIP ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId) + '\nIndex_frame: ' + str(self.index_frame)

			self.requestSent = self.SKIP
			self.state = self.READY
		
		# Setup request
		elif requestCode == self.SETUP and self.state == self.INIT:
			threading.Thread(target = self.recvRtspReply).start()

			# Update RTSP sequence number
			self.rtspSeq += 1

			# Write the RTSP request to be sent
			request = 'SETUP ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nTransport: RTP/UDP; client_port= ' + str(self.rtpPort)

			# Keep track of the sent request
			self.requestSent = self.SETUP

		# Play request
		elif requestCode == self.PLAY and self.state == self.READY:
			self.rtspSeq += 1
			request = 'PLAY ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId)
			self.requestSent = self.PLAY
			self.played = 1

		# Pause request
		elif requestCode == self.PAUSE and self.state == self.PLAYING:
			self.rtspSeq += 1
			request = 'PAUSE ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId)
			self.requestSent = self.PAUSE
			self.playEvent.set()

		# Teardown request
		elif requestCode == self.TEARDOWN and not self.state == self.INIT:
			self.rtspSeq += 1
			request = 'TEARDOWN ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId)
			self.requestSent = self.TEARDOWN


		else:
			return

		# Send the RTSP request using rtspSocket
		self.rtspSocket.send(request.encode('utf-8'))

		print('\nData sent:\n' + request)
	
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		#TODO
		while True:
			reply = self.rtspSocket.recv(1024)
			
			if reply:
				self.parseRtspReply(reply.decode("utf-8"))

			# Close the RTSP socket upon requesting Teardown
			if self.requestSent == self.TEARDOWN:
				if self.removed == 0 and self.breakpoint == 0 or self.removed == 0 and self.paused == 1:
					print("recv")
					os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT)
					self.removed = 1
					self.sessionId = 0
					self.paused = 0
				
				self.rtspSocket.close()
				break
	
	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server."""
		#TODO
		lines = data.split('\n')

		seqNum = int(lines[1].split(' ')[1])
		totalTime = float(lines[3].split(' ')[1])

		# Process if only the server reply's sequence number is the same as the request's
		if seqNum == self.rtspSeq:
			session = int(lines[2].split(' ')[1])

			# New RTSP session ID
			if self.sessionId == 0:
				self.sessionId = session

			# Process only if the session ID is the same
			if self.sessionId == session:
				if int(lines[0].split(' ')[1]) == 200:
					if self.requestSent == self.SETUP:
						if self.state == self.INIT:
							self.rate = 0
							self.loss = 0
							self.end_time['text'] = str(datetime.timedelta(seconds=totalTime))
							v = datetime.timedelta()
							self.my_slider = Scale(self.master, variable = v, from_ = 0, to = totalTime, orient=HORIZONTAL)
							self.my_slider.grid(row=2, column=0, columnspan=4, sticky='ew')
							
							self.slider_label = Label(self.master, text='0')
							self.slider_label.grid(row=3, columnspan=4, sticky='ew')
							# Update RTSP state
							self.state = self.READY

							# Open RTSP port
							self.openRtpPort()
					elif self.requestSent == self.PLAY and self.state == self.READY:
						self.state = self.PLAYING
						self.playEvent = threading.Event()
						self.threadlisten = threading.Thread(target=self.listenRtp)
						self.threadlisten.start()
					elif self.requestSent == self.PAUSE and self.state == self.PLAYING:
						self.state = self.READY

						# The PLAY thread exists, a new thread is created on resume
						
					elif self.requestSent == self.TEARDOWN and self.state != self.INIT:
						self.state = self.INIT

						# Flag the teardownAcked to close the socket
						self.teardownAcked = 1
					elif self.requestSent == self.SKIP and self.state != self.INIT:
						self.state = self.READY

	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		#-------------
		# TO COMPLETE
		#-------------
		# Create a new datagram socket to receive RTP packets from the server
		# self.rtpSocket = ...
		
		# Set the timeout value of the socket to 0.5sec
		# ...
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.rtpSocket.settimeout(0.5)

		try:
			# Bind the socket to address using RTP port given by the client user
			self.rtpSocket.bind(("", self.rtpPort))
		except:
			tkinter.messagebox.showwarning('Unable to bind', 'Unable to bind PORT=%d' % self.rtpPort)
			self.rtpSocket.shutdown(socket.SHUT_RDWR)
			self.state = self.INIT
			self.rtpSocket.close()
		
	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		#TODO
		self.pauseMovie()
		
		if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
			if self.teardownAcked != 1:
				self.exitClient()
			self.master.destroy()
		
		# When the user presses Cancel, resume playing
		else:
			self.playMovie()
