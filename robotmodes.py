# This file contains the generic RobotThread to define basic robot behavior revolving around
# when tensorflow inferences are available.  Each action (thread) of the robot extends this class
# and adds functionality to the framework, but uses the same timing.

import threading
import time
import copy
import math

# defines basic robot mode methods, children need a run() method


class RobotThread(threading.Thread):
    # constructor, takes robot as input
    def __init__(self, robot, videoDisplay, detector):
        super().__init__()
        self.robot = robot
        self.videoDisplay = videoDisplay
        self.stopFlag = False
        self.pauseFlag = False
        self.tfFinishedFlag = False
        self.waitedOnce = False
        self.detector = detector

    # this method is called when a new inference is available
    def tfFinished(self):
        self.tfFinishedFlag = True

    # this method changes the stop flag to true, stopping the infinite loop
    def stop(self):
        self.stopFlag = True

    # this method sets the pause flag to true, temporarily stopping the loop
    def pause(self):
        self.pauseFlag = True
        self.waitedOnce = False
        self.robot.stop()

    # this method sets the pause flag to false, enabling movement again
    def resume(self):
        self.pauseFlag = False

    # this generically runs an infinite loop, allowing pauses and stops
    def run(self):
        while not self.stopFlag:  # run thread until stop flag is raised
            if self.tfFinishedFlag:  # if tensorflow inference is available
                self.tfFinishedFlag = False
                if self.waitedOnce:  # if this is the second frame (frame from stopping point)
                    self.waitedOnce = False
                    if self.taskComplete():  # if task is finished, move on to the next one
                        self.nextThread()
                        return
                    else:
                        self.resume()
                        self.videoDisplay.startTime = time.time()
                else:
                    self.waitedOnce = True
            if self.pauseFlag:  # if the pause flag is raised, do not do anything
                self.robot.stop()
            else:
                self.runLoop()  # otherwise, do the action specified by the thread
        self.robot.stop()

    # children must override this, checks if the current task has finished
    def taskComplete(self):
        return True

    # children must override this, runs the thread in time with tensorflow detections
    def runLoop(self):
        pass

    # children must override this, runs activates the next thread
    def nextThread(self):
        pass

# thread for the robot to line follow in the background


class LineFollowThread(RobotThread):
    # override constructor to add odometry boolean to make sure movements are only counted once
    def __init__(self, robot, videoDisplay, detector):
        super().__init__(robot, videoDisplay, detector)
        self.hasMoved = True

    # checks if the student id is currently in view
    def taskComplete(self):
        for i in range(len(self.detector.labelData)):
            if self.detector.labelData[i][0] == "studentid":
                return True
        self.hasMoved = True  # this is the most convenient place to change this before runLoop()
        return False

    # moves on to the next thread in order, retrieving the student id
    def nextThread(self):
        self.videoDisplay.mode = "retrieve"
        self.robot.retrieve()

    # thread runs this code to line follow
    def runLoop(self):
        if self.hasMoved:
            self.robot.position += 1.5
            print(self.robot.position)
            self.hasMoved = False
        values = self.robot.linesensors.readLineValues()
        if values[0] == values[1]:  # drive forward if same color on both sides
            self.robot.drive("forward", 0.5)
        elif values[0] == "white":  # turn left if only left side is white
            self.robot.drive("left", 0.5)
        else:  # turn right if only right side is white
            self.robot.drive("right", 0.5)

# thread to grab the student id


class RetrieveThread(RobotThread):
    # override constructor to add variables
    def __init__(self, robot, videoDisplay, detector):
        super().__init__(robot, videoDisplay, detector)
        self.studentidCoordinates = None
        self.width = 300

    # checks if the card has disappeared from the frame, meaning it has been acquired
    def taskComplete(self):
        if self.studentidCoordinates:
            return False
        return True

    # move to the next thread, navigating to the exit
    def nextThread(self):
        self.videoDisplay.mode = "findcrocs"
        self.robot.findCrocs()

    # thread runs this code in the loop, finds and drives to the student id
    def runLoop(self):
        oldStudentidCoordinates = self.studentidCoordinates
        # copy to prevent modification by other threads
        labelData = copy.deepcopy(self.detector.labelData)
        studentidFound = False
        for i in range(len(labelData)):
            if labelData[i][0] == "studentid":
                self.studentidCoordinates = labelData[i][2]
                studentidFound = True
                break
        if not studentidFound:
            self.studentidCoordinates = None
        # only run if the student id has moved (received a new frame) and it is still visible
        if self.studentidCoordinates and not self.studentidCoordinates == oldStudentidCoordinates:
            xOffset = self.studentidCoordinates[0] + self.studentidCoordinates[2] - self.width
            if xOffset < -self.width * 0.25:  # card is to the left
                self.robot.drive("left")
                time.sleep(0.1)
            elif xOffset > self.width * 0.25:  # card is to the right
                self.robot.drive("right")
                time.sleep(0.1)
            else:  # card straight ahead
                self.robot.drive("forward")
                time.sleep(1)
                self.robot.position += 1
            self.robot.stop()

# thread to locate and drive to the crocs


