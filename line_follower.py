#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait

ev3 = EV3Brick()
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)

def pid_line_follower(follow_sensor_port=Port.S1,
                      stop_sensor_port=Port.S4,
                      base_speed=400,
                      Kp=2, Kd=3, Ki=0,
                      target=30,
                      max_angle=None,
                      stop_mode="c",
                      stop_threshold=20,
                      side="r"):

    follow_sensor = ColorSensor(follow_sensor_port)
    stop_sensor = ColorSensor(stop_sensor_port)

    integral = 0
    last_error = 0

    left_motor.reset_angle(0)
    right_motor.reset_angle(0)

    while True:
        reflection = follow_sensor.reflection()
        stop_reflection = stop_sensor.reflection()

        # ===== STOP CONDITION =====
        if stop_mode == "c":
            if stop_reflection < stop_threshold:
                break

        elif stop_mode == "a":
            if max_angle is not None:
                if abs(left_motor.angle()) >= max_angle or abs(right_motor.angle()) >= max_angle:
                    break

        # ===== ERROR =====
        if side == "l":
            error = target - reflection 
        else:
            error = reflection - target

        integral += error
        derivative = error - last_error

        turn = Kp * error + Ki * integral + Kd * derivative

        right_speed = base_speed + turn
        left_speed = base_speed - turn

        # Your motor direction convention
        left_motor.run(-left_speed)
        right_motor.run(right_speed)

        last_error = error
        wait(10)

    left_motor.run(0)
    right_motor.run(0)
    wait(50)
    left_motor.hold()
    right_motor.hold()
    #ev3.speaker.beep()
