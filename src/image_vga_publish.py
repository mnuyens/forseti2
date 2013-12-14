import cv
import cv2

import numpy as np
import matplotlib.pyplot as plt

import lcm
import forseti2

vc = cv2.VideoCapture(1)
cv2.namedWindow('native')

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

msg = forseti2.image_t()
msg.channels = 3
msg.utime = 0
msg.width = 640
msg.height = 480
msg.size = 640 * 480 * 3
while True:
	retval, frame = vc.read()
	msg.image = frame.flatten()
	lc.publish("sprocket/video1", msg.encode())
	cv2.imshow('native', frame)
	cv2.waitKey(1)