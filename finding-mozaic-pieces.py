#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight
from outil import move_motors


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

    #The second way requires a lot less code
    #However, it needs for everything to be very VERY precise and for it to follow a set order
    #2. Have a move forwards by 100+(target_row)*20 cm
    """
    for example:
    move forwards by 100 (base distance) + target_row * 20 (intervals between each tile) cm
    """
    move_motors(-500, 500, rotations=0.3 + target_row * 0.2)

    if abs(dir) > 0:
        if not target_matrix[target_row - 1][max(0, dir)]:
            target_matrix[target_row - 1][max(0, dir)] = False
            #Furthermore, to be able to grab only left or only right, your robot needs to be offset from the center
            #of all the tiles. You can easily solve this with this program (make it at the begining tho)
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

