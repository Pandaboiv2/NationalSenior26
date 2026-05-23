#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Direction
from pybricks.tools import wait
from config import ev3, colorsensorLeft, colorsensorRight
from line_follower import pid_line_follower
from outil import move_motors
import math

left_motor  = Motor(Port.B)
right_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE)

WHEEL_DIAMETER = 56
AXLE_TRACK     = 120

def calc_motor_deg(turn_angle):
    arc = math.pi * AXLE_TRACK * (turn_angle / 360)
    return (arc / (math.pi * WHEEL_DIAMETER)) * 360

def pivot_turn(turn_angle, speed=50, kp=1.8, kd=0.8):
    motor_target = calc_motor_deg(turn_angle)

    left_motor.reset_angle(0)
    right_motor.reset_angle(0)

    last_error = motor_target

    while True:
        pos = (left_motor.angle() - right_motor.angle()) / 2
        error = motor_target - pos
        derivative = error - last_error

        correction = kp * error + kd * derivative
        correction = max(-speed, min(speed, correction))

        left_motor.dc(correction)
        right_motor.dc(-correction)

        last_error = error

        if abs(error) < 10:
            break

        wait(10)

    left_motor.brake()
    right_motor.brake()
    wait(300)

pivot_turn(132, speed=40)
wait(100)
pivot_turn(-132, speed=40)
ev3.speaker.beep()
wait(5000)











'''
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
move_motors(-300, 300, rotations=0.25)
grab_tiles(test_matrix, 0, 1)  # grab row 1, left side
'''