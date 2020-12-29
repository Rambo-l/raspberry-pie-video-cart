import RPi.GPIO as GPIO
import time
import ps2_control as ps
import spidev#linux环境下用于spi通讯
import io
import cv2
import os
os.environ['SDL_VIDEODRIVE'] = 'x11'
from time import ctime,sleep,time
import threading


def pi_capture():
    global train_img, is_capture_running,train_labels,key
    #init the train_label array        
    is_capture_running = True
    print("Start capture") 
    cap = cv2.VideoCapture(0)

    while is_capture_running:
        ret,frame = cap.read()
        cv2.imshow("img",frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    is_capture_running = False