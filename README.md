# Object-Retrieval

Code for an object retrieval robot using tensor flow and opencv.

This code runs on a Raspberry Pi Zero W.  It can be connected to and controlled remotely using a VNC, so the user interface and remote control capabilities are accessible from any device.  It can autonomously find the key to my dorm room and push it under the door, giving me access.  It displays information to the user including live camera feeds and information about the estimated state of the robot.  It does this using opencv, tensorflow, and line following to localize, map, and identify objects.  The user can begin the autonomous retrieval of the key from any point in the process.  The hardware required includes:
-Raspberry Pi Zero W
-2x Continuous Rotation Servos
-Custom line following sensor (may work with some COTS components)
-USB webcam
-Picamera
