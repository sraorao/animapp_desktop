import argparse

parser = argparse.ArgumentParser(description='Process mouse videos. esc or q to quit, space to (un)pause')
parser.add_argument('-p', '--path', help = 'input path (default = current directory). If given, _all_ **mp4** files in the folder are analysed. This argument is ignored if -f is given', default = ".")
parser.add_argument('-f', '--file', help = 'input single filename with full path')
parser.add_argument('-l', '--lower', type = int, nargs = 3, help = '3 integers separated by spaces, in hsv scale for lower limit of colour (default = 160 75 75). 0-179 0-255 0-255', default = [160, 75, 75])
parser.add_argument('-u', '--upper', type = int, nargs = 3, help = '3 integers separated by spaces, in hsv scale for upper limit of colour (default = 179 255 255). 0-179 0-255 0-255', default = [179, 255, 255])
parser.add_argument('-l2', '--lower2', type = int, nargs = 3, help = '3 integers separated by spaces, in hsv scale for lower limit of colour (default = lower). 0-179 0-255 0-255 This needs to be set in cases where the target colour is red, but should be ignored for all other cases.', default = None)
parser.add_argument('-u2', '--upper2', type = int, nargs = 3, help = '3 integers separated by spaces, in hsv scale for upper limit of colour (default = upper). 0-179 0-255 0-255 This needs to be set in case the target colour is red, but can be ignored in all other cases.', default = None)
parser.add_argument('-d', '--delay', type = float, help = 'time delay (float) between frames in seconds (default = 0)', default = 0)
parser.add_argument('-m', '--mask', help = 'show mask? acceptable values are "1" (mask from lower and upper), "2" (mask from lower2 and upper2), "3" (mask1 + mask2 overlaid on original video, and showing a bounding circle around the object), "both" (mask 1 + mask 2), or anything else ( = default, shows original video.)', default = '')
parser.add_argument('-dw', '--dontwrite', help = 'if specified, do not write values to csv file(s)', action = 'store_true')
parser.add_argument('-r', '--radius', type = int, help = 'minimum size of object (default = 5)', default = 5)
parser.add_argument('-s', '--logsettings', help = 'file to which to write settings (default = settings.log)', default = "settings.log")
parser.add_argument('-o', '--outprefix', help = 'prefix to append to csv output filename (default = "")', default = "")
parser.add_argument('-b', '--box', type = int, nargs = 4, help = 'region of interest (x1, y1, x2, y2)')
parser.add_argument('-t', '--tracker', help = 'use in-built tracker function', action = 'store_true')
parser.add_argument('-ta', '--trackeralgorithm', help = 'algorithm to use for in-built tracker (ignored if opencv version > 3.2)', default = "KCF")
parser.add_argument('-ov', '--outvideo', help = 'prefix to append to output avi of thresholded object', default = "")
#parser.add_argument('-rs', '--readsettings', help = 'file from which to read settings (default = settings.log)', default = "settings.log")

args = parser.parse_args()

lower = tuple(args.lower)
upper = tuple(args.upper)


if args.lower2 is None:
    lower2 = lower
else:
    lower2 = tuple(args.lower2)

if args.upper2 is None:
    upper2 = upper
else:
    upper2 = tuple(args.upper2)

print(lower, upper, lower2, upper2)

if args.box is None:
    box = 0
else:
    box = tuple(args.box)

import re
import cv2
ver = cv2.__version__
ver_float = float(re.sub('.[0-9]{1,2}$', '', ver)) # convert opencv version number to float (remove sub-sub-version number)

import platform
operating_sys = platform.system()

import os
import numpy as np
import fnmatch
import time
import sys
from datetime import datetime
os.chdir(args.path)


