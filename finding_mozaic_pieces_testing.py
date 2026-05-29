#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight
from outil import move_motors

def grab_tiles(target_matrix: list, target_row: int, dir: int, grabbed_tiles: list, facing: int = 1) -> list:
    #dir (0 for both, -1 for left and 1 for right)
    #facing is
    if abs(dir) > 0:
        target_matrix[target_row][max(0, dir)] = False
        move_motors(300*dir*facing, -300*dir*facing, rotations=0.25+max(dir, 0)*0.08)
        move_motors(300*facing, 300*facing, rotations=0.74)
        target_matrix[target_row][max(0, dir)] = False
    else:
        target_matrix[target_row][0] = False
        target_matrix[target_row][1] = False
        move_motors(300, 300, rotations=0.745)
      
    motor_a.run_time(500, 300)
    motor_d.run_time(1000, 650)
    if (grabbed_tiles[2] != 0 and grabbed_tiles[3] != 0) and (grabbed_tiles[0] != 0 or grabbed_tiles[1] != 0):
        motor_a.run_time(-250, 200)
    else:
        motor_a.run_time(-750, 400)
    move_motors(-300, 300, rotations=0.575 + target_row * 0.35)
    wait(80)
    motor_a.run_time(300, 600)
    motor_d.run(-750)
    wait(600)
    motor_a.run_time(-500, 300)
    move_motors(300, -300, rotations=0.56 + target_row * 0.35)
    move_motors(-300*facing, -300*facing, rotations=0.74)
    if abs(dir) > 0:
        move_motors(-300*dir, 300*dir, rotations=0.33)
    return target_matrix

def move_to_tiles(color: int):
    #only works if it starts behind the yellow
    black_line_counter = 0
    while black_line_counter < color:
        pid_line_follower(follow_sensor_port=Port.S4,
                stop_sensor_port=Port.S1,
                base_speed=300,
                Kp=2, Kd=3, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="l")
        
        black_line_counter += 1
        move_motors(-300, 300, rotations=0.24)

    left_motor.hold()
    right_motor.hold()

def go_to_some_tiles(target_color: int, starting_color: int) -> None:
    get_distance = 0.5 * (target_color - starting_color)
    #go from starting at one color to going to another
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
        move_motors(-300, 300, rotations=0.24)
        wait(100)
        move_motors(300, 300, rotations=1.52)

def grab_horizontal(mosaic_pattern: list, grabbed_tiles: list, color_arrays: list):
    back_color = mosaic_pattern[0]
    front_color = mosaic_pattern[1]

    #grab back first
    move_to_tiles(back_color)
    grabbed_tiles[2] = back_color
    grabbed_tiles[3] = back_color
    color_arrays[back_color - 1] = grab_tiles(color_arrays[back_color - 1], 0, 0, grabbed_tiles)

    go_to_some_tiles(front_color, back_color)
    color_arrays[front_color - 1] = grab_tiles(color_arrays[front_color - 1], 0, 0, grabbed_tiles)
    grabbed_tiles[0] = front_color
    grabbed_tiles[1] = front_color

    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]

