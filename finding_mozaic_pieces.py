#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight
from outil import move_motors, turn_motors


def grab_tiles(target_matrix : list, target_row : int, dir : int, facing : int = 1) -> list:
    if abs(dir) > 0:
        if target_matrix[target_row][max(0, dir)]:
            target_matrix[target_row][max(0, dir)] = False
            move_motors(300*dir*facing, -300*dir*facing, rotations=0.35)
            move_motors(300*facing, 300*facing, rotations=0.74)
            target_matrix[target_row][max(0, dir)] = False
        else:
            print("ERROR")
    else:
        if target_matrix[target_row][0] and target_matrix[target_row][1]:
            target_matrix[target_row][0] = False
            target_matrix[target_row][1] = False
            turn_motors(-132, speed=40)
            #move_motors(300, 300, rotations=0.74)
        else:
            print("ERROR")
    
    motor_d.run_time(1000, 500)
    wait(100)
    motor_a.run_time(-750, 350)
    move_motors(-300*facing, 300*facing, rotations=0.575 + target_row * 0.35)
    wait(100)
    motor_a.run_time(300, 600)
    motor_d.run(-400)
    wait(500)
    motor_a.run_time(-500, 200)
    move_motors(300*facing, -300*facing, rotations=0.6 + target_row * 0.35)
    move_motors(-300*facing, -300*facing, rotations=0.76)
    if dir == 1:
        move_motors(-300, 300, rotations=0.25)
    if dir == -1:
        move_motors(300, -300, rotations=0.25)
    return target_matrix


def move_to_tiles(color : int):
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
        print(black_line_counter)
        ev3.speaker.beep()
        move_motors(-300, 300, rotations=0.18)

    left_motor.hold()
    right_motor.hold()


def go_to_some_tiles(target_color : int, starting_color : int) -> None:
    get_distance = 0.5 * (target_color - starting_color)
    
    if get_distance > 0:
        pid_line_follower(follow_sensor_port=Port.S4,
                stop_sensor_port=Port.S1,
                base_speed=300,
                Kp=2, Kd=3, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="l",
                stop_count=int(get_distance / 0.5))
        wait(100)
        move_motors(-300, 300, rotations=0.18)
    else:
        turn_motors(-264, speed=45)
        #move_motors(300, 300, rotations=1.52)
        pid_line_follower(follow_sensor_port=Port.S1,
                stop_sensor_port=Port.S4,
                base_speed=300,
                Kp=2, Kd=3, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="r",
                stop_count=int(abs(get_distance) / 0.5))
        wait(100)
        move_motors(-300, 300, rotations=0.35)
        wait(100)
        turn_motors(-264, speed=45)
        ev3.speaker.beep()
        #move_motors(300, 300, rotations=1.52)

