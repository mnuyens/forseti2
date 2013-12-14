import cv
import cv2

import numpy as np
import matplotlib.pyplot as plt

import time

import lcm
import forseti2

vc = cv2.VideoCapture(1)
vc.set(cv.CV_CAP_PROP_FRAME_WIDTH, 1920)
vc.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 1080)
vc.set(cv.CV_CAP_PROP_FOURCC, cv.CV_FOURCC('M', 'J', 'P', 'G'))
vc.set(cv.CV_CAP_PROP_FPS, 30)

cv2.namedWindow('native')

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

msg = forseti2.image_t()
msg.width = 1920
msg.height = 1080
while True:
	msg.utime = time.time()
	retval, frame = vc.read()
	msg.image = cv2.imencode('.jpg',
                             frame,
                             (cv.CV_IMWRITE_JPEG_QUALITY, 90))[1]
	msg.size = msg.image.shape[0]
	lc.publish("sprocket/video1", msg.encode())
	cv2.imshow('native', frame)
	cv2.waitKey(1)