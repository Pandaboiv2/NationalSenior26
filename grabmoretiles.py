#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight
from outil import move_motors
from finding_mozaic_pieces import grab_tiles

"""
REMINDER:
CLOCKWISE = --
COUNTER-CLOCKWISE = ++
FORWARD = -+
BACKWARD = +-

COLORS:
YELLOW = 1
BLUE = 2
GREEN = 3
WHITE = 4

MOZAIC:
    0, 1, 2, 3
    4, 5, 6, 7
    8, 9, 10, 11

GRABBED_TILES = [
FRONT
    0, 0,
    0, 0,
BACK
]
"""

def grab_second_four_tiles(mosaic_pattern: list, color_arrays: list):
    grabbed_tiles = [
        0, 0,
        0, 0,
    ]
    move_motors(300, -300, rotations=0.8)
    move_motors(300, 300, rotations=1.48)
    pid_line_follower(follow_sensor_port=Port.S1,
                stop_sensor_port=Port.S4,
                base_speed=300,
                Kp=3, Kd=4, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="r",)
    wait(250)

    move_motors(-300, 300, rotations=0.3)
    move_motors(-300, -300, rotations=0.76)

    #all same
    if mosaic_pattern[6] == mosaic_pattern[7] and mosaic_pattern[10] == mosaic_pattern[11] and mosaic_pattern[6] == mosaic_pattern[10]:
        GrabSAME(grabbed_tiles, color_arrays, mosaic_pattern[6] - 1)
    
    elif mosaic_pattern[6] == mosaic_pattern[11] and mosaic_pattern[7] == mosaic_pattern[10]:
        pass

    #horizontal
    elif mosaic_pattern[6] == mosaic_pattern[7] and mosaic_pattern[10] == mosaic_pattern[11]:
        GrabHORI(grabbed_tiles, color_arrays, mosaic_pattern[6] - 1, mosaic_pattern[10] - 1)
    #vertical
    elif mosaic_pattern[6] == mosaic_pattern[10] and mosaic_pattern[7] == mosaic_pattern[11]:
        GrabVERT(grabbed_tiles, color_arrays, mosaic_pattern[6] - 1, mosaic_pattern[10] - 1)
    #vertical only left
    elif mosaic_pattern[6] == mosaic_pattern[10]:
        GrabVERTL(grabbed_tiles, color_arrays, mosaic_pattern[6] - 1, mosaic_pattern[11] - 1)
    #vertical only right
    elif mosaic_pattern[7] == mosaic_pattern[11]:
        GrabVERTR(grabbed_tiles, color_arrays, mosaic_pattern[7] - 1, mosaic_pattern[10] - 1)
    #horizontal only one side
    elif mosaic_pattern[6] == mosaic_pattern[7] or mosaic_pattern[10] == mosaic_pattern[11]:
        GrabVERTR(grabbed_tiles, color_arrays, mosaic_pattern[7] - 1, mosaic_pattern[10] - 1)
    #else
    else:
        GrabELSE(grabbed_tiles, color_arrays, mosaic_pattern)
    
    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]
    # grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3] = grabRight2Tiles(mosaic_pattern, grabbed_tiles, color_arrays)
    # grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3] = grabLeft2Tiles(mosaic_pattern, grabbed_tiles, color_arrays)

#these programs are now useless
def grab_similar(grabbed_tiles: list, color_index: int, color_arrays):
    left = GetClosestAvailableTiles(color_arrays[color_index - 1], -1)
    right = GetClosestAvailableTiles(color_arrays[color_index - 1], 1)
    if left == right:
        color_arrays[color_index - 1] = grab_tiles(color_arrays[color_index - 1], left, 0, grabbed_tiles)
    else:
        if left > right:
            color_arrays[color_index - 1] = grab_tiles(color_arrays[color_index - 1], right, 1, grabbed_tiles)
            color_arrays[color_index - 1] = grab_tiles(color_arrays[color_index - 1], left, -1, grabbed_tiles)
        else:
            color_arrays[color_index - 1] = grab_tiles(color_arrays[color_index - 1], left, -1, grabbed_tiles)
            color_arrays[color_index - 1] = grab_tiles(color_arrays[color_index - 1], right, 1, grabbed_tiles)
    return grabbed_tiles, color_arrays

