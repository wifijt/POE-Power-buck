#!/usr/bin/env python3
"""Full-size print-and-cut sticker for the case lid (Silhouette or similar).

Writes, all at exact 1:1 scale in millimetres, in case coordinates seen from above (terminal end at
the top), into docs/:
    lid_sticker.svg / .pdf              black artwork, no background (white or clear vinyl)
    lid_sticker_black.svg / .pdf        white artwork on a black background (white vinyl)
    lid_sticker_cut.dxf / _inch.dxf     cut lines only, in mm / in inches, same for both
    lid_sticker_print.png, lid_sticker_black_print.png
                                        artwork only, 600 dpi, for Silhouette Studio Basic (which
                                        cannot open SVG or PDF): pair with the DXF, align centres
    lid_sticker_preview.png, lid_sticker_black_preview.png
Each SVG/PDF has the artwork and the cut lines (red hairline) in one file, already aligned.

The cut outline comes from lid_sticker() in enclosure/case.scad (the lid's top face, inset
sticker_inset from the edge, every hole grown by the same amount), so it always matches the lid.
The black version's background runs sticker_bleed (1 mm) past the cut line, so a slightly
off cut never leaves a white edge.

Needs openscad on PATH and matplotlib.   python3 scripts/gen_lid_sticker.py
"""
import os
import re
import subprocess
import tempfile

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"     # text as outlines: no font needed on the cutter PC
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findfont
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SCAD = os.path.join(ROOT, "enclosure", "case.scad")
DOCS = os.path.join(ROOT, "docs")

# board coords (KiCad: x right, y down from the terminal edge) -> case coords (y up); see case.scad
BX0 = BY0 = 3.5            # wall + clearance
PCB_L = 57.0
def C(bx, by): return (BX0 + bx, BY0 + PCB_L - by)

try:
    FONT = FontProperties(family="Liberation Sans", weight="bold")
    findfont(FONT, fallback_to_default=False)
except Exception:
    FONT = FontProperties(family="DejaVu Sans", weight="bold")
CAP = TextPath((0, 0), "H", prop=FONT, size=1).get_extents().height
INK = "black"
CUT = "#ff0000"


