#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight

'''
left_motor.run_angle(left_speed, angle, Stop.BRAKE, wait=False)
right_motor.run_angle(right_speed, angle, Stop.BRAKE, wait=True)
'''
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
def mozaic():
    move_motors(250, -250, duration_ms=900) # aligns with the wall
    wait(500)

    move_motors(-250, 250, rotations=1.16) # moves to the first row of yellow blocks
    left_motor.stop(Stop.BRAKE)
    right_motor.stop(Stop.BRAKE)
    wait(500)

    motor_a.run_angle(600, 260) # move down the white thing to take first row of yellow blocks
    wait(500)

    motor_d.run(500) # holds the blocks in place
    wait(100)

    motor_a.run_time(-1000, 900)  # move up the white thing

    move_motors(500,-500, rotations=0.1)

    move_motors(-500,-500, rotations=0.41) # turns to go deposit to the black grid
    wait(100)

    move_motors(-567, 575, rotations=3.35) 
    wait(100)

    while colorsensorLeft.reflection() > 22:
        left_motor.run(-350)
        right_motor.run(350)

    left_motor.stop(Stop.BRAKE)
    right_motor.stop(Stop.BRAKE)
    wait(250)

    move_motors(-300, 300, rotations=0.4)
    wait(100)

    move_motors(-300, -300, rotations=0.3)

    pid_line_follower(follow_sensor_port=Port.S4,
                        stop_sensor_port=Port.S1,
                        base_speed=300,
                        Kp=2, Kd=3, Ki=0,
                        target=48,
                        max_angle=None,
                        stop_mode="c",
                        stop_threshold=20,
                        side="r")

    move_motors(-250, 250, rotations=0.55)

    motor_a.run_angle(1000, 260) # moves the white thing down to deposit on black thing

    motor_d.stop(Stop.HOLD)
    wait(50)

    motor_d.run_time(-300, 250) # releases the first row in the grid
    wait(250)

    motor_a.run_angle(-1000, 250) # moves the white thing up a little bit
    wait(250)