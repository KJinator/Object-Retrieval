# linesensor.py
# defines the code to operate the homemade line sensor usign gpio pins

import RPi.GPIO as GPIO

# class to control the line sensor and take input
class LineSensor(object):
	# constructor, initialize pins
	def __init__(self):
		self.pins = [22, 23]
		GPIO.setup(self.pins[0], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(self.pins[1], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	# returns a list of the 2 line sensor values
	def readLineValues(self):
		values = ["white", "white"]
		for i in range(len(self.pins)):
			if GPIO.input(self.pins[i]) == True:
				values[i] = "black"
		return values
