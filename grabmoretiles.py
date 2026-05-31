#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight
from outil import move_motors
from finding_mozaic_pieces import grab_tiles

# moves to the correct color (absolute, from reference color)
def MoveToColor(target_color: int, starting_color: int) -> None:
    get_distance = 0.5 * (target_color - starting_color)
    if get_distance > 0:
        pid_line_follower(
            follow_sensor_port=Port.S4,
            stop_sensor_port=Port.S1,
            base_speed=300,
            Kp=3, Kd=3, Ki=0,
            target=48,
            max_angle=None,
            stop_mode="c",
            stop_threshold=22,
            side="l",
            stop_count=int(get_distance / 0.5),
        )
        wait(250)
        move_motors(-300, 300, rotations=0.24)
        left_motor.hold()
        right_motor.hold()
    else:
        move_motors(300, 300, rotations=1.54)
        pid_line_follower(
            follow_sensor_port=Port.S1,
            stop_sensor_port=Port.S4,
            base_speed=300,
            Kp=3, Kd=3, Ki=0,
            target=48,
            max_angle=None,
            stop_mode="c",
            stop_threshold=22,
            side="r",
            stop_count=int(abs(get_distance) / 0.5),
        )
        wait(100)
        move_motors(-300, 300, rotations=0.22)
        wait(100)
        move_motors(300, 300, rotations=1.54)

# relative move between colors (same as first sorting logic)
def go_to_some_tiles(target_color: int, starting_color: int) -> None:
    distance = 0.5 * (target_color - starting_color)

    if distance > 0:
        pid_line_follower(
            follow_sensor_port=Port.S4,
            stop_sensor_port=Port.S1,
            base_speed=300,
            Kp=3, Kd=3, Ki=0,
            target=48,
            max_angle=None,
            stop_mode="c",
            stop_threshold=22,
            side="l",
            stop_count=int(distance / 0.5),
        )
        wait(250)
        move_motors(-300, 300, rotations=0.24)
        left_motor.hold()
        right_motor.hold()
    else:
        move_motors(300, 300, rotations=1.54)
        pid_line_follower(
            follow_sensor_port=Port.S1,
            stop_sensor_port=Port.S4,
            base_speed=300,
            Kp=3, Kd=3, Ki=0,
            target=48,
            max_angle=None,
            stop_mode="c",
            stop_threshold=22,
            side="r",
            stop_count=int(abs(distance) / 0.5),
        )
        wait(100)
        move_motors(-300, 300, rotations=0.22)
        wait(100)
        move_motors(300, 300, rotations=1.54)

# both back tiles same color (index 0 and 4 same)
def two_same_second(color, grabbed_tiles, color_arrays):
    # go to that color from second-sorting start (2.5)
    MoveToColor(color, 2.5)

    # first grab left side (direction -1), row auto-chosen by grab_tiles
    color_arrays[color - 1] = grab_tiles(color_arrays[color - 1], -1, -1, grabbed_tiles)
    grabbed_tiles[2] = color  # back-left

    # then grab right side (direction 1), again row auto-chosen
    color_arrays[color - 1] = grab_tiles(color_arrays[color - 1], -1, 1, grabbed_tiles)
    grabbed_tiles[3] = color  # back-right

    return grabbed_tiles, color_arrays

# back-left and back-right different colors
def two_not_same_second(left_color, right_color, grabbed_tiles, color_arrays):
    # choose closest color first (same rule as before)
    if left_color <= right_color:
        first_color, first_dir = left_color, -1   # left
        second_color, second_dir = right_color, 1 # right
    else:
        first_color, first_dir = right_color, 1
        second_color, second_dir = left_color, -1

    # FIRST TILE
    MoveToColor(first_color, 2.5)
    color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], -1, first_dir, grabbed_tiles)
    if first_dir == -1:
        grabbed_tiles[2] = first_color
    else:
        grabbed_tiles[3] = first_color

    # SECOND TILE (relative move between colors)
    go_to_some_tiles(second_color, first_color)
    color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], -1, second_dir, grabbed_tiles)
    if second_dir == -1:
        grabbed_tiles[2] = second_color
    else:
        grabbed_tiles[3] = second_color

    return grabbed_tiles, color_arrays