def grab_vertical(mosaic_pattern: list, grabbed_tiles: list, color_arrays: list):
    left_color = mosaic_pattern[0]
    right_color = mosaic_pattern[4]

    first_color = min(left_color, right_color)
    second_color = max(left_color, right_color)

    if left_color == first_color:
        first_dir = -1
        second_dir = 1
    else:
        first_dir = 1
        second_dir = -1

    # Trip 1: back of first color
    move_to_tiles(first_color)
    color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, first_dir, grabbed_tiles)
    if first_dir == -1:
        grabbed_tiles[2] = first_color  # back-left
    else:
        grabbed_tiles[3] = first_color  # back-right
    print("after trip 1:", grabbed_tiles)

    # Trip 2: back of second color
    go_to_some_tiles(second_color, first_color)
    color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, second_dir, grabbed_tiles)  # CHANGED: target_row=1 to grab both rows at once
    if second_dir == -1:
        grabbed_tiles[2] = second_color  # back-left
    else:
        grabbed_tiles[3] = second_color  # back-right
    print("after trip 2:", grabbed_tiles)

    # Trip 3: front of second color
    print(color_arrays[first_color - 1])
    color_arrays[first_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, 0, grabbed_tiles)
    ev3.speaker.beep()
    if second_dir == -1:
        grabbed_tiles[0] = second_color  # front-left
    else:
        grabbed_tiles[1] = second_color  # front-right
    print("after trip 3:", grabbed_tiles)


    # Trip 4: front of first color
    go_to_some_tiles(first_color, second_color)
    color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, 0, grabbed_tiles)
    if first_dir == -1:
        grabbed_tiles[0] = first_color  # front-left
    else:
        grabbed_tiles[1] = first_color  # front-right
    print("after trip 4:", grabbed_tiles)

    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], first_color

def grab_vertical_single(grabbed_tiles, color_arrays, mozaic_colors):
    if mozaic_colors[0] == mozaic_colors[1]:
        direction = -1
        first_color = mozaic_colors[0]
        second_top_color = mozaic_colors[5]
        second_bottom_color = mozaic_colors[4]
    else:
        direction = 1
        first_color = mozaic_color[4]
        second_top_color = mozaic_colors[1]
        second_bottom_color = mozaic_colors[0]

    # Trip 2: back of second color
    move_to_tiles(first_color)
    color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, direction, grabbed_tiles)
    color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, 0, grabbed_tiles)
    ev3.speaker.beep()
    if direction == -1:
        grabbed_tiles[0] = first_color
        grabbed_tiles[2] = first_color
    else:
        grabbed_tiles[1] = first_color
        grabbed_tiles[3] = first_color

    go_to_some_tiles(second_bottom_color, first_color)
    color_arrays[second_bottom_color - 1] = grab_tiles(color_arrays[second_bottom_color - 1], 0, -direction, grabbed_tiles)

    go_to_some_tiles(second_top_color, second_bottom_color)
    color_arrays[second_top_color - 1] = grab_tiles(color_arrays[second_top_color - 1], 0, -direction, grabbed_tiles)

    if direction == -1:
        grabbed_tiles[1] = second_top_color
        grabbed_tiles[3] = second_bottom_color
    else:
        grabbed_tiles[0] = second_top_color
        grabbed_tiles[2] = second_bottom_color
    
    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], second_top_color

def grab_else(mosaic_pattern: list, grabbed_tiles: list, color_arrays: list):
    back_left = mosaic_pattern[0]
    back_right = mosaic_pattern[4]
    front_left = mosaic_pattern[1]
    front_right = mosaic_pattern[5]

    # closest back first (lower color number = closer to start)
    if back_left <= back_right:
        back_first = back_left
        dir1 = -1
        back_second = back_right
        dir2 = 1
    else:
        back_first = back_right
        dir1 = 1
        back_second = back_left
        dir2 = -1

    # grab first back
    move_to_tiles(back_first)
    color_arrays[back_first - 1] = grab_tiles(color_arrays[back_first - 1], 0, dir1, grabbed_tiles)
    if dir1 == -1:
        grabbed_tiles[2] = back_first
    else:
        grabbed_tiles[3] = back_first
    print("after back first grab:", grabbed_tiles)

    # grab second back
    go_to_some_tiles(back_second, back_first)
    color_arrays[back_second - 1] = grab_tiles(color_arrays[back_second - 1], 0, dir2, grabbed_tiles)
    if dir2 == -1:
        grabbed_tiles[2] = back_second
    else:
        grabbed_tiles[3] = back_second
    print("after back second grab:", grabbed_tiles)

    # front slots, closest from current position (back_second)
    front_first = min(front_left, front_right, key=lambda c: abs(c - back_second))
    front_second = front_left if front_first == front_right else front_right

    # dir based on which side front_first is on
    dir3 = -1 if front_first == front_left else 1
    dir4 = -1 if front_second == front_left else 1

    go_to_some_tiles(front_first, back_second)
    color_arrays[front_first - 1] = grab_tiles(color_arrays[front_first - 1], 0, dir3, grabbed_tiles)
    if dir3 == -1:
        grabbed_tiles[1] = front_first
    else:
        grabbed_tiles[0] = front_first
    print("after front first grab:", grabbed_tiles)

    go_to_some_tiles(front_second, front_first)
    color_arrays[front_second - 1] = grab_tiles(color_arrays[front_second - 1], 0, dir4, grabbed_tiles)
    if dir4 == -1:
        grabbed_tiles[1] = front_second
    else:
        grabbed_tiles[0] = front_second
    print("after front second grab:", grabbed_tiles)

    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], front_second

