#!/bin/bash
chek1=$(pip list|grep -o -E 'Pillow.+'|cut -d ' ' -f 25)
if [ "$chek1" == "2.2.1" ]; then 
    pip install pillow==6.2.1
fi
catkin_make
source devel/setup.sh
roslaunch launch/styx.launch