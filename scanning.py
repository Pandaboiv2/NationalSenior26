#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.tools import wait
from pixy2 import Pixy2

ev3 = EV3Brick()
pixy2 = Pixy2(port=2, i2c_address=0x54)

COLOR_MAP = {
    1: "yellow",
    2: "blue",
    3: "green",
    4: "white"
}

X_MIN, X_MAX = 100, 280
Y_MIN, Y_MAX = 100, 200

GRID_POSITIONS = [
    # Row 1
    (110, 115), (144, 115), (175, 115), (210, 116),
    # Row 2
    (105, 135), (142, 135), (182, 134), (220, 135),
    # Row 3
    (95, 160), (140, 160), (183, 160), (225, 160),
]

TOLERANCE = 10

def find_sig_at(blocks, target_x, target_y):
    best_sig = 4  # default white
    best_dist = TOLERANCE
    for block in blocks:
        if block.x_center < X_MIN or block.x_center > X_MAX:
            continue
        if block.y_center < Y_MIN or block.y_center > Y_MAX:
            continue
        dx = abs(block.x_center - target_x)
        dy = abs(block.y_center - target_y)
        dist = dx + dy
        if dx < TOLERANCE and dy < TOLERANCE and dist < best_dist:
            best_dist = dist
            best_sig = block.sig
    return best_sig

def scan_mosaic():
    mosaic = []
    result = pixy2.get_blocks(255, 12)
    count = result[0]
    blocks = result[1]
    print("Detected", count, "blocks")
    for i, (gx, gy) in enumerate(GRID_POSITIONS):
        sig = find_sig_at(blocks, gx, gy)
        color = COLOR_MAP[sig]
        mosaic.append(color)
        row = (i // 4) + 1
        col = (i % 4) + 1
        print("Row", row, "Col", col, "| Sig:", sig, "| Color:", color)
    return mosaic

ev3.speaker.beep()
mosaic_pattern = scan_mosaic()
print("--- Final mosaic ---")
print(mosaic_pattern)
