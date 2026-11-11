# FRC PoE-switch 12 V buck-boost

A small 4-layer board that takes FRC robot power (a PDH/PDP breaker slot) and
holds a steady **12.1 V** for a Linovision **POE-Switch0504GDF**
(4-port gigabit PoE, DC 9-57 V input). It keeps the switch and its PoE cameras or
coprocessors alive when the battery sags below 9 V under heavy drive load.

![top](docs/board_top.png)

| | |
|---|---|
| Board | 36.0 x 57.0 mm, 4 layers, 1.6 mm, 1 oz outer copper, rounded corners |
| Mounting | 3x M3 (3.2 mm, non-plated, no copper within 3.3 mm): top-left at (2.9, 3.4) mm, bottom corners at (3.5, 53.4) and (32.5, 53.4) mm from the top-left corner. Isolated from every net, as FRC requires for the robot frame |
| Input | 6-16 V (starts at ~5.5 V rising, stops at ~5.0 V; 16 V TVS clamp), reverse-polarity protected |
| Output | 12.1 V, 5 A continuous (60 W). Full power down to about 5.3 V input (14.9 A typ / 12.7 A min average inductor-current limit) |
| Converter | TI **TPS552882** 4-switch buck-boost (standalone, no I2C), 400 kHz |
| Connectors | 2x **WAGO 2604-3102** lever terminals (5.0 mm, up to 12 AWG / 4 mm²). Vertical wire entry; levers face the top edge |
| Indicator | Green LED = 12 V output present |

Silkscreen, left to right along the top edge: **OUT 12V (+ -)** then **IN (+ -)**.

## Wiring on the robot

* **IN**: from a PDH/PDP channel through a **10-20 A breaker**, 14-16 AWG.
* **OUT**: to the switch's PWR1 terminal (9-57 V). The switch's PoE budget is 60 W at
  12 V input (Linovision datasheet), so keep total PoE load plus the switch's own draw under about 55 W.
* The output's `-` is the board's ground, behind the reverse-polarity FET. Don't tie it to the
  input `-` anywhere else.

## Ordering (JLCPCB PCB + assembly)

1. **PCB**: upload `fab/gerbers_JLCPCB.zip` with these options:
   * Layers: **4**, thickness **1.6 mm**
   * Outer copper weight: **1 oz** (default). Inner copper weight: 0.5 oz (default)
   * Surface finish: ENIG recommended for the 0.5 mm-pitch U1 pads (HASL also works). Impedance control: off
   * **Via covering: Epoxy Filled & Capped** (a paid option on 4 layers). U1 has six 0.2 mm-drill
     vias inside its PGND and VOUT center pads; open vias there would wick solder away from the QFN.
     Set **min via hole size to 0.2 mm** (0.35 mm diameter) in the quote.

   1 oz outer copper is enough for the planned 40-55 W load (two Raspberry Pi 5s and an
   Orange Pi 5 on PoE). VIN, VOUT and GND each have a full inner plane alongside the top pour, and
   the top-only runs (GND_IN, SW1, SW2) are short: about a 10 °C rise at 12 V in, about 35 °C only
   with a sustained 6 V input. Avoid 2 oz: JLC then asks for a 0.254 mm annular ring on plated
   holes, and this board's vias have 0.15 mm (0.6/0.3) and 0.075 mm (0.35/0.2 via-in-pad) rings.
2. **Assembly**: top side only. Upload `fab/BOM_JLCPCB.csv` and `fab/CPL_JLCPCB.csv`.
   * Every line has a JLCPCB/LCSC part number, taken from jlcpcb.com part pages (Nov 2026).
     Stock changes daily, so re-run JLC's matching before you pay and swap anything out of stock
     for the same value, package and voltage rating.
   * Stock was checked against JLC's live matching on 2026-11-11. Two lines had none, so they
     were swapped: C1/C20 are now the MA35V100M6X8 polymer (C46550467, 100 µF 35 V, 30 mΩ,
     Economic OK) instead of EEH-ZK1V101XP (C454360), and R9 is now UniOhm 0402WGF2672TCE (C25876).
     Fallback for C1/C20: Lelon HBV101M1VTR-0608 hybrid (C967098). L1 (C41422303) and
     Q1-Q3 (C201632) have only a few hundred in stock.
   * Rotations were checked in JLC's placement preview (2026-11-10). C1/C20 needed 180° and
     `gen_fab.py` now applies that; U1, Q1-Q3 and D1-D3 match. Still glance at the preview: the
     magenta **+** on C1/C20 must sit on the bottom pad, next to the white silkscreen **+**.
3. **Hand-solder** J1 and J2 (WAGO 2604-3102, `fab/BOM_hand_solder.csv`) after the board
   arrives. The pads are 2.6 mm with 1.4 mm drills, two pins per pole, and are connected solid to
   the copper planes, so use a big iron tip.

## First power-up

0. Before any power, check D1 (the SMBJ16A TVS) isn't reversed: meter in diode mode, red probe on
   OUT - (board GND), black on IN +. Expect ~0.6-0.7 V; swapped probes read open (or C1 charging).
   ~0.6 V with red on IN + means D1 is backwards and would short the input.
1. Bench supply at 12 V with a 0.5 A current limit and no load. Expect 12.1 V (±2 %) and the LED on.
2. Sweep the input from 6 V to 16 V with a 1-2 A load and check the output stays at 12 V.
3. Raise the load step by step to 5 A at 12 V input, then at 7 V input. Watch the temperatures of
   L1, Q1 and Q2 (the buck-leg FETs) and U1.
