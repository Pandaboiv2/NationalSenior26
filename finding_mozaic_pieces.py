#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight
from outil import move_motors
import wro2026

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
        if target_matrix[target_row - 1][max(0, dir)]:
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
        if target_matrix[target_row - 1][0] and target_matrix[target_row - 1][1]:
            target_matrix[target_row - 1][0] = False
            target_matrix[target_row - 1][1] = False
        else:
            print("ERROR")
    #code that makes you go back to the original position (the one you were at before you moved to the tiles)

    move_motors(-300, 300, rotations=0.45 + target_row * 0.25)
    motor_a.run_time(750, 700)
    motor_d.run_time(-1000, 500)
    move_motors(300, -300, rotations=0.45 + target_row * 0.25)

def move_to_tiles(color : int):
    black_line_counter = 0

    while black_line_counter < color:
        pid_line_follower(follow_sensor_port=Port.S4,
                stop_sensor_port=Port.S1,
                base_speed=250,
                Kp=2, Kd=3, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="l")
        
        black_line_counter += 1
        print(black_line_counter)
        ev3.speaker.beep()
        move_motors(-300, 300, rotations=0.25)

    left_motor.hold()
    right_motor.hold()

#this is a comment

def grab_first_four_tiles(mosaic_pattern : list, grabbed_tiles : list, yellow_tiles : list, blue_tiles : list, green_tiles : list, white_tiles : list) -> None:
    array_of_colors = {
        1: wro2026.yellow_tiles,
        2: wro2026.blue_tiles,
        3: wro2026.green_tiles,
        4: wro2026.white_tiles,
    }
    if mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5] and mosaic_pattern[0] == mosaic_pattern[4]:
        move_to_tiles(mosaic_pattern[0])
        move_motors(300, 300, rotations=0.74)
        grab_tiles(array_of_colors[mosaic_pattern[0]], 2, 0)
        array_of_colors[mosaic_pattern[0]][0][0] = False
        array_of_colors[mosaic_pattern[0]][0][1] = False
        grabbed_tiles[0] = mosaic_pattern[0]
        grabbed_tiles[1] = mosaic_pattern[0]
        grabbed_tiles[4] = mosaic_pattern[0]
        grabbed_tiles[5] = mosaic_pattern[0]
    elif mosaic_pattern[0] == mosaic_pattern[4] and mosaic_pattern[1] == mosaic_pattern[5]:
        #676767676767
        grab_tiles(array_of_colors[mosaic_pattern[0]], 2, 0)
        #move to the correct color place
        grab_tiles(array_of_colors[mosaic_pattern[1]], 2, 0)
        wro2026.grabbed_tiles[0] = 1
        wro2026.grabbed_tiles[1] = 1
        wro2026.grabbed_tiles[2] = 1
        wro2026.grabbed_tiles[3] = 1
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