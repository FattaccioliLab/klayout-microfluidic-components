import pya
import math

# ============================================================
# USER PARAMETERS (all in microns)
# ============================================================
THETA_DEG  = 30.0    # half-angle between each inlet arm and horizontal (degrees)

W_UPPER    =  80.0   # width of upper inlet arm
W_LOWER    =  80.0   # width of lower inlet arm
W_OUTLET   = 150.0   # width of outlet arm

L_UPPER    = 400.0   # horizontal length of upper inlet (leftward from junction)
L_LOWER    = 400.0   # horizontal length of lower inlet
L_OUTLET   = 500.0   # length of outlet arm (rightward from junction)

LAYER_INFO = pya.LayerInfo(1, 0)

X_OFFSET   = 0.0
Y_OFFSET   = 0.0


# ============================================================
# GEOMETRY
#
# Junction centre at origin. Main flow along +x.
# Upper inlet at angle (pi - THETA), lower inlet at -(pi - THETA).
#
# Walls are defined by y-offset at junction (+W/2 top, -W/2 bottom)
# and run parallel to the arm direction.
# Caps are VERTICAL at x = -L (inlets) or x = +L_OUTLET (outlet).
#
# 9-point CCW contour:
#   ot_cap_top -> P_top -> up_cap_top -> up_cap_bot
#   -> P_mid -> lo_cap_bot -> lo_cap_top -> P_bot -> ot_cap_bot
#
# P_mid (chevron tip) sits between the caps and the junction,
# forming the notch between the two inlet channels.
# ============================================================

def wall_at_x(start, direction, x_target):
    t = (x_target - start[0]) / direction[0]
    return (x_target, start[1] + t * direction[1])

def line_intersect(p1, d1, p2, d2):
    cross = d1[0]*d2[1] - d1[1]*d2[0]
    if abs(cross) < 1e-12:
        raise ValueError("Parallel walls — check angle/width parameters.")
    dx = p2[0]-p1[0]; dy = p2[1]-p1[1]
    t  = (dx*d2[1] - dy*d2[0]) / cross
    return (p1[0]+t*d1[0], p1[1]+t*d1[1])


def build_y_junction(theta_deg, w_upper, w_lower, w_outlet,
                     l_upper, l_lower, l_outlet,
                     x0=0.0, y0=0.0):

    T    = math.radians(theta_deg)
    A_up =  math.pi - T
    A_lo = -(math.pi - T)

    u_up = (math.cos(A_up), math.sin(A_up))
    u_lo = (math.cos(A_lo), math.sin(A_lo))
    u_ot = (1.0, 0.0)

    hw_up = w_upper  / 2.0
    hw_lo = w_lower  / 2.0
    hw_ot = w_outlet / 2.0

    # Wall origins at junction (top = +hw, bot = -hw in y)
    up_top_s = (0.0,  hw_up);  up_bot_s = (0.0, -hw_up)
    lo_top_s = (0.0,  hw_lo);  lo_bot_s = (0.0, -hw_lo)
    ot_top_s = (0.0,  hw_ot);  ot_bot_s = (0.0, -hw_ot)

    # Vertical cap points
    up_cap_top = wall_at_x(up_top_s, u_up, -l_upper)
    up_cap_bot = wall_at_x(up_bot_s, u_up, -l_upper)
    lo_cap_top = wall_at_x(lo_top_s, u_lo, -l_lower)
    lo_cap_bot = wall_at_x(lo_bot_s, u_lo, -l_lower)
    ot_cap_top = ( l_outlet,  hw_ot)
    ot_cap_bot = ( l_outlet, -hw_ot)

    # Junction corners
    P_top = line_intersect(ot_top_s, u_ot, up_top_s, u_up)   # outlet top / upper inlet top
    P_mid = line_intersect(up_bot_s, u_up, lo_top_s, u_lo)   # upper inlet bot / lower inlet top
    P_bot = line_intersect(lo_bot_s, u_lo, ot_bot_s, u_ot)   # lower inlet bot / outlet bot

    pts_um = [
        ot_cap_top,
        P_top,
        up_cap_top,
        up_cap_bot,
        P_mid,
        lo_cap_top,
        lo_cap_bot,
        P_bot,
        ot_cap_bot,
    ]

    return [pya.DPoint(x0 + p[0], y0 + p[1]) for p in pts_um]


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
        cell = layout.create_cell("Y_JUNCTION")
        print("Created new cell:", cell.name)

layer_index = layout.layer(LAYER_INFO)


# ============================================================
# BUILD + INSERT
# ============================================================
pts = build_y_junction(
    theta_deg=THETA_DEG,
    w_upper=W_UPPER, w_lower=W_LOWER, w_outlet=W_OUTLET,
    l_upper=L_UPPER, l_lower=L_LOWER, l_outlet=L_OUTLET,
    x0=X_OFFSET, y0=Y_OFFSET,
)

poly = pya.DPolygon(pts)
cell.shapes(layer_index).insert(poly.to_itype(layout.dbu))

try:
    lv.add_missing_layers()
except:
    pass

try:
    lv.zoom_fit()
except:
    pass

print("Y-junction inserted into cell:", cell.name)
print("theta_deg:     %.1f" % THETA_DEG)
print("w_upper_um:    %.1f" % W_UPPER)
print("w_lower_um:    %.1f" % W_LOWER)
print("w_outlet_um:   %.1f" % W_OUTLET)
print("l_upper_um:    %.1f" % L_UPPER)
print("l_lower_um:    %.1f" % L_LOWER)
print("l_outlet_um:   %.1f" % L_OUTLET)
