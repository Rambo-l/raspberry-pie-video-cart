import RPi.GPIO as GPIO
import time
import spidev#linux环境下用于spi通讯
import io
import cv2
import os
os.environ['SDL_VIDEODRIVE'] = 'x11'
from time import ctime,sleep,time

#手柄按键定义
PSB_SELECT = 1
PSB_L3 =  2
PSB_R3 =  3
PSB_START = 4
PSB_PAD_UP = 5
PSB_PAD_RIGHT = 6
PSB_PAD_DOWN  = 7
PSB_PAD_LEFT  = 8
PSB_L2 = 9
PSB_R2 = 10
PSB_L1 = 11
PSB_R1 = 12
PSB_TRIANGLE = 13
PSB_CIRCLE = 14
PSB_CROSS  = 15
PSB_SQUARE = 16

#PS2引脚设置,接树莓派引脚
PS2_DAT_PIN = 10 #MOS
PS2_CMD_PIN = 9  #MIS
PS2_SEL_PIN = 25 #CS  
PS2_CLK_PIN = 11 #SCK

#回发过来的后4个数据是摇杆的数据
PSS_RX = 5    #右摇杆X轴数据
PSS_RY = 6    #右摇杆Y轴数据
PSS_LX = 7    #左摇杆X轴数据
PSS_LY = 8    #右摇杆Y轴数据

global PS2_KEY
global X1
global Y1
global X2
global Y2
global Handkey
scan=[0x01,0x42,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
Data=[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
MASK = [PSB_SELECT,PSB_L3,PSB_R3,PSB_START,PSB_PAD_UP,PSB_PAD_RIGHT,PSB_PAD_DOWN,PSB_PAD_LEFT,PSB_L2,PSB_R2,PSB_L1,PSB_R1,PSB_TRIANGLE,PSB_CIRCLE,PSB_CROSS,PSB_SQUARE]

#设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)

#忽略警告信息
GPIO.setwarnings(False)

#spi初始化 
def spi_init():
    spi = spidev.SpiDev()
    spi.open(0,0)
    GPIO.setup(PS2_CMD_PIN,GPIO.OUT,initial=GPIO.HIGH)
    GPIO.setup(PS2_CLK_PIN,GPIO.OUT,initial=GPIO.HIGH)
    GPIO.setup(PS2_DAT_PIN, GPIO.IN)
    GPIO.setup(PS2_SEL_PIN,GPIO.OUT,initial=GPIO.HIGH)
    
#读取PS2摇杆的模拟值
def PS2_AnologaData(button):
    return Data[button] 
    
#清空接受PS2的数据
def PS2_ClearData():
    Data[:]=[]
    
#读取PS2的数据
def PS2_ReadData(command):
    res = 0
    j = 1 
    i = 0
    for i in range(8):
        if command & 0x01:
            GPIO.output(PS2_CMD_PIN, GPIO.HIGH)
        else:
            GPIO.output(PS2_CMD_PIN, GPIO.LOW)
        command = command >> 1
        sleep(0.000008)
        GPIO.output(PS2_CLK_PIN, GPIO.LOW)
        sleep(0.000008)
        if GPIO.input(PS2_DAT_PIN):
            res = res + j
        j = j << 1
        GPIO.output(PS2_CLK_PIN, GPIO.HIGH)
        sleep(0.000008)
    GPIO.output(PS2_CMD_PIN, GPIO.HIGH)
    sleep(0.00004)
    return res
    
#PS2获取按键类型
def PS2_Datakey():
    global Data
    global scan
    index = 0
    i = 0
    PS2_ClearData()
    GPIO.output(PS2_SEL_PIN, GPIO.LOW)
    for i in range(9):
        Data.append( PS2_ReadData(scan[i]))
    GPIO.output(PS2_SEL_PIN, GPIO.HIGH)
    
    Handkey = (Data[4] << 8) | Data[3]
    for index in range(16):
        if Handkey & (1 << (MASK[index] - 1)) == 0:
            return index+1
    return 0