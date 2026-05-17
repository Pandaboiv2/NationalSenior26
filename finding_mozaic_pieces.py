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

    move_motors(-300*facing, 300*facing, rotations=0.6 + target_row * 0.35)
    motor_a.run_time(600, 500)
    motor_d.run(-400)
    wait(500)
    motor_a.run_time(-500, 200)
    move_motors(300*facing, -300*facing, rotations=0.6 + target_row * 0.35)
    return target_matrix

def move_to_tiles(color : int):
    black_line_counter = 0

    while black_line_counter < color:
        pid_line_follower(follow_sensor_port=Port.S4,
                stop_sensor_port=Port.S1,
                base_speed=400,
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
        move_motors(300, 300, rotations=1.52)

def grab_first_four_tiles(mosaic_pattern : list, grabbed_tiles : list, color_arrays : list):
    if mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5] and mosaic_pattern[0] == mosaic_pattern[4]:
        move_to_tiles(mosaic_pattern[0])
        move_motors(300, 300, rotations=0.74)
        color_arrays[mosaic_pattern[0] - 1] = grab_tiles(color_arrays[mosaic_pattern[0] - 1], 0, 0)
        color_arrays[mosaic_pattern[0] - 1][0][0] = False
        color_arrays[mosaic_pattern[0] - 1][0][1] = False
        print(color_arrays[mosaic_pattern[0] - 1])
        grabbed_tiles[0] = mosaic_pattern[0]
        grabbed_tiles[1] = mosaic_pattern[0]
        grabbed_tiles[2] = mosaic_pattern[0]
        grabbed_tiles[3] = mosaic_pattern[0]

        distance_to_move_back = 1 * (mosaic_pattern[0] - 2.5)
        move_motors(300, 300, rotations=0.76)
        move_motors(-300, 300, rotations=distance_to_move_back)
        move_motors(300, 300, rotations=0.74)
        move_motors(-300, 300, rotations=0.5)
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
        move_motors(300, 300, rotations=0.74)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, first_dir)
        move_motors(-300, -300, rotations=0.74)
        if first_dir == -1:
            grabbed_tiles[2] = first_color
        else:
            grabbed_tiles[1] = first_color

        # Trip 2 — grab both second color slots
        go_to_some_tiles(second_color, first_color)
        move_motors(300, 300, rotations=0.74)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, second_dir)
        move_motors(-300, -300, rotations=0.72)
        move_motors(-300*second_dir, 300*second_dir, rotations=0.35)
        move_motors(300, 300, rotations=0.72)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, -second_dir)
        move_motors(-300, -300, rotations=0.74)
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
#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight
from outil import move_motors


def grab_tiles(target_matrix : list, target_row : int, dir : int) -> list:
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
            move_motors(-300, -300, rotations=0.72)
            move_motors(300*dir, -300*dir, rotations=0.35)
            move_motors(300, 300, rotations=0.72)
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

    move_motors(-300, 300, rotations=0.35 + target_row * 0.25)
    motor_a.run_time(600, 500)
    motor_d.run(-500)
    wait(500)
    motor_a.run_time(-500, 200)
    move_motors(300, -300, rotations=0.35 + target_row * 0.25)
    return target_matrix

