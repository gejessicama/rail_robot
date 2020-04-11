import RPi.GPIO as IO 
from ptpy import PTPy
from time import sleep
from gpiozero import Button
from math import pi

forward = 1
back = 0

# this function is incomplete. We need to know how to relate the speed 
# of the motor to the pwm signal given.
def calcPWMSpeed(overlap, time_int, height):
    speed = (height*0.9366-0.1941)*(1-overlap)/time_int #desired speed in m/s
    pwmsig = speed*CONV_FACTOR #TBD: NEED CONVERSION FACTOR FOR PWM(SPEED)
    return pwmsig
    
def enc_counter():
    global clkLastState
    global counter

    try:
        clkState = IO.input(ENC_clk)
        if clkState!= clkLastState:
            dtState = IO.input(ENC_dt)
            if dtState != clkState:
                counter +=1
            else:
                counter -=1
        clkLastState= clkState

def forwardRun(button, speed):
    IO.output(DIR_pin, forward)
    p.start(speed) 

def returnToBase(channel):
    camera = PTPy() # instantiate connection to Parrot Sequoia
    with camera.session():
        end_cap = camera.terminate_open_capture()
    
    IO.output(DIR_pin, backward)
    p.ChangeDutyCycle(100)

def endRun(channel):
    p.ChangeDutyCycle(0)

# pin locations, BCM 
ENC_clk = 5
ENC_dt = 3
PWM_pin = 20
DIR_pin = 21
BASE_pin = 14
END_pin = 8
START_pin = 1
freq = 100 # in Hz

ENC_wheel_circ = 0.055*pi # 55mm diameter
start_button = Button(start_button)
pwm_speed = calcPWMSpeed(coverage, time_int, height)

IO.setmode(IO.BCM)
IO.setup(PWM_pin, IO.OUT) # for PWM signal
IO.setup(DIR_pin, IO.OUT) # for direction
p = IO.PWM(PWM_pin, 100) # initialize 100k frequency spectrum

IO.setup(ENC_clk, IO.IN, pull_up_down = IO.PUD_UP) 
IO.setup(ENC_dt, IO.IN, pull_up_down = IO.PUD_UP)
clkLastState = IO.input(clk)
counter = 0 

IO.setup(BASE_pin, IO.IN, pull_up_down = IO.PUD_UP) # collision switch at base
IO.setup(END_pin, IO.IN, pull_up_down = IO.PUD_UP) # collision switch at end

start_button.when_pressed = startRun(start_button, speed)
IO.add_event_detect(ENC_clk, IO.FALLING  , callback=enc_counter, bouncetime=300)
IO.add_event_detect(END_pin, IO.FALLING, callback=returnToBase, bouncetime=300)  
IO.add_event_detect(BASE_pin, IO.FALLING, callback=endRun, bouncetime=300)

IO.cleanup()