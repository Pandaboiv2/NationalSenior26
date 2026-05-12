#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch
import usocket as socket
from taking import move_motors
from line_follower import pid_line_follower
from config import ev3, left_motor, right_motor, motor_a, motor_d, colorsensorLeft, colorsensorRight

def send_cmd(sock, cmd):
    sock.send((cmd + "\n").encode())

def done(sock):
    send_cmd(sock, "done")
    sock.close()

def tool1():
    ev3.speaker.beep()
    sock = socket.socket()

    connected = False
    while not connected:
        try:
            ev3.screen.print("Linking to Slave...")
            sock.connect(socket.getaddrinfo('192.168.0.1', 12345)[0][-1])
            connected = True
        except OSError:
            ev3.screen.print("Retry in 1s...")
            wait(1000) 

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

    pid_line_follower(follow_sensor_port=Port.S1,
                        stop_sensor_port=Port.S4,
                        base_speed=300,
                        Kp=2, Kd=3, Ki=0,
                        target=48,
                        max_angle=None,
                        stop_mode="c",
                        stop_threshold=22,
                        side="l")

    move_motors(500, -500, rotations=1.15)
    wait(150)

    move_motors(600, 600, rotations=1.53)
    wait(150)

    move_motors(400, -400, rotations=0.97)
    wait(150)

    send_cmd(sock, "T,-500, 500")
    wait(500)


    


    '''
    ev3.screen.print("Connected!")
    ev3.speaker.beep()
    wait(500)

    move_motors(500, -500, rotations= 0.15) # moves back from the grid 

    move_motors(-500, -500, rotations= 1.485) # turns 180° 

    send_cmd(sock, "T, 250, 400") # turns down the motor A
    wait(500)

    move_motors(-75, -75, degrees=30)  # twists to put the blocks in the black grid
    wait(250)
    move_motors(75, 75, degrees=50) # twists to put the blocks in the black grid

    move_motors(-200, 200, rotations=0.1)
    wait(100)

    send_cmd(sock, "T,-1000, 500") # turns up the motor A
    wait(150)

    move_motors(-500, 500, rotations=1.47) # moves to go and get the second row
    wait(150)

    move_motors(500, 500, rotations=0.75) # moves to go and get the second row
    wait(150)

    move_motors(-500, 500, rotations=1.9) # moves to go and get the second row
    wait(150)

    while colorsensorLeft.reflection() > 22:   # moves to go and get the second row
        left_motor.run(-300)
        right_motor.run(300)

    left_motor.stop(Stop.BRAKE)
    right_motor.stop(Stop.BRAKE)
    wait(250)

    move_motors(-300, 300, rotations=0.12)   # moves to go and get the second row
    wait(150)

    move_motors(-500, -500, rotations=0.75)   # moves to go and get the second row
    wait(150)

    pid_line_follower(follow_sensor_port=Port.S1,   # moves to go and get the second row
                        stop_sensor_port=Port.S4,
                        base_speed=300,
                        Kp=2, Kd=3, Ki=0,
                        target=48,
                        max_angle=None,
                        stop_mode="c",
                        stop_threshold=20,
                        side="l")

    move_motors(-350, 350, rotations=0.15)  # moves to go and get the second row

    pid_line_follower(follow_sensor_port=Port.S1,   # moves to go and get the second row
                        stop_sensor_port=Port.S4,
                        base_speed=300,
                        Kp=2, Kd=3, Ki=0,
                        target=48,
                        max_angle=None,
                        stop_mode="c",
                        stop_threshold=22,
                        side="l")
    wait(250)

    motor_d.run_time(-100, 100)
    wait(100)


    move_motors(-300, 300, rotations=0.945) # moves to go and get the second row
    wait(250)

    move_motors(-300, -300, rotations=0.744) # moves to go and get the second row
    wait(250)

    move_motors(-300, 300, rotations=0.435) # moves to go and get the second row
    wait(250)

    motor_a.run_angle(600, 260) # moves down the 3d print with the second row
    wait(250)

    motor_d.run(500) # holds the blocks in place
    wait(150)

    motor_a.run_time(-1000, 750) # moves up the 3d print with the second row
    wait(250)

    move_motors(500, -500, rotations=0.6) # goes to take the first tool, bowl
    wait(150)

    move_motors(-500, -500, rotations=0.745)
    wait(150)

    move_motors(-500, 500, rotations=0.9)
    wait(250)


    pid_line_follower(follow_sensor_port=Port.S1,
                        stop_sensor_port=Port.S4,
                        base_speed=607,
                        Kp=2, Kd=2, Ki=0,
                        target=48,
                        max_angle=1167,
                        stop_mode="a",
                        stop_threshold=20,
                        side="r")
    
    pid_line_follower(follow_sensor_port=Port.S1,
                        stop_sensor_port=Port.S4,
                        base_speed=400,
                        Kp=2, Kd=2, Ki=0,
                        target=48,
                        max_angle=500,
                        stop_mode="c",
                        stop_threshold=20,
                        side="r")

    move_motors(-300, 300, rotations=0.2)
    wait(250)

    move_motors(450, 450, rotations=0.745)
    wait(250)

    send_cmd(sock,"T, 506, 450") # turns down the motor A
    wait(500)

    move_motors(-450, -450, rotations=0.745)
    wait(100)

    pid_line_follower(follow_sensor_port=Port.S1,
                        stop_sensor_port=Port.S4,
                        base_speed=650,
                        Kp=2, Kd=3, Ki=0,
                        target=48,
                        max_angle=1200,
                        stop_mode="a",
                        stop_threshold=22,
                        side="r")
    
    wait(100)


    move_motors(250, 250, rotations=0.77)
    wait(100)

    move_motors(-500, 500, rotations=2.35)
    wait(100)

    move_motors(350, -350, rotations=0.2)
    wait(250)

    send_cmd(sock,"T, -250, 480") # turns up the motor A
    wait(1200)

    move_motors(-500, 500, rotations=0.15)
    wait(250)

    while colorsensorLeft.reflection() > 15:
        left_motor.run(-350)
        right_motor.run(350)

    left_motor.stop(Stop.BRAKE)
    right_motor.stop(Stop.BRAKE)
    wait(250)

    move_motors(-350, 350, rotations=0.2)
    wait(250)

    move_motors(400, 400, rotations=0.745)
    wait(100)

    pid_line_follower(follow_sensor_port=Port.S1,
                        stop_sensor_port=Port.S4,
                        base_speed=400,
                        Kp=2, Kd=3, Ki=0,
                        target=48,
                        max_angle=None,
                        stop_mode="c",
                        stop_threshold=22,
                        side="l")
    
    wait(250)

    move_motors(-200, 200, rotations=0.5)

    motor_a.run_angle(1000, 250) # moves the white thing down to deposit on black thing
    wait(100)

    motor_d.stop(Stop.BRAKE)
    wait(50)

    motor_d.run_time(-300, 250) # releases the first row in the grid
    wait(250)

    motor_a.run_angle(-1000, 250) # moves the white thing up a little bit
    wait(250)

    move_motors(500, -500, rotations= 0.2) # moves back from the grid 

    move_motors(-500, -500, rotations= 1.485) # turns 180° 

    send_cmd(sock, "T, 250, 400") # turns down the motor A
    wait(500)

    move_motors(-75, -75, degrees=30)  # twists to put the blocks in the black grid
    wait(250)
    move_motors(75, 75, degrees=40) # twists to put the blocks in the black grid

    send_cmd(sock, "T,-1000, 500") # turns up the motor A
    wait(150)

    move_motors(-75, -75, degrees=10)
    '''

    return sock