"""Generate the KiCad schematic from design.py (label-connected, one sheet)."""
import math, os, uuid
from sexp import find_symbol, dump
import design


def _kicad_share(sub):
    """Stock KiCad library dir: $KICAD_SHARE, Linux /usr/share/kicad, or macOS KiCad.app."""
    for base in (os.environ.get("KICAD_SHARE"), "/usr/share/kicad",
                 "/Applications/KiCad/KiCad.app/Contents/SharedSupport"):
        if base and os.path.isdir(os.path.join(base, sub)):
            return os.path.join(base, sub)
    raise SystemExit(f"KiCad {sub} library not found; set KICAD_SHARE")


SYM = _kicad_share("symbols")
OUT = os.path.join(os.path.dirname(__file__), "..", f"{design.PROJECT}.kicad_sch")
U = lambda: str(uuid.uuid4())
ROOT = "6f1c3c4e-2b1a-4d61-9a55-5a7d0c0f0001"


def q(s):
    return '"' + s.replace('"', '\\"') + '"'


# ---------------------------------------------------------------- symbols
def tps552882():
    left = [("VIN", "3"), ("EN/UVLO", "4"), ("MODE", "15"), ("FSW", "8"), ("ILIM", "17"),
            ("DITH/SYNC", "7"), ("COMP", "18"), ("CDC", "16"), ("FB", "14")]
    right = [("DR1H", "2"), ("BOOT1", "22"), ("SW1", "23"), ("DR1L", "1"), ("SW2", "21"),
             ("SW2", "25"), ("BOOT2", "20"), ("VOUT", "11"), ("VOUT", "26"), ("ISP", "12"),
             ("ISN", "13"), ("VCC", "19"), ("PG", "5"), ("CC_N", "6")]
    bottom = [("PGND", "9"), ("PGND", "24"), ("AGND", "10")]
    top = 2.54 * (len(right) - 1) / 2
    pins = []
    for i, (n, num) in enumerate(left):
        pins.append(f'(pin passive line (at -15.24 {top - i * 2.54 * 1.5:.2f} 0) (length 2.54) (name {q(n)} (effects (font (size 1.27 1.27)))) (number {q(num)} (effects (font (size 1.27 1.27)))))')
    for i, (n, num) in enumerate(right):
        pins.append(f'(pin passive line (at 15.24 {top - i * 2.54:.2f} 180) (length 2.54) (name {q(n)} (effects (font (size 1.27 1.27)))) (number {q(num)} (effects (font (size 1.27 1.27)))))')
    yb = -(top + 5.08)
    for i, (n, num) in enumerate(bottom):
        pins.append(f'(pin passive line (at {-5.08 + i * 5.08:.2f} {yb:.2f} 90) (length 2.54) (name {q(n)} (effects (font (size 1.27 1.27)))) (number {q(num)} (effects (font (size 1.27 1.27)))))')
    body = f'(rectangle (start -12.7 {top + 2.54:.2f}) (end 12.7 {yb + 2.54:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))'
    return f'''(symbol "frc_poe:TPS552882" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at -12.7 {top + 3.81:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "TPS552882RPMR" (at 0 {top + 3.81:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Footprint" "frc_poe:TI_RPM0026A_VQFN-HR-26_4x3.5mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "https://www.ti.com/lit/ds/symlink/tps552882.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "TPS552882_0_1" {body})
      (symbol "TPS552882_1_1" {" ".join(pins)}))'''


def lib_symbol_text(lib_id):
    if lib_id == "frc_poe:TPS552882":
        return tps552882()
    lib, name = lib_id.split(":")
    path = f"{SYM}/{lib}.kicad_sym"
    tree = find_symbol(path, name)
    # A derived symbol ('extends') has no graphics or pins of its own: start from the
    # base symbol's body and lay the derived symbol's properties over it.
    while any(isinstance(e, list) and e[0] == "extends" for e in tree):
        base_name = next(e[1] for e in tree if isinstance(e, list) and e[0] == "extends").strip('"')
        base = find_symbol(path, base_name)
        props = {e[1]: e for e in tree if isinstance(e, list) and e[0] == "property"}
        merged = []
        for e in base:
            if isinstance(e, list) and e[0] == "property" and e[1] in props:
                merged.append(props.pop(e[1]))
            elif isinstance(e, list) and e[0] == "symbol":
                e[1] = e[1].replace(base_name, name)
                merged.append(e)
            else:
                merged.append(e)
        tree = merged + list(props.values())
    tree[1] = q(lib_id)
    for e in tree:
        if isinstance(e, list) and e[:2] == ["property", '"Value"']:
            e[2] = q(name)
    return dump(tree)


