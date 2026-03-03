import pya

# ============================================================
# USER PARAMETERS (all in microns)
# ============================================================
W_MAIN   = 100.0    # width of the main channel (left and right arms)
W_TOP    =  50.0    # width of the lateral inlet arm

L_LEFT   = 400.0    # length of left arm
L_RIGHT  = 500.0    # length of right arm
L_TOP    = 400.0    # length of top arm

LAYER_INFO = pya.LayerInfo(1, 0)

X_OFFSET = 0.0
Y_OFFSET = 0.0


# ============================================================
# GEOMETRY
#
# Union of 3 rectangles merged via EdgeProcessor:
#   top:   x in [-W_TOP/2,  +W_TOP/2],  y in [0, L_TOP]
#   left:  x in [-L_LEFT,   0],          y in [-W_MAIN/2, +W_MAIN/2]
#   right: x in [0,          L_RIGHT],   y in [-W_MAIN/2, +W_MAIN/2]
#
# Since left and right share W_MAIN, the merged contour is simply
# 8 points (a rectangle with a notch cut for the top arm):
#
#     +--+         +--+
#     |  |  top    |  |  <- this simplifies to just:
#  ---+  +---------+  +---
#  left      main       right
#  ---+------------------+---
#
# i.e. an upside-down T shape.
# ============================================================

def make_rect(x1, y1, x2, y2):
    return pya.DPolygon([
        pya.DPoint(x1, y1), pya.DPoint(x2, y1),
        pya.DPoint(x2, y2), pya.DPoint(x1, y2),
    ])


def build_t_junction(w_main, w_top, l_left, l_right, l_top,
                     x0=0.0, y0=0.0, dbu=0.001):

    hm = w_main / 2.0
    ht = w_top  / 2.0

    rects = [
        make_rect(x0 - ht,     y0,       x0 + ht,      y0 + l_top),
        make_rect(x0 - l_left, y0 - hm,  x0,           y0 + hm),
        make_rect(x0,          y0 - hm,  x0 + l_right, y0 + hm),
    ]

    ipolys = [r.to_itype(dbu) for r in rects]
    ep = pya.EdgeProcessor()
    merged = ep.boolean_p2p(
        ipolys, [],
        pya.EdgeProcessor.ModeOr,
        True, True
    )
    return [p.to_dtype(dbu) for p in merged]


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
        cell = layout.create_cell("T_JUNCTION")
        print("Created new cell:", cell.name)

layer_index = layout.layer(LAYER_INFO)


# ============================================================
# BUILD + INSERT
# ============================================================
polys = build_t_junction(
    w_main=W_MAIN, w_top=W_TOP,
    l_left=L_LEFT, l_right=L_RIGHT, l_top=L_TOP,
    x0=X_OFFSET, y0=Y_OFFSET,
    dbu=layout.dbu,
)

for poly in polys:
    cell.shapes(layer_index).insert(poly.to_itype(layout.dbu))

try:
    lv.add_missing_layers()
except:
    pass

try:
    lv.zoom_fit()
except:
    pass

print("T-junction inserted into cell:", cell.name)
print("n_polygons after merge: %d" % len(polys))
print("w_main_um:  %.1f" % W_MAIN)
print("w_top_um:   %.1f" % W_TOP)
print("l_left_um:  %.1f" % L_LEFT)
print("l_right_um: %.1f" % L_RIGHT)
print("l_top_um:   %.1f" % L_TOP)
