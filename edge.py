import time 
import picamera
import cv2
import threading
import numpy as np
import socket
import math
import subprocess
from scikit import compare_ssim
from pylepton import Lepton
import select

HOST = '192.168.68.196'
PORT = 6667

def capture(flip_v = False, device = "/dev/spidev0.0"):
  with Lepton(device) as l:
    a,_ = l.capture()
    b = np.copy(a)
  if flip_v:
    cv2.flip(a,0,a)
  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  return np.uint8(a), np.uint16(b)

def fill_color(img, color):
    img = img.astype(np.float32)
    img = np.dstack([img]*3)
    img = img * color
    return img

def classfy(flir_val):
    th_70 = 7680        #8900
    th_100 = 7700       #9650
    flir_val = cv2.resize(flir_val,(640,480))
    flir_val = np.dstack([flir_val]*3)
    first = np.where(flir_val < th_70,(255,0,0), 0)
    second_1 = np.where(flir_val >= th_70, (0,255,0), 0)
    second_2 = np.where(flir_val >= th_100, 0, (0,255,0))
    second = np.bitwise_and(second_1,second_2)
    third = np.where(flir_val >= th_100, (0,0,255),0)
    fusion = first + second + third
    return fusion.astype(np.float32)


def sobel(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray,(3,3),0)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
    sobelx = np.uint8(np.absolute(sobelx))
    sobely = np.uint8(np.absolute(sobely))
    sobel_combine = cv2.bitwise_or(sobelx,sobely)
    return sobel_combine

def img_processing(ir_img,flir_val,flir_img):
        global img_combine,refresh 
        flir_img = cv2.applyColorMap(flir_img, cv2.COLORMAP_JET)
        #cv2.imwrite('flir1.jpg',flir_img)
        flir_img = cv2.resize(flir_img,(640,480))
        ir_img = cv2.resize(ir_img,(640,480))
        ir_img = sobel(ir_img)
        ir_img = np.dstack([ir_img]*3)
        white = ir_img.copy()
        classfy_color = classfy(flir_val)
        flir_tmp = cv2.resize(classfy_color,(ir_weight-120,ir_height-100),interpolation = cv2.INTER_CUBIC)
        #flir_tmp = cv2.resize(flir_img,(ir_weight-120,ir_height-100),interpolation = cv2.INTER_CUBIC)
        white[move_y:move_y+flir_height,move_x:move_x+flir_weight] = flir_tmp
        img_combine = cv2.addWeighted(ir_img,0.8,white,0.2,0)
        refresh = True

count = 0
cv2.namedWindow('picamera',cv2.WINDOW_AUTOSIZE)
cv2.moveWindow('picamera',30,30)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
packet_size = 10000
request_flag = 0
ir_height = 480 #tmp1.shape[0]
ir_weight = 640 #tmp1.shape[1]
flir_height = 380   #flir_tmp.shape[0]
flir_weight = 520   #flir_tmp.shape[1]
move_y = 24
move_x = 50

refresh = False
img_combine = np.zeros((ir_height,ir_weight,3),np.uint8)
try:
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 40
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
    s.send(("Nadine").ljust(16).encode())
    save_msg_count = 0
    #pic_count = 0
    while True:
    #while(pic_count<100):
        #pic_count+=1
        t0 = time.time()
        flir_img, flir_val = capture()
        t1 = time.time()
        camera.capture("ir1.jpg",use_video_port = True)
        t2 = time.time()
        print("flir_time = ",t1-t0)
        print("ir_time = ",t2-t1)
        tmp1 = cv2.imread('ir1.jpg')
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, imgencode = cv2.imencode('.jpg',tmp1,encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()
        s.send(str(len(stringData)).ljust(16).encode())
        s.send(stringData)
        
        thread_img = threading.Thread(target = img_processing,args=(tmp1,flir_val,flir_img))
        thread_img.start()
        if(refresh):
            refresh = False
            cv2.imshow("combine",img_combine)
            cv2.waitKey(1)
        '''
        cv2.imshow('flir',flir_img)
        cv2.imshow('picamera',tmp1)
        cv2.waitKey(1)
        '''
finally:
        camera.close()
        s.close()





