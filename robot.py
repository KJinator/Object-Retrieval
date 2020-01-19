# robot.py
# This file contains the Robot class, which puts movement and low-level sensing code together
# Functionality specific to this robot is defined here

from servo import *
from linesensor import *
import threading
from robotmodes import *

# robot class, puts together hardware code
class Robot(object):
	# constructor, intializes hardware
	def __init__(self):
		GPIO.setmode(GPIO.BCM) # use broadcom SOC pins for cross-compatibility with other pi's
		# PINS:
		# left servo: 17
		# right servo: 18
		# left line sensor: 22
		# right line sensor: 23
		self.leftServo = Servo(17)
		self.rightServo = Servo(18)
		self.linesensors = LineSensor()
		self.videoDisplay = None # this must be set manually after the display has been created
		self.detector = None # this must be set manually after the display has been created
		self.thread = None
		self.position = 0 # the unit is the distance covered by the robot in 1 second
		self.accuratePosition = 0 # this is in feet, and is modified only using higher fidelity localization than odometry

	# move the robot in a given direction
	def drive(self, direction, speed=1):
		if direction == "forward":
			self.leftServo.setSpeed(speed)
			self.rightServo.setSpeed(speed)
		elif direction == "left":
			self.leftServo.setSpeed(0)
			self.rightServo.setSpeed(speed)
		elif direction == "right":
			self.leftServo.setSpeed(speed)
			self.rightServo.setSpeed(0)

	# stop driving
	def stop(self):
		self.leftServo.setSpeed(0)
		self.rightServo.setSpeed(0)
		
	# stop the thread running movements
	def stopCurrentThread(self):
		self.thread.stop()
		self.thread.join()

	# start line following, create a new thread
	def lineFollow(self):
		self.thread = LineFollowThread(self, self.videoDisplay, self.detector)
		self.thread.start()
		
	# retrieve the student id
	def retrieve(self):
		self.thread = RetrieveThread(self, self.videoDisplay, self.detector)
		self.thread.start()

	# locate the crocs and drive to them
	def findCrocs(self):
		self.thread = findCrocsThread(self, self.videoDisplay, self.detector)
		self.thread.start()
		
	# drive to the door
	def findDoor(self):
		self.thread = findDoorThread(self, self.videoDisplay, self.detector)
		self.thread.start()
