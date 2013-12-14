
import numpy as np
import matplotlib.pyplot as plt

import lcm
import forseti2
import cv2

cv2.namedWindow('frame')

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

def receive_image(channel, data):
    global msg
    msg = forseti2.image_t.decode(data)
    # print("Received message on channel \"%s\"" % channel)
    frame = np.fromstring(msg.image, dtype=np.uint8)
    frame2 = cv2.imdecode(frame, cv2.CV_LOAD_IMAGE_COLOR)
    #frame2 = frame.reshape((480, 640, 3))
    try:
        cv2.imshow('frame', frame2)
        cv2.waitKey(1)
    except:
        print frame2

sub = lc.subscribe("sprocket/video1", receive_image)
try:
    while True:
        lc.handle()
except KeyboardInterrupt:
    pass
