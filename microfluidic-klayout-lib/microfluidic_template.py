import pya
import math
import os

# ---------------------------------------------------------------------------
# Chemin vers le fichier .lyp (dans le même dossier que ce script)
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
LYP_PATH = os.path.join(_HERE, "microfluidic.lyp")

# ---------------------------------------------------------------------------
# Paramètres du template
# ---------------------------------------------------------------------------
WAFER_DIAM_UM  = 100_000   # 4 pouces = 100 mm
MASK_DIAM_UM   = 114_000   # masque 4.5" standard (bord de sécurité)
DBU            = 0.001     # 1 nm

LAYERS = {
    "PDMS_channel":    pya.LayerInfo(1,  0),
    "alignment_marks": pya.LayerInfo(10, 0),
    "masque":          pya.LayerInfo(20, 0),
    "wafer_outline":   pya.LayerInfo(99, 0),
}


def polygon_circle(cx, cy, radius_um, dbu, n=360):
    """Retourne un pya.Polygon approximant un cercle."""
    scale = 1.0 / dbu
    pts = [
        pya.Point(
            int(round((cx + radius_um * math.cos(2 * math.pi * i / n)) * scale)),
            int(round((cy + radius_um * math.sin(2 * math.pi * i / n)) * scale))
        )
        for i in range(n)
    ]
    return pya.Polygon(pts)


def create_cross(cell, layer_idx, cx_um, cy_um, arm_um, thickness_um, dbu):
    """Insère une croix (alignment mark) dans une cellule."""
    scale = 1.0 / dbu
    s = int(round(arm_um       * scale))
    t = int(round(thickness_um * scale))
    ox = int(round(cx_um * scale))
    oy = int(round(cy_um * scale))
    cell.shapes(layer_idx).insert(pya.Box(ox - s, oy - t, ox + s, oy + t))
    cell.shapes(layer_idx).insert(pya.Box(ox - t, oy - s, ox + t, oy + s))


def create_template():
    app = pya.Application.instance()
    mw  = app.main_window()

    # Nouveau layout dans un nouvel onglet
    cv     = mw.create_layout(True)
    layout = cv.layout()
    layout.dbu = DBU

    # Layers
    layer_idx = {name: layout.layer(info) for name, info in LAYERS.items()}

    # Cellule TOP
    top = layout.create_cell("TOP")
    layout.top_cell().change_name("TOP") if layout.top_cell() else None
    cv.cell_name = "TOP"

    # --- Wafer outline ---
    wafer_cell = layout.create_cell("WAFER_OUTLINE")
    wafer_cell.shapes(layer_idx["wafer_outline"]).insert(
        polygon_circle(0, 0, WAFER_DIAM_UM / 2, DBU))
    # Flat (détrompeur) : segment en bas à ~32.5 mm du centre (4")
    flat_y  = -32_500  # µm
    flat_hw = 16_000   # demi-largeur du flat
    scale   = 1.0 / DBU
    flat_pts = [
        pya.Point(int(flat_hw * scale),  int(flat_y * scale)),
        pya.Point(-int(flat_hw * scale), int(flat_y * scale)),
    ]
    # On ne trace pas le flat comme une découpe ici, juste une ligne repère
    wafer_cell.shapes(layer_idx["wafer_outline"]).insert(
        pya.Path(flat_pts, int(200 * scale), 0, 0))  # trait 200 µm d'épaisseur
    top.insert(pya.CellInstArray(wafer_cell.cell_index(), pya.Trans()))

    # --- Masque outline ---
    mask_cell = layout.create_cell("MASK_OUTLINE")
    mask_cell.shapes(layer_idx["masque"]).insert(
        polygon_circle(0, 0, MASK_DIAM_UM / 2, DBU))
    top.insert(pya.CellInstArray(mask_cell.cell_index(), pya.Trans()))

    # --- Alignment marks (4 coins, à 35% du rayon) ---
    mark_cell = layout.create_cell("ALIGNMENT_MARK")
    # La marque est définie à l'origine, on instancie en 4 positions
    cross_arm = 500    # µm
    cross_t   = 50     # µm
    create_cross(mark_cell, layer_idx["alignment_marks"], 0, 0, cross_arm, cross_t, DBU)
    # Carré de référence autour de la croix
    sq = int(round(700 * scale))
    mark_cell.shapes(layer_idx["alignment_marks"]).insert(
        pya.Box(-sq, -sq, sq, sq).transformed(
            pya.Trans()).to_dtype(DBU).to_itype(DBU))  # outline seul via Path
    # (optionnel : on insère juste la croix pour rester simple)

    offset_um = WAFER_DIAM_UM * 0.35
    for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        top.insert(pya.CellInstArray(
            mark_cell.cell_index(),
            pya.Trans(pya.Trans.R0,
                      pya.Point(int(round(dx * offset_um * scale)),
                                int(round(dy * offset_um * scale))))
        ))

    # --- Layer properties ---
    if os.path.isfile(LYP_PATH):
        mw.current_view().load_layer_props(LYP_PATH)
        print(f"Layer properties chargées depuis {LYP_PATH}")
    else:
        print(f"[WARN] Fichier .lyp introuvable : {LYP_PATH}")

    mw.current_view().zoom_fit()
    print("Template 4\" créé. Layers disponibles :")
    for name, info in LAYERS.items():
        print(f"  {info.layer}/{info.datatype}  →  {name}")
    print("Ajoutez vos PCells depuis Edit > Libraries > MicrofluidicLib.")


create_template()