def move_to_tiles(color : int):
    black_line_counter = 0

    while black_line_counter < color:
        pid_line_follower(follow_sensor_port=Port.S4,
                stop_sensor_port=Port.S1,
                base_speed=400,
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


def go_to_some_tiles(target_color : int, starting_color : int) -> None:
    get_distance = 0.5 * (target_color - starting_color)
    
    if get_distance > 0:
        # moving forward (away from start)
        #move_motors(-300, -300, rotations=0.25)  # turn to face line
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
    else:
        # moving backward (towards start)
        move_motors(300, 300, rotations=1.52)  # turn to face line other way
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




def go_to_some_tiles(target_color : int, starting_color : int) -> None:
    get_distance = 0.5 * (target_color - starting_color)
    move_motors(-300, 300, rotations=get_distance)

def grab_first_four_tiles(mosaic_pattern : list, grabbed_tiles : list, color_arrays : list):
    if mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5] and mosaic_pattern[0] == mosaic_pattern[4]:
        move_to_tiles(mosaic_pattern[0])
        move_motors(300, 300, rotations=0.74)
        color_arrays[mosaic_pattern[0] - 1] = grab_tiles(color_arrays[mosaic_pattern[0] - 1], 2, 0)
        color_arrays[mosaic_pattern[0] - 1][0][0] = False
        color_arrays[mosaic_pattern[0] - 1][0][1] = False
        print(color_arrays[mosaic_pattern[0] - 1])
        grabbed_tiles[0] = mosaic_pattern[0]
        grabbed_tiles[1] = mosaic_pattern[0]
        grabbed_tiles[2] = mosaic_pattern[0]
        grabbed_tiles[3] = mosaic_pattern[0]

        distance_to_move_back = 1 * (mosaic_pattern[0] - 2.5)
        move_motors(300, 300, rotations=0.76)
        move_motors(-300, 300, rotations=distance_to_move_back)
        move_motors(300, 300, rotations=0.74)
        move_motors(-300, 300, rotations=0.5)
        #drop blocks code
        return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]
    
    elif mosaic_pattern[0] == mosaic_pattern[4] and mosaic_pattern[1] == mosaic_pattern[5]:
        #676767676767
        move_to_tiles(mosaic_pattern[0])
        move_motors(300, 300, rotations=0.74)
        grab_tiles(color_arrays[mosaic_pattern[0] - 1], 1, 0)
        move_motors(-300, -300, rotations=0.75)
        go_to_some_tiles(mosaic_pattern[0], mosaic_pattern[1])
        move_motors(300, 300, rotations=0.74)
        grab_tiles(color_arrays[mosaic_pattern[1] - 1], 2, 0)
        move_motors(-300, -300, rotations=0.75)

        #front tiles
        grabbed_tiles[0] = mosaic_pattern[0]
        grabbed_tiles[1] = mosaic_pattern[0]
        #back tiles
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

        # figure out which side each color is on
        if mosaic_pattern[0] == first_color:
            first_dir = -1   # first color is on left
            second_dir = 1   # second color is on right
        else:
            first_dir = 1    # first color is on right
            second_dir = -1  # second color is on left

        # Trip 1 — grab back slot of first color
        move_to_tiles(first_color)
        move_motors(300, 300, rotations=0.74)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 1, first_dir)
        move_motors(-300, -300, rotations=0.74)
        if first_dir == -1:
            grabbed_tiles[2] = first_color  # back left
        else:
            grabbed_tiles[1] = first_color  # front right

        # Trip 2 — grab both second color slots
        go_to_some_tiles(second_color, first_color)
        move_motors(300, 300, rotations=0.74)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 1, second_dir)
        move_motors(-500, -500, rotations=0.72)
        move_motors(-500*second_dir, 500*second_dir, rotations=0.35)
        move_motors(500, 500, rotations=0.72)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 1, -second_dir)
        move_motors(-300, -300, rotations=0.74)
        if second_dir == -1:
            grabbed_tiles[3] = second_color  # back right
            wait(2500)
            grabbed_tiles[0] = second_color  # front left
        else:
            grabbed_tiles[0] = second_color  # front left
            wait(2500)
            grabbed_tiles[3] = second_color  # back right

        # Trip 3 — grab remaining first color slot
        go_to_some_tiles(first_color, second_color)
        move_motors(300, 300, rotations=0.74)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 1, -first_dir)
        move_motors(-300, -300, rotations=0.74)
        if first_dir == -1:
            grabbed_tiles[1] = first_color  # front right
        else:
            grabbed_tiles[2] = first_color  # back left

        return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3] 
    
    elif mosaic_pattern[0] == mosaic_pattern[1] and mosaic_pattern[4] == mosaic_pattern[5]:
        #for this one, all the tiles are aligned vertically
        pass
    else:
        #for this one, all the tiles are different
        #plus im too lazy to continue so im just gonna leave it like this
        pass


'''

'''
    elif mosaic_pattern[1] == mosaic_pattern[4] and mosaic_pattern[0] == mosaic_pattern[5]:
        # criss cross case
        first_color = min(mosaic_pattern[0], mosaic_pattern[1])
        second_color = max(mosaic_pattern[0], mosaic_pattern[1])

        # figure out which side each color is on
        if mosaic_pattern[0] == first_color:
            first_dir = -1   # first color is on left
            second_dir = 1   # second color is on right
        else:
            first_dir = 1    # first color is on right
            second_dir = -1  # second color is on left

        # Trip 1 — grab back slot of first color
        move_to_tiles(first_color)
        move_motors(300, 300, rotations=0.74)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 1, first_dir)
        move_motors(-300, -300, rotations=0.74)
        if first_dir == -1:
            grabbed_tiles[2] = first_color  # back left
        else:
            grabbed_tiles[1] = first_color  # front right

        # Trip 2 — grab front slot of first color
        move_to_tiles(first_color)
        move_motors(300, 300, rotations=0.74)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 1, -first_dir)
        move_motors(-300, -300, rotations=0.74)
        if first_dir == -1:
            grabbed_tiles[1] = first_color  # front right
        else:
            grabbed_tiles[2] = first_color  # back left

        # Trip 3 — grab back slot of second color
        move_to_tiles(second_color)
        move_motors(300, 300, rotations=0.74)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 1, second_dir)
        move_motors(-300, -300, rotations=0.74)
        if second_dir == -1:
            grabbed_tiles[3] = second_color  # back right
        else:
            grabbed_tiles[0] = second_color  # front left

        # Trip 4 — grab front slot of second color
        move_to_tiles(second_color)
        move_motors(300, 300, rotations=0.74)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 1, -second_dir)
        move_motors(-300, -300, rotations=0.74)
        if second_dir == -1:
            grabbed_tiles[0] = second_color  # front left
        else:
            grabbed_tiles[3] = second_color  # back right

        return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]
'''