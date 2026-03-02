# KLayout Serpentine Channel Macro

This repository contains a KLayout Python macro for generating a parametric constant-width meander (serpentine) microchannel inside the active layout.

## Geometry

The generated channel is composed of:

- parallel horizontal straight runs,
- alternating 180-degree rounded U-bends,
- a vertical inlet leg,
- a vertical outlet leg.

In the current version, the inlet and outlet legs connect at the midpoint of the first and last horizontal runs.

## Main parameters

All dimensions are in microns.

- `TOTAL_LENGTH`: total centerline length, including inlet and outlet vertical legs
- `CHANNEL_WIDTH`: channel width
- `PITCH`: centerline-to-centerline spacing between adjacent horizontal runs
- `EXT_WIDTH`: external horizontal footprint of the serpentine
- `VERTICAL_LEG`: inlet and outlet leg length
- `ARC_POINTS`: number of points used to discretize each rounded bend

## Geometric rules

The macro uses:

- bend radius `R = PITCH / 2`
- constraint `PITCH > 2 * CHANNEL_WIDTH`
- constraint `EXT_WIDTH > PITCH + CHANNEL_WIDTH`

If these conditions are not satisfied, the macro raises an error.

## Behavior

The macro:

1. reads the active KLayout layout view,
2. selects the active cell (or falls back to a top cell if needed),
3. solves the serpentine geometry from the requested total length,
4. creates a `pya.DPath` centerline with rounded U-bends,
5. inserts the path into the selected layer.

## Typical use

This is useful for:

- microfluidic delay lines,
- residence-time control,
- compact long-channel routing,
- mask-layout generation for soft lithography.

## Suggested repository contents

- `Serpentine_v2.py`: KLayout macro
- `README.md`: repository documentation
- `LICENSE.md`: license text
- `PROMPT.md`: archived design prompt used to specify the geometry

## Notes

- The total length is the centerline length, not the wall perimeter.
- If the geometry does not appear immediately in KLayout, use Zoom Fit.
- If no active cell is selected, select a layout tab and target cell before running the macro.
