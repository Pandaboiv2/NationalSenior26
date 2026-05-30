#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight
from outil import move_motors

def grab_tiles(target_matrix: list, target_row: int, direction: int, grabbed_tiles: list, facing: int = 1) -> list:
    # direction: 0 = both, -1 = left, 1 = right

    if abs(direction) > 0:
        # left or right grab
        side = 0 if direction == -1 else 1

        # NEW: if target_row is forced, use it
        if target_row in (0, 1, 2):
            row = target_row
        else:
            # auto mode (old behavior)
            for r in [0, 1, 2]:
                if target_matrix[r][side]:
                    row = r
                    break

        # mark tile as used
        target_matrix[row][side] = False

        # perform movement
        #move_motors(300 * direction * facing, -300 * direction * facing, rotations=0.36 - (0.06 if direction == -1 else 0))
        if direction == -1:
            move_motors(300 * facing, -300 * facing, rotations=0.30)

        elif direction == 1:
            move_motors(-300 * facing, 300 * facing, rotations=0.36)
        move_motors(300 * facing, 300 * facing, rotations=0.75) #problem with the rotation constant

    else:
        ev3.speaker.beep()
        # grabbing both tiles (pair)
        if target_row in (0, 1, 2):
            row = target_row
        else:
            for r in [0, 1, 2]:
                if target_matrix[r][0] and target_matrix[r][1]:
                    row = r
                    break

        # mark both as used
        target_matrix[row][0] = False
        target_matrix[row][1] = False

        move_motors(300, 300, rotations=0.745)

    motor_a.run_time(500, 300)
    motor_d.run_time(1000, 650)

    if (grabbed_tiles[2] != 0 and grabbed_tiles[3] != 0) and (grabbed_tiles[0] != 0 or grabbed_tiles[1] != 0):
        motor_a.run_time(-500, 300)
    else:
        motor_a.run_time(-750, 400)

    move_motors(-300, 300, rotations=0.575 + row * 0.35)
    wait(80)
    motor_a.run_time(300, 600)
    motor_d.run(-750)
    wait(600)
    motor_a.run_time(-500, 300)
    move_motors(300, -300, rotations=0.56 + row * 0.35)
    move_motors(-300 * facing, -300 * facing, rotations=0.74)

    if abs(direction) > 0:
        move_motors(300 * direction, -300 * direction, rotations=0.33)

    return target_matrix

def move_to_tiles(color: int):
    # starts behind yellow
    black_line_counter = 0
    while black_line_counter < color:
        pid_line_follower(
            follow_sensor_port=Port.S4,
            stop_sensor_port=Port.S1,
            base_speed=300,
            Kp=3.5, Kd=4, Ki=0,
            target=48,
            max_angle=None,
            stop_mode="c",
            stop_threshold=22,
            side="l",
        )
        black_line_counter += 1
        move_motors(-300, 300, rotations=0.22)

    left_motor.hold()
    right_motor.hold()

def go_to_some_tiles(target_color: int, starting_color: int) -> None:
    distance = 0.5 * (target_color - starting_color)

    if distance > 0:
        pid_line_follower(
            follow_sensor_port=Port.S4,
            stop_sensor_port=Port.S1,
            base_speed=300,
            Kp=3.5, Kd=4, Ki=0,
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
            Kp=3.5, Kd=4, Ki=0,
            target=48,
            max_angle=None,
            stop_mode="c",
            stop_threshold=22,
            side="r",
            stop_count=int(abs(distance) / 0.5),
        )
        wait(100)
        move_motors(-300, 300, rotations=0.24)
        wait(100)
        move_motors(300, 300, rotations=1.52)