# FINAL: grab_second_four_tiles
def grab_second_four_tiles(mosaic_pattern: list, color_arrays: list):
    grabbed_tiles = [0, 0, 0, 0]

    # repositioning (Option B)
    move_motors(500, -500, rotations=1.5)
    move_motors(500, 500, rotations=1.48)
    pid_line_follower(
        follow_sensor_port=Port.S1,
        stop_sensor_port=Port.S4,
        base_speed=380,
        Kp=3, Kd=4, Ki=0,
        target=48,
        max_angle=None,
        stop_mode="c",
        stop_threshold=22,
        side="r",
    )
    wait(250)

    move_motors(-400, 400, rotations=0.35)
    move_motors(-400, -400, rotations=0.76)

    # ONLY INDEX 0 AND 4
    back_left  = mosaic_pattern[0]
    back_right = mosaic_pattern[4]

    if back_left == back_right:
        grabbed_tiles, color_arrays = two_same_second(back_left, grabbed_tiles, color_arrays)
    else:
        grabbed_tiles, color_arrays = two_not_same_second(back_left, back_right, grabbed_tiles, color_arrays)

    go_to_bottom(back_right if back_left != back_right else back_left)

    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]

def go_to_bottom(starting_color) -> None:
    distance = 0.5 * (2.5 - starting_color)

    if starting_color == 1:
        distance += 0.8
    elif starting_color == 2:
        distance += 0.3
    elif starting_color == 3:
        distance += -0.08
    elif starting_color == 4:
        distance += -0.45

    move_motors(-400, 400, rotations=distance)
    wait(100)
    move_motors(-400, -400, rotations=0.76)
    wait(100)
    move_motors(-390, 390, rotations=0.25)
    wait(100)

    pid_line_follower(
        follow_sensor_port=Port.S4,
        stop_sensor_port=Port.S1,
        base_speed=350,
        Kp=3, Kd=4, Ki=0,
        target=48,
        max_angle=None,
        stop_mode="c",
        stop_threshold=22,
        side="l",
    )
    wait(100)

    left_motor.run_angle(-300, 65)
    wait(100)
    right_motor.run_angle(300, 60)
    wait(100)

    motor_a.run_time(400, 400)
    wait(100)

    motor_d.run(-750)

    motor_a.run_time(-500, 300)
    wait(100)

    move_motors(-300, 300, rotations=0.55)
    wait(250)

    motor_a.run_time(1000, 350)
    wait(100)

    motor_d.run_time(750, 650)
    wait(100)

    motor_a.run_time(-1000, 600)
    wait(100)
    motor_a.run_time(1500, 1000)
    wait(100)
    motor_a.run_time(-500, 600)
    wait(100)

















