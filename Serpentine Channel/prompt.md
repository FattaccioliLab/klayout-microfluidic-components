# Prompt leading to the serpentine channel macro

The following user prompt led to the serpentine channel specification and macro development:

> Can you provide a KLayout macro to create A constant-width meander channel composed of parallel straight runs connected by alternating 180° rounded U-bends, with vertical inlet and outlet legs for integration into the full circuit. The vertical inlets and outlets have a length of 250 microns, and the parameters are the full length of the serpentine channel (including the vertical parts), the width of the channel, the pitch (the pitch should always be greated than 2x the channel width, the external horizontal width of the serpentine).
>
> The serpentine should be added in the selected layout

A later refinement requested that the vertical inlet and outlet connect at the midpoint of the first and last horizontal channel segments.