def grab_first_four_tiles(mosaic_pattern: list, grabbed_tiles: list, color_arrays: list):
    if mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5] and mosaic_pattern[0] == mosaic_pattern[4]:
        # all 4 are the same color
        move_to_tiles(mosaic_pattern[0])
        color_arrays[mosaic_pattern[0] - 1] = grab_tiles(color_arrays[mosaic_pattern[0] - 1], 1, 0, grabbed_tiles)
        grabbed_tiles[0] = mosaic_pattern[0]
        grabbed_tiles[1] = mosaic_pattern[0]
        grabbed_tiles[2] = mosaic_pattern[0]
        grabbed_tiles[3] = mosaic_pattern[0]
        go_to_center(mosaic_pattern[0])

    elif mosaic_pattern[1] == mosaic_pattern[4] and mosaic_pattern[0] == mosaic_pattern[5]:
        # criss cross
        first_color = min(mosaic_pattern[0], mosaic_pattern[1])
        second_color = max(mosaic_pattern[0], mosaic_pattern[1])

        if mosaic_pattern[0] == first_color:
            first_dir = -1
            second_dir = 1
        else:
            first_dir = 1
            second_dir = -1

        # Trip 1: back slot of first color
        move_to_tiles(first_color)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, first_dir, grabbed_tiles)
        if first_dir == -1:
            grabbed_tiles[2] = first_color  # back-left
        else:
            grabbed_tiles[3] = first_color  # back-right

        # Trip 2: both second color slots
        go_to_some_tiles(second_color, first_color)
        wait(150)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, second_dir, grabbed_tiles)
        if second_dir == -1:
            grabbed_tiles[2] = second_color  # back-left
        else:
            grabbed_tiles[3] = second_color  # back-right
        wait(250)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, -second_dir, grabbed_tiles)
        if second_dir == -1:
            grabbed_tiles[0] = second_color  # front-left (opposite of back-left)
        else:
            grabbed_tiles[1] = second_color  # front-right (opposite of back-right)

        # Trip 3: front slot of first color
        go_to_some_tiles(first_color, second_color)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, -first_dir, grabbed_tiles)
        if first_dir == -1:
            grabbed_tiles[0] = first_color  # front-right (opposite of back-left)
        else:
            grabbed_tiles[1] = first_color  # front-left (opposite of back-right)

        go_to_center(first_color)

    elif mosaic_pattern[0] == mosaic_pattern[4] and mosaic_pattern[1] == mosaic_pattern[5]:
        #horizontal case
        grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3] = grab_horizontal(mosaic_pattern, grabbed_tiles, color_arrays)
        go_to_center(mosaic_pattern[1])

    elif mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5]:
        #vertical case
        grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], last_color = grab_vertical(mosaic_pattern, grabbed_tiles, color_arrays)
        go_to_center(last_color)

    #vertical only one
    elif mosaic_pattern[0] == mosaic_pattern[1] or mosaic_pattern[4] == mosaic_pattern[5]:
        grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], last_color = grab_vertical_single(grabbed_tiles, color_arrays, mosaic_pattern)
        go_to_center(last_color)

    else:
        #all different or mixed use grab_else
        grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], last_color = grab_else(mosaic_pattern, grabbed_tiles, color_arrays)
        go_to_center(last_color)

    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]

