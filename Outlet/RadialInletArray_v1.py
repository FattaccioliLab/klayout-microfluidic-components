import pya
import math

# ============================================================
# USER PARAMETERS (all in microns)
# ============================================================
R           = 2000.0    # radius of the reference circle
N           = 8         # number of trapezoidal inlets
ANGLE_START = 0.0       # start angle in degrees (0 = right, 90 = top)
ANGLE_END   = 180.0     # end angle in degrees
W_INNER     = 200.0     # width of trapezoid at inner (circle-side) end
W_OUTER     = 400.0     # width of trapezoid at outer end
L_TRAP      = 500.0     # radial length of trapezoid
GAP         = 100.0     # radial gap between circle edge and trapezoid inner edge

ARC_POINTS  = 128       # points for the circle

LAYER_INFO  = pya.LayerInfo(1, 0)

X_OFFSET    = 0.0
Y_OFFSET    = 0.0


# ============================================================
# HELPERS
# ============================================================
def make_trapezoid(cx, cy, angle_rad, w_inner, w_outer, length):
    """
    Trapezoidal DPolygon centred at (cx, cy), radially oriented.
    Inner edge (w_inner) faces the circle, outer edge (w_outer) faces away.
    Local frame: +x = radial outward, +y = tangential.
    """
    hi = w_inner / 2.0
    ho = w_outer / 2.0
    hl = length  / 2.0

    local = [
        (-hl, -hi),
        (-hl,  hi),
        ( hl,  ho),
        ( hl, -ho),
    ]

    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    pts = []
    for (lx, ly) in local:
        gx = lx * cos_a - ly * sin_a + cx
        gy = lx * sin_a + ly * cos_a + cy
        pts.append(pya.DPoint(gx, gy))

    return pya.DPolygon(pts)


def make_circle(cx, cy, r, n_pts):
    pts = []
    for i in range(n_pts):
        a = 2.0 * math.pi * i / n_pts
        pts.append(pya.DPoint(cx + r * math.cos(a), cy + r * math.sin(a)))
    return pya.DPolygon(pts)


# ============================================================
# BUILD GEOMETRY
# ============================================================
def build_radial_inlets(r, n, angle_start_deg, angle_end_deg,
                        w_inner, w_outer, l_trap, gap,
                        x0=0.0, y0=0.0, arc_pts=128):

    shapes = []
    shapes.append(make_circle(x0, y0, r, arc_pts))

    a0 = math.radians(angle_start_deg)
    a1 = math.radians(angle_end_deg)
    angles = [a0 + i * (a1 - a0) / (n - 1) for i in range(n)] if n > 1 else [(a0+a1)/2.0]

    r_centre = r + gap + l_trap / 2.0

    for angle in angles:
        cx = x0 + r_centre * math.cos(angle)
        cy = y0 + r_centre * math.sin(angle)
        shapes.append(make_trapezoid(cx, cy, angle, w_inner, w_outer, l_trap))

    return shapes, angles


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
        cell = layout.create_cell("RADIAL_INLETS")
        print("Created new cell:", cell.name)

layer_index = layout.layer(LAYER_INFO)


# ============================================================
# BUILD + INSERT
# ============================================================
shapes, angles = build_radial_inlets(
    r=R, n=N,
    angle_start_deg=ANGLE_START,
    angle_end_deg=ANGLE_END,
    w_inner=W_INNER, w_outer=W_OUTER,
    l_trap=L_TRAP, gap=GAP,
    x0=X_OFFSET, y0=Y_OFFSET,
    arc_pts=ARC_POINTS,
)

for poly in shapes:
    cell.shapes(layer_index).insert(poly.to_itype(layout.dbu))

try:
    lv.add_missing_layers()
except:
    pass

try:
    lv.zoom_fit()
except:
    pass

pitch = math.degrees((angles[-1]-angles[0])/(N-1)) if N > 1 else 0.0
print("Radial inlet array inserted into cell:", cell.name)
print("circle_radius_um:     %.1f" % R)
print("n_inlets:             %d"   % N)
print("angle_span_deg:       %.1f to %.1f" % (ANGLE_START, ANGLE_END))
print("angular_pitch_deg:    %.2f" % pitch)
print("w_inner_um:           %.1f" % W_INNER)
print("w_outer_um:           %.1f" % W_OUTER)
print("trap_length_um:       %.1f" % L_TRAP)
print("gap_um:               %.1f" % GAP)
print("r_trap_centre_um:     %.1f" % (R + GAP + L_TRAP / 2.0))