def grab_first_four_tiles(mosaic_pattern : list, grabbed_tiles : list, color_arrays : list):
    if mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5] and mosaic_pattern[0] == mosaic_pattern[4]:
        #all 4 are the same color
        move_to_tiles(mosaic_pattern[0])
        color_arrays[mosaic_pattern[0] - 1] = grab_tiles(color_arrays[mosaic_pattern[0] - 1], 1, 0)
        color_arrays[mosaic_pattern[0] - 1] = grab_tiles(color_arrays[mosaic_pattern[0] - 1], 0, 0)
        grabbed_tiles[0] = mosaic_pattern[0]
        grabbed_tiles[1] = mosaic_pattern[0]
        grabbed_tiles[2] = mosaic_pattern[0]
        grabbed_tiles[3] = mosaic_pattern[0]
        return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]


    elif mosaic_pattern[0] == mosaic_pattern[4] and mosaic_pattern[1] == mosaic_pattern[5]:
        move_to_tiles(mosaic_pattern[0])
        move_motors(300, 300, rotations=0.74)
        grab_tiles(color_arrays[mosaic_pattern[0] - 1], 0, 0)
        move_motors(-300, -300, rotations=0.75)
        go_to_some_tiles(mosaic_pattern[1], mosaic_pattern[0])
        move_motors(300, 300, rotations=0.74)
        grab_tiles(color_arrays[mosaic_pattern[1] - 1], 1, 0)
        move_motors(-300, -300, rotations=0.75)

        grabbed_tiles[0] = mosaic_pattern[0]
        grabbed_tiles[1] = mosaic_pattern[0]
        grabbed_tiles[2] = mosaic_pattern[1]
        grabbed_tiles[3] = mosaic_pattern[1]

        distance_to_move_back = 0.50 * (mosaic_pattern[1] - 2.5)
        move_motors(300, 300, rotations=0.74)
        move_motors(-300, 300, rotations=distance_to_move_back)
        move_motors(300, 300, rotations=0.74)
        move_motors(-300, 300, rotations=0.5)
        return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]
    
    elif mosaic_pattern[1] == mosaic_pattern[4] and mosaic_pattern[0] == mosaic_pattern[5]:
        # criss cross apple sauce case D:
        first_color = min(mosaic_pattern[0], mosaic_pattern[1])
        second_color = max(mosaic_pattern[0], mosaic_pattern[1])

        if mosaic_pattern[0] == first_color:
            first_dir = -1
            second_dir = 1
        else:
            first_dir = 1
            second_dir = -1

        # Trip 1: go grab the first cloest color
        move_to_tiles(first_color)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, first_dir)
        if first_dir == -1:
            grabbed_tiles[2] = first_color
        else:
            grabbed_tiles[1] = first_color

        # Trip 2 — go grab both of the second color
        go_to_some_tiles(second_color, first_color)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, second_dir)
        wait(250)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, -second_dir)
        grabbed_tiles[0] = second_color
        grabbed_tiles[3] = second_color

        # Trip 3 — go grab back to grab first color
        go_to_some_tiles(first_color, second_color)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, -first_dir)
        #move_motors(-300, -300, rotations=0.74)
        if first_dir == -1:
            grabbed_tiles[1] = first_color
        else:
            grabbed_tiles[2] = first_color

        return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]
    
    elif mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5]:
        # for this one, all the tiles are aligned vertically
        pass
    else:
        # for this one, all the tiles are different
        pass
















