#these programs are now useless
def grab_else(GrabbedTiles, LeftColor, RightColor, ColorArrays, first : bool = True):
    left = GetClosestAvailableTiles(ColorArrays[LeftColor - 1], -1)
    right = GetClosestAvailableTiles(ColorArrays[RightColor - 1], 1)
    firstcolor = min(LeftColor, RightColor)
    secondcolor = max(LeftColor, RightColor)
    if firstcolor == left:
        firstdir = -1
    else:
        firstdir = 1
    seconddir = firstdir*-1
    if firstdir == -1:
        ColorArrays[firstcolor - 1] = grab_tiles(ColorArrays[firstcolor - 1], left, firstdir, GrabbedTiles)
    else:
        ColorArrays[firstcolor - 1] = grab_tiles(ColorArrays[firstcolor - 1], right, firstdir, GrabbedTiles)
        
    MoveToColor(secondcolor, firstcolor)

    if seconddir == 1:
        ColorArrays[secondcolor - 1] = grab_tiles(ColorArrays[secondcolor - 1], right, seconddir, GrabbedTiles)
    else:
        ColorArrays[secondcolor - 1] = grab_tiles(ColorArrays[secondcolor - 1], left, seconddir, GrabbedTiles)
    
    if first:
        if firstdir == 1:
            GrabbedTiles[0] = secondcolor
            GrabbedTiles[1] = firstcolor
        else:
            GrabbedTiles[1] = secondcolor
            GrabbedTiles[0] = firstcolor
    else:
        if firstdir == 1:
            GrabbedTiles[2] = secondcolor
            GrabbedTiles[3] = firstcolor
        else:
            GrabbedTiles[3] = secondcolor
            GrabbedTiles[2] = firstcolor
    return GrabbedTiles, ColorArrays

#move to a color, and turn to face it
def MoveToColor(target_color: int, starting_color: int) -> None:
    get_distance = 0.5 * (target_color - starting_color)
    if get_distance > 0:
        pid_line_follower(follow_sensor_port=Port.S4,
                stop_sensor_port=Port.S1,
                base_speed=300,
                Kp=3, Kd=3, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="l",
                stop_count=int(get_distance / 0.5))
        wait(250)
        move_motors(-300, 300, rotations=0.24)
        left_motor.hold()
        right_motor.hold()
    else:
        move_motors(300, 300, rotations=1.54)
        pid_line_follower(follow_sensor_port=Port.S1,
                stop_sensor_port=Port.S4,
                base_speed=300,
                Kp=3, Kd=3, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="r",
                stop_count=int(abs(get_distance) / 0.5))
        wait(100)
        move_motors(-300, 300, rotations=0.28)
        wait(100)
        move_motors(300, 300, rotations=1.54)

#get closest tile index to the front (0, 1, 2 in that order)
def GetClosestAvailableTiles(color_list, dir):
    index = 0
    for i in range(3):
        if color_list[i][dir]:
            index = min(index, i)
    return index

#if all 4 tiles are the same
def GrabSAME(GrabbedTiles, ColorArrays, ColorIndex):
    MoveToColor(ColorIndex, 2.5)
    left = GetClosestAvailableTiles(ColorArrays[ColorIndex - 1], -1)
    right = GetClosestAvailableTiles(ColorArrays[ColorIndex - 1], 1)
    if left == right:
        ColorArrays[ColorIndex - 1] = grab_tiles(ColorArrays[ColorIndex - 1], right + 1, 0, GrabbedTiles)
        grabbed_tiles[0] = ColorIndex
        grabbed_tiles[1] = ColorIndex
        grabbed_tiles[2] = ColorIndex
        grabbed_tiles[3] = ColorIndex
    else:
        if left < 2 or right < 2:
            if left < right:
                fewest_dir = -1
            else:
                fewest_dir = 1
            
    return GrabbedTiles, ColorArrays

#def Grab