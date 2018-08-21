#! /home/srao/virtualenvs/opencv/bin/python
import re
import cv2
ver = cv2.__version__
ver_float = float(re.sub('.[0-9]{1,2}$', '', ver)) # convert opencv version number to float (remove sub-sub-version number)

import platform
operating_sys = platform.system()

import numpy as np
import os
import argparse
import math

mouseldown = False # true if mouse left button is pressed
mouserdown = False # True if mouse right button is pressed
initialx, initialy = -1,-1
box = ""
circle = ""

parser = argparse.ArgumentParser(description='Accessory tool to set thresholding limits; esc or q to quit, p to print current hsv limits to terminal.')
parser.add_argument('-p', '--path', help = 'input path (default = current directory)', default = ".")
parser.add_argument('-f', '--file', help = 'input single filename with full path (required)')
parser.add_argument('-r', '--resize', type = float, help = 'resize the video for display by this factor (e.g. 0.5 halves the resolution). Please note that this is just for thresholding and does not affect the values output by this script nor the actual analysis, which is done at full resolution.', default = 1.0)
args = parser.parse_args()

os.chdir(args.path)

def nothing(x):
    pass

# mouse callback function
def draw_line(event,x,y,flags,param):
    global initialx, initialy, mouseldown, mouserdown, firstframe, ff_copy, box, circle
    # print x, y, event
    if event == cv2.EVENT_LBUTTONDOWN:
        mouseldown = True
        initialx,initialy = x,y
    elif event == cv2.EVENT_RBUTTONDOWN:
        mouserdown = True
        initialx, initialy = x, y
        #print x, y, event
    elif event == cv2.EVENT_MOUSEMOVE:
        if mouseldown:
            firstframe = np.copy(ff_copy)
            cv2.rectangle(firstframe,(initialx,initialy),(x,y),(0,255,0), 1)
        elif mouserdown:
            firstframe = np.copy(ff_copy)
            cv2.circle(firstframe, (initialx, initialy), int(math.sqrt((x - initialx)**2 + (y - initialy)**2)), (0, 255, 0), 1)
    elif event == cv2.EVENT_LBUTTONUP:
        mouseldown = False
        cv2.rectangle(firstframe,(initialx, initialy),(x,y),(0,255,0), 1)
        box = "corner 1: " + str(initialx/args.resize) + " " + str(initialy/args.resize) + "\ncorner 2: " + str(x/args.resize) + " " + str(y/args.resize) + "\nbox width = " + str(abs(x/args.resize - initialx/args.resize)) + "px" + "\nbox height = " + str(abs(initialy/args.resize - y/args.resize)) + "px"
        initialx, initialy = -1, -1
    elif event == cv2.EVENT_RBUTTONUP:
        mouserdown = False
        cv2.circle(firstframe, (initialx, initialy), int(math.sqrt((x - initialx)**2 + (y - initialy)**2)), (0, 255, 0), 1)
        circle = "centre: " + str(initialx/args.resize) + " " + str(initialy/args.resize) + "\nradius: " + str(int(math.sqrt((x/args.resize - initialx/args.resize)**2 + (y/args.resize - initialy/args.resize)**2)))
        initialx, initialy = -1, -1

# load first frame, resize, change to hsv channel
cap = cv2.VideoCapture(args.file)
ret, firstframe = cap.read()
if not ret:
    print "\n\nnot a valid input stream. is the path/filename correct?\n\n"
cv2.namedWindow('image')
cv2.namedWindow('original')
#cv2.namedWindow('measures')
firstframe = cv2.resize(firstframe, (0,0), fx = args.resize, fy = args.resize) # resizing affects thresholding of low-res videos
ff_copy = np.copy(firstframe)
cv2.setMouseCallback('original', draw_line)
hsv = cv2.cvtColor(firstframe, cv2.COLOR_BGR2HSV)

# create trackbars for thresholding
cv2.createTrackbar('lh','image',35,180,nothing)
cv2.createTrackbar('ls','image',70,255,nothing)
cv2.createTrackbar('lv','image',70,255,nothing)
cv2.createTrackbar('uh','image',179,180,nothing)
cv2.createTrackbar('us','image',255,255,nothing)
cv2.createTrackbar('uv','image',255,255,nothing)

while(ret):
    # get current positions trackbars
    lh = cv2.getTrackbarPos('lh','image')
    uh = cv2.getTrackbarPos('uh','image')
    ls = cv2.getTrackbarPos('ls','image')
    lv = cv2.getTrackbarPos('lv','image')
    us = cv2.getTrackbarPos('us','image')
    uv = cv2.getTrackbarPos('uv','image')
    mask = cv2.inRange(hsv, np.array([lh, ls, lv]), np.array([uh, us, uv]))
    cv2.imshow('image', mask)
    if operating_sys == "Darwin":
        k = cv2.waitkey(20)
    else:
        k = cv2.waitKey(1) & 0xFF
    if k == 27 or k == 113:
        break
    if k == 112:
        print "--Thresholds--\n", "lower = ", lh, ls, lv, "\nupper = ", uh, us, uv
        print "\n--Box--\n", box
        print "\n--Circle--\n", circle
    #print mask.shape
    #print firstframe.shape
    res = None
    alpha = 0.3
    #res = cv2.bitwise_or(firstframe, firstframe, mask = mask)
    res = cv2.addWeighted(cv2.cvtColor(mask,cv2.COLOR_GRAY2RGB), alpha, firstframe, 1 - alpha, 0)
    cv2.imshow('original', res)
    #cv2.imshow('measures', ff_copy)

print "--Thresholds--\n", "lower = ", lh, ls, lv, "\nupper = ", uh, us, uv
print "\n--Box--\n", box
print "\n--Circle--\n", circle
#print firstframe.shape
cv2.destroyAllWindows()
