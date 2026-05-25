from pixy2 import Pixy2
from pybricks.tools import wait

pixy2 = Pixy2(port=2, i2c_address=0x54)

COLOR_MAP = {
    1: "yellow",
    2: "blue",
    3: "green",
    4: "white"
}

X_MIN, X_MAX = 90, 250
Y_MIN, Y_MAX = 95, 180

TOLERANCE = 18

# Origin is hardcoded from calibration — consistent across all runs
ORIGIN_X = 98
ORIGIN_Y = 113

ROW_CONFIGS = [
    {"y_offset":  0,  "col_x_offsets": [ 0, 41, 82, 121]},
    {"y_offset": 19,  "col_x_offsets": [ 0, 41, 82, 121]},
    {"y_offset": 42,  "col_x_offsets": [ 0, 43, 85, 124]},
]

ROW_Y_BOUNDARIES = [
    (95,  128),
    (129, 148),
    (149, 180),
]

def get_blocks():
    result = pixy2.get_blocks(255, 12)
    return result[1]

def blocks_in_roi(blocks):
    return [
        b for b in blocks
        if X_MIN < b.x_center < X_MAX and Y_MIN < b.y_center < Y_MAX
    ]

def compute_grid_positions():
    """Grid positions are fixed since origin is hardcoded."""
    positions = []
    for row in ROW_CONFIGS:
        for col_offset in row["col_x_offsets"]:
            x = ORIGIN_X + col_offset
            y = ORIGIN_Y + row["y_offset"]
            positions.append((x, y))
    return positions

# Pre-compute once at import time
GRID_POSITIONS = compute_grid_positions()

def find_sig_at(blocks, target_x, target_y):
    best_sig = 4
    best_dist = TOLERANCE
    for block in blocks_in_roi(blocks):
        dx = abs(block.x_center - target_x)
        dy = abs(block.y_center - target_y)
        if dx < TOLERANCE and dy < TOLERANCE:
            dist = dx + dy
            if dist < best_dist:
                best_dist = dist
                best_sig = block.sig
    return best_sig

def scan_mosaic():
    wait(500)
    all_results = []
    for attempt in range(5):
        blocks = get_blocks()
        mosaic = []
        for (gx, gy) in GRID_POSITIONS:
            sig = find_sig_at(blocks, gx, gy)
            mosaic.append(sig)
        all_results.append(mosaic)
        wait(100)

    final = []
    for i in range(12):
        votes = [r[i] for r in all_results]
        final.append(max(set(votes), key=votes.count))

    print("--- Mosaic result ---")
    for row in range(3):
        row_data = final[row*4 : row*4+4]
        print([COLOR_MAP.get(s, "?") for s in row_data])
    return final

def calibrate():
    wait(500)
    blocks = get_blocks()
    candidates = blocks_in_roi(blocks)
    if not candidates:
        print("No blocks detected in ROI")
        return
    print("--- Raw blocks in ROI ---")
    for b in sorted(candidates, key=lambda b: (b.y_center, b.x_center)):
        print("  sig=" + str(b.sig) + "  x=" + str(b.x_center) + "  y=" + str(b.y_center))
    print("--- Expected grid positions ---")
    for i, (gx, gy) in enumerate(GRID_POSITIONS):
        row = i // 4
        col = i % 4
        print("  row=" + str(row) + " col=" + str(col) + "  expected_x=" + str(gx) + "  expected_y=" + str(gy))