#Importing libraries
import RPi.GPIO as GPIO
import glob
import time
import psutil

from time import sleep

#Initializing directories to read tempreature
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#Control sequence to statrt gauge
control = [5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10]

#setting the servo physical pin
servo = 22

#setting pin numbering library
GPIO.setmode(GPIO.BOARD)

#Setting pin 22 to output
GPIO.setup(servo,GPIO.OUT)

# In this servo motor,
# 1ms pulse for 0 degree (LEFT)
# 1.5ms pulse for 45 degree (MIDDLE)
# 2ms pulse for 90 degree (RIGHT)

# For 50hz, one frequency is 20ms
# Duty cycle for 0 degree = (1/20)*100 = 5%
# Duty cycle for 45 degree = (1.5/20)*100 = 7.5%
# Duty cycle for 90 degree = (2/20)*100 = 10%

p=GPIO.PWM(servo,50)# 50hz frequency

p.start(2.5)# starting duty cycle ( it set the servo to 0 degree )


#Method for read temperature in raw format
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

#Method for convert raw temperarture reading to readable format
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

#Method for rotate the gauge according to temperature.
def rotateServoMotor(temp):
    try:
        if(temp < 20):
            print("Temperature Level : Cool")
            p.ChangeDutyCycle(9.5)
        elif(temp < 30):
            p.ChangeDutyCycle(7.5)
            print("Temperature Level : Warm")
        else:
            p.ChangeDutyCycle(5.5)
            print("Temperature Level : Hot")
    
    except Exception as e:
        print("Error in displaying the temperature")

#Loop to kill all pulse in process
for proc in psutil.process_iter():
    if proc.name() == 'libgpiod_pulsein' or proc.name() == 'libgpiod_pulsei':
        proc.kill()
        
#Gague starting here
print("Gauge Starting")

#Loop to check gauge working from lowest reading to highest.
for x in range(11):
    p.ChangeDutyCycle(control[x])
    time.sleep(0.125)
    
#Loop to check gauge working from highest reading to lowest.         
for x in range(9,0,-1):
    p.ChangeDutyCycle(control[x])
    time.sleep(0.125)
    

#Infinite loop to actuate the motor
while True:
    try:
        temp = read_temp()
        rotateServoMotor(temp)
        time.sleep(2.0)
    except KeyboardInterrupt:
        GPIO.cleanup()
        break
