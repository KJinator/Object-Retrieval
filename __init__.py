# Main file, __init__.py
# This file runs the application and manages threads, enabling real-time tasks to occur
# on time.

# In this directory is sapp.py, detections.py, linesensor.py, livecam.py, robot.py,
# robotmodes.py, servo.py, and singleshot.py.
# It also contains graph.pbtxt and frozen_inference_graph.pb,
# tensorflow-generated model files needed to make inferences

from singleshot import *
from app import *
from robot import *
from livecam import *

lineFollowTime = 2.5

# initialize robot
robot = Robot()

# define paths and information about the tensorflow model
labels = ["background", "crocs", "recycling", "skateboard", "studentid", "tidepods"]
protoPath = "graph.pbtxt"
modelPath = "frozen_inference_graph.pb"
confidenceErrorMargin = 0.2

# initialize detector
detector = SSD(protoPath, modelPath, labels, confidenceErrorMargin)

# initialize cameras and application window
SSD.initCamera()
liveCamera = piCam()
videoDisplay = App(robot)
robot.videoDisplay = videoDisplay

# run detector once before entering the loop
detectorThread = DetectorThread(detector)
detectorThread.start()
detectorThread.join()
robot.detector = detector

# run the live camera once before entering the loop
liveCameraThread = piCamThread(liveCamera)
liveCameraThread.start()
liveCameraThread.join()

# infinite loop to control threads
while True:
	# if the detector has finished the last frame, begin processing another
	if not detectorThread.isAlive():
		videoDisplay.canvas.delete("all")
		videoDisplay.drawImage(detector.getCurrTkImage(), "left")
		videoDisplay.drawBounds(detector.labelData)
		videoDisplay.drawLabels(detector.labelData)
		videoDisplay.drawMap()
		detectorThread = DetectorThread(detector)
		detectorThread.start()
		# tell the active robot thread that a new tensorflow inference is available
		if not robot.thread == None:
			robot.thread.tfFinished()
	# if the live camera has finished taking an image, take another
	if not liveCameraThread.isAlive():
		videoDisplay.canvas.delete("liveCam")
		videoDisplay.drawImage(liveCamera.getCurrTkImage(), "right")
		liveCameraThread = piCamThread(liveCamera)
		liveCameraThread.start()
	# if robot has line followed long enough, pause to take an image
	if videoDisplay.mode == "search" and not robot.thread.pauseFlag and time.time() - lineFollowTime > videoDisplay.startTime:
		robot.thread.pause()
	if videoDisplay.mode == "help":
		videoDisplay.drawHelp()
	else:
		videoDisplay.drawButtons()
		videoDisplay.drawPosition()
	videoDisplay.lines = robot.linesensors.readLineValues()
	videoDisplay.drawLines()
	videoDisplay.root.update()
	if videoDisplay.quitting:
		liveCameraThread.join()
		videoDisplay.root.destroy()
		break
