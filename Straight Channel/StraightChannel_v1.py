import pya
import math

# ============================================================
# USER PARAMETERS (all in microns)
# ============================================================
LENGTH       = 5000.0   # channel length (along centreline)
WIDTH        =   50.0   # channel width
ANGLE_DEG    =    0.0   # channel angle (degrees, CCW from +x axis)

LAYER_INFO   = pya.LayerInfo(1, 0)

X_OFFSET     = 0.0      # start point of centreline
Y_OFFSET     = 0.0


# ============================================================
# GEOMETRY
#
# Centreline from (X_OFFSET, Y_OFFSET) in direction ANGLE_DEG.
# The rectangle is defined by the two wall offsets (+W/2, -W/2)
# perpendicular to the centreline direction.
#
#   u = (cos A, sin A)        — along channel
#   n = (-sin A, cos A)       — normal (left wall = +W/2)
#
# 4 corners (CCW):
#   P0 = origin + (W/2)*n
#   P1 = origin + L*u + (W/2)*n
#   P2 = origin + L*u - (W/2)*n
#   P3 = origin - (W/2)*n
# ============================================================

A  = math.radians(ANGLE_DEG)
ux, uy =  math.cos(A),  math.sin(A)   # along channel
nx, ny = -math.sin(A),  math.cos(A)   # normal

hw = WIDTH / 2.0
ox, oy = X_OFFSET, Y_OFFSET

pts = [
    pya.DPoint(ox          + hw*nx,  oy          + hw*ny),
    pya.DPoint(ox + LENGTH*ux + hw*nx,  oy + LENGTH*uy + hw*ny),
    pya.DPoint(ox + LENGTH*ux - hw*nx,  oy + LENGTH*uy - hw*ny),
    pya.DPoint(ox          - hw*nx,  oy          - hw*ny),
]

# ============================================================
# GET CURRENT VIEW / CELL
# ============================================================
lv = pya.LayoutView.current()
if lv is None:
    raise RuntimeError("No LayoutView open.")

cv = lv.cellview(lv.active_cellview_index)
if cv is None or not cv.is_valid():
    raise RuntimeError("No active cellview.")

layout = cv.layout()
cell   = cv.cell
if cell is None:
    tops = list(layout.top_cells())
    cell = tops[0] if tops else layout.create_cell("STRAIGHT_CHANNEL")

layer_index = layout.layer(LAYER_INFO)

# ============================================================
# INSERT
# ============================================================
poly = pya.DPolygon(pts)
cell.shapes(layer_index).insert(poly.to_itype(layout.dbu))

try:
    lv.add_missing_layers()
    lv.zoom_fit()
except:
    pass

print("Straight channel inserted into cell: %s" % cell.name)
print("LENGTH    = %.1f um" % LENGTH)
print("WIDTH     = %.1f um" % WIDTH)
print("ANGLE_DEG = %.2f deg" % ANGLE_DEG)
print("Start:  (%.1f, %.1f)" % (X_OFFSET, Y_OFFSET))
print("End:    (%.1f, %.1f)" % (X_OFFSET + LENGTH*ux, Y_OFFSET + LENGTH*uy))
