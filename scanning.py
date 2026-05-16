from pixy2 import Pixy2

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
    (107, 111), (141, 110), (173, 110), (206, 112),
    # Row 2
    (104, 134), (140, 132), (176, 132), (212, 131),
    # Row 3
    (94, 158), (136, 159), (181, 154), (220, 152),
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
    from pybricks.tools import wait
    wait(500)
    
    all_results = []
    for _ in range(5):
        mosaic = []
        result = pixy2.get_blocks(255, 12)
        blocks = result[1]
        for i, (gx, gy) in enumerate(GRID_POSITIONS):
            sig = find_sig_at(blocks, gx, gy)
            mosaic.append(sig)
        all_results.append(mosaic)
        wait(100)
    
    final = []
    for i in range(12):
        votes = [r[i] for r in all_results]
        final.append(max(set(votes), key=votes.count))
    
    print("--- Final mosaic ---")
    print(final)
    return final

