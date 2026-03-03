import pya
import math

# ============================================================
# USER PARAMETERS (all in microns)
# ============================================================
TOTAL_LENGTH = 6478.1       # total centerline length INCLUDING both vertical legs
CHANNEL_WIDTH = 50.0       # channel width
PITCH = 150.0               # centerline-to-centerline pitch
EXT_WIDTH = 1000.0          # external horizontal width of serpentine footprint
VERTICAL_LEG = 250.0        # inlet and outlet leg length
ARC_POINTS = 32             # points per 180° turn

LAYER_INFO = pya.LayerInfo(1, 0)

# Placement of the serpentine footprint (top-left outer corner reference)
X_OFFSET = 0.0
Y_OFFSET = 5000.0


# ============================================================
# HELPERS
# ============================================================
def add_point_if_new(pts, p, tol=1e-9):
    if not pts:
        pts.append(p)
        return
    q = pts[-1]
    if abs(q.x - p.x) > tol or abs(q.y - p.y) > tol:
        pts.append(p)

def add_arc_points(pts, cx, cy, r, a0, a1, nseg):
    for i in range(1, nseg + 1):
        t = a0 + (a1 - a0) * (float(i) / float(nseg))
        x = cx + r * math.cos(t)
        y = cy + r * math.sin(t)
        add_point_if_new(pts, pya.DPoint(x, y))

def solve_serpentine_midlegs(total_length, w, pitch, ext_width, leg):
    """
    Solve a serpentine where:
      - the inlet leg connects to the midpoint of the first run
      - the outlet leg connects to the midpoint of the last run

    Let:
      R = pitch / 2
      H = full horizontal tangent-to-tangent span

    Then:
      total_length =
          2*leg
        + (N-2)*H
        + h_first + h_last
        + (N-1)*pi*R

    with:
      H/2 <= h_first <= H
      H/2 <= h_last <= H

    because the midpoint must lie on the first/last run.
    """
    if total_length <= 0:
        raise ValueError("TOTAL_LENGTH must be > 0")
    if w <= 0:
        raise ValueError("CHANNEL_WIDTH must be > 0")
    if pitch <= 0:
        raise ValueError("PITCH must be > 0")
    if ext_width <= 0:
        raise ValueError("EXT_WIDTH must be > 0")
    if leg < 0:
        raise ValueError("VERTICAL_LEG must be >= 0")

    if pitch <= 2.0 * w:
        raise ValueError("PITCH must be strictly greater than 2 x CHANNEL_WIDTH")

    # Bend radius from pitch
    R = pitch / 2.0

    # Full tangent-to-tangent horizontal span
    # ext width = (R + w/2) + H + (R + w/2) = pitch + w + H
    H = ext_width - (pitch + w)
    if H <= 0:
        raise ValueError("EXT_WIDTH too small. Need EXT_WIDTH > PITCH + CHANNEL_WIDTH")

    # Minimum possible: 1 U-bend (N=2), and both first/last runs must at least reach their midpoint
    min_len = 2.0 * leg + math.pi * R + H
    if total_length < min_len:
        raise ValueError(
            "TOTAL_LENGTH too short for midpoint-connected legs.\n"
            "Minimum feasible length is about %.3f µm" % min_len
        )

    for N in range(2, 100000):
        S = total_length - 2.0 * leg - (N - 1) * math.pi * R - (N - 2) * H
        # S = h_first + h_last, with each in [H/2, H]
        if S < H - 0.1:
            break
        if S <= 2.0 * H + 0.1:
            # prefer h_first = H so inlet/outlet legs are centred on the footprint
            h_first = min(H, max(H / 2.0, S / 2.0))
            h_last  = S - h_first

            if h_last < H / 2.0:
                h_last  = H / 2.0
                h_first = S - h_last
            if h_last > H:
                h_last  = H
                h_first = S - h_last

            h_first = max(H / 2.0, min(H, h_first))
            h_last  = max(H / 2.0, min(H, S - h_first))

            if (H / 2.0 - 0.1) <= h_first <= (H + 0.1) and (H / 2.0 - 0.1) <= h_last <= (H + 0.1):
                return N, h_first, h_last, H, R

    raise ValueError("No valid serpentine found for these parameters")

