import RPi.GPIO as GPIO
import time
import ps2_control as ps
import spidev#linux环境下用于spi通讯
import io
import cv2
import os
os.environ['SDL_VIDEODRIVE'] = 'x11'
from time import ctime,sleep,time

def main():
    ps.spi_init()
    while True:
        PS2_KEY = ps.PS2_Datakey()
        print("state is:",PS2_KEY)
        sleep(0.1)

try:
    main()
except KeyboardInterrupt:
    pass

GPIO.cleanup