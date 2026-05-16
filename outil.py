#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight
from scanning import scan_mosaic

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
    #--------------------------------#
    # will go scan and take the bowl #
    right_motor.run_angle(500, 90)
    wait(100)

    move_motors(-500, 500, rotations=0.6)

    left_motor.run_angle(-500, 90)
    wait(100)

    pid_line_follower(follow_sensor_port=Port.S1,
                    stop_sensor_port=Port.S4,
                    base_speed=750,
                    Kp=2, Kd=3, Ki=0,
                    target=48,
                    max_angle=1350,
                    stop_mode="a",
                    stop_threshold=22,
                    side="r",)

    wait(100)


    pid_line_follower(follow_sensor_port=Port.S1,
                    stop_sensor_port=Port.S4,
                    base_speed=300,
                    Kp=2, Kd=3, Ki=0,
                    target=48,
                    max_angle=None,
                    stop_mode="c",
                    stop_threshold=22,
                    side="r",)
    
    wait(250)

    move_motors(-500, 500, rotations=0.2)
    wait(100)

    move_motors(-500, -500, rotations=0.72)
    wait(100)

    move_motors(500, -500, rotations=0.67)

    wait(100)

    mosaic_pattern = scan_mosaic()
    print(mosaic_pattern)

    move_motors(-750, -750, rotations=1.52)
    wait(100)

    move_motors(500, -500, rotations=0.82)
    wait(100)

    motor_a.run_time(-750, 750, wait=False)
    motor_d.run_time(750, 400)
    wait(100)
    # will go scan and take the bowl #
    #--------------------------------#

    #----------------#
    # put the trowel #
    move_motors(-500, -500, rotations=0.68)
    wait(100)

    move_motors(500, -500, rotations=2)
    wait(100)
    #----------------#
    # put the trowel #


    #------------------------#
    # will go place the bowl #
    right_motor.run_angle(500, 180)
    wait(100)

    move_motors(-500, 500, rotations=0.4)
    wait(100)

    left_motor.run_angle(-500, 210)
    wait(100)


    pid_line_follower(follow_sensor_port=Port.S1,
                    stop_sensor_port=Port.S4,
                    base_speed=750,
                    Kp=2, Kd=3, Ki=0,
                    target=48,
                    max_angle=1300,
                    stop_mode="a",
                    stop_threshold=22,
                    side="r",)

    wait(100)
    
    pid_line_follower(follow_sensor_port=Port.S1,
                    stop_sensor_port=Port.S4,
                    base_speed=500,
                    Kp=2, Kd=3, Ki=0,
                    target=48,
                    max_angle=None,
                    stop_mode="c",
                    stop_threshold=22,
                    side="r",)
    
    wait(250)

    move_motors(500, -500, rotations=0.3)

    move_motors(-500, -500, rotations=0.72)
    wait(100)

    motor_a.run_time(1000, 750)
    wait(100)

    move_motors(500, 500, rotations=0.72)
    wait(100)
    # will go place the bowl #
    #------------------------#

    #------------------------------#
    # will go take the blue blocks #
    right_motor.run_angle(500, 300)
    wait(100)

    while colorsensorRight.reflection() > 22:
        left_motor.run(-500)
        right_motor.run(500)

    left_motor.hold()
    right_motor.hold()

    move_motors(-200, 200, rotations=0.15)
    wait(100)

    move_motors(-300, -300, rotations=0.4)
    wait(100)
    
    pid_line_follower(follow_sensor_port=Port.S1,
                    stop_sensor_port=Port.S4,
                    base_speed=350,
                    Kp=2, Kd=3, Ki=0,
                    target=48,
                    max_angle=None,
                    stop_mode="c",
                    stop_threshold=22,
                    side="l",)
    wait(250)

    # will go take the blue blocks #
    #------------------------------#