'''
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
    move_motors(500, -500, rotations=1.5)
    move_motors(500, 500, rotations=1.48)
    pid_line_follower(follow_sensor_port=Port.S1,
                stop_sensor_port=Port.S4,
                base_speed=380,
                Kp=3, Kd=4, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="r",)
    wait(250)

    move_motors(-400, 400, rotations=0.35)
    move_motors(-400, -400, rotations=0.76)

    #all same
    if mosaic_pattern[6] == mosaic_pattern[7] and mosaic_pattern[10] == mosaic_pattern[11] and mosaic_pattern[6] == mosaic_pattern[10]:
        grabbed_tiles, color_arrays = GrabSAME(grabbed_tiles, color_arrays, mosaic_pattern[6])
    
    elif mosaic_pattern[6] == mosaic_pattern[11] and mosaic_pattern[7] == mosaic_pattern[10]:
        pass

    #horizontal
    elif mosaic_pattern[6] == mosaic_pattern[7] and mosaic_pattern[10] == mosaic_pattern[11]:
        grabbed_tiles, color_arrays = GrabHORI(grabbed_tiles, color_arrays, mosaic_pattern[6], mosaic_pattern[10])
    #vertical
    elif mosaic_pattern[6] == mosaic_pattern[10] and mosaic_pattern[7] == mosaic_pattern[11]:
        grabbed_tiles, color_arrays = GrabVERT(grabbed_tiles, color_arrays, mosaic_pattern[6], mosaic_pattern[7])
    #else
    else:
        #GrabELSE(grabbed_tiles, color_arrays, mosaic_pattern)
        pass
        #to lazy to do this function. ask claude to do it urself.
    
    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]
    # grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3] = grabRight2Tiles(mosaic_pattern, grabbed_tiles, color_arrays)
    # grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3] = grabLeft2Tiles(mosaic_pattern, grabbed_tiles, color_arrays)

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
    else:
        if left < right:
            fewest_dir = 1
        else:
            fewest_dir = -1
        if left >= 2 or right >= 2:
            ColorArrays[ColorIndex - 1] = grab_tiles(ColorArrays[ColorIndex - 1], 0, -fewest_dir, GrabbedTiles)
            ColorArrays[ColorIndex - 1] = grab_tiles(ColorArrays[ColorIndex - 1], 1, 0, GrabbedTiles)
            ColorArrays[ColorIndex - 1] = grab_tiles(ColorArrays[ColorIndex - 1], 2, 0, GrabbedTiles)
        else:
            ColorArrays[ColorIndex - 1] = grab_tiles(ColorArrays[ColorIndex - 1], 0, -fewest_dir, GrabbedTiles)
            ColorArrays[ColorIndex - 1] = grab_tiles(ColorArrays[ColorIndex - 1], 1, 0, GrabbedTiles)
            ColorArrays[ColorIndex - 1] = grab_tiles(ColorArrays[ColorIndex - 1], 2, fewest_dir, GrabbedTiles)

    GrabbedTiles[0] = ColorIndex
    GrabbedTiles[1] = ColorIndex
    GrabbedTiles[2] = ColorIndex
    GrabbedTiles[3] = ColorIndex
    return GrabbedTiles, ColorArrays

def GrabHORI(GrabbedTiles, ColorArrays, ColorTOP, ColorBOTTOM):
    MoveToColor(ColorBOTTOM, 2.5)
    lefttop = GetClosestAvailableTiles(ColorArrays[ColorTOP - 1], -1)
    righttop = GetClosestAvailableTiles(ColorArrays[ColorTOP - 1], 1)

    leftbot = GetClosestAvailableTiles(ColorArrays[ColorBOTTOM - 1], -1)
    rightbot = GetClosestAvailableTiles(ColorArrays[ColorBOTTOM - 1], 1)

    if leftbot == rightbot:
        ColorArrays[ColorBOTTOM - 1] = grab_tiles(ColorArrays[ColorBOTTOM - 1], leftbot, 0, GrabbedTiles)
    else:
        if leftbot < rightbot:
            ColorArrays[ColorBOTTOM - 1] = grab_tiles(ColorArrays[ColorBOTTOM - 1], leftbot, -1, GrabbedTiles)
            ColorArrays[ColorBOTTOM - 1] = grab_tiles(ColorArrays[ColorBOTTOM - 1], rightbot, 1, GrabbedTiles)
        else:
            ColorArrays[ColorBOTTOM - 1] = grab_tiles(ColorArrays[ColorBOTTOM - 1], rightbot, 1, GrabbedTiles)
            ColorArrays[ColorBOTTOM - 1] = grab_tiles(ColorArrays[ColorBOTTOM - 1], leftbot, -1, GrabbedTiles)

    MoveToColor(ColorTOP, ColorBOTTOM)

    if lefttop == righttop:
        ColorArrays[ColorTOP - 1] = grab_tiles(ColorArrays[ColorTOP - 1], lefttop, 0, GrabbedTiles)
    else:
        if lefttop < righttop:
            ColorArrays[ColorTOP - 1] = grab_tiles(ColorArrays[ColorTOP - 1], righttop, -1, GrabbedTiles)
            ColorArrays[ColorTOP - 1] = grab_tiles(ColorArrays[ColorTOP - 1], lefttop, 1, GrabbedTiles)
        else:
            ColorArrays[ColorTOP - 1] = grab_tiles(ColorArrays[ColorTOP - 1], righttop, 1, GrabbedTiles)
            ColorArrays[ColorTOP - 1] = grab_tiles(ColorArrays[ColorTOP - 1], lefttop, -1, GrabbedTiles)

    
    GrabbedTiles[0] = ColorTOP
    GrabbedTiles[1] = ColorTOP
    GrabbedTiles[2] = ColorBOTTOM
    GrabbedTiles[3] = ColorBOTTOM
    return GrabbedTiles, ColorArrays
    
def GrabVERT(GrabbedTiles, ColorArrays, ColorLEFT, ColorRIGHT):
    first_color = min(ColorLEFT, ColorRIGHT)
    second_color = max(ColorLEFT, ColorRIGHT)
    
    LLeft = GetClosestAvailableTiles(ColorArrays[ColorLEFT - 1], -1)
    LRight = GetClosestAvailableTiles(ColorArrays[ColorLEFT - 1], 1)

    RLeft = GetClosestAvailableTiles(ColorArrays[ColorRIGHT - 1], -1)
    RRight = GetClosestAvailableTiles(ColorArrays[ColorRIGHT - 1], 1)

    if left_color == first_color:
        first_dir = -1
        second_dir = 1
    else:
        first_dir = 1
        second_dir = -1
    
    MoveToColor(first_color, 2.5)
    if LLeft < LRight:
        LFewest = 1
    else:
        LFewest = -1
    
    if RLeft < RRight:
        RFewest = 1
    else:
        RFewest = -1

    if first_dir == -1:
        if LLeft == LRight:
            ColorArrays[first_color - 1] = grab_tiles(ColorArrays[first_color - 1], LLeft, first_dir, GrabbedTiles)
        else:
            ColorArrays[first_color - 1] = grab_tiles(ColorArrays[first_color - 1], LLeft if LFewest == -1 else LRight, 0, GrabbedTiles)

    else:
        if RLeft == RRight:
            ColorArrays[first_color - 1] = grab_tiles(ColorArrays[first_color - 1], RLeft, first_dir, GrabbedTiles)
        else:
            ColorArrays[first_color - 1] = grab_tiles(ColorArrays[first_color - 1], RLeft if RFewest == -1 else RRight, 0, GrabbedTiles)

    go_to_some_tiles(second_color, first_color)

    if second_dir == -1:
        if LLeft == LRight:
            ColorArrays[second_color - 1] = grab_tiles(ColorArrays[second_color - 1], LLeft, second_dir, GrabbedTiles)
            ColorArrays[second_color - 1] = grab_tiles(ColorArrays[second_color - 1], LLeft, 0, GrabbedTiles)
        else:
            ColorArrays[second_color - 1] = grab_tiles(ColorArrays[second_color - 1], LLeft if LFewest == -1 else LRight, 0, GrabbedTiles)
            ColorArrays[second_color - 1] = grab_tiles(ColorArrays[second_color - 1], LRight if LFewest == -1 else LLeft, second_dir, GrabbedTiles)
    else:
        if RLeft == RRight:
            ColorArrays[second_color - 1] = grab_tiles(ColorArrays[second_color - 1], RLeft, second_dir, GrabbedTiles)
            ColorArrays[second_color - 1] = grab_tiles(ColorArrays[second_color - 1], RLeft, 0, GrabbedTiles)
        else:
            ColorArrays[second_color - 1] = grab_tiles(ColorArrays[second_color - 1], RLeft if RFewest == -1 else RRight, 0, GrabbedTiles)
            ColorArrays[second_color - 1] = grab_tiles(ColorArrays[second_color - 1], RRight if RFewest == -1 else RLeft, second_dir, GrabbedTiles)

    go_to_some_tiles(first_color, second_color)
    if first_dir == -1:
        if LLeft == LRight:
            ColorArrays[first_color - 1] = grab_tiles(ColorArrays[first_color - 1], LLeft, first_dir, GrabbedTiles)
        else:
            ColorArrays[first_color - 1] = grab_tiles(ColorArrays[first_color - 1], LRight if LFewest == -1 else LRight, first_dir, GrabbedTiles)
    else:
        if RLeft == RRight:
            ColorArrays[first_color - 1] = grab_tiles(ColorArrays[first_color - 1], RLeft, first_dir, GrabbedTiles)
        else:
            ColorArrays[first_color - 1] = grab_tiles(ColorArrays[first_color - 1], LRight if LFewest == -1 else LRight, first_dir, GrabbedTiles)

    GrabbedTiles[0] = ColorLEFT
    GrabbedTiles[1] = ColorRIGHT
    GrabbedTiles[2] = ColorLEFT
    GrabbedTiles[3] = ColorRIGHT

    return GrabbedTiles, ColorArrays

def go_to_bottom(starting_color) -> None:
    get_distance = 0.5 * (0 - starting_color)
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
    move_motors(-350, 350, rotations=get_distance)
    wait(50)
    move_motors(-300, -300, rotations=0.76)
    wait(50)
    move_motors(-300, 300, rotations=0.25)
    wait(50)
    
    pid_line_follower(follow_sensor_port=Port.S4,
                stop_sensor_port=Port.S1,
                base_speed=350,
                Kp=3, Kd=4, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="l",)
    wait(250)

'''