# function to analyse first frame----
def analyse_firstframe(inputfilename):
    cap = cv2.VideoCapture(inputfilename)
    ret, firstframe = cap.read()
    #firstframe = cv2.resize(firstframe, (0,0), fx = 0.5, fy = 0.5)
    if box: firstframe = firstframe[box[1]:box[3], box[0]:box[2]]
    newcontours = list()
    previousx, previousy = 0, 0
    #firstframe = cv2.resize(firstframe, (0,0), fx = 0.5, fy = 0.5)
    hsv = cv2.cvtColor(firstframe, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, lower, upper)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask = cv2.bitwise_or(mask1, mask2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            center = (cX, cY)

            # only proceed if the radius meets a minimum size
            # if radius > 5:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                # cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
    return cX, cY, firstframe.shape

# function----
def analyse_vid(inputfilename):
    count = 0
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    cap = cv2.VideoCapture(inputfilename)
    previousx, previousy, shape = analyse_firstframe(inputfilename)
    bbox = (518, 361, 37, 23) # hardcoded for now; change later
    ret, frame = cap.read()
    if ver_float <= 3.2: # later versions of opencv have different syntax for tracker
        tracker = cv2.Tracker_create(args.trackeralgorithm)
    #frame = cv2.resize(frame, (0,0), fx = 0.5, fy = 0.5)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, lower, upper)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask = cv2.bitwise_or(mask1, mask2)
    mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    if ver_float <= 3.2: # later versions of opencv have different syntax for tracker
        ok = tracker.init(mask_rgb, bbox)
    out = cv2.VideoWriter(inputfilename + args.outvideo + '_output.avi', fourcc, 20.0, (shape[1], shape[0]))

    ellipse = list()
    newcontours = list()
    while(1):
        ret, frame = cap.read()
        if ret == False:
            break
        #frame = cv2.resize(frame, (0,0), fx = 0.5, fy = 0.5)
        if box: frame = frame[box[1]:box[3], box[0]:box[2]]
        blank_image = np.zeros((540,960,3), np.uint8)
        #frame = cv2.resize(frame, (0,0), fx = 0.5, fy = 0.5)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, lower, upper)
        mask2 = cv2.inRange(hsv, lower2, upper2)
	mask = cv2.bitwise_or(mask1, mask2)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        original = np.copy(frame) 
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            center = (cX, cY)
 	    bounding_box = cv2.minAreaRect(c)
            # only proceed if the radius meets a minimum size
            if radius > args.radius:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
		if not args.dontwrite:
                    previousx = cX
                    previousy = cY
                    outputfilename = open(args.outprefix + inputfilename + ".csv", "a")
                    outputfilename.write(str(cX) + "," + str(cY) + "," + str(count) + "," + str(bounding_box).replace("(", "").replace(")", "") + "\n")
                    outputfilename.close()
		#cv2.circle(frame, center, 5, (0, 0, 255), -1)
        # show the frame to our screen
	if args.mask == "both":
	    cv2.imshow("Frame", mask)
	elif args.mask == "1":
	    cv2.imshow("Frame", mask1)
	elif args.mask == "2":
	    cv2.imshow("Frame", mask2)
        elif args.mask == "3":
            alpha = 0.3
            overlay = cv2.addWeighted(cv2.cvtColor(mask,cv2.COLOR_GRAY2RGB), alpha, frame, 1 - alpha, 0)
            cv2.putText(overlay, str(int(max(bounding_box[1][0], bounding_box[1][1]))), (int(bounding_box[0][0]) - 5, int(bounding_box[0][1]) - 5), 1, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow('Frame', overlay)
            if not args.dontwrite:
                out.write(overlay)
	elif args.tracker:
            if ver_float <= 3.2: # later versions of opencv have a different syntax for tracker
                # Update tracker
                mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
                ok, bbox = tracker.update(mask_rgb)

                # Draw bounding box
                if ok:
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(original, p1, p2, (0,0,255))

                # Display result
                cv2.imshow("Frame", original)
	        out.write(original)
        else:
	    cv2.imshow("Frame", frame)
            if not args.dontwrite:
                out.write(frame)
	count = count + 1
        time.sleep(args.delay)
        if operating_sys == "Darwin": # on MacOS
            key = cv2.waitkey(20)
        else: # Windows and Linux
            key = cv2.waitKey(1) & 0xFF

        # if the 'q' or esc key is pressed, stop the loop
        if key == 27 or key == ord("q"):
            break
        elif key == 32:
            key = cv2.waitKey(0)
            if key == 32:
                key = 0
    #print(frame.shape)
    cv2.destroyAllWindows()


# In[9]:

if args.file is not None:
    analyse_vid(args.file)
elif args.path is not None:
    mp4filelist = list()
    files = os.listdir(os.curdir)
    for eachfile in files:
        if fnmatch.fnmatch(eachfile, "*.mp4"):
            mp4filelist.append(eachfile)

    for eachfile in mp4filelist:
        print "processing file... " + eachfile
        analyse_vid(eachfile)
else:
    print("Need either path (-p) or file (-f) argument!")

if args.logsettings is not None:
    logfile = open(time.ctime() + args.logsettings, "w")
    for key, value in vars(args).iteritems():
        print(str(key) + " = " + str(value))
        logfile.write(str(key) + ":" + str(value) + "\n")
    logfile.write("\n")
    logfile.write("#" + " ".join(sys.argv) + "\n")
    logfile.write("#" + str(datetime.now()) + "\n")
    logfile.close()

