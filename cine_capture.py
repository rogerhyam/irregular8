from picamera2 import Picamera2, Preview
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import numpy as np

from pynput import keyboard
import RPi.GPIO as GPIO

import time
from datetime import date
import board

import os

# create a directory to put results in
save_dir = "/home/roger/Pictures/cine_capture";
os.makedirs(save_dir, exist_ok=True)

picam2 = Picamera2()
preview_config = picam2.create_preview_configuration()
capture_config = picam2.create_still_configuration()
#print(camera_config)
picam2.configure(preview_config)
picam2.start_preview(Preview.QTGL)
picam2.start()
time.sleep(2)
#picam2.capture_file("test.jpg")

# show where perf trigger will be
overlay = np.zeros((480, 640, 4), dtype=np.uint8)
overlay[0:480, 20:80] = (0, 255, 0, 64) # blue
overlay[40:100, 20:80] = (255, 0, 0, 64) # reddish
picam2.set_overlay(overlay)

# set up the kits to control the motors
kit = MotorKit(i2c=board.I2C())
takeup_kit = MotorKit(i2c=board.I2C(), address=0x61)

# listen for the takeup stop signal
tension_switch = 21 # gpio pin 21 is the switch
GPIO.setup(tension_switch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# control variables
record_on = False
tighten  =  False
loosen = False
nudge_forward = False
nudge_backward = False
next_frame = False
in_perf = False

def get_file_path():
    count = 0
    # Iterate directory
    for path in os.listdir(save_dir):
        # check if current path is a file
        if os.path.isfile(os.path.join(save_dir, path)):
            count += 1
            
    return save_dir + "/" + str(date.today()) + '_' + str(count + 1).zfill(3) + ".jpg";

def new_perf():
    prof = picam2.capture_array("main")

    target = prof[40:100, 20:80]

    # hurts my head to do this other than by looping
    pixel_count = 0
    r = 0
    b = 0
    g = 0
    for h in target:
        for w in h:
            pixel_count += 1
            r += w[0]
            b += w[1]
            g += w[2]
            # fourth is opacity so ignore it
    average_pixel = (r/pixel_count,b/pixel_count,g/pixel_count)
    average_brightness = sum(average_pixel)/len(average_pixel)
    print(average_brightness)
    if average_brightness > 252:
        return True
    else:
        return False
    
def on_press(key):
    pass

def on_release(key):

    global record_on, tighten, loosen, nudge_forward, nudge_backward,next_frame
    
    # beware of doing anything in this thread that
    # doesn't return immediately
    # this is separate from the application loop
    # can be a good thing

    if key == keyboard.Key.right:
        nudge_backward = True
    if key == keyboard.Key.left:
        nudge_forward = True
    if key == keyboard.Key.up:
        tighten = True
    if key == keyboard.Key.down:
        loosen = True
        
    try:
        if key.char == 'n':
            next_frame = True
        if key.char == 'b':
            next_frame = True
    except AttributeError:
        pass
    
    if key == keyboard.Key.space:
        if record_on == True:
            record_on = False
        else:
            record_on = True
    if key == keyboard.Key.esc:
        kit.stepper1.release()
        kit.stepper2.release()
        return False # Stop listener
    
    print(key)

# listen to the keyboard  
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()
    
# application loop
while True:
    
    if record_on:
        kit.stepper1.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
        kit.stepper2.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
        #time.sleep(0.05)
        if new_perf():
            if not in_perf:
                print("SNAP!")
                picam2.switch_mode_and_capture_file(capture_config, get_file_path())
                #record_on = False
                in_perf = True
        else:
            in_perf = False
            
        # keep tension in the takeup spool if
        while True:
            if GPIO.input(tension_switch) == GPIO.LOW and record_on:
                takeup_kit.stepper1.onestep(direction=stepper.FORWARD)
            else:
                break
                
      
    if tighten:
        print("Tighten")
        for i in range(2):
            kit.stepper1.onestep(style=stepper.INTERLEAVE, direction=stepper.FORWARD)
            kit.stepper2.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
        tighten = False;

    if loosen:
        print("Loosen")
        for i in range(2):
            kit.stepper1.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
            kit.stepper2.onestep(style=stepper.INTERLEAVE, direction=stepper.FORWARD)
        loosen = False
    
    if nudge_forward:
        for i in range(1):
            kit.stepper1.onestep(style=stepper.INTERLEAVE, direction=stepper.FORWARD)
            kit.stepper2.onestep(style=stepper.INTERLEAVE, direction=stepper.FORWARD)
        nudge_forward = False

    if nudge_backward:
        for i in range(1):
            kit.stepper1.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
            kit.stepper2.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
        nudge_backward = False
        
    if next_frame:
        for i in range(33):
            kit.stepper1.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
            kit.stepper2.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
        next_frame = False
        
    