def go_to_center(starting_color) -> None:
    get_distance = 0.5 * (2.5 - starting_color)
    #at yellow
    if starting_color == 1:
        get_distance += 0.8
    #at blue
    elif starting_color == 2:
        get_distance += 0.3
    #at green
    elif starting_color == 3:
        get_distance += -0.12
    #at white
    elif starting_color == 4:
        get_distance += -0.45
    move_motors(-400, 400, rotations=get_distance)
    wait(100)
    move_motors(-400, -400, rotations=0.76)
    wait(100)
    move_motors(-390, 390, rotations=0.25)
    wait(100)
    
    pid_line_follower(follow_sensor_port=Port.S4,
                stop_sensor_port=Port.S1,
                base_speed=350,
                Kp=3, Kd=4, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="l",)
    wait(100)

    motor_a.run_time(200, 300)
    wait(100)

    left_motor.run_angle(-300, 65)
    wait(100)
    right_motor.run_angle(300, 65)
    wait(100)

    motor_a.run_time(-850, 500)
    wait(100)

    move_motors(-300, 300, rotations=0.7)
    wait(250)

    motor_a.run_time(550, 350)
    wait(100)
    
    motor_d.run_time(750, 650)
    wait(100)

    motor_a.run_time(-750, 600)
    wait(100)
    motor_a.run_time(1000, 650)
    wait(100)
    motor_a.run_time(-500, 600)
    wait(100)

    move_motors(300, -300, rotations=0.3)
    wait(100)

    motor_a.run_time(750, 500)
    wait(100)

    motor_a.run_time(-1050, 500)
    wait(100)

def grab_vertical_single(grabbed_tiles, color_arrays, mosaic_colors):
    if mosaic_colors[0] == mosaic_colors[1]:
        first_color = mosaic_colors[0]
        second_top_color = mosaic_colors[5]
        second_bottom_color = mosaic_colors[4]
        direction = -1
    else:
        first_color = mosaic_colors[4]
        second_top_color = mosaic_colors[1]
        second_bottom_color = mosaic_colors[0]
        direction = 1

    # Back of doubled color
    move_to_tiles(first_color)
    color_arrays[first_color - 1] = grab_tiles(
        color_arrays[first_color - 1], 0, direction, grabbed_tiles
    )
    if direction == -1:
        grabbed_tiles[2] = first_color
    else:
        grabbed_tiles[3] = first_color

    # Back of single color
    go_to_some_tiles(second_bottom_color, first_color)
    color_arrays[second_bottom_color - 1] = grab_tiles(
        color_arrays[second_bottom_color - 1], 0, -direction, grabbed_tiles
    )
    if direction == -1:
        grabbed_tiles[3] = second_bottom_color
    else:
        grabbed_tiles[2] = second_bottom_color

    # Front of single color
    go_to_some_tiles(second_top_color, second_bottom_color)
    color_arrays[second_top_color - 1] = grab_tiles(
        color_arrays[second_top_color - 1], 0, -direction, grabbed_tiles
    )
    if direction == -1:
        grabbed_tiles[1] = second_top_color
    else:
        grabbed_tiles[0] = second_top_color

    # Front of doubled color
    go_to_some_tiles(first_color, second_top_color)
    color_arrays[first_color - 1] = grab_tiles(
        color_arrays[first_color - 1], 0, direction, grabbed_tiles
    )
    if direction == -1:
        grabbed_tiles[0] = first_color
    else:
        grabbed_tiles[1] = first_color

    return (
        grabbed_tiles,color_arrays[0],color_arrays[1],color_arrays[2],color_arrays[3],first_color)