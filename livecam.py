# livecam.py
# This file contains the code for using the picamera as a live camera stream
# It also defines a thread for the camera, since it runs too slowly for the main loop

from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
from PIL import Image, ImageTk
import threading

# thread for the camera to run in the background
class piCamThread(threading.Thread):
	# constructor, takes piCam as input
	def __init__(self, camera):
		super().__init__()
		self.camera = camera
	# thread runs this code
	def run(self):
		self.camera.takeImage()

# class for the picamera hardware control
class piCam(object):
	# constructor, intialize the camera
	def __init__(self):
		self.camera = PiCamera()
		self.rawData = PiRGBArray(self.camera)
		self.image = None
		self.imageSize = 300
		self.finishedImage = None
	
	# take a frame
	def takeImage(self):
		self.rawData.truncate(0)
		self.camera.capture(self.rawData, format="bgr")
		self.image = self.rawData.array
		self.image = cv2.flip(self.image, -1)

	# convert the image to a tkinter image for viewing
	def getCurrTkImage(self):
		return ImageTk.PhotoImage(Image.fromarray(cv2.resize(self.image, (self.imageSize, self.imageSize))))
