#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.tools import wait
from line_follower import pid_line_follower
from finding_mozaic_pieces import grab_tiles
from pybricks.parameters import Port
from outil import move_motors
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight


ev3 = EV3Brick()

# test matrix with all tiles available
test_matrix = [
    [True, True],
    [True, True],
    [True, True],
]

ev3.speaker.beep()
pid_line_follower(follow_sensor_port=Port.S4,
                stop_sensor_port=Port.S1,
                base_speed=250,
                Kp=3, Kd=4, Ki=0,
                target=48,
                max_angle=None,
                stop_mode="c",
                stop_threshold=22,
                side="l",)
move_motors(-300, 300, rotations=0.24)
wait(100)
grabbed_tiles = [0, 0, 0, 0]
grab_tiles(test_matrix, 0, -1, grabbed_tiles)  # grab row 1, left side