def grab_horizontal(mosaic_pattern: list, grabbed_tiles: list, color_arrays: list):
    back_color = mosaic_pattern[0]
    front_color = mosaic_pattern[1]

    move_to_tiles(back_color)
    grabbed_tiles[2] = back_color
    grabbed_tiles[3] = back_color
    color_arrays[back_color - 1] = grab_tiles(color_arrays[back_color - 1], 0, 0, grabbed_tiles)

    go_to_some_tiles(front_color, back_color)
    color_arrays[front_color - 1] = grab_tiles(color_arrays[front_color - 1], 0, 0, grabbed_tiles)
    grabbed_tiles[0] = front_color
    grabbed_tiles[1] = front_color

    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]

def grab_horizontal_single(mosaic_pattern: list, grabbed_tiles: list, color_arrays: list):
    # one row is a pair, the other row has two different colors
    back_left = mosaic_pattern[0]
    front_left = mosaic_pattern[1]
    back_right = mosaic_pattern[4]
    front_right = mosaic_pattern[5]

    if back_left == back_right:
        pair_color = back_left
        single1 = front_left
        single2 = front_right
        pair_row_is_back = True
    else:
        pair_color = front_left
        single1 = back_left
        single2 = back_right
        pair_row_is_back = False

    # always fill back row first
    if pair_row_is_back:
        # back pair first
        move_to_tiles(pair_color)
        color_arrays[pair_color - 1] = grab_tiles(color_arrays[pair_color - 1], 0, 0, grabbed_tiles)
        grabbed_tiles[2] = pair_color
        grabbed_tiles[3] = pair_color

        # then front singles, closest color first
        first_front = min(single1, single2, key=lambda c: abs(c - pair_color))
        second_front = single1 if first_front == single2 else single2

        go_to_some_tiles(first_front, pair_color)
        color_arrays[first_front - 1] = grab_tiles(color_arrays[first_front - 1], 0, -1, grabbed_tiles)
        grabbed_tiles[0 if first_front == single1 else 1] = first_front

        go_to_some_tiles(second_front, first_front)
        color_arrays[second_front - 1] = grab_tiles(color_arrays[second_front - 1], 0, 1, grabbed_tiles)
        grabbed_tiles[1 if first_front == single1 else 0] = second_front

    else:
        # back singles first, closest to pair_color
        first_back = min(single1, single2, key=lambda c: abs(c - pair_color))
        second_back = single1 if first_back == single2 else single2

        move_to_tiles(first_back)
        color_arrays[first_back - 1] = grab_tiles(color_arrays[first_back - 1], 0, -1, grabbed_tiles)
        grabbed_tiles[2 if first_back == single1 else 3] = first_back

        go_to_some_tiles(second_back, first_back)
        color_arrays[second_back - 1] = grab_tiles(color_arrays[second_back - 1], 0, 1, grabbed_tiles)
        grabbed_tiles[3 if first_back == single1 else 2] = second_back

        # then front pair
        go_to_some_tiles(pair_color, second_back)
        color_arrays[pair_color - 1] = grab_tiles(color_arrays[pair_color - 1], 0, 0, grabbed_tiles)
        grabbed_tiles[0] = pair_color
        grabbed_tiles[1] = pair_color

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

    # back of first color
    move_to_tiles(first_color)
    color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, first_dir, grabbed_tiles)
    if first_dir == -1:
        grabbed_tiles[2] = first_color
    else:
        grabbed_tiles[3] = first_color

    # back of second color
    go_to_some_tiles(second_color, first_color)
    color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, second_dir, grabbed_tiles)
    if second_dir == -1:
        grabbed_tiles[2] = second_color
    else:
        grabbed_tiles[3] = second_color

    # front of second color
    color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, -second_dir, grabbed_tiles)
    if second_dir == -1:
        grabbed_tiles[0] = second_color
    else:
        grabbed_tiles[1] = second_color

    # front of first color
    go_to_some_tiles(first_color, second_color)
    color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, -first_dir, grabbed_tiles)
    if first_dir == -1:
        grabbed_tiles[1] = first_color
    else:
        grabbed_tiles[0] = first_color

    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], second_color

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

    # back of doubled color
    move_to_tiles(first_color)
    color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, direction, grabbed_tiles)
    if direction == -1:
        grabbed_tiles[2] = first_color
    else:
        grabbed_tiles[3] = first_color

    # back of single color
    go_to_some_tiles(second_bottom_color, first_color)
    color_arrays[second_bottom_color - 1] = grab_tiles(color_arrays[second_bottom_color - 1], 0, -direction, grabbed_tiles)
    if direction == -1:
        grabbed_tiles[3] = second_bottom_color
    else:
        grabbed_tiles[2] = second_bottom_color

    # front of single color
    go_to_some_tiles(second_top_color, second_bottom_color)
    color_arrays[second_top_color - 1] = grab_tiles(color_arrays[second_top_color - 1], 0, -direction, grabbed_tiles)
    if direction == -1:
        grabbed_tiles[1] = second_top_color
    else:
        grabbed_tiles[0] = second_top_color

    # front of doubled color
    go_to_some_tiles(first_color, second_top_color)
    color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, direction, grabbed_tiles)
    if direction == -1:
        grabbed_tiles[0] = first_color
    else:
        grabbed_tiles[1] = first_color

    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], first_color

def grab_three_same(mosaic_pattern, grabbed_tiles, color_arrays):
    a, b, c, d = mosaic_pattern[0], mosaic_pattern[1], mosaic_pattern[4], mosaic_pattern[5]

    colors = [a, b, c, d]
    for color in [1, 2, 3, 4]:
        if colors.count(color) == 3:
            triple_color = color
            break

    for color in [a, b, c, d]:
        if color != triple_color:
            odd_color = color
            break

    back_same = (a == triple_color and c == triple_color)

    # --- SCENARIO 1: back row same color ---
    if back_same:
        move_to_tiles(triple_color)
        color_arrays[triple_color - 1] = grab_tiles(color_arrays[triple_color - 1], 0, 0, grabbed_tiles)
        grabbed_tiles[2] = triple_color
        grabbed_tiles[3] = triple_color

        if b == triple_color:
            front_dir = -1
            front_index = 1
        else:
            front_dir = 1
            front_index = 0

        color_arrays[triple_color - 1] = grab_tiles(color_arrays[triple_color - 1], 1, front_dir, grabbed_tiles)
        grabbed_tiles[front_index] = triple_color

        go_to_some_tiles(odd_color, triple_color)
        odd_dir = -1 if b == odd_color else 1
        odd_index = 1 if odd_dir == -1 else 0
        color_arrays[odd_color - 1] = grab_tiles(color_arrays[odd_color - 1], 0, odd_dir, grabbed_tiles)
        grabbed_tiles[odd_index] = odd_color

        return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], odd_color

    # --- SCENARIO 2: back row NOT same color ---
    else:
        # figure out which side the odd color is on
        if a == odd_color:
            odd_dir = -1
            odd_back_index = 2
            triple_back_dir = 1
            triple_back_index = 3
        else:  # c == odd_color
            odd_dir = 1
            odd_back_index = 3
            triple_back_dir = -1
            triple_back_index = 2

        # figure out front slots of triple_color
        # b = front-left, d = front-right
        if b == triple_color and d == triple_color:
            front_same_side = (1 if triple_back_dir == 1 else -1, 0 if triple_back_dir == 1 else 1)
            front_other_side = (-1 if triple_back_dir == 1 else 1, 1 if triple_back_dir == 1 else 0)
        elif b == triple_color:
            front_same_side = (-1, 1)    # front-left
            front_other_side = None
        else:
            front_same_side = (1, 0)     # front-right
            front_other_side = None

        # Step 1: take odd color back
        move_to_tiles(odd_color)
        color_arrays[odd_color - 1] = grab_tiles(color_arrays[odd_color - 1], 0, odd_dir, grabbed_tiles)
        grabbed_tiles[odd_back_index] = odd_color

        # Step 2: go to triple color, take back slot
        go_to_some_tiles(triple_color, odd_color)
        color_arrays[triple_color - 1] = grab_tiles(color_arrays[triple_color - 1], 0, triple_back_dir, grabbed_tiles)
        grabbed_tiles[triple_back_index] = triple_color

        # Step 3: take front slot same side as back
        front_dir, front_index = front_same_side
        color_arrays[triple_color - 1] = grab_tiles(color_arrays[triple_color - 1], 1, front_dir, grabbed_tiles)  # CHANGED: no go_to_some_tiles, already at triple_color
        grabbed_tiles[front_index] = triple_color

        # Step 4: take front slot other side (only if exists)
        if front_other_side is not None:
            front_dir, front_index = front_other_side
            color_arrays[triple_color - 1] = grab_tiles(color_arrays[triple_color - 1], 0, front_dir, grabbed_tiles)  # CHANGED: no go_to_some_tiles
            grabbed_tiles[front_index] = triple_color

        return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], triple_color

def grab_else(mosaic_pattern: list, grabbed_tiles: list, color_arrays: list):
    back_left = mosaic_pattern[0]
    back_right = mosaic_pattern[4]
    front_left = mosaic_pattern[1]
    front_right = mosaic_pattern[5]

    # back first: closer to start (lower color number)
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

    move_to_tiles(back_first)
    color_arrays[back_first - 1] = grab_tiles(color_arrays[back_first - 1], 0, dir1, grabbed_tiles)
    if dir1 == -1:
        grabbed_tiles[2] = back_first
    else:
        grabbed_tiles[3] = back_first

    go_to_some_tiles(back_second, back_first)
    color_arrays[back_second - 1] = grab_tiles(color_arrays[back_second - 1], 0, dir2, grabbed_tiles)
    if dir2 == -1:
        grabbed_tiles[2] = back_second
    else:
        grabbed_tiles[3] = back_second

    # front: closest to last back color
    front_first = min(front_left, front_right, key=lambda c: abs(c - back_second))
    front_second = front_left if front_first == front_right else front_right

    dir3 = -1 if front_first == front_left else 1
    dir4 = -1 if front_second == front_left else 1

    go_to_some_tiles(front_first, back_second)
    color_arrays[front_first - 1] = grab_tiles(color_arrays[front_first - 1], 0, dir3, grabbed_tiles)
    if dir3 == -1:
        grabbed_tiles[1] = front_first
    else:
        grabbed_tiles[0] = front_first

    go_to_some_tiles(front_second, front_first)
    color_arrays[front_second - 1] = grab_tiles(color_arrays[front_second - 1], 0, dir4, grabbed_tiles)
    if dir4 == -1:
        grabbed_tiles[1] = front_second
    else:
        grabbed_tiles[0] = front_second

    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], front_second