class findCrocsThread(RobotThread):
    # override constructor to add variables
    def __init__(self, robot, videoDisplay, detector):
        super().__init__(robot, videoDisplay, detector)
        self.crocCoordinates = None
        self.width = 300
        self.xOffset = None
        self.crocWidth = None
        self.moved = False
        self.crocTargetWidth = 170

    # checks if the crocs are close enough to the robot, completing this task
    def taskComplete(self):
        print(self.crocWidth)
        if self.crocWidth and abs(self.crocWidth) > self.crocTargetWidth:
            return True
        return False

    # move to the next thread, navigating to the exit
    def nextThread(self):
        self.videoDisplay.mode = "finddoor"
        self.robot.findDoor()

    # override this to also change the self.moved variable
    def tfFinished(self):
        super().tfFinished()
        self.moved = False

    # thread runs this code in the loop, finds and turns towards the crocs
    def runLoop(self):
        oldCrocCoordinates = self.crocCoordinates
        # copy to prevent modification by other threads
        labelData = copy.deepcopy(self.detector.labelData)
        crocsFound = False
        skateboardFound = False
        for i in range(len(labelData)):
            if labelData[i][0] == "crocs":
                self.crocCoordinates = labelData[i][2]
                self.crocWidth = abs(self.crocCoordinates[2] - self.crocCoordinates[0])
                crocsFound = True
                break
            elif labelData[i][0] == "skateboard":
                skateboardFound = True
        if not crocsFound:
            self.crocCoordinates = None
            self.xOffset = None
            self.crocWidth = None
        # only run if the crocs have moved (received a new frame) and are still visible
        if crocsFound and not self.crocCoordinates == oldCrocCoordinates:
            self.xOffset = self.crocCoordinates[0] + self.crocCoordinates[2] - self.width
            if self.xOffset < -self.width * 0.3:
                self.robot.drive("left")
                time.sleep(0.15)
            elif self.xOffset > self.width * 0.3:
                self.robot.drive("right")
                time.sleep(0.15)
            elif self.crocWidth < self.crocTargetWidth:
                self.robot.drive("forward")
                time.sleep(2)
                self.robot.position += 2
        # rotate 180 degrees if the skateboard is visible (turn toward crocs), and drive forward
        elif skateboardFound and not self.moved:
            self.moved = True
            self.robot.drive("right")
            time.sleep(3.5)
            self.robot.drive("forward")
            time.sleep(4)
            self.robot.position += 4
        # scan for the crocs if they are not currently visible
        elif not crocsFound and not self.moved:
            self.moved = True
            self.robot.drive("right")
            time.sleep(0.3)
        self.robot.stop()

# thread to locate and drive to the door


class findDoorThread(RobotThread):
    # override constructor to add variables
    def __init__(self, robot, videoDisplay, detector):
        super().__init__(robot, videoDisplay, detector)
        self.podsCoordinates = None
        self.width = 300
        self.xOffset = None
        self.podsWidth = None
        self.moved = False
        self.podsTargetWidth = 200
        self.robot.drive("right")
        time.sleep(0.5)
        self.robot.stop()

    # checks if the tide pods are close enough to the robot, completing this task
    def taskComplete(self):
        print(self.podsWidth)
        if self.podsWidth and abs(self.podsWidth) > self.podsTargetWidth:
            return True
        return False

    # drive to the door and go back to idle, delivering the card
    def nextThread(self):
        self.robot.drive("left")
        time.sleep(1.5)
        self.robot.drive("forward")
        time.sleep(6)
        self.robot.stop()
        self.videoDisplay.mode = "idle"
        self.robot.thread = None
        self.videoDisplay.finished = True

    # override this to also change the self.moved variable
    def tfFinished(self):
        super().tfFinished()
        self.moved = False

    # thread runs this code in the loop, goes to the tide pods
    def runLoop(self):
        oldPodsCoordinates = self.podsCoordinates
        # copy to prevent modification by other threads
        labelData = copy.deepcopy(self.detector.labelData)
        podsFound = False
        for i in range(len(labelData)):
            if labelData[i][0] == "tidepods":
                self.podsCoordinates = labelData[i][2]
                self.podsWidth = abs(self.podsCoordinates[2] - self.podsCoordinates[0])
                podsFound = True
                break
        if not podsFound:
            self.podsCoordinates = None
            self.xOffset = None
            self.podsWidth = None
        # only run if the tide pods have moved (received a new frame) and are still visible
        if podsFound and not self.moved:
            self.moved = True
            self.xOffset = self.podsCoordinates[0] + self.podsCoordinates[2] - self.width
            width = abs(self.podsCoordinates[2] - self.podsCoordinates[0])
            self.robot.accuratePosition = 1 / (3 * math.tan(width * math.pi / 2400))
            if self.xOffset < -self.width * 0.3:
                self.robot.drive("left")
                time.sleep(0.1)
            elif self.xOffset > self.width * 0.3:
                self.robot.drive("right")
                time.sleep(0.1)
            elif self.podsWidth < self.podsTargetWidth:
                self.robot.drive("forward")
                time.sleep(2)
        # scan for the tide pods if they are not currently visible
        elif not podsFound and not self.moved:
            self.moved = True
            self.robot.drive("right")
            time.sleep(0.3)
        self.robot.stop()
