import RPi.GPIO as GPIO
import time
import ps2_control as ps
import spidev#linux环境下用于spi通讯
import io
import cv2
import os
os.environ['SDL_VIDEODRIVE'] = 'x11'
import threading

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

MASK = [PSB_SELECT,PSB_L3,PSB_R3,PSB_START,PSB_PAD_UP,PSB_PAD_RIGHT,PSB_PAD_DOWN,PSB_PAD_LEFT,PSB_L2,PSB_R2,PSB_L1,PSB_R1,PSB_TRIANGLE,PSB_CIRCLE,PSB_CROSS,PSB_SQUARE]

#小车运行状态值定义
enSTOP = 0
enRUN =1
enBACK = 2
enLEFT = 3
enRIGHT = 4
enTLEFT =5
enTRIGHT = 6
enUPLEFT = 7
enUPRIGHT = 8
enDOWNLEFT = 9
enDOWNRIGHT = 10

#电机引脚定义
IN1 = 5
IN2 = 6
#pwm驱动口
ENA = 16
#转向舵机引脚定义
ServoPin = 14
#舵机支架
cmotor1=23
cmotor2=24
#初始化直流电机速度
CarSpeedControl = 50
angle1=90
angle2=90
#初始化就GPIO口
def init():
    #直流电机pwm
    global pwm_ENA
    #转向舵机pwm
    global pwm_servo
    #舵机支架pwm
    global p1
    global p2
    GPIO.setup(ENA,GPIO.OUT,initial=GPIO.HIGH)
    GPIO.setup(IN1,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(IN2,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(ServoPin, GPIO.OUT)
    GPIO.setup(cmotor1,GPIO.OUT)
    GPIO.setup(cmotor2,GPIO.OUT)
    pwm_ENA = GPIO.PWM(ENA, 100)
    p1=GPIO.PWM(cmotor1,50)
    p2=GPIO.PWM(cmotor2,50)
    pwm_servo = GPIO.PWM(ServoPin, 50)
    pwm_servo.start(0)
    p1.start(0)
    p2.start(0)
    pwm_ENA.start(0)

#摄像头显示线程
def pi_capture():
    global is_capture_running
    is_capture_running = True
    print("Start capture") 
    cap = cv2.VideoCapture(0)

    while is_capture_running:
        ret,frame = cap.read()
        cv2.imshow("img",frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    is_capture_running = False
    
def run():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(CarSpeedControl)
    pwm_servo.ChangeDutyCycle(2.5+10*138/180)
    time.sleep(0.02)
    pwm_servo.ChangeDutyCycle(0)
#小车后退
def back():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(CarSpeedControl)
    pwm_servo.ChangeDutyCycle(2.5+10*138/180)
    time.sleep(0.02)
    pwm_servo.ChangeDutyCycle(0)

#小车左转   
def left():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(CarSpeedControl)
    pwm_servo.ChangeDutyCycle(2.5+10*96/180)
    time.sleep(0.02)
    pwm_servo.ChangeDutyCycle(0)

#小车右转
def right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(CarSpeedControl)
    pwm_servo.ChangeDutyCycle(2.5+10*180/180)
    time.sleep(0.02)
    pwm_servo.ChangeDutyCycle(0)
   #小车沿左后方后退
def downleft():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(CarSpeedControl)
    pwm_servo.ChangeDutyCycle(2.5+10*96/180)
    time.sleep(0.02)
    pwm_servo.ChangeDutyCycle(0)
#小车沿右下方后退
def downright():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(CarSpeedControl)
    pwm_servo.ChangeDutyCycle(2.5+10*180/180)
    time.sleep(0.02)
    pwm_servo.ChangeDutyCycle(0)
    
#小车停止   
def brake():
   GPIO.output(IN1, GPIO.LOW)
   GPIO.output(IN2, GPIO.LOW)
   pwm_ENA.ChangeDutyCycle(0)
   pwm_servo.ChangeDutyCycle(2.5+10*138/180)
   time.sleep(0.02)
   pwm_servo.ChangeDutyCycle(0)
def cmotor11():
    p1.ChangeDutyCycle(2.5+10*angle1/180)
    time.sleep(0.02)
    p1.ChangeDutyCycle(0)
def cmotor22():
    p2.ChangeDutyCycle(2.5+10*angle2/180)
    time.sleep(0.02)
    #p2.ChangeDutyCycle(0)
def control():
    global is_capture_running,CarSpeedControl,angle1,angle2
    global PS2_KEY
    global CarSpeedControl
    global g_ServoState
    print("Start control!")
    try:
        init()
        ps.spi_init()
        while True:
            PS2_KEY = ps.PS2_Datakey()
            print('state is:',PS2_KEY)
            #PSB_SELECT键按下
            if PS2_KEY == PSB_SELECT:
                print ("PSB_SELECT")
            #PSB_R3键按下，舵机归位
            elif PS2_KEY == PSB_R3:
                print ("PSB_R3")
      
            #PSB_START键按下
            elif PS2_KEY == PSB_START:
                print ("PSB_START")
                #g_Carstate=enDOWNRIGHT
            #PSB_PAD_UP键按下，小车前进
            elif PS2_KEY == PSB_PAD_UP:
                g_Carstate = enRUN
                print ("PSB_PAD_UP")
            #PSB_PAD_RIGHT键按下，小车右转
            elif PS2_KEY == PSB_PAD_RIGHT:
                g_Carstate = enRIGHT
                print ("PSB_PAD_RIGHT") 
     
            #PSB_PAD_DOWN键按下，小车后退
            elif PS2_KEY == PSB_PAD_DOWN:
                g_Carstate = enBACK
                print ("PSB_PAD_DOWN")
  
            #PSB_PAD_LEFT键按下，小车左转
            elif PS2_KEY == PSB_PAD_LEFT:
                g_Carstate = enLEFT
                print ("PSB_PAD_LEFT")
                
            #L2键按下，小车每次加速
            elif PS2_KEY == PSB_L2:
                print ("PSB_L2_SPEED+")
                CarSpeedControl += 10
                if CarSpeedControl > 100:
                    CarSpeedControl = 100
            #R2键按下，小车每次减速
            elif PS2_KEY == PSB_R2:
                print ("PSB_R2_SPEED-")
                CarSpeedControl -= 10
                if CarSpeedControl < 0:
                    CarSpeedControl = 0
            #L1键按下
            elif PS2_KEY == PSB_L1:
                g_Carstate=enDOWNRIGHT
                print ("PSB_L1")
                
                #downright()
            #R1键按下
            elif PS2_KEY == PSB_R1:
                g_Carstate=enDOWNLEFT
                print ("PSB_R1")
                
                #downleft()
            elif PS2_KEY ==PSB_TRIANGLE:
                print('camera_down')
                angle1+=10
                if angle1>180:
                    angle1=180
                cmotor11()
            elif PS2_KEY ==PSB_CROSS:
                print('camera_up')
                angle1-=10
                if angle1<0:
                    angle1=0
                cmotor11()
            elif PS2_KEY ==PSB_SQUARE:
                print('camera_left')
                angle2+=10
                if angle2>180:
                    angle2=180
                cmotor22()
            elif PS2_KEY ==PSB_CIRCLE:
                print('camera_right')
                angle2-=10
                if angle2<-0:
                    angle2=-0
                cmotor22()
            
            else:
                g_Carstate = enSTOP
                #brake()
#            #当L1或者R1按下时，读取摇杆数据的模拟值
            #if PS2_KEY == PSB_L1 or PS2_KEY == PSB_R1:    
#                #左侧摇杆控制小车的运动状态
#                if Y1 < 5 and  80 < X1 < 180:
#                    g_Carstate = enRUN
#                elif Y1 > 230 and 80 < X1 < 180:
#                    g_Carstate = enBACK
#                elif X1 < 5 and 80 < Y1 < 180:
#                    g_Carstate = enLEFT
#                elif X1 > 230 and 80 < Y1 < 180:
#                    g_Carstate = enRIGHT
#                elif X1 <= 80 and Y1 <= 80:
#                    g_Carstate = enUPLEFT
#                elif X1 >= 180 and Y1 < 80:
#                    g_Carstate = enUPRIGHT
#                elif Y1 >= 180 and X1 <= 80:
#                    g_Carstate = enDOWNLEFT
#                elif Y1 >= 180 and X1 >= 180:
#                    g_Carstate = enDOWNRIGHT
#                else:
#                    g_Carstate = enSTOP

            #小车运动状态判断
            if g_Carstate == enSTOP:
                brake()
            elif g_Carstate == enRUN:
                run()
            elif g_Carstate == enLEFT:
                left()
            elif g_Carstate == enRIGHT:
                right()
            elif g_Carstate == enBACK:
                back()
            elif g_Carstate == enDOWNLEFT:
                downleft()
            elif g_Carstate == enDOWNRIGHT:
                downright()
            else:
                brake()
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
            
    

if __name__ == '__main__':
    #print("capture thread")
    #print('-' * 50)
    control()
    capture_thread = threading.Thread(target=pi_capture,args=())   # 开启线程
    capture_thread.setDaemon(True)
    capture_thread.start()
    
   
pwm_ENA.stop()
pwm_servo.stop()
GPIO.cleanup()
                
#20201230   

    