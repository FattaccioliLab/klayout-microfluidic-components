import pya
import math


# ---------------------------------------------------------------------------
# PCell : canal serpentin
# ---------------------------------------------------------------------------

class SerpentineChannel(pya.PCellDeclarationHelper):
    """Canal serpentin paramétrique."""

    def __init__(self):
        super().__init__()
        self.param("total_length",  self.TypeDouble, "Total length (µm)",       default=10000.0)
        self.param("radius",        self.TypeDouble, "Turn radius (µm)",         default=100.0)
        self.param("width",         self.TypeDouble, "Channel width (µm)",       default=20.0)
        self.param("max_ext_width", self.TypeDouble, "Max external width (µm)",  default=1000.0)
        self.param("n_arc_pts",     self.TypeInt,    "Arc points / half-turn",   default=32)
        self.param("layer",         self.TypeLayer,  "Layer",                    default=pya.LayerInfo(1, 0))

    def display_text_impl(self):
        return f"Serpentine(L={self.total_length:.0f}, R={self.radius:.0f}, W={self.width:.0f})"

    def coerce_parameters_impl(self):
        min_w = 2 * (self.radius + self.width / 2)
        if self.max_ext_width < min_w:
            self.max_ext_width = min_w + self.width

    def can_create_from_shape_impl(self):
        return False

    def produce_impl(self):
        dbu   = self.layout.dbu
        L, R, W, W_ext = self.total_length, self.radius, self.width, self.max_ext_width
        N     = self.n_arc_pts
        layer = self.layer_layer

        straight  = W_ext - 2 * (R + W / 2)
        if straight <= 0:
            raise ValueError("max_ext_width trop petit.")

        half_turn = math.pi * R
        unit      = straight + half_turn
        n_units   = int(L / unit)
        remainder = L - n_units * unit

        pts = [pya.DPoint(0.0, 0.0)]
        x, y, direction = 0.0, 0.0, 1

        for i in range(n_units):
            x += direction * straight
            pts.append(pya.DPoint(x, y))

            sign_y = 1 if (i % 2 == 0) else -1
            cx_c, cy_c = x, y + sign_y * R
            a0 = math.atan2(y - cy_c, x - cx_c)
            for j in range(1, N + 1):
                frac = j / N
                a = a0 - sign_y * math.pi * frac if direction == 1 else a0 + sign_y * math.pi * frac
                pts.append(pya.DPoint(cx_c + R * math.cos(a), cy_c + R * math.sin(a)))

            x, y = pts[-1].x, pts[-1].y
            direction *= -1

        if remainder > 0:
            if remainder <= straight:
                x += direction * remainder
                pts.append(pya.DPoint(x, y))
            else:
                x += direction * straight
                pts.append(pya.DPoint(x, y))
                arc_frac = (remainder - straight) / half_turn
                sign_y = 1 if (n_units % 2 == 0) else -1
                cx_c, cy_c = x, y + sign_y * R
                a0 = math.atan2(y - cy_c, x - cx_c)
                n_arc = max(1, int(N * arc_frac))
                for j in range(1, n_arc + 1):
                    frac = j / N
                    a = a0 - sign_y * math.pi * frac if direction == 1 else a0 + sign_y * math.pi * frac
                    pts.append(pya.DPoint(cx_c + R * math.cos(a), cy_c + R * math.sin(a)))

        scale = 1.0 / dbu
        ipts  = [pya.Point(int(round(p.x * scale)), int(round(p.y * scale))) for p in pts]
        hw    = int(round(W / 2 * scale))
        self.cell.shapes(layer).insert(pya.Path(ipts, int(round(W * scale)), hw, hw))


# ---------------------------------------------------------------------------
# PCell : canal droit
# ---------------------------------------------------------------------------

class StraightChannel(pya.PCellDeclarationHelper):
    """Canal droit avec extrémités arrondies optionnelles."""

    def __init__(self):
        super().__init__()
        self.param("length",   self.TypeDouble, "Length (µm)",         default=1000.0)
        self.param("width",    self.TypeDouble, "Channel width (µm)",  default=20.0)
        self.param("rounded",  self.TypeBoolean,"Rounded ends",        default=True)
        self.param("layer",    self.TypeLayer,  "Layer",               default=pya.LayerInfo(1, 0))

    def display_text_impl(self):
        return f"StraightChannel(L={self.length:.0f}, W={self.width:.0f})"

    def can_create_from_shape_impl(self):
        return False

    def produce_impl(self):
        dbu   = self.layout.dbu
        scale = 1.0 / dbu
        L, W  = self.length, self.width
        layer = self.layer_layer

        p1 = pya.Point(0, 0)
        p2 = pya.Point(int(round(L * scale)), 0)
        hw = int(round(W / 2 * scale))
        ext = hw if self.rounded else 0
        self.cell.shapes(layer).insert(pya.Path([p1, p2], int(round(W * scale)), ext, ext))


# ---------------------------------------------------------------------------
# PCell : jonction en T
# ---------------------------------------------------------------------------

class TJunction(pya.PCellDeclarationHelper):
    """Jonction en T symétrique."""

    def __init__(self):
        super().__init__()
        self.param("main_width",   self.TypeDouble, "Main channel width (µm)",  default=100.0)
        self.param("side_width",   self.TypeDouble, "Side channel width (µm)",  default=40.0)
        self.param("main_length",  self.TypeDouble, "Main channel length (µm)", default=500.0)
        self.param("side_length",  self.TypeDouble, "Side channel length (µm)", default=300.0)
        self.param("layer",        self.TypeLayer,  "Layer",                    default=pya.LayerInfo(1, 0))

    def display_text_impl(self):
        return f"TJunction(Wm={self.main_width:.0f}, Ws={self.side_width:.0f})"

    def can_create_from_shape_impl(self):
        return False

    def produce_impl(self):
        dbu   = self.layout.dbu
        scale = 1.0 / dbu
        Wm, Ws = self.main_width, self.side_width
        Lm, Ls = self.main_length, self.side_length
        layer  = self.layer_layer

        # Canal principal (horizontal, centré en 0)
        hw_m = int(round(Wm / 2 * scale))
        p1 = pya.Point(int(round(-Lm / 2 * scale)), 0)
        p2 = pya.Point(int(round( Lm / 2 * scale)), 0)
        self.cell.shapes(layer).insert(pya.Path([p1, p2], int(round(Wm * scale)), hw_m, hw_m))

        # Canal latéral (vertical, part du centre vers le haut)
        hw_s = int(round(Ws / 2 * scale))
        p3 = pya.Point(0, 0)
        p4 = pya.Point(0, int(round(Ls * scale)))
        self.cell.shapes(layer).insert(pya.Path([p3, p4], int(round(Ws * scale)), 0, hw_s))


# ---------------------------------------------------------------------------
# Enregistrement de la bibliothèque
# ---------------------------------------------------------------------------

class MicrofluidicLibrary(pya.Library):
    def __init__(self):
        self.description = "Microfluidic components (IPGG)"
        self.layout().register_pcell("SerpentineChannel", SerpentineChannel())
        self.layout().register_pcell("StraightChannel",   StraightChannel())
        self.layout().register_pcell("TJunction",         TJunction())
        self.register("MicrofluidicLib")


MicrofluidicLibrary()