def lib_pins(lib_id):
    """[(number, x, y, angle)] in library (y-up) coordinates."""
    import re
    txt = lib_symbol_text(lib_id)
    out = []
    for m in re.finditer(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)\s+\(length\s+[\d.]+\)(?:\s+hide|\s+\(hide\s+\w+\))?\s+\(name\s+"[^"]*".*?\(number\s+"([^"]*)"', txt, re.S):
        out.append((m.group(4), float(m.group(1)), float(m.group(2)), int(m.group(3))))
    return out


# ---------------------------------------------------------------- placement
# (ref, x, y, rotation) on an A3 sheet, mm.  Grouped by function.
PLACE = {
    # input + protection
    "J1": (25.4, 50.8, 180), "Q3": (55.88, 76.2, 0), "R12": (40.64, 66.04, 0),
    "R13": (45.72, 86.36, 0), "D3": (40.64, 91.44, 90), "D1": (68.58, 50.8, 90),
    "C1": (81.28, 50.8, 0), "C2": (93.98, 50.8, 0), "C3": (104.14, 50.8, 0),
    "C4": (114.3, 50.8, 0), "C5": (124.46, 50.8, 0), "C7": (144.78, 50.8, 0),
    # buck leg
    "Q1": (190.5, 45.72, 0), "Q2": (190.5, 76.2, 0), "R1": (170.18, 45.72, 90),
    "R2": (170.18, 76.2, 90), "L1": (226.06, 63.5, 90), "C8": (210.82, 88.9, 0),
    "C9": (241.3, 88.9, 0),
    # controller
    "U1": (167.64, 147.32, 0),
    "R3": (86.36, 119.38, 0), "R4": (96.52, 119.38, 0), "R5": (86.36, 147.32, 0), "R9": (106.68, 147.32, 0),
    "C11": (116.84, 147.32, 0), "R10": (86.36, 175.26, 0), "C12": (86.36, 193.04, 0),
    "C13": (101.6, 175.26, 0), "R6": (116.84, 172.72, 0), "R7": (116.84, 190.5, 0),
    "C14": (232.41, 172.72, 0), "C15": (242.57, 172.72, 0),
    # output
    "C16": (264.16, 119.38, 0), "C17": (274.32, 119.38, 0), "C18": (284.48, 119.38, 0),
    "C19": (294.64, 119.38, 0), "C20": (304.8, 119.38, 0), "C21": (314.96, 119.38, 0),
    "R11": (330.2, 116.84, 0), "D2": (330.2, 132.08, 90), "J2": (370.84, 119.38, 0),
}

NOTES = [
    (20, 25, "FRC 12 V PoE-switch supply  -  TPS552882 4-switch buck-boost, 6-16 V in -> 12.1 V / 5 A out", 2.5),
    (20, 32, "Input: WAGO J1 from a PDH/PDP breaker slot (10-20 A).  Q3 = low-side reverse-polarity FET, D1 = 16 V TVS.", 1.6),
    (160, 32, "Buck leg uses external FETs Q1/Q2; boost leg FETs are inside U1.", 1.6),
    (60, 105, "UVLO rising = 1.23 V x (1 + R3/R4) = 5.5 V    FSW: R5 49.9k = 400 kHz    ILIM: R9 22.1k = 14.9 A avg    MODE: tied to GND = internal LDO, forced PWM", 1.6),
    (60, 205, "VOUT = 1.2 V x (1 + R6/R7) = 12.1 V.   ISP/ISN tied to VOUT (output current sense unused).   PG, CC_N, CDC not used.", 1.6),
    (255, 105, "Output: to Linovision POE-Switch0504GDF PWR1 (DC 9-57 V).  At 12 V input the switch's PoE budget is 60 W.", 1.6),
]


def main():
    lib_ids = sorted({p["sym"] for p in design.PARTS})
    out = [f'(kicad_sch (version 20230121) (generator eeschema)', f'  (uuid {ROOT})', '  (paper "A3")',
           f'  (title_block (title "FRC PoE switch 12V buck-boost") (date "2026-11-10") (rev "A") (company "") (comment 1 "TPS552882 standalone, 6-16V in, 12V 5A out"))',
           '  (lib_symbols']
    for lid in lib_ids:
        out.append("    " + lib_symbol_text(lid))
    out.append("  )")
    seen_pts = set()
    for p in design.PARTS:
        ref = p["ref"]
        X, Y, R = PLACE[ref]
        pins = lib_pins(p["sym"])
        props = [("Reference", ref, (X + 3.5, Y - 1.5), False), ("Value", p["value"], (X + 3.5, Y + 1.5), False),
                 ("Footprint", p["fp"], (X, Y + 5), True), ("Datasheet", "~", (X, Y), True),
                 ("MPN", p["mpn"], (X, Y), True), ("LCSC", p.get("lcsc", ""), (X, Y), True),
                 ("Description", p["desc"], (X, Y), True)]
        if p["sym"] == "frc_poe:TPS552882":
            props[0] = ("Reference", ref, (X - 12.7, Y - 22), False)
            props[1] = ("Value", p["value"], (X, Y - 22), False)
        s = [f'  (symbol (lib_id {q(p["sym"])}) (at {X:.2f} {Y:.2f} {R}) (unit 1) (in_bom yes) (on_board yes) (dnp no)',
             f'    (uuid {U()})']
        for k, v, (px, py), hide in props:
            s.append(f'    (property {q(k)} {q(v)} (at {px:.2f} {py:.2f} 0) (effects (font (size 1.27 1.27)) (justify left){" hide" if hide else ""}))')
        for num, *_ in pins:
            s.append(f'    (pin {q(num)} (uuid {U()}))')
        s.append(f'    (instances (project {q(design.PROJECT)} (path "/{ROOT}" (reference {q(ref)}) (unit 1))))')
        s.append("  )")
        out += s
        # wires + labels
        r = math.radians(R)
        for num, px, py, a in pins:
            rx = px * math.cos(r) - py * math.sin(r)
            ry = px * math.sin(r) + py * math.cos(r)
            cx, cy = round(X + rx, 2), round(Y - ry, 2)
            if (ref, num) in design.NO_CONNECT:
                out.append(f'  (no_connect (at {cx:.2f} {cy:.2f}) (uuid {U()}))')
                continue
            net = p["pins"].get(num)
            if not net:
                continue
            key = (cx, cy)
            if key in seen_pts:
                continue
            seen_pts.add(key)
            oa = (a + 180 + R) % 360
            dx, dy = round(math.cos(math.radians(oa)), 3), -round(math.sin(math.radians(oa)), 3)
            ex, ey = round(cx + 2.54 * dx, 2), round(cy + 2.54 * dy, 2)
            out.append(f'  (wire (pts (xy {cx:.2f} {cy:.2f}) (xy {ex:.2f} {ey:.2f})) (stroke (width 0) (type default)) (uuid {U()}))')
            just = {0: "left bottom", 90: "left bottom", 180: "right bottom", 270: "right bottom"}[oa]
            out.append(f'  (label {q(net)} (at {ex:.2f} {ey:.2f} {oa}) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify {just})) (uuid {U()}))')
    for x, y, t, sz in NOTES:
        out.append(f'  (text {q(t)} (at {x} {y} 0) (effects (font (size {sz} {sz})) (justify left bottom)) (uuid {U()}))')
    out.append('  (sheet_instances (path "/" (page "1")))')
    out.append(")")
    open(OUT, "w").write("\n".join(out) + "\n")
    print("wrote", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
