#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from taking import mozaic
from outil1 import tool1
from outil2 import tool2
from ciment import tool3
from lastpart import part_last

ev3 = EV3Brick()

#mozaic()
sock=tool1()
'''
tool2(sock)
tool3(sock)
'''