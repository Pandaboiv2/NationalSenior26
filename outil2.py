#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
import usocket as socket
from line_follower import pid_line_follower
from taking import move_motors
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight


def send_cmd(sock, cmd):
    sock.send((cmd + "\n").encode())

def done(sock):
    send_cmd(sock, "done")
    sock.close()

def tool2(sock):
    pid_line_follower(follow_sensor_port=Port.S1,
                        stop_sensor_port=Port.S4,
                        base_speed=650,
                        Kp=2, Kd=3, Ki=0,
                        target=48,
                        max_angle=1000,
                        stop_mode="a",
                        stop_threshold=22,
                        side="l")
    
    wait(100)

    pid_line_follower(follow_sensor_port=Port.S1,
                        stop_sensor_port=Port.S4,
                        base_speed=450,
                        Kp=2, Kd=3, Ki=0,
                        target=48,
                        max_angle=None,
                        stop_mode="c",
                        stop_threshold=22,
                        side="l")
    wait(400)

    move_motors(500, -500, rotations=0.3)
    wait(200)

    move_motors(-500, -500, rotations=1.53)
    wait(250)

    move_motors(500, -500, rotations=0.25)
    wait(100)

    send_cmd(sock,"T, 500, 480") # turns down the motor A
    wait(500)

    move_motors(200, 200, rotations=0.2)
    move_motors(-200, -200, rotations=0.2)
    wait(350)

    pid_line_follower(follow_sensor_port=Port.S4,
                        stop_sensor_port=Port.S1,
                        base_speed=750,
                        Kp=2, Kd=3, Ki=0,
                        target=48,
                        max_angle=950,
                        stop_mode="a",
                        stop_threshold=22,
                        side="r")
    
    wait(150)

    pid_line_follower(follow_sensor_port=Port.S4,
                        stop_sensor_port=Port.S1,
                        base_speed=300,
                        Kp=2, Kd=3, Ki=0,
                        target=48,
                        max_angle=None,
                        stop_mode="c",
                        stop_threshold=22,
                        side="r")

    move_motors(500, -500, rotations=1.15)
    wait(250)

    move_motors(600, 600, rotations=1.53)
    wait(250) 

    move_motors(400, -400, rotations=0.97)
    wait(250)

    send_cmd(sock, "T,-500, 500")
    wait(500)

    return sock