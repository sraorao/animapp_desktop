# Animapp
## The desktop app has undergone a major revamp and all documentation is now here: https://animapp.readthedocs.io/en/latest/index.html . The following instructions may still work for python2 systems, but but are deprecated. The latest version available on Conda is easier to install and use, so please try that if you are starting out with Animapp!

This is the desktop version. For the Android version, see separate repository.

## Installation on Ubuntu 16.04

### Docker container (Ubuntu 16.04, opencv 3.2.0 with ffmpeg)
The easiest way to run this software is through a Docker container. Once you have [installed Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce-1), retrieve the AnimApp container from the public repository on Docker Hub as follows (may require `sudo` permissions depending on your Docker installation):
```
docker pull sraorao/docker-python2-opencv-ffmpeg-animapp:initial
```
Following this, run the container as follows:
```
xhost +
docker run --tty --interactive --network=host --env DISPLAY=$DISPLAY --volume $XAUTH:/root/.Xauthority -it srao/docker-python2-opencv-ffmpeg-animapp:initial
```

### Manual installation for opencv 3.2.0

```
# Install all dependencies for OpenCV 3.2
apt-get -y update && apt-get -y install python2.7-dev wget unzip \
    build-essential cmake git pkg-config libatlas-base-dev gfortran \
    libjasper-dev libgtk2.0-dev libavcodec-dev libavformat-dev \
    libswscale-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libv4l-dev \
    && wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && pip install numpy\
    && wget https://github.com/Itseez/opencv/archive/3.2.0.zip -O opencv3.zip \
    && unzip -q opencv3.zip && mv /opencv-3.2.0 /opencv && rm opencv3.zip \
    && wget https://github.com/Itseez/opencv_contrib/archive/3.2.0.zip -O opencv_contrib3.zip \
    && unzip -q opencv_contrib3.zip && mv /opencv_contrib-3.2.0 /opencv_contrib && rm opencv_contrib3.zip \

    # prepare build
    && mkdir /opencv/build && cd /opencv/build \
    && cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D BUILD_PYTHON_SUPPORT=ON \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D OPENCV_EXTRA_MODULES_PATH=/opencv_contrib/modules \
      -D BUILD_EXAMPLES=OFF \
      -D WITH_IPP=OFF \
      -D WITH_FFMPEG=ON \
      -D WITH_V4L=ON .. \

    # install
    && cd /opencv/build && make -j$(nproc) && make install && ldconfig \
    && cd /home/ && git clone https://github.com/sraorao/animapp_desktop && mkdir /home/data
```
* Install Pandas, Numpy python packages - `pip install numpy matplotlib pandas`

Either with Docker or manual installation, run AnimApp scripts (located in the `/home/animapp_desktop` folder) as follows:
```
python /home/animapp_desktop/set_thresholds_v5.py -f /home/animapp_desktop/sample_videos/VID_20180408_193620.mp4
python /home/animapp_desktop/opencv_colour_tracking_v12.py -f /home/animapp_desktop/sample_videos/cut_video.mp4 -dw -l 0 0 0 -u 180 255 40 -r 5 -m 3
```
## Installation on MacOS (High Sierra)
Installation on MacOS is very simple, but Homebrew must be installed on the Mac. [See here for instructions.](https://brew.sh/)
Enter the following in the terminal (command + T) after Homebrew is installed.
```
brew install ffmpeg
brew install opencv --with-contrib --with-ffmpeg
git clone "https://github.com/sraorao/animapp_desktop"
```
## Usage

### Pre-processing (get region of interest coordinates, hsv threshold values)

#### Commandline arguments
```
python set_thresholds_v5.py [-h] [-p PATH] [-f FILE]

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
python opencv_colour_tracking_v11.py [-h] [-p PATH] [-f FILE]
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
python process_csv.py [-h] [-f FILE] [-o OUTPUT]

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
