# opencv_animal_tracking

Initially for desktop version, currently working on extending it to Android, will post code soon.

## Prerequisites

* OS - in theory, should work with any OS that has the following requirements installed, but has been tested only on MacOS X (High Sierra), Ubuntu 16.04 and Lubuntu 17.04 so far
* Python 2.7 
* Opencv for python - this is complicated, do **exactly** as below
  * First install opencv 3.3.0 as described here: http://docs.opencv.org/trunk/d7/d9f/tutorial_linux_install.html (install with opencv-contrib, and make sure to run `cmake`/`cmake-gui` with option `WITH_FFMPEG=TRUE`)
  * From the resultant build/lib/ folder, copy cv2.so to your python site-packages/cv2 folder, e.g.: `cp ~/bin/opencv/build/lib/cv2.so ~/.local/lib/python2.7/site-packages/cv2/`
* Ffmpeg - `sudo apt-get install ffmpeg`
* Pandas, Numpy - `pip install numpy matplotlib pandas`

## Installation on MacOS (High Sierra)
Installation on MacOS is very simple, but Homebrew must be installed on the Mac. [See here for instructions.](https://brew.sh/)
Enter the following in the terminal (command + T) after Homebrew is installed.
* `brew install ffmpeg`
* `brew install opencv --with-contrib --with-ffmpeg`
* `git clone "https://github.com/sraorao/opencv_animal_tracking"`

## Usage

### Pre-processing (get region of interest coordinates, hsv threshold values)

#### Commandline arguments
```
usage: set_thresholds_v5.py [-h] [-p PATH] [-f FILE]

Accessory tool to set thresholding limits; esc or q to quit, p to print
current hsv limits to terminal.

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  input path (default = current directory)
  -f FILE, --file FILE  input single filename with full path (required)

```
#### Output

* HSV value ranges for `-l` and `-u` arguments in the script below.
* If a rectangle is drawn, coordinates of the rectangle, which can be used for cropped box `-b` argument, useful to define a region of interest

### Run tracking script

#### Commandline arguments
```
usage: opencv_colour_tracking_v11.py [-h] [-p PATH] [-f FILE]
                                     [-l LOWER LOWER LOWER]
                                     [-u UPPER UPPER UPPER]
                                     [-l2 LOWER2 LOWER2 LOWER2]
                                     [-u2 UPPER2 UPPER2 UPPER2] [-d DELAY]
                                     [-m MASK] [-dw] [-r RADIUS]
                                     [-s LOGSETTINGS] [-o OUTPREFIX]
                                     [-b BOX BOX BOX BOX] [-ov OUTVIDEO]

Process mouse videos. esc or q to quit, space to (un)pause

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  input path (default = current directory) - ignored if
                        -f is given
  -f FILE, --file FILE  input single filename with full path
  -l LOWER LOWER LOWER, --lower LOWER LOWER LOWER
                        3 integers separated by spaces, in hsv scale for lower
                        limit of colour (default = 160 75 75). 0-179 0-255
                        0-255
  -u UPPER UPPER UPPER, --upper UPPER UPPER UPPER
                        3 integers separated by spaces, in hsv scale for upper
                        limit of colour (default = 179 255 255). 0-179 0-255
                        0-255
  -l2 LOWER2 LOWER2 LOWER2, --lower2 LOWER2 LOWER2 LOWER2
                        3 integers separated by spaces, in hsv scale for lower
                        limit of colour (default = lower). 0-179 0-255 0-255
  -u2 UPPER2 UPPER2 UPPER2, --upper2 UPPER2 UPPER2 UPPER2
                        3 integers separated by spaces, in hsv scale for upper
                        limit of colour (default = upper). 0-179 0-255 0-255
  -d DELAY, --delay DELAY
                        time delay (float) between frames in seconds (default
                        = 0)
  -m MASK, --mask MASK  show mask? acceptable values are "1" (mask from lower
                        and upper), "2" (mask from lower2 and upper2), "3"
                        (mask1 + mask2 overlaid on original video), "both"
                        (mask 1 + mask 2), or anything else ( = default, shows
                        original video.)
  -dw, --dontwrite      if specified, do not write values to csv file(s)
  -r RADIUS, --radius RADIUS
                        minimum size of object (default = 5)
  -s LOGSETTINGS, --logsettings LOGSETTINGS
                        file to which to write settings (default =
                        settings.log)
  -o OUTPREFIX, --outprefix OUTPREFIX
                        prefix to append to csv output filename (default = "")
  -b BOX BOX BOX BOX, --box BOX BOX BOX BOX
                        region of interest (x1, y1, x2, y2)
  -ov OUTVIDEO, --outvideo OUTVIDEO
                        prefix to append to output avi

```
#### Output

* CSV file with columns in the following order:
1. x
2. y
3. frame number
4. rotated_rectangle_centre_x
5. rotated_rectangle_centre_y
6. rotated_rectangle_width
7. rotated_rectangle_height
8. rotated_rectangle_angle

### Post-processing coordinates from CSV

#### Commandline arguments
```
usage: process_csv.py [-h] [-f FILE] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  csv file with 3 columns (x, y, frame) without header
                        line
  -o OUTPUT, --output OUTPUT
                        suffix to be added to output csv file
```
#### Output

##### processed.csv
* CSV file with columns in the following order:
1. x
2. y
3. frame number
4. Euclidean distance (from previous position)
5. rolling velocity
