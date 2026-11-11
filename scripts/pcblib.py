"""pcbnew helpers: placement, tracks, vias, zones, debug rendering."""
import math, os
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM

O = (100.0, 100.0)          # board origin on the KiCad page (mm)
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..")
SYSFP = "/usr/share/kicad/footprints"


def V(x, y):
    return VECTOR2I(FromMM(O[0] + x), FromMM(O[1] + y))


class Board:
    def __init__(self, w, h):
        self.b = pcbnew.BOARD()
        self.w, self.h = w, h
        self.fp = {}
        self.nets = {}
        self.layers = {"F": pcbnew.F_Cu, "In1": pcbnew.In1_Cu, "In2": pcbnew.In2_Cu, "B": pcbnew.B_Cu}
        self.b.SetCopperLayerCount(4)

    # ---- nets ------------------------------------------------------------
    def net(self, name):
        if name not in self.nets:
            n = pcbnew.NETINFO_ITEM(self.b, name)
            self.b.Add(n)
            self.nets[name] = n
        return self.nets[name]

    # ---- footprints --------------------------------------------------------
    def place(self, part, x, y, rot=0):
        lib, name = part["fp"].split(":")
        path = os.path.join(PROJ, f"{lib}.pretty") if lib == "frc_poe" else os.path.join(SYSFP, f"{lib}.pretty")
        f = pcbnew.FootprintLoad(path, name)
        f.SetFPID(pcbnew.LIB_ID(lib, name))
        f.SetReference(part["ref"])
        f.SetValue(part["value"])
        self.b.Add(f)
        f.SetPosition(V(x, y))
        f.SetOrientationDegrees(rot)
        for pad in f.Pads():
            n = part["pins"].get(pad.GetNumber())
            if n:
                pad.SetNet(self.net(n))
        for k in ("MPN", "LCSC"):
            if part.get(k.lower()):
                f.SetField(k, part[k.lower()]) if hasattr(f, "SetField") else None
        self.fp[part["ref"]] = f
        return f

    def pad(self, ref, num, which=0):
        pads = [p for p in self.fp[ref].Pads() if p.GetNumber() == num]
        p = pads[which].GetPosition()
        return (ToMM(p.x) - O[0], ToMM(p.y) - O[1])

    # ---- copper -------------------------------------------------------------
    def track(self, net, pts, w=0.25, layer="F"):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(self.b)
            t.SetStart(V(x1, y1)); t.SetEnd(V(x2, y2))
            t.SetWidth(FromMM(w)); t.SetLayer(self.layers[layer]); t.SetNet(self.net(net))
            self.b.Add(t)

    def via(self, net, x, y, d=0.6, drill=0.3):
        v = pcbnew.PCB_VIA(self.b)
        v.SetPosition(V(x, y)); v.SetWidth(FromMM(d)); v.SetDrill(FromMM(drill))
        v.SetNet(self.net(net)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
        self.b.Add(v)

    def vias(self, net, pts, **k):
        for x, y in pts:
            self.via(net, x, y, **k)

    def zone(self, net, layer, pts, prio=1, clearance=0.2, minw=0.2, thermal=False):
        z = pcbnew.ZONE(self.b)
        z.SetLayer(self.layers[layer])
        z.SetNet(self.net(net))
        z.SetAssignedPriority(prio)
        z.SetLocalClearance(FromMM(clearance))
        z.SetMinThickness(FromMM(minw))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
        z.SetThermalReliefGap(FromMM(0.25)); z.SetThermalReliefSpokeWidth(FromMM(0.4))
        z.SetIsFilled(False)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline(); ol.NewOutline()
        for x, y in pts:
            ol.Append(FromMM(O[0] + x), FromMM(O[1] + y))
        self.b.Add(z)
        return z

    def rect_zone(self, net, layer, x1, y1, x2, y2, **k):
        return self.zone(net, layer, [(x1, y1), (x2, y1), (x2, y2), (x1, y2)], **k)

    # ---- outline / text -------------------------------------------------------
    def outline(self, r=1.0):
        w, h = self.w, self.h
        segs = [((r, 0), (w - r, 0)), ((w, r), (w, h - r)), ((w - r, h), (r, h)), ((0, h - r), (0, r))]
        for a, b in segs:
            s = pcbnew.PCB_SHAPE(self.b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(V(*a)); s.SetEnd(V(*b)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1))
            self.b.Add(s)
        k = r * (1 - 2 ** -0.5)
        for st, md, en in (((0, r), (k, k), (r, 0)), ((w - r, 0), (w - k, k), (w, r)),
                           ((w, h - r), (w - k, h - k), (w - r, h)), ((r, h), (k, h - k), (0, h - r))):
            s = pcbnew.PCB_SHAPE(self.b); s.SetShape(pcbnew.SHAPE_T_ARC)
            s.SetArcGeometry(V(*st), V(*md), V(*en))
            s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1))
            self.b.Add(s)

    def hide_refs(self, keep=()):
        for f in self.b.GetFootprints():
            if f.GetReference() not in keep:
                f.Reference().SetVisible(False)
            else:
                f.Reference().SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8)))
                f.Reference().SetTextThickness(FromMM(0.12))

    def text(self, s, x, y, size=1.0, layer=pcbnew.F_SilkS, rot=0, bold=False, mirror=False):
        t = pcbnew.PCB_TEXT(self.b)
        t.SetText(s); t.SetPosition(V(x, y)); t.SetLayer(layer)
        t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
        t.SetTextThickness(FromMM(size * (0.2 if bold else 0.15)))
        t.SetTextAngleDegrees(rot)
        if mirror:
            t.SetMirrored(True)
        self.b.Add(t)

    def hole(self, x, y, d):
        f = pcbnew.FootprintLoad(os.path.join(SYSFP, "MountingHole.pretty"), "MountingHole_3.2mm_M3")
        self.b.Add(f); f.SetPosition(V(x, y))
        return f

    def fill(self):
        pcbnew.ZONE_FILLER(self.b).Fill(self.b.Zones())

    def save(self, path):
        self.b.Save(path)