def openscad(fmt, part="sticker"):
    out = tempfile.NamedTemporaryFile(suffix="." + fmt, delete=False).name
    subprocess.run(["openscad", "-D", 'part="%s"' % part, "-o", out, SCAD], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


def load_outline(svg):
    """OpenSCAD SVG -> one compound matplotlib Path (y flipped back to up)."""
    verts, codes = [], []
    for d in re.findall(r'd="([^"]+)"', open(svg).read()):
        for sub in re.findall(r"M[^M]*", d):
            pts = [tuple(map(float, p.split(","))) for p in re.findall(r"(-?[\d.e+-]+,-?[\d.e+-]+)", sub)]
            for i, (x, y) in enumerate(pts):
                verts.append((x, -y)); codes.append(Path.MOVETO if i == 0 else Path.LINETO)
            verts.append(verts[-len(pts)]); codes.append(Path.CLOSEPOLY)
    return Path(verts, codes)


def text(ax, s, bx, by, cap_mm, color=INK):
    size = cap_mm / CAP
    p = TextPath((0, 0), s, prop=FONT, size=size)
    e = p.get_extents()
    x, y = C(bx, by)
    t = Affine2D().translate(x - (e.x0 + e.width / 2), y - CAP * size / 2)
    ax.add_patch(PathPatch(t.transform_path(p), fc=color, ec="none", lw=0))


def artwork(ax, ink=INK, paper="white"):
    # polarity marks over each terminal pole (J2 = OUT: + 10.4, - 15.4; J1 = IN: + 24.9, - 29.9)
    mark, bar, pole_y = 3.6, 1.0, 20.4
    for bx, sign in [(10.4, "+"), (15.4, "-"), (24.9, "+"), (29.9, "-")]:
        x, y = C(bx, pole_y)
        ax.add_patch(Rectangle((x - mark / 2, y - bar / 2), mark, bar, fc=ink, ec="none"))
        if sign == "+":
            ax.add_patch(Rectangle((x - bar / 2, y - mark / 2), bar, mark, fc=ink, ec="none"))
    text(ax, "OUT", 12.9, 24.4, 3.0, ink)
    text(ax, "12V", 12.9, 28.2, 2.5, ink)
    text(ax, "IN", 27.4, 24.4, 3.0, ink)
    text(ax, "6-16V", 27.4, 28.2, 2.5, ink)
    # 20A in a solid box (inverted): the number to match the input breaker to
    bw, bh = 8.6, 3.6
    x, y = C(24.6, 32.8)
    ax.add_patch(Rectangle((x - bw / 2, y - bh / 2), bw, bh, fc=ink, ec="none"))
    text(ax, "20A", 24.6, 32.8, 2.5, paper)
    text(ax, "TURNER VISION", 18.0, 51.7, 3.0, ink)
    text(ax, "POE BUCK BOOST", 18.0, 55.5, 2.4, ink)


def page(ext, scale=1):
    m = 5.0                                        # margin round the sticker on the page
    x0, y0, w, h = ext.x0 - m, ext.y0 - m, ext.width + 2 * m, ext.height + 2 * m
    fig = plt.figure(figsize=(w / 25.4 * scale, h / 25.4 * scale))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(x0, x0 + w); ax.set_ylim(y0, y0 + h); ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def main():
    svg = openscad("svg")
    outline = load_outline(svg)
    svg_b = openscad("svg", "sticker_bleed")
    bleed = load_outline(svg_b)
    os.unlink(svg); os.unlink(svg_b)
    ext = outline.get_extents()

    styles = {  # name: (ink, paper, background path or None)
        "lid_sticker": (INK, "white", None),
        "lid_sticker_black": ("white", "black", bleed),
    }
    for name, (ink, paper, bg) in styles.items():
        fig, ax = page(ext)
        if bg is not None:
            ax.add_patch(PathPatch(bg, fc=paper, ec="none", lw=0))
        artwork(ax, ink, paper)
        ax.add_patch(PathPatch(outline, fill=False, ec=CUT, lw=0.25))   # cut lines
        for ext_ in ("svg", "pdf"):
            fig.savefig(os.path.join(DOCS, "%s.%s" % (name, ext_)), transparent=True)
        plt.close(fig)

        # preview: the cut sticker on an orange lid
        fig, ax = page(ext, scale=3)
        ax.add_patch(PathPatch(outline, fc=paper, ec="none", lw=0))
        artwork(ax, ink, paper)
        fig.savefig(os.path.join(DOCS, name + "_preview.png"), dpi=100, facecolor="#f07d1a")
        plt.close(fig)

        # Silhouette Studio Basic opens only DXF (cut lines) and images (artwork). This PNG is cropped
        # so its centre is the cut outline's centre: the white one to the outline's box, the black one
        # to the bleed box (1 mm bigger all round). Aligning the two centres lines them up exactly.
        box = (bg if bg is not None else outline).get_extents()
        fig = plt.figure(figsize=(box.width / 25.4, box.height / 25.4))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(box.x0, box.x1); ax.set_ylim(box.y0, box.y1); ax.set_aspect("equal"); ax.axis("off")
        if bg is not None:
            ax.add_patch(PathPatch(bg, fc=paper, ec="none", lw=0))
        artwork(ax, ink, paper)
        fig.savefig(os.path.join(DOCS, name + "_print.png"), dpi=600, transparent=True)
        plt.close(fig)
        print("%s_print.png: %.2f x %.2f mm" % (name, box.width, box.height))

    # Cut lines as DXF, written here (not by OpenSCAD) so each hole is one closed polyline, the
    # drawing starts at 0,0 and the header names its units. Silhouette Studio Basic can read DXF
    # numbers as inches and then shrinks a "42 inch" drawing to the page, so there is an inch copy.
    write_dxf(os.path.join(DOCS, "lid_sticker_cut.dxf"), outline, 1.0, 4)            # millimetres
    write_dxf(os.path.join(DOCS, "lid_sticker_cut_inch.dxf"), outline, 1 / 25.4, 1)  # inches
    print("sticker %.1f x %.1f mm -> docs/lid_sticker{,_black}.{svg,pdf,_preview.png,_print.png}, "
          "lid_sticker_cut{,_inch}.dxf" % (ext.width, ext.height))


def write_dxf(path, outline, scale, insunits):
    """R12 DXF of the outline: one closed POLYLINE per loop, origin at the bottom-left corner."""
    e = outline.get_extents()
    loops = [[((x - e.x0) * scale, (y - e.y0) * scale) for x, y in poly[:-1]]
             for poly in outline.to_polygons(closed_only=True)]
    w, h = e.width * scale, e.height * scale
    out = ["0", "SECTION", "2", "HEADER",
           "9", "$ACADVER", "1", "AC1009",
           "9", "$INSUNITS", "70", str(insunits),
           "9", "$MEASUREMENT", "70", "1" if insunits == 4 else "0",
           "9", "$EXTMIN", "10", "0.0", "20", "0.0",
           "9", "$EXTMAX", "10", "%.4f" % w, "20", "%.4f" % h,
           "9", "$LIMMIN", "10", "0.0", "20", "0.0",
           "9", "$LIMMAX", "10", "%.4f" % w, "20", "%.4f" % h,
           "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for loop in loops:
        out += ["0", "POLYLINE", "8", "CUT", "66", "1", "70", "1"]
        for x, y in loop:
            out += ["0", "VERTEX", "8", "CUT", "10", "%.4f" % x, "20", "%.4f" % y]
        out += ["0", "SEQEND", "8", "CUT"]
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")

if __name__ == "__main__":
    main()