4. Reverse the input briefly at a low current limit and confirm nothing conducts.

## What's in here

```
frc-poe-buckboost.kicad_pro / .kicad_sch / .kicad_pcb   KiCad 10 project
frc_poe.pretty/      TPS552882 VQFN-HR-26, WAGO 2604-3102, NexFET SON3x3 footprints
fab/                 Gerbers + drill (zip), JLC BOM, JLC CPL, hand-solder BOM
docs/                schematic.pdf, board_top.png, board_layers.png
scripts/             generators - design.py is the single source of truth
```

Regenerate everything after editing `scripts/design.py`. The PCB scripts need KiCad's own
Python (the one that can `import pcbnew`). Tested with KiCad 10.0.6 on macOS; the scripts also
still handle KiCad 7 on Linux (`/usr/bin/python3`, libraries in `/usr/share/kicad`). Set
`KICAD_SHARE` if the stock symbol/footprint libraries live somewhere else.

```bash
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
KCLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli

python3 scripts/gen_footprints.py
python3 scripts/gen_sch.py
$KPY scripts/gen_pcb.py            # placement, tracks, zones (unfilled)
$KPY scripts/fill_drc.py           # reload, fill zones, save, DRC report -> drc.rpt
$KPY scripts/gen_fab.py            # BOM / CPL / hand-solder BOM

# gerbers + drill -> fab/gerbers_JLCPCB.zip
rm -f fab/gerbers/* fab/gerbers_JLCPCB.zip
$KCLI pcb export gerbers -o fab/gerbers/ --use-drill-file-origin \
  -l F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts frc-poe-buckboost.kicad_pcb
$KCLI pcb export drill -o fab/gerbers/ --drill-origin plot --format excellon -u mm --excellon-separate-th frc-poe-buckboost.kicad_pcb
(cd fab/gerbers && zip -q ../gerbers_JLCPCB.zip *)

# check the schematic against design.py
$KCLI sch export netlist -o /tmp/frc.net frc-poe-buckboost.kicad_sch
python3 scripts/check_netlist.py /tmp/frc.net
```

KiCad 10 notes: the `pcbnew` scripts print harmless wxWidgets assert lines. Don't call
`pcbnew.WriteDRCReport()` from a script; it segfaults outside the GUI, which is why
`fill_drc.py` runs DRC through `kicad-cli`.

## Design notes

* **Copper**: 1 oz outer layers, 0.2 mm minimum track and clearance throughout (more than JLC's 1 oz minimum).
* **Layers**: top = parts, switch-node and power pours. Inner 1 = solid GND. Inner 2 = VOUT
  plane (left) and VIN plane (right). Bottom = GND plus the DR1H and EN traces.
* **U1 grounding** (TI SLVSFC5 sec. 10.1): three filled-and-capped vias in each of U1's center pads
  (PGND to the In1 ground plane, VOUT to the In2 VOUT plane) for heat and current. Analog ground
  (U1 AGND and MODE pins, R7, R9, C12 and C13) is its own AGND net, routed as traces and joined
  to power ground only at C14's ground terminal through net tie NT1. R4, R5 and C11 stay on the
  main ground plane.
* **Reverse polarity**: Q3 (low-side N-FET, gate from VIN through R12, 12 V zener clamp D3).
* **Values** (FB 100k/11k = 12.1 V; the reference used 102k/11.3k, FSW 49.9k, ILIM 22.1k (was 26.7k), UVLO 100k/28.7k (was 26.1k), compensation 15k + 10 nF + 100 pF, VCC 22 µF,
  6.8 µH inductor, external CSD17577Q3A buck FETs) follow two published TPS552882/TPS55288
  designs: a 12 V output stage in EwoudVV/ducktop2 and a 16 A booster in
  mikegoelzer/Homebrew-ECP5-SBC. The output bulk (100 µF hybrid + 4x 22 µF) is at least what
  the 12 V reference uses, which keeps the boost-mode right-half-plane zero well above crossover.
* **Checks done**: the schematic netlist, the PCB pad nets and `design.py` all match. KiCad DRC
  reports 0 unconnected items and 0 clearance errors. What's left is courtyard overlap between
  deliberately tight parts (hot-loop caps next to the FETs, boot cap next to U1) and silkscreen
  clipping.
* **Checked against TI's TPS552882 datasheet (SLVSFC5, Nov 2020)**: all 26 pins, the RPM0026A
  land pattern (pads match TI's example layout to <0.005 mm), and the FB, FSW, ILIM, EN/UVLO,
  MODE, DITH, VCC and bootstrap values. Two values changed as a result: R9 26.7k -> 22.1k (the
  old limit could fall to ~10.5 A, below the ~11 A needed at 6 V in / 60 W out) and R4 26.1k ->
  28.7k (the old divider could need 6.09 V to start). PG, CC and CDC may float; ISP/ISN tied to
  VOUT is TI's documented way to disable output current limiting.
* **Compensation** (15k + 10 nF + 100 pF) puts crossover at roughly 3-4 kHz, close to the
  datasheet's limit of 1/5 of the boost right-half-plane zero (~11-14 kHz at 6 V in, 5 A). It
  relies on the C20 polymer cap counting toward Cout. If bench tests show ringing in boost mode,
  drop R10 to about 12k.
* **Not yet verified**: there is no simulation and no built prototype.