def build_serpentine_points_midlegs(total_length, w, pitch, ext_width, leg, x0=0.0, y0=0.0, arc_points=32):
    N, h_first, h_last, H, R = solve_serpentine_midlegs(total_length, w, pitch, ext_width, leg)

    # Tangency x positions
    x_left = x0 + (R + w / 2.0)
    x_right = x0 + ext_width - (R + w / 2.0)

    # First run goes left -> right, ends at x_right
    x_first_start = x_right - h_first
    x_first_mid = x_first_start + h_first / 2.0

    pts = []

    # Inlet vertical leg to midpoint of first run
    add_point_if_new(pts, pya.DPoint(x_first_mid, y0))
    add_point_if_new(pts, pya.DPoint(x_first_mid, y0 - leg))

    # Complete first run from midpoint to right end
    y = y0 - leg
    add_point_if_new(pts, pya.DPoint(x_right, y))

    x = x_right

    # First U-bend and intermediate full runs
    for i in range(N - 1):
        current_run_is_even = (i % 2 == 0)  # run 0 was left->right and ended at right

        if current_run_is_even:
            # right-side downward semicircle
            add_arc_points(pts, x_right, y - R, R, math.pi / 2.0, -math.pi / 2.0, arc_points)
            y -= pitch
            x = x_right

            # Next run direction: right -> left
            if i == N - 2:
                # Last run: only go to its midpoint connection point
                x_last_start = x_right
                x_last_end = x_right - h_last
                x_last_mid = x_last_start - h_last / 2.0
                add_point_if_new(pts, pya.DPoint(x_last_mid, y))
                add_point_if_new(pts, pya.DPoint(x_last_mid, y - leg))
            else:
                add_point_if_new(pts, pya.DPoint(x_left, y))
                x = x_left

        else:
            # left-side downward semicircle
            add_arc_points(pts, x_left, y - R, R, math.pi / 2.0, 3.0 * math.pi / 2.0, arc_points)
            y -= pitch
            x = x_left

            # Next run direction: left -> right
            if i == N - 2:
                # Last run: only go to its midpoint connection point
                x_last_start = x_left
                x_last_end = x_left + h_last
                x_last_mid = x_last_start + h_last / 2.0
                add_point_if_new(pts, pya.DPoint(x_last_mid, y))
                add_point_if_new(pts, pya.DPoint(x_last_mid, y - leg))
            else:
                add_point_if_new(pts, pya.DPoint(x_right, y))
                x = x_right

    info = {
        "n_horizontal_runs": N,
        "first_run_length": h_first,
        "last_run_length": h_last,
        "full_run_length": H,
        "bend_radius": R,
        "approx_total_height": (N - 1) * pitch + 2.0 * leg + w,
    }
    return pts, info


# ============================================================
# GET CURRENT VIEW / CELL
# ============================================================
lv = pya.LayoutView.current()
if lv is None:
    raise RuntimeError("No LayoutView open. Open a layout first.")

cv_index = lv.active_cellview_index
if cv_index < 0:
    raise RuntimeError("No active cellview. Open a layout tab and click inside it.")

cv = lv.cellview(cv_index)
if cv is None or not cv.is_valid():
    raise RuntimeError("Active cellview is invalid.")

layout = cv.layout()
if layout is None:
    raise RuntimeError("No layout found.")

cell = cv.cell
if cell is None:
    tops = list(layout.top_cells())
    if tops:
        cell = tops[0]
        print("No active cell selected. Using top cell:", cell.name)
    else:
        cell = layout.create_cell("SERPENTINE")
        print("Created new cell:", cell.name)

layer_index = layout.layer(LAYER_INFO)


# ============================================================
# BUILD + INSERT
# ============================================================
pts, info = build_serpentine_points_midlegs(
    total_length=TOTAL_LENGTH,
    w=CHANNEL_WIDTH,
    pitch=PITCH,
    ext_width=EXT_WIDTH,
    leg=VERTICAL_LEG,
    x0=X_OFFSET,
    y0=Y_OFFSET,
    arc_points=ARC_POINTS
)

dpath = pya.DPath(pts, CHANNEL_WIDTH)
dpath.bgn_ext = 0
dpath.end_ext = 0
dpoly = dpath.polygon()
cell.shapes(layer_index).insert(dpoly.to_itype(layout.dbu))

try:
    lv.add_missing_layers()
except:
    pass

try:
    lv.zoom_fit()
except:
    pass

print("Serpentine inserted into cell:", cell.name)
for k, v in info.items():
    print("%s: %s" % (k, v))