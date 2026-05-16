#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight
from outil import move_motors
import WRO2026
from outil import mosaic_pattern


def grab_tiles(target_matrix : list, target_row : int, dir : int) -> None:
    #the dir parameter is which block you want to take, either the left (-1) right (1) or both (0)
    #the target_row parameter is which row of tiles you want to grab. the first row is 1, second 2 and last row 3
    #target_matrix is which matrix you want to take (the lists that I made on top containing all tile colors)

    #There are 2 ways you can go the right distance
    #1. Have an if/else tree that changes based off the target_row you inputed
    """
    for example:
    if target_row == 3:
        move forwards by 100 cm
    elif target_row == 2:
        move forwards by 120 cm
    elif target_row == 1:
        move farwards by 140 cm
    """

    if abs(dir) > 0:
        if not target_matrix[target_row - 1][max(0, dir)]:
            target_matrix[target_row - 1][max(0, dir)] = False
            #Furthermore, to be able to grab only left or only right, your robot needs to be offset from the center
            #of all the tiles. You can easily solve this with this program (make it at the begining tho)
            move_motors(500*dir, -500*dir, rotations=0.3)
            move_motors(-500, 500, rotations=0.5)
            move_motors(-500*dir, -500*dir, rotations=0.3)
            move_motors(500, -500, rotations=0.4)
            target_matrix[target_row - 1][max(0, dir)] = False
            """
            move_right by -dir*50 cm.
            or you can equally put:
            move_left by dir*50 cm.
            """
        else:
            print("ERROR")
    else:
        if not target_matrix[target_row - 1][0] and not target_matrix[target_row - 1][1]:
            target_matrix[target_row - 1][0] = False
            target_matrix[target_row - 1][1] = False
        else:
            print("ERROR")
    #code that makes you go back to the original position (the one you were at before you moved to the tiles)

    #The second way requires a lot less code
    #However, it needs for everything to be very VERY precise and for it to follow a set order
    #2. Have a move forwards by 100+(target_row)*20 cm
    """
    for example:
    move forwards by 100 (base distance) + target_row * 20 (intervals between each tile) cm
    """
    move_motors(-500, 500, rotations=0.3 + target_row * 0.2)
    #Code that lowers the lifter
    #Code that grabs the tile

def grab_first_four_tiles(mosaic_pattern : list) -> None:
    array_of_colors = {
        1: WRO2026.yellow_tiles,
        2: WRO2026.blue_tiles,
        3: WRO2026.green_tiles,
        4: WRO2026.white_tiles,
    }
    if mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5] and mosaic_pattern[0] == mosaic_pattern[4]:
        #move to the correct color place
        grab_tiles(array_of_colors[mosaic_pattern[0]], 1, 0)
        grab_tiles(array_of_colors[mosaic_pattern[0]], 2, 0)
        WRO2026.grabbed_tiles[0] = 1
        WRO2026.grabbed_tiles[1] = 1
        WRO2026.grabbed_tiles[4] = 1
        WRO2026.grabbed_tiles[5] = 1
    elif mosaic_pattern[0] == mosaic_pattern[4] and mosaic_pattern[1] == mosaic_pattern[5]
        #676767676767
        grab_tiles(array_of_colors[mosaic_pattern[0]], 2, 0)
        #move to the correct color place
        grab_tiles(array_of_colors[mosaic_pattern[1]], 2, 0)
        WRO2026.grabbed_tiles[0] = 1
        WRO2026.grabbed_tiles[1] = 1
        WRO2026.grabbed_tiles[4] = 1
        WRO2026.grabbed_tiles[5] = 1
    elif mosaic_pattern[1] == mosaic_pattern[4] and mosaic_pattern[0] == mosaic_pattern[5]:
        #this is a criss cross thingy
        pass
        #i dont really know how to do this one D:
    elif mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5]:
        #for this one, all the tiles are aligned vertically
        pass
    else:
        #for this one, all the tiles are different
        #plus im too lazy to continue so im just gonna leave it like this
        pass