"""Reload the saved board, fill zones, save, and write a DRC report.
Usage: <kicad-python> scripts/fill_drc.py [report.txt]

DRC runs through kicad-cli: pcbnew.WriteDRCReport() segfaults in a standalone
script on KiCad 10 (its library-parity test needs a GUI-loaded project)."""
import os, sys, re, shutil, subprocess
import pcbnew
HERE = os.path.dirname(os.path.abspath(__file__))
pcb = os.path.abspath(os.path.join(HERE, "..", "frc-poe-buckboost.kicad_pcb"))
b = pcbnew.LoadBoard(pcb)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(pcb)
rep = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "drc.rpt"))
cli = shutil.which("kicad-cli") or "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
subprocess.run([cli, "pcb", "drc", "--severity-all", "-o", rep, pcb], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(re.findall(r"\*\* Found \d+ [^*]*", open(rep).read()))
