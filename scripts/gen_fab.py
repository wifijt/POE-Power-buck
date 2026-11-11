"""Write JLCPCB BOM + CPL from the finished board.  <kicad-python> scripts/gen_fab.py"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew, design
HERE = os.path.dirname(os.path.abspath(__file__))
FAB = os.path.join(HERE, "..", "fab")
b = pcbnew.LoadBoard(os.path.join(HERE, "..", f"{design.PROJECT}.kicad_pcb"))
parts = {p["ref"]: p for p in design.PARTS}
HAND = {r for r, p in parts.items() if p.get("tht")}       # WAGO terminals: hand-solder

groups = {}
for r, p in parts.items():
    if r in HAND:
        continue
    key = (p["value"], p["fp"].split(":")[1], p["mpn"], p.get("lcsc", ""))
    groups.setdefault(key, []).append(r)
natural = lambda r: (r.rstrip("0123456789"), int("".join(c for c in r if c.isdigit())))
# JLC's matcher reads Comment + Footprint, so give it plain package names
# (KiCad names like C_0402_1005Metric get misread as 01005).
PKG = {"C_0402_1005Metric": "0402", "R_0402_1005Metric": "0402", "R_0603_1608Metric": "0603",
       "LED_0603_1608Metric": "0603", "C_1206_3216Metric": "1206", "C_1210_3225Metric": "1210",
       "CP_Elec_6.3x7.7": "SMD,D6.3xL7.7mm", "D_SMB": "SMB(DO-214AA)", "D_SOD-123": "SOD-123",
       "NexFET_SON-8_3.3x3.3mm": "VSONP-8(3.3x3.3)", "TI_RPM0026A_VQFN-HR-26_4x3.5mm": "VQFN-26-HR(4x3.5)",
       "L_TaiTech_TMPC1265_13.5x12.5mm": "SMD,13.5x12.8mm"}
with open(os.path.join(FAB, "BOM_JLCPCB.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "JLCPCB Part #", "MPN", "Qty"])
    for (val, fp, mpn, lcsc), refs in sorted(groups.items(), key=lambda kv: natural(sorted(kv[1], key=natural)[0])):
        refs = sorted(refs, key=natural)
        w.writerow([val, ",".join(refs), PKG[fp], lcsc, mpn, len(refs)])
with open(os.path.join(FAB, "BOM_hand_solder.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Part", "Qty", "Note"])
    w.writerow(["J1,J2", "WAGO 2604-3102", 2, "2-pole 5.0 mm lever terminal, solder by hand after PCBA"])

ox, oy = 100.0, 100.0 + 49.5   # JLC CPL: origin at board lower-left, +Y up
with open(os.path.join(FAB, "CPL_JLCPCB.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for fp in sorted(b.GetFootprints(), key=lambda x: natural(x.GetReference())):
        r = fp.GetReference()
        if r in HAND:
            continue
        pos = fp.GetPosition()
        x = pcbnew.ToMM(pos.x) - ox
        y = oy - pcbnew.ToMM(pos.y)
        w.writerow([r, f"{x:.3f}mm", f"{y:.3f}mm", "Top", f"{fp.GetOrientationDegrees() % 360:.0f}"])
print("BOM lines:", len(groups), " placed parts:", sum(len(v) for v in groups.values()))