'''
#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight
from outil import move_motors




def grab_tiles(target_matrix : list, target_row : int, dir : int, facing : int = 1) -> list:
    if abs(dir) > 0:
        if target_matrix[target_row][max(0, dir)]:
            target_matrix[target_row][max(0, dir)] = False
            move_motors(-300*facing, -300*facing, rotations=0.74)
            move_motors(300*dir*facing, -300*dir*facing, rotations=0.35)
            move_motors(300*facing, 300*facing, rotations=0.74)
            target_matrix[target_row][max(0, dir)] = False
        else:
            print("ERROR")
    else:
        if target_matrix[target_row][0] and target_matrix[target_row][1]:
            target_matrix[target_row][0] = False
            target_matrix[target_row][1] = False
        else:
            print("ERROR")
    
    motor_d.run_time(600, 500)
    wait(100)
    motor_a.run_time(-750, 350)
    move_motors(-300*facing, 300*facing, rotations=0.6 + target_row * 0.35)
    wait(100)
    motor_a.run_time(600, 500)
    motor_d.run(-400)
    wait(500)
    motor_a.run_time(-500, 200)
    move_motors(300*facing, -300*facing, rotations=0.6 + target_row * 0.35)
    move_motors(-300*facing, -300*facing, rotations=0.74)
    if dir == 1:
        move_motors(-300, 300, rotations=0.3)
    return target_matrix

    
def move_to_tiles(color : int):
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
        print(black_line_counter)
        ev3.speaker.beep()
        move_motors(-300, 300, rotations=0.18)

    left_motor.hold()
    right_motor.hold()


def go_to_some_tiles(target_color : int, starting_color : int) -> None:
    get_distance = 0.5 * (target_color - starting_color)
    
    if get_distance > 0:
        pid_line_follower(follow_sensor_port=Port.S4,
                stop_sensor_port=Port.S1,
                base_speed=300,
                Kp=2, Kd=3, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="l",
                stop_count=int(get_distance / 0.5))
        move_motors(-300, 300, rotations=0.18)
    else:
        move_motors(300, 300, rotations=1.52)
        pid_line_follower(follow_sensor_port=Port.S1,
                stop_sensor_port=Port.S4,
                base_speed=300,
                Kp=2, Kd=3, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="r",
                stop_count=int(abs(get_distance) / 0.5))
        move_motors(-300, 300, rotations=0.35)
        move_motors(300, 300, rotations=1.52)

def grab_first_four_tiles(mosaic_pattern : list, grabbed_tiles : list, color_arrays : list):
    if mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5] and mosaic_pattern[0] == mosaic_pattern[4]:
        #all 4 are the same color
        move_to_tiles(mosaic_pattern[0])
        move_motors(300, 300, rotations=0.74)
        color_arrays[mosaic_pattern[0] - 1] = grab_tiles(color_arrays[mosaic_pattern[0] - 1], 1, 0)  # front 2
        #color_arrays[mosaic_pattern[0] - 1] = grab_tiles(color_arrays[mosaic_pattern[0] - 1], 1, 0)  # back 2
        color_arrays[mosaic_pattern[0] - 1][0][0] = False
        color_arrays[mosaic_pattern[0] - 1][0][1] = False
        color_arrays[mosaic_pattern[0] - 1][1][0] = False
        color_arrays[mosaic_pattern[0] - 1][1][1] = False
        print(color_arrays[mosaic_pattern[0] - 1])
        grabbed_tiles[0] = mosaic_pattern[0]
        grabbed_tiles[1] = mosaic_pattern[0]
        grabbed_tiles[2] = mosaic_pattern[0]
        grabbed_tiles[3] = mosaic_pattern[0]

        distance_to_move_back = 1 * (mosaic_pattern[0] - 2.5)
        return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]


    elif mosaic_pattern[0] == mosaic_pattern[4] and mosaic_pattern[1] == mosaic_pattern[5]:
        move_to_tiles(mosaic_pattern[0])
        move_motors(300, 300, rotations=0.74)
        grab_tiles(color_arrays[mosaic_pattern[0] - 1], 0, 0)
        move_motors(-300, -300, rotations=0.75)
        go_to_some_tiles(mosaic_pattern[0], mosaic_pattern[1])
        move_motors(300, 300, rotations=0.74)
        grab_tiles(color_arrays[mosaic_pattern[1] - 1], 1, 0)
        move_motors(-300, -300, rotations=0.75)

        grabbed_tiles[0] = mosaic_pattern[0]
        grabbed_tiles[1] = mosaic_pattern[0]
        grabbed_tiles[2] = mosaic_pattern[1]
        grabbed_tiles[3] = mosaic_pattern[1]

        distance_to_move_back = 0.50 * (mosaic_pattern[1] - 2.5)
        move_motors(300, 300, rotations=0.74)
        move_motors(-300, 300, rotations=distance_to_move_back)
        move_motors(300, 300, rotations=0.74)
        move_motors(-300, 300, rotations=0.5)
        return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]
    
    elif mosaic_pattern[1] == mosaic_pattern[4] and mosaic_pattern[0] == mosaic_pattern[5]:
        # criss cross apple sauce case D:
        first_color = min(mosaic_pattern[0], mosaic_pattern[1])
        second_color = max(mosaic_pattern[0], mosaic_pattern[1])

        if mosaic_pattern[0] == first_color:
            first_dir = -1
            second_dir = 1
        else:
            first_dir = 1
            second_dir = -1

        # Trip 1 — grab back slot of first color
        move_to_tiles(first_color)
        move_motors(300, 300, rotations=0.75)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, first_dir)
        if first_dir == -1:
            grabbed_tiles[2] = first_color
        else:
            grabbed_tiles[1] = first_color

        # Trip 2 — grab both second color slots
        go_to_some_tiles(second_color, first_color)
        move_motors(300, 300, rotations=0.75)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, second_dir)
        move_motors(-300*second_dir, 300*second_dir, rotations=0.35)
        move_motors(300, 300, rotations=0.72)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, -second_dir)
        if second_dir == -1:
            grabbed_tiles[3] = second_color
            grabbed_tiles[0] = second_color
        else:
            grabbed_tiles[0] = second_color
            grabbed_tiles[3] = second_color

        # Trip 3 — grab remaining first color slot
        go_to_some_tiles(first_color, second_color)
        move_motors(300, 300, rotations=0.74)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, -first_dir)
        move_motors(-300, -300, rotations=0.74)
        if first_dir == -1:
            grabbed_tiles[1] = first_color
        else:
            grabbed_tiles[2] = first_color

        return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]
    
    elif mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5]:
        #for this one, all the tiles are aligned vertically
        pass
    else:
        #for this one, all the tiles are different
        pass
'''