def grab_first_four_tiles(mosaic_pattern: list, grabbed_tiles: list, color_arrays: list):
    a, b, c, d = mosaic_pattern[0], mosaic_pattern[1], mosaic_pattern[4], mosaic_pattern[5]

    # all 4 same
    if a == b == c == d:
        move_to_tiles(a)
        color_arrays[a - 1] = grab_tiles(color_arrays[a - 1], 1, 0, grabbed_tiles)
        grabbed_tiles[0] = grabbed_tiles[1] = grabbed_tiles[2] = grabbed_tiles[3] = a
        go_to_center(a)

    # full criss-cross: 0==5 and 1==4
    elif a == d and b == c:
        first_color = min(a, b)
        second_color = max(a, b)

        if a == first_color:
            first_dir = -1
            second_dir = 1
        else:
            first_dir = 1
            second_dir = -1

        move_to_tiles(first_color)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, first_dir, grabbed_tiles)
        if first_dir == -1:
            grabbed_tiles[2] = first_color
        else:
            grabbed_tiles[3] = first_color

        go_to_some_tiles(second_color, first_color)
        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, second_dir, grabbed_tiles)
        if second_dir == -1:
            grabbed_tiles[2] = second_color
        else:
            grabbed_tiles[3] = second_color

        color_arrays[second_color - 1] = grab_tiles(color_arrays[second_color - 1], 0, -second_dir, grabbed_tiles)
        if second_dir == -1:
            grabbed_tiles[0] = second_color
        else:
            grabbed_tiles[1] = second_color

        go_to_some_tiles(first_color, second_color)
        color_arrays[first_color - 1] = grab_tiles(color_arrays[first_color - 1], 0, -first_dir, grabbed_tiles)
        if first_dir == -1:
            grabbed_tiles[1] = first_color
        else:
            grabbed_tiles[0] = first_color

        go_to_center(first_color)

    #3 same colors
    elif len({a,b,c,d})==2 and not(a==b==c==d) and (a==b==c or a==b==d or a==c==d or b==c==d):
        ev3.speaker.beep()
        grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], last_color = grab_three_same(mosaic_pattern, grabbed_tiles, color_arrays)
        go_to_center(last_color)

    # partial criss-cross: one diagonal equal, other not
    elif a == d or b == c:
        grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], last_color = grab_else(mosaic_pattern, grabbed_tiles, color_arrays)
        go_to_center(last_color)

    # horizontal pair both rows
    elif a == c and b == d:
        grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3] = grab_horizontal(mosaic_pattern, grabbed_tiles, color_arrays)
        go_to_center(b)
    
    # horizontal single
    elif a == c or b == d:
        grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3] = grab_horizontal_single(mosaic_pattern, grabbed_tiles, color_arrays)
        go_to_center(a if a == c else b)

    # vertical pair both columns
    elif a == b and c == d:
        grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], last_color = grab_vertical(mosaic_pattern, grabbed_tiles, color_arrays)
        go_to_center(last_color)

    # vertical single
    elif a == b or c == d:
        grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], last_color = grab_vertical_single(grabbed_tiles, color_arrays, mosaic_pattern)
        go_to_center(last_color)

    else:
        grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3], last_color = grab_else(mosaic_pattern, grabbed_tiles, color_arrays)
        go_to_center(last_color)

    return grabbed_tiles, color_arrays[0], color_arrays[1], color_arrays[2], color_arrays[3]

def go_to_center(starting_color) -> None:
    distance = 0.5 * (2.5 - starting_color)

    if starting_color == 1:
        distance += 0.8
    elif starting_color == 2:
        distance += 0.3
    elif starting_color == 3:
        distance += -0.08
    elif starting_color == 4:
        ev3.speaker.beep()
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

    motor_a.run_time(500, 200)
    wait(100)

    motor_a.run_time(-500, 300)
    wait(100)

    move_motors(-300, 300, rotations=0.65)
    wait(250)

    motor_a.run_time(550, 350)
    wait(100)

    motor_d.run_time(750, 650)
    wait(100)

    motor_a.run_time(-1000, 600)
    wait(100)
    motor_a.run_time(1500, 850)
    wait(100)
    motor_a.run_time(-500, 600)
    wait(100)

    move_motors(300, -300, rotations=0.3)
    wait(100)

    motor_a.run_time(1000, 500)
    wait(100)

    motor_a.run_time(-1050, 500)
    wait(100)









'''
def grab_tiles(target_matrix: list, target_row: int, direction: int, grabbed_tiles: list, facing: int = 1) -> list:
    # direction: 0 = both, -1 = left, 1 = right
    if abs(direction) > 0:
        target_matrix[target_row][max(0, direction)] = False
        move_motors(300 * direction * facing, -300 * direction * facing, rotations=0.25 + max(direction, 0) * 0.08)
        move_motors(300 * facing, 300 * facing, rotations=0.74)
        target_matrix[target_row][max(0, direction)] = False
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
    move_motors(-300 * facing, -300 * facing, rotations=0.74)

    if abs(direction) > 0:
        move_motors(-300 * direction, 300 * direction, rotations=0.33)

    return target_matrix
'''