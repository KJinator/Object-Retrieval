# singleshot.py
# This file contains code relating to the opencv/dnn/tensorflow object detection.
# It defines the DetectorThread and SSD classes.  SSD makes inferences, and
# DetectorThread allows inferences to be made outside the main thread.

import numpy as np
import cv2
import os
from PIL import Image, ImageTk
import threading
from detections import *

# thread for the detector to run in the background
class DetectorThread(threading.Thread):
	# constructor, takes detector as input
	def __init__(self, detector):
		super().__init__()
		self.detector = detector
	# thread runs this code
	def run(self):
		SSD.takeImage("currentFrame.jpg")
		self.detector.detectObjects()

# class for single shot detectors
class SSD(object):
	# constructor, takes a model and its corresponding information as input
	def __init__(self, protoPath, modelPath, labels, confidenceErrorMargin):
		self.labels = labels
		self.confidenceErrorMargin = confidenceErrorMargin
		self.net = cv2.dnn.readNetFromTensorflow(modelPath, protoPath)
		self.imageSize = 300
	
	# initialize the camera by changing uvcvideo settings
	# without this, usb webcams are glitchy on a raspberry pi
	@staticmethod
	def initCamera():
		os.system("sudo rmmod uvcvideo")
		os.system("sudo modprobe uvcvideo nodrop=1 timeout=5000")
	
	@staticmethod
	# take an image from command line
	def takeImage(fileName):
		os.system("sudo fswebcam -S 20 -d /dev/video0 " + fileName)
	
	# converts current frame to a tkinter image
	def getCurrTkImage(self):
		b, g, r = cv2.split(cv2.resize(cv2.imread("currentFrame.jpg"), (self.imageSize, self.imageSize)))
		return ImageTk.PhotoImage(Image.fromarray(cv2.merge((r, g, b))))
	
	# detect objects in the current image, dump information in labelData
	def detectObjects(self):
		# load the current frame at 300x300 pixels, as this version of mobilenet requires
		frame = cv2.resize(cv2.imread("currentFrame.jpg"), (self.imageSize, self.imageSize))
		frameH = frame.shape[0]
		frameW = frame.shape[1]
		# set the current image at the input node
		self.net.setInput(cv2.dnn.blobFromImage(frame, size=(self.imageSize, self.imageSize), swapRB=True, crop=False))
		# run image through the network
		detectedObjects = self.net.forward()
		self.labelData = []
		for i in range(detectedObjects.shape[2]): # loop through detected objects
			confidence = detectedObjects[0, 0, i, 2]
			if confidence > self.confidenceErrorMargin:
				boundingBox = detectedObjects[0, 0, i, 3:7] # get the corners (0 to 1)
				boundingBox *=  np.array([frameW, frameH, frameW, frameH]) # convert to pixel values
				labelIndex = int(detectedObjects[0, 0, i, 1])
				x0, y0, x1, y1 = boundingBox.astype("int") # convert to integer pixel value approximations
				self.labelData.append((self.labels[labelIndex], confidence, (x0, y0, x1, y1)))
				Detection.detectedLabels.add(self.labels[labelIndex])
