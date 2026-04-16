# Trapping Array — KLayout PCell Library

Parametric GDS layout generator for single-layer PDMS microfluidic
hydrodynamic trapping arrays, distributed as a KLayout PCell library.

Based on:
> Ruyssen N., Fina G., Allena R., Jullien M.-C., Fattaccioli J.
> *Using lateral dispersion to optimise microfluidic trap array efficiency.*
> Computers and Fluids **297** (2025) 106643.
> <https://doi.org/10.1016/j.compfluid.2025.106643>

---

## Installation

1. Open KLayout.
2. Go to **Macros → Import…**
3. Select `trapping_array_pcell.lym` and click **OK**.
4. **Restart KLayout.**

On first load the macro writes all library modules to
`~/.klayout/pymacros/trapping_array/` and registers the library.
After restart the **Trapping Array** entry appears in the
**Libraries panel** (bottom-left of the KLayout window).

---

## Usage

1. In the **Libraries panel**, expand **Trapping Array**.
2. Drag **TrapArray_A** or **TrapArray_B** into your layout.
3. **Double-click** the placed instance to open the parameter editor.
4. Edit any parameter and click **OK** — the geometry regenerates instantly.

If a parameter combination is invalid (e.g. slit wider than the trap
interior), a cross marker is drawn and an error message is printed to
the KLayout log. Correct the parameters and click OK again.

---

## The two PCells

### TrapArray_A — Fixed grid

You specify exactly how many traps you want and the inter-trap gaps.
The pitches, array footprint, and margins are all derived automatically.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `L` | Cavity streamwise length (µm) | 1500 |
| `W` | Cavity lateral width (µm) | 1200 |
| `N_l` | Number of trap lines (streamwise x) | 7 |
| `N_c` | Number of trap columns (lateral y) | 14 |
| `gap_x` | Inter-trap gap in x (µm) → Δx = l_trap + gap_x | 10 |
| `gap_y` | Inter-trap gap in y (µm) → Δy = w_trap + gap_y | 10 |
| `gap_x_margin` | Streamwise wall margin override (µm, 0 = use gap_x) | 0 |
| `gap_y_margin` | Lateral wall margin override (µm, 0 = use Δy/2) | 0 |

The array is centred in the cavity. Lateral wall margin defaults to
Δy/2, so the distance from the outermost trap edge to the cavity wall
matches the half inter-column spacing. Odd columns are staggered by
+Δx/2 in x. A warning is printed if the array does not fit.

### TrapArray_B — Max traps

You specify the pitch and the cavity; the number of traps is maximised
automatically.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `L` | Cavity streamwise length (µm) | 1500 |
| `W` | Cavity lateral width (µm) | 1200 |
| `Delta_x` | Streamwise pitch (µm) | 40 |
| `Delta_y` | Lateral pitch (µm) | 35 |
| `margin_x` | Streamwise wall margin override (µm, 0 = Δy/2) | 0 |
| `margin_y` | Lateral wall margin override (µm, 0 = Δy/2) | 0 |

N_c = ⌊(W − 2·margin_y − w_trap) / Δy⌋ + 1
N_l = ⌊(L − 2·margin_x − l_trap) / Δx⌋ + 1

---

## Shared parameters (both PCells)

### Trap shape

| Parameter | Description | Default |
|-----------|-------------|---------|
| `l_trap` | Trap streamwise length (µm) | 30 |
| `w_trap` | Trap lateral outer width (µm) | 25 |
| `wall_t` | Pillar wall thickness (µm) | 3 |
| `base_t` | Downstream base bar depth (µm) | 4 |
| `w_o_down` | Downstream slit width (µm) | 8 |

The trap is an inverted-U shape: two vertical pillars (`wall_t` wide,
`l_trap` long) joined by a base bar (`base_t` deep) at the downstream
end. The base bar has a centred slit of width `w_o_down`. The upstream
face is fully open over `w_o = w_trap − 2·wall_t`.

Constraints checked automatically:
- `w_o_down` must be in (0, w_trap − 2·wall_t)
- `base_t` must be < `l_trap`
- `wall_t` must satisfy w_trap − 2·wall_t > 0

### IO mode

| Parameter | Description | Default |
|-----------|-------------|---------|
| `io_mode` | `'direct'` or `'diverging'` | `'direct'` |
| `C` | Centring [0–1], direct mode only (1 = aligned, 0 = max offset) | 1.0 |
| `w_io` | Channel width (µm) | 100 |
| `channel_len` | Stub length outside the chip (µm) | 100 |
| `l_div` | Diverging section length (µm), diverging mode only | 200 |

**Direct mode** — rectangular stubs connect directly to the chamber
walls. The inlet can be laterally offset by Δy_io = (1−C)·(W−w_io)/2
relative to the outlet, creating an oblique flow that improves filling
efficiency (C = 0.44 is the globally optimised value from the paper).

**Diverging mode** — straight trapezoidal sections fan the channel
from `w_io` to the full chamber width `W` over length `l_div`, then
rectangular stubs continue outside the chip. Both channels are centred
on W/2. The parameter C is ignored. The half-angle
α = atan((W−w_io)/(2·l_div)) is printed to the log on each generation.

### Disorder

| Parameter | Description | Default |
|-----------|-------------|---------|
| `D_f` | Disorder factor [0–1] (0 = perfectly regular) | 0.0 |
| `disorder_type` | `'uniform'` or `'gaussian'` (σ = 0.3) | `'uniform'` |
| `seed` | Random seed for reproducibility (0 = random) | 42 |

Each trap position is perturbed by (ψ_x·D_f·Δx, ψ_y·D_f·Δy).
Recommended: D_f = 0.3–0.4 (uniform) for ~80% filling efficiency.
Disordered traps are clamped to remain inside the chamber.
The same seed always produces the same disorder pattern.

### Layer

| Parameter | Description | Default |
|-----------|-------------|---------|
| `layer` | GDS output layer | layer 1, datatype 0 |

---

## Coordinate convention

```
y (lateral)
↑
│   ┌──────────────────────────────────┐
│   │  chamber (origin at BL corner)  │
│   └──────────────────────────────────┘
└─────────────────────────────────────────→  x (streamwise)
outlet (−x)                        inlet (+x)
                   flow →
```

Trap open face at +x (upstream). Base bar at −x (downstream).
Stagger: columns with index ic odd (0-indexed) shifted +Δx/2 in x.

---

## Files installed on first load

```
~/.klayout/pymacros/trapping_array/
├── core/
│   ├── __init__.py      make_fixed_grid, make_max_traps, generate_gds
│   ├── grid.py          ArrayGrid — geometry solver
│   ├── builder.py       TrappingArrayBuilder — layout generator
│   ├── primitives.py    rect, polygon, draw_trap
│   └── io_shapes.py     direct and diverging channel drawing
└── trapping_array_lib.py  PCell declarations and library registration
```

The core modules can also be imported directly in Python scripts
(outside KLayout) by adding the directory to `sys.path`:

```python
import sys
sys.path.insert(0, "~/.klayout/pymacros/trapping_array")
from core import make_fixed_grid, generate_gds
```

---

## License

MIT — Fattaccioli Lab, Institut Pierre-Gilles de Gennes, Paris.
