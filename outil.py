#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight

# movement function (kind of like tht pink blocks in ev3 classroom)

def move_motors(left_speed, right_speed, duration_ms=None, rotations=None, degrees=None):
    if rotations is not None:
        angle = 360 * rotations
        left_motor.run_angle(left_speed, angle, Stop.BRAKE, wait=False)
        right_motor.run_angle(right_speed, angle, Stop.BRAKE, wait=True)
        left_motor.stop(Stop.BRAKE)
        right_motor.stop(Stop.BRAKE)
        return

    elif degrees is not None:
        left_motor.run_angle(left_speed, degrees, Stop.BRAKE, wait=False)
        right_motor.run_angle(right_speed, degrees, Stop.BRAKE, wait=True)
        left_motor.stop(Stop.BRAKE)
        right_motor.stop(Stop.BRAKE)
        return
    
    elif duration_ms is not None:
        left_motor.run_time(left_speed, duration_ms, Stop.BRAKE, wait=False)
        right_motor.run_time(right_speed, duration_ms, Stop.BRAKE, wait=True)
        left_motor.stop(Stop.BRAKE)
        right_motor.stop(Stop.BRAKE)
        return

# start of the program
def tool():
    right_motor.run_angle(500, 65)
    wait(100)

    move_motors(-500, 500, rotations=0.5)

    left_motor.run_angle(-500, 35)
    wait(100)

    pid_line_follower(follow_sensor_port=Port.S1,
                    stop_sensor_port=Port.S4,
                    base_speed=450,
                    Kp=2, Kd=3, Ki=0,
                    target=48,
                    max_angle=1200,
                    stop_mode="a",
                    stop_threshold=22,
                    side="r",)

    wait(100)



