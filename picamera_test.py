import time 
import picamera
import cv2
import sys
s = time.time()
#count = 100
try:
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 80
    cv2.namedWindow('picamera',cv2.WINDOW_NORMAL)
    #:count=sys.argv[1]
    while(1):
    #for num in range (0,100):
        start = time.time()
        #count+=1
        #pic = "img"+str(num)+".jpg"
        pic = "pic.jpg"
        camera.capture(pic,use_video_port = True)
        end = time.time()
        tmp = cv2.imread(pic)
        cv2.imshow('picamera',tmp)
        cv2.waitKey(1)
        #print (end-start)
finally:
    camera.close()




