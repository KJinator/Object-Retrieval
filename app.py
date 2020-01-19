# app.py
# This file contains the App object, and code for drawing the app view using tkinter.
# All gui code is here, and this code is run in the main thread in __init__.py for maximum
# responsiveness to user input.

from tkinter import *
import time
from detections import *

# class for the main app
class App(object):
	# constructor, intialize canvas
	def __init__(self, robot):
		self.robot = robot
		self.width, self.height = 800, 500
		self.imageSize = 300
		self.margin = 10
		self.tfX = self.imageSize//2 + self.margin
		self.tfY = self.imageSize//2 + self.margin
		self.root = Tk()
		self.root.resizable(width=False, height=False)
		self.canvas = Canvas(self.root, width=self.width, height=self.height)
		self.canvas.configure(bd=0, highlightthickness=0)
		self.canvas.pack()
		self.root.config(cursor="none")
		self.lines = ["white", "white"]
		self.lineWidth = 85
		self.menuY = self.imageSize + self.margin
		# bind keys to methods
		self.root.bind("<Left>", self.left)
		self.root.bind("<Right>", self.right)
		self.root.bind("<Up>", self.up)
		self.root.bind("<Down>", self.down)
		self.root.bind("<Return>", self.enter)
		self.selectedButton = 0
		self.selectedColumn = 0
		self.numButtons = [4, 3]
		self.buttonList = [["Teleop", "Find Key", "Help", "Quit"], ["Pick Up Key", "Drive to Crocs", "Drive to Door"]]
		self.mode = "idle"
		self.startTime = 0
		self.quitting = False
		self.mapWidth = 190
		self.mapHeight = 170
		self.finished = False
		
	# method for left arrow
	def left(self, event):
		if self.mode == "teleop":
			self.robot.drive("left")
		elif self.mode == "idle" and not self.selectedButton == 3:
			self.selectedColumn = (self.selectedColumn + 1) % 2

	# method for right arrow
	def right(self, event):
		if self.mode == "teleop":
			self.robot.drive("right")
		elif self.mode == "idle" and not self.selectedButton == 3:
			self.selectedColumn = (self.selectedColumn + 1) % 2

	# method for up arrow
	def up(self, event):
		if self.mode == "idle":
			self.selectedButton = (self.selectedButton - 1) % self.numButtons[self.selectedColumn]
		elif self.mode == "teleop":
			self.robot.drive("forward")

	# method for down arrow
	def down(self, event):
		if self.mode == "idle":
			self.selectedButton = (self.selectedButton + 1) % self.numButtons[self.selectedColumn]
		elif self.mode == "teleop":
			self.robot.stop()
		
	# method for return/enter key
	def enter(self, event):
		if self.mode == "idle":
			if self.selectedColumn == 0:
				if self.selectedButton == 0:
					self.mode = "teleop"
				elif self.selectedButton == 1:
					self.mode = "search"
					self.robot.lineFollow()
					self.startTime = time.time()
				elif self.selectedButton == 2:
					self.mode = "help"
				elif self.selectedButton == 3:
					if not self.robot.thread == None:
						self.robot.stopCurrentThread()
					self.quitting = True
			else:
				if self.selectedButton == 0:
					self.mode = "retrieve"
					self.robot.retrieve()
				elif self.selectedButton == 1:
					self.mode = "findcrocs"
					self.robot.findCrocs()
				elif self.selectedButton == 2:
					self.mode = "finddoor"
					self.robot.findDoor()
		elif self.mode == "teleop" or self.mode == "help":
			self.mode = "idle"
			self.robot.stop()
		else: # robot is running a movement/action thread
			self.mode = "idle"
			self.robot.stopCurrentThread()

	# draw an image on the canvas
	def drawImage(self, img, location):
		if location == "left":
			self.leftImg = img # this avoids python's garbage collection from removing the image
			return self.canvas.create_image(self.tfX, self.tfY, image=self.leftImg)
		elif location == "right":
			self.rightImg = img
			return self.canvas.create_image(self.tfX + self.imageSize, self.tfY, image=self.rightImg, tags="liveCam")
	
	# draw the lines to show the line location
	def drawLines(self):
		self.canvas.create_rectangle(self.width - self.margin, self.margin,\
			self.width - self.margin - self.lineWidth, self.imageSize + self.margin, fill=self.lines[1], tags="gui")
		self.canvas.create_rectangle(self.width - self.margin - 2 * self.lineWidth, self.margin,\
			self.width - self.margin - self.lineWidth, self.imageSize + self.margin, fill=self.lines[0], tags="gui")

	# draw the bounds and name for objects given by a list of label information
	def drawBounds(self, labelData):
		for label, confidence, (x0, y0, x1, y1) in labelData:
			self.canvas.create_rectangle(x0 + self.margin, y0 + self.margin, x1 + self.margin, y1 + self.margin, fill=None, width=5, outline="green")
			self.canvas.create_text(x0 + (x1-x0)//2 + self.margin, y0 + self.margin, text = label, anchor = "n", font = "Arial 10 bold", fill = "green")

	# draw the buttons in the bottom left, all tagged with "gui"
	def drawButtons(self):
		self.canvas.delete("gui")
		buttonW = 125
		buttonH = (self.height - self.imageSize - (2 + self.numButtons[0]) * self.margin) // self.numButtons[0]
		for i in range(self.numButtons[0]):
			color = "blue"
			textColor = "white"
			if i == self.selectedButton and self.selectedColumn == 0:
				color = "white"
				textColor = "blue"
			x0 = self.margin
			y0 = 2 * self.margin + self.imageSize + i * (buttonH + self.margin)
			x1 = x0 + buttonW
			y1 = y0 + buttonH
			self.canvas.create_rectangle(x0, y0, x1, y1, width=4, tags="gui", fill=color)
			self.canvas.create_text(x0 + (x1 - x0) / 2, y0 + (y1 - y0) / 2, text=self.buttonList[0][i], fill=textColor, tags="gui")
		for i in range(self.numButtons[1]):
			color = "blue"
			textColor = "white"
			if i == self.selectedButton and self.selectedColumn == 1:
				color = "white"
				textColor = "blue"
			x0 = self.margin * 2 + buttonW
			y0 = 2 * self.margin + self.imageSize + i * (buttonH + self.margin)
			x1 = x0 + buttonW
			y1 = y0 + buttonH
			self.canvas.create_rectangle(x0, y0, x1, y1, width=4, tags="gui", fill=color)
			self.canvas.create_text(x0 + (x1 - x0) / 2, y0 + (y1 - y0) / 2, text=self.buttonList[1][i], fill=textColor, tags="gui")
		action = "Idle"
		if self.mode == "teleop":
			action = "Teleop"
		elif self.mode == "search":
			action = "Searching for ID"
		elif self.mode == "retrieve":
			action = "Retrieving ID"
		elif self.mode == "findcrocs":
			action = "Driving to Crocs"
		elif self.mode == "finddoor":
			action = "Driving to Door"
		self.canvas.create_text(self.margin * 4 + 2 * buttonW + self.width/6.4, 2 * self.margin + self.imageSize, \
		text="Current action:\n" + action, fill="black", anchor="nw", tags="gui", font="Arial 16")

	# draw the labels already seen
	def drawLabels(self, labels):
		buttonW = 125
		self.canvas.create_text(self.margin * 3 + 2 * buttonW, 2 * self.margin + self.imageSize,\
			text="Objects seen so far:\n" + "\n".join(Detection.detectedLabels), fill="black", anchor="nw")

	# draw the help instructions
	def drawHelp(self):
		self.canvas.delete("gui")
		helpText = """Press the teleop button to remote control
the robot. Press the find key button to
autonomously find the key and slide it
under the door. At any time during robot
movement, press return to exit the
movement and go to idle mode. Press the
other mode buttons to skip straight to
that mode. The left image is used for
inference and the right is a live feed.
The vertical bars display line sensor
data and the lower right is a map that
displays the robot's estimated position."""
		self.canvas.create_text(self.margin, 2 * self.margin + self.imageSize, text=helpText, tags="gui", anchor="nw")

	# draw the static map in the lower right corner
	def drawMap(self):
		x0 = self.width - self.margin - self.mapWidth
		y0 = self.height - self.margin - self.mapHeight
		self.canvas.create_rectangle(self.width - self.margin,\
			self.height - self.margin,\
			self.width - self.margin - self.mapWidth,\
			self.height - self.margin - self.mapHeight)
		self.canvas.create_rectangle(x0, y0, x0 + self.mapWidth * 1/3, y0 + self.mapHeight * 2/3, fill="green")
		self.canvas.create_rectangle(x0 + self.mapWidth * 2/3, y0, x0 + self.mapWidth, y0 + self.mapHeight * 2/3, fill="blue")
		self.canvas.create_rectangle(x0 + self.mapWidth * 1/4, y0 + self.mapHeight * 9/10,\
			x0 + self.mapWidth, y0 + self.mapHeight, fill="brown")
	
	# draw the robot position
	def drawPosition(self):
		robotSize = 20
		if self.finished: # if the program has completed, draw the robot at the door
			x0 = self.width - self.mapWidth + 3/4 * robotSize
			y0 = self.height - self.margin
			x1 = x0 + robotSize/2
			y1 = y0 - robotSize
			x2 = x0 - robotSize/2
			y2 = y1
		# use odometry to localize in these modes
		elif self.mode == "idle" or self.mode == "findcrocs" or self.mode == "retrieve" or self.mode == "search":
			x0 = self.width - self.margin - self.mapWidth/2
			y0 = robotSize + self.height - self.margin - self.mapHeight + 11.3 * self.robot.position # 11.3 pixels/movement (1 foot)
			x1 = x0 + robotSize/2
			y1 = y0 - robotSize
			x2 = x0 - robotSize/2
			y2 = y1
		# otherwise, use detected landmark objects in the room to localize
		else:
			x0 = self.width - self.margin - self.mapWidth + 12 * self.robot.accuratePosition
			y0 = self.height - self.margin - robotSize * 2
			x1 = x0 + robotSize
			y1 = y0 + robotSize / 2
			x2 = x1
			y2 = y0 - robotSize / 2
		self.canvas.create_polygon(x0, y0, x1, y1, x2, y2, fill="red", tags="gui")
