# servo.py
# This file contains the Servo class and code for controlling servos

import RPi.GPIO as GPIO

# class to hold all servo control code
class Servo(object):
	# constructor, takes a pwm pin and intializes servo
	def __init__(self, pin):
		self.pin = pin
		self.frequency = 50 # 50 Hz for most servos
		GPIO.setup(pin, GPIO.OUT)
		self.servo = GPIO.PWM(self.pin, self.frequency)
		self.pwmSignal = 0
		self.servo.start(0)

	# set the speed of the servo, input speed from -1 to 1
	def setSpeed(self, speed):
		# set speed to 0 rather than middle of range to stop twitching at 0 speed
		if speed == 0: self.pwmSignal = 0
		# duty cycle = signal / period, so signal/20 needs to be in the range 1 to 2
		else: self.pwmSignal = 7.5 + 2.5 * speed
		self.servo.ChangeDutyCycle(self.pwmSignal)
