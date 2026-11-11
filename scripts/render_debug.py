"""Debug PNG of a .kicad_pcb: courtyards, pads coloured by net, MST ratsnest,
tracks, vias and filled zones of one copper layer.  Uses system python + PIL."""
import sys, math, colorsys, hashlib
import pcbnew
from PIL import Image, ImageDraw, ImageFont

S = 36  # px per mm


def col(name, a=255):
    h = int(hashlib.md5(name.encode()).hexdigest()[:4], 16) / 65535
    r, g, b = colorsys.hsv_to_rgb(h, 0.75, 0.95)
    return (int(r * 255), int(g * 255), int(b * 255), a)


def main(pcb, out, layer="F", rats=True):
    b = pcbnew.LoadBoard(pcb)
    bb = b.GetBoardEdgesBoundingBox()
    x0, y0 = pcbnew.ToMM(bb.GetX()) - 2, pcbnew.ToMM(bb.GetY()) - 2
    W, H = pcbnew.ToMM(bb.GetWidth()) + 4, pcbnew.ToMM(bb.GetHeight()) + 4
    im = Image.new("RGBA", (int(W * S), int(H * S)), (20, 20, 24, 255))
    d = ImageDraw.Draw(im, "RGBA")
    P = lambda v: ((pcbnew.ToMM(v.x) - x0) * S, (pcbnew.ToMM(v.y) - y0) * S)
    L = {"F": pcbnew.F_Cu, "In1": pcbnew.In1_Cu, "In2": pcbnew.In2_Cu, "B": pcbnew.B_Cu}[layer]
    # board
    d.rectangle([P(bb.GetOrigin()), P(bb.GetEnd())], outline=(200, 200, 200, 255), width=2)
    # zones
    for z in b.Zones():
        if z.GetLayer() != L or not z.IsFilled():
            continue
        poly = z.GetFilledPolysList(L)
        for i in range(poly.OutlineCount()):
            o = poly.Outline(i)
            pts = [P(o.CPoint(j)) for j in range(o.PointCount())]
            if len(pts) > 2:
                d.polygon(pts, fill=col(z.GetNetname(), 110))
            for h in range(poly.HoleCount(i)):
                hh = poly.Hole(i, h)
                d.polygon([P(hh.CPoint(j)) for j in range(hh.PointCount())], fill=(20, 20, 24, 255))
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            c = P(t.GetPosition()); r = pcbnew.ToMM(t.GetWidth()) / 2 * S
            d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=col(t.GetNetname()), outline=(255, 255, 255, 255))
        elif t.GetLayer() == L:
            d.line([P(t.GetStart()), P(t.GetEnd())], fill=col(t.GetNetname()), width=max(1, int(pcbnew.ToMM(t.GetWidth()) * S)))
    # footprints
    font = ImageFont.load_default()
    netpads = {}
    for f in b.GetFootprints():
        cy = f.GetCourtyard(pcbnew.F_CrtYd)
        bx = f.GetBoundingBox(False, False)
        d.rectangle([P(bx.GetOrigin()), P(bx.GetEnd())], outline=(90, 90, 110, 255))
        for p in f.Pads():
            if not p.IsOnCopperLayer():
                continue
            try:
                poly = p.GetEffectivePolygon()
            except TypeError:                        # KiCad 8+: per-layer
                poly = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
            for i in range(poly.OutlineCount()):
                o = poly.Outline(i)
                d.polygon([P(o.CPoint(j)) for j in range(o.PointCount())], fill=col(p.GetNetname() or "nc", 230), outline=(0, 0, 0, 255))
            if p.GetNetname():
                netpads.setdefault(p.GetNetname(), []).append(P(p.GetPosition()))
        c = P(f.GetPosition())
        d.text((c[0] - 8, c[1] - 6), f.GetReference(), fill=(255, 255, 255, 255), font=font)
    if rats:
        for n, pts in netpads.items():
            if n in ("GND",):
                continue
            done = [pts[0]]; rest = pts[1:]
            while rest:
                best = min(((a, r) for a in done for r in rest), key=lambda ar: math.dist(*ar))
                d.line(best, fill=(255, 255, 0, 160), width=1)
                done.append(best[1]); rest.remove(best[1])
    # grid ticks every 5 mm
    for gx in range(0, int(W), 5):
        d.text(((gx - x0 + math.floor(x0)) * S, 2), str(gx), fill=(150, 150, 150, 255), font=font)
    im.save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(sys.argv[3:4] or ["F"]), rats=len(sys.argv) < 5)
