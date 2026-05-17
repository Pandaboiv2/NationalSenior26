#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from outil import tool
from finding_mozaic_pieces import grab_first_four_tiles

#mwehehehehe

ev3 = EV3Brick()

blue_tiles = [
    [True, True],
    [True, True],
    [True, True],
]
green_tiles = [
    [True, True],
    [True, True],
    [True, True],
]
yellow_tiles = [
    [True, True],
    [True, True],
    [True, True],
]
white_tiles = [
    [True, True],
    [True, True],
    [True, True],
]

grabbed_tiles = [
    #front of the robot
    0, 0,
    0, 0,
    #back of the robot
]


mosaic_pattern = tool()
grab_first_four_tiles(mosaic_pattern, grabbed_tiles, yellow_tiles, blue_tiles, green_tiles, white_tiles)