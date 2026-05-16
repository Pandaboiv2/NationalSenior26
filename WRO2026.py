#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from outil import tool

ev3 = EV3Brick()

grabbed_tiles = [
#front of the robot
    0, 0,
    0, 0,
#back of the robot
]

tool()