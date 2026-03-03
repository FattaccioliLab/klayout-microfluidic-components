import pya

# ============================================================
# USER PARAMETERS (all in microns)
# ============================================================
MARGIN       = 2000.0   # distance from chip bounding box to the mark corner
MARK_LENGTH  =  500.0   # length of each arm of the L
MARK_WIDTH   =   50.0   # line width of the mark
LAYER_INFO   = pya.LayerInfo(10, 0)


# ============================================================
# GEOMETRY
#
# Each corner is an L-shaped polygon (12 points).
# Convention: corner at (cx, cy), arms extend inward by MARK_LENGTH.
#
#   For the bottom-left corner (arms go right and up):
#
#   (cx, cy+ML) o--o
#               |  |
#               |  o-----------o (cx+ML, cy+MW)
#               |              |
#   (cx, cy)    o--------------o (cx+ML, cy)
#
#   where ML = MARK_LENGTH, MW = MARK_WIDTH
#
# The other three corners are rotations/reflections of this.
# ============================================================

def l_corner(cx, cy, dx, dy, mw):
    """
    L-shaped polygon for one corner.
    cx, cy  : outer corner position
    dx, dy  : signs indicating arm directions (+1 or -1)
               dx=+1 -> horizontal arm goes right
               dy=+1 -> vertical arm goes up
    mw      : mark width
    Returns list of 8 DPoints (CCW).
    """
    ML = MARK_LENGTH
    MW = mw

    # All coordinates relative to corner (cx, cy)
    # Horizontal arm: from corner, extends dx * ML in x, MW thick in y
    # Vertical arm:   from corner, extends dy * ML in y, MW thick in x
    # The two arms share the corner square (MW x MW)

    pts = [
        pya.DPoint(cx,            cy),
        pya.DPoint(cx + dx*ML,    cy),
        pya.DPoint(cx + dx*ML,    cy + dy*MW),
        pya.DPoint(cx + dx*MW,    cy + dy*MW),
        pya.DPoint(cx + dx*MW,    cy + dy*ML),
        pya.DPoint(cx,            cy + dy*ML),
    ]
    return pts


# ============================================================
# GET CURRENT VIEW / CELL
# ============================================================
lv = pya.LayoutView.current()
if lv is None:
    raise RuntimeError("No LayoutView open.")

cv = lv.cellview(lv.active_cellview_index)
layout = cv.layout()
cell   = cv.cell

layer_index = layout.layer(LAYER_INFO)


# ============================================================
# GET BOUNDING BOX OF SELECTED OBJECTS
# ============================================================
bbox = pya.DBox()
n_selected = 0
for obj in lv.each_object_selected():
    bbox += obj.shape.dbbox()
    n_selected += 1

if n_selected == 0:
    # Fall back to full cell bbox
    bbox = cell.dbbox()
    print("No selection found — using full cell bounding box.")
else:
    print("Selected %d object(s)." % n_selected)

if bbox.empty():
    raise RuntimeError("Bounding box is empty.")

print("Chip bbox: (%.1f, %.1f) -> (%.1f, %.1f)" % (
    bbox.left, bbox.bottom, bbox.right, bbox.top))

# Expand by margin
x0 = bbox.left   - MARGIN
y0 = bbox.bottom - MARGIN
x1 = bbox.right  + MARGIN
y1 = bbox.top    + MARGIN

print("Mark bbox: (%.1f, %.1f) -> (%.1f, %.1f)" % (x0, y0, x1, y1))


# ============================================================
# BUILD + INSERT FOUR CORNER MARKS
# ============================================================
corners = [
    (x0, y0, +1, +1),   # bottom-left:  arms go right and up
    (x1, y0, -1, +1),   # bottom-right: arms go left  and up
    (x1, y1, -1, -1),   # top-right:    arms go left  and down
    (x0, y1, +1, -1),   # top-left:     arms go right and down
]

for cx, cy, dx, dy in corners:
    pts  = l_corner(cx, cy, dx, dy, MARK_WIDTH)
    poly = pya.DPolygon(pts)
    cell.shapes(layer_index).insert(poly.to_itype(layout.dbu))

try:
    lv.add_missing_layers()
    lv.zoom_fit()
except:
    pass

print("Cutting marks inserted on layer %s." % LAYER_INFO)
print("MARGIN=%.1f  MARK_LENGTH=%.1f  MARK_WIDTH=%.1f" % (
    MARGIN, MARK_LENGTH, MARK_WIDTH))
