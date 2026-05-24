from pixy2 import Pixy2
from pybricks.tools import wait

pixy2 = Pixy2(port=2, i2c_address=0x54)

# --- Color map ---
COLOR_MAP = {
    1: "yellow",
    2: "blue",
    3: "green",
    4: "white"
}

# --- Region of interest ---
X_MIN, X_MAX = 80, 25
Y_MIN, Y_MAX = 95, 180

# --- Tolerance for matching a block to a grid position ---
TOLERANCE = 15

# --- Per-row configuration (offsets from top-left origin) ---
# Run calibrate() once to fill these in
ROW_CONFIGS = [
    {"y_offset":  0,  "col_x_offsets": [ 0, 33, 65, 98]},
    {"y_offset":  45, "col_x_offsets": [ 0, 39, 78, 117]},
    {"y_offset":  95, "col_x_offsets": [ 0, 48, 96, 144]},
]

# ----------------------------------------------------------------

def get_blocks():
    result = pixy2.get_blocks(255, 12)
    return result[1]

def blocks_in_roi(blocks):
    return [
        b for b in blocks
        if X_MIN < b.x_center < X_MAX and Y_MIN < b.y_center < Y_MAX
    ]

def cluster_into_rows(candidates):
    """Sort blocks into rows by proximity of y values."""
    if not candidates:
        return []

    candidates.sort(key=lambda b: b.y_center)
    rows = []
    current_row = [candidates[0]]

    for b in candidates[1:]:
        if abs(b.y_center - current_row[0].y_center) < 20:
            current_row.append(b)
        else:
            rows.append(sorted(current_row, key=lambda b: b.x_center))
            current_row = [b]
    rows.append(sorted(current_row, key=lambda b: b.x_center))

    return rows

def estimate_origin(blocks):
    """
    Estimate the true top-left origin of the grid (even if that tile is white)
    by averaging back-calculated origins from all detected blocks.
    """
    candidates = blocks_in_roi(blocks)
    if not candidates:
        return None

    rows = cluster_into_rows(candidates)
    origin_votes = []

    for row_i, row in enumerate(rows):
        if row_i >= len(ROW_CONFIGS):
            break
        for col_i, block in enumerate(row):
            if col_i >= len(ROW_CONFIGS[row_i]["col_x_offsets"]):
                break
            ox = block.x_center - ROW_CONFIGS[row_i]["col_x_offsets"][col_i]
            oy = block.y_center - ROW_CONFIGS[row_i]["y_offset"]
            origin_votes.append((ox, oy))

    if not origin_votes:
        return None

    avg_x = sum(o[0] for o in origin_votes) / len(origin_votes)
    avg_y = sum(o[1] for o in origin_votes) / len(origin_votes)
    return (avg_x, avg_y)

def compute_grid_positions(origin_x, origin_y):
    """Compute all 12 grid positions from the top-left origin."""
    positions = []
    for row in ROW_CONFIGS:
        for col_offset in row["col_x_offsets"]:
            x = origin_x + col_offset
            y = origin_y + row["y_offset"]
            positions.append((x, y))
    return positions

def find_sig_at(blocks, target_x, target_y):
    """Find the signature of the block closest to (target_x, target_y)."""
    best_sig = 4  # default: white
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

# ----------------------------------------------------------------

def scan_mosaic():
    """
    Scan the mosaic 5 times and return the majority-voted result.
    Returns a list of 12 signature values, row by row, left to right.
    White tiles (undetected) default to sig=4.
    """
    wait(500)
    all_results = []

    for attempt in range(5):
        blocks = get_blocks()
        origin = estimate_origin(blocks)

        if origin is None:
            print(f"Scan {attempt+1}: could not estimate origin, skipping")
            wait(100)
            continue

        grid_positions = compute_grid_positions(origin[0], origin[1])

        mosaic = []
        for (gx, gy) in grid_positions:
            sig = find_sig_at(blocks, gx, gy)
            mosaic.append(sig)

        all_results.append(mosaic)
        wait(100)

    if not all_results:
        print("ERROR: no valid scans collected")
        return None

    # Majority vote across all scans
    final = []
    for i in range(12):
        votes = [r[i] for r in all_results]
        final.append(max(set(votes), key=votes.count))

    # Print result as grid
    print("--- Mosaic result ---")
    for row in range(3):
        row_data = final[row*4 : row*4+4]
        print([COLOR_MAP.get(s, "?") for s in row_data])

    return final

# ----------------------------------------------------------------

def calibrate():
    """
    Print all detected block coordinates and their offsets from the
    estimated top-left origin. Use this to fill in ROW_CONFIGS.
    
    How to use:
      1. Place all non-white tiles on the grid
      2. Run calibrate()
      3. Group printed offsets into 3 rows by dy value
      4. Fill ROW_CONFIGS with those dx/dy values
    """
    wait(500)
    blocks = get_blocks()
    candidates = blocks_in_roi(blocks)

    if not candidates:
        print("No blocks detected in ROI")
        return

    rows = cluster_into_rows(candidates)

    print("--- Calibration data (raw) ---")
    for row_i, row in enumerate(rows):
        for col_i, b in enumerate(row):
            print(f"  row={row_i} col={col_i}  sig={b.sig}  x={b.x_center}  y={b.y_center}")

    # Use the top-left detected block as a temporary anchor
    anchor = rows[0][0]
    print(f"\nTemporary anchor: x={anchor.x_center}, y={anchor.y_center}")
    print("Offsets from anchor:")
    for row_i, row in enumerate(rows):
        for col_i, b in enumerate(row):
            dx = b.x_center - anchor.x_center
            dy = b.y_center - anchor.y_center
            print(f"  row={row_i} col={col_i}  sig={b.sig}  dx={dx}  dy={dy}")

# ----------------------------------------------------------------

# Entry point:
# Step 1 — run calibrate() and fill in ROW_CONFIGS above
# Step 2 — comment out calibrate(), uncomment scan_mosaic()

calibrate()
# result = scan_mosaic()