"""Write the three project footprints into frc_poe.pretty/.

TI_RPM0026A: pad geometry is TI's recommended land pattern for RPM0026A
(VQFN-HR-26, 4.0 x 3.5 mm), cross-checked against two independent published
footprints (LCSC/EasyEDA export and EwoudVV/ducktop2).
WAGO 2604-3102: 2 solder pins per pole, 5.0 mm pole pitch, 8.2 mm pin pair,
checked against WAGO's 2604-3102 data sheet (23.12.2024): Ø1.3 (+0.1) drill,
front face 4.9 mm in front of pin row 1, body 16.7 deep.  Wires enter VERTICALLY
(conductor axis 90° to the PCB) from the top of the block; the orange levers are
on the front face, which is the -Y side and swings ~9 mm further out when opened.
"""
import os
D = os.path.join(os.path.dirname(__file__), "..", "frc_poe.pretty")


def rect(n, x, y, w, h, layers='"F.Cu" "F.Paste" "F.Mask"', rr=0.25):
    return f'  (pad "{n}" smd roundrect (at {x:.4f} {y:.4f}) (size {w:.4f} {h:.4f}) (layers {layers}) (roundrect_rratio {rr}))'


def poly_pad(n, x, y, pts):
    p = " ".join(f"(xy {a:.4f} {b:.4f})" for a, b in pts)
    return (f'  (pad "{n}" smd custom (at {x:.4f} {y:.4f}) (size 0.2 0.2) (layers "F.Cu" "F.Paste" "F.Mask")\n'
            f'    (options (clearance outline) (anchor rect))\n'
            f'    (primitives (gr_poly (pts {p}) (width 0) (fill yes))))')


def line(x1, y1, x2, y2, layer, w):
    return f'  (fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (layer "{layer}"))'


def box(x1, y1, x2, y2, layer, w):
    return "\n".join([line(x1, y1, x2, y1, layer, w), line(x2, y1, x2, y2, layer, w),
                      line(x2, y2, x1, y2, layer, w), line(x1, y2, x1, y1, layer, w)])


def header(name, descr, smd=True):
    return [f'(footprint "{name}" (version 20221018) (generator pcbnew) (layer "F.Cu")',
            f'  (descr "{descr}")', f'  (attr {"smd" if smd else "through_hole"})',
            f'  (fp_text reference "REF**" (at 0 -3) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
            f'  (fp_text value "{name}" (at 0 3) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))']


def tps():
    L = header("TI_RPM0026A_VQFN-HR-26_4x3.5mm", "TI RPM0026A VQFN-HR-26 4x3.5mm (TPS55288/TPS552882), TI land pattern")
    side = [("2", -1.9, -1.0, .6), ("3", -1.8375, -.5, .725), ("4", -1.8375, 0, .725), ("5", -1.8375, .5, .725), ("6", -1.9, 1.0, .6)]
    for n, x, y, w in side:
        L.append(rect(n, x, y, w, .25))
        L.append(rect(str(20 - int(n)), -x, y, w, .25))   # 18,17,16,15,14 mirror
    for n, x in (("8", -1.125), ("9", -.625), ("10", -.125), ("11", .625), ("12", 1.125)):
        L.append(rect(n, x, 1.6375, .25, .625))
    for n, x, h, y in (("23", -1.05, .675, -1.6125), ("22", -.25, .6, -1.65), ("21", .25, .6, -1.65), ("20", 1.05, .675, -1.6125)):
        L.append(rect(n, x, y, .25, h))
    for n, x in (("24", -.625), ("25", 0), ("26", .625)):
        L.append(rect(n, x, 0, .375, 1.425, rr=0.1))
    c1 = [(-.575, -.1125), (.2, -.1125), (.2, -.4625), (-.2, -.4625), (-.2, -.1125)]
    pad1 = [(-.575, -.1125), (-.2, -.1125), (-.2, -.4625), (.2, -.4625), (.2, .1125), (-.575, .1125)]
    L.append(poly_pad("1", -1.625, -1.4875, pad1))
    L.append(poly_pad("19", 1.625, -1.4875, [(-a, b) for a, b in pad1]))
    pad7 = [(-.525, -.1125), (.175, -.1125), (.175, .4625), (-.175, .4625), (-.175, .1125), (-.525, .1125)]
    L.append(poly_pad("7", -1.675, 1.4875, pad7))
    L.append(poly_pad("13", 1.675, 1.4875, [(-a, b) for a, b in pad7]))
    L.append(box(-2.0, -1.75, 2.0, 1.75, "F.Fab", 0.1))
    L.append(box(-2.45, -2.2, 2.45, 2.2, "F.CrtYd", 0.05))
    # silk corner marks + pin-1 dot
    for sx in (-1, 1):
        for sy in (-1, 1):
            L.append(line(sx * 2.15, sy * 1.9, sx * 2.15, sy * 1.6, "F.SilkS", 0.12) if False else "")
    L.append('  (fp_circle (center -2.55 -2.0) (end -2.45 -2.0) (stroke (width 0.2) (type solid)) (fill solid) (layer "F.SilkS"))')
    L.append(")")
    return "\n".join(x for x in L if x)


def wago():
    L = header("WAGO_2604-3102_1x02_P5.00mm", "WAGO 2604-3102 PCB terminal block, lever, push-in, 2-pole, 5.0mm pitch, 4mm2. Vertical wire entry; levers on -Y face.", smd=False)
    for n, x in (("1", 0.0), ("2", 5.0)):
        for y in (0.0, 8.2):
            shape = "rect" if n == "1" else "circle"
            L.append(f'  (pad "{n}" thru_hole {shape} (at {x} {y}) (size 2.6 2.6) (drill 1.4) (layers "*.Cu" "*.Mask"))')
    L.append(box(-3.9, -5.1, 8.9, 11.9, "F.Fab", 0.1))
    L.append(box(-4.0, -5.2, 9.0, 12.0, "F.CrtYd", 0.05))
    L.append(line(-3.9, 11.9, 8.9, 11.9, "F.SilkS", 0.12))
    L.append(line(-3.9, 11.9, -3.9, -5.0, "F.SilkS", 0.12))
    L.append(line(8.9, 11.9, 8.9, -5.0, "F.SilkS", 0.12))
    for x in (0, 5):   # lever marks (front face)
        L.append(box(x - 1.2, -5.0, x + 1.2, -4.0, "F.Fab", 0.1))
    L.append(")")
    return "\n".join(L)


def nexfet():
    L = header("NexFET_SON-8_3.3x3.3mm", "TI NexFET SON 3.3x3.3mm (Q3/Q3A): 1-3 source, 4 gate, 5-8 + tab drain")
    for i, y in enumerate((-.975, -.325, .325, .975)):
        L.append(rect(str(i + 1), -1.44, y, .63, .45))
    L.append(f'  (pad "5" smd rect (at 0.595 0) (size 2.32 2.45) (layers "F.Cu" "F.Mask"))')
    for x in (0.0, 1.2):
        for y in (-.6, .6):
            L.append(f'  (pad "" smd rect (at {x} {y}) (size 0.85 0.9) (layers "F.Paste"))')
    L.append(box(-1.65, -1.65, 1.65, 1.65, "F.Fab", 0.1))
    L.append(box(-2.0, -1.9, 2.0, 1.9, "F.CrtYd", 0.05))
    L.append(line(-1.65, -1.75, 1.65, -1.75, "F.SilkS", 0.12))
    L.append(line(-1.65, 1.75, 1.65, 1.75, "F.SilkS", 0.12))
    L.append('  (fp_circle (center -2.05 -1.45) (end -1.95 -1.45) (stroke (width 0.2) (type solid)) (fill solid) (layer "F.SilkS"))')
    L.append(")")
    return "\n".join(L)


os.makedirs(D, exist_ok=True)
for name, txt in (("TI_RPM0026A_VQFN-HR-26_4x3.5mm", tps()), ("WAGO_2604-3102_1x02_P5.00mm", wago()),
                  ("NexFET_SON-8_3.3x3.3mm", nexfet())):
    open(os.path.join(D, name + ".kicad_mod"), "w").write(txt + "\n")
print("footprints written")
