"""Reload the saved board, fill zones, save, and write a DRC report.
Usage: /usr/bin/python3 scripts/fill_drc.py [report.txt]"""
import os, sys, re
import pcbnew
HERE = os.path.dirname(os.path.abspath(__file__))
pcb = os.path.join(HERE, "..", "frc-poe-buckboost.kicad_pcb")
b = pcbnew.LoadBoard(pcb)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(pcb)
rep = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "drc.rpt")
pcbnew.WriteDRCReport(b, rep, pcbnew.EDA_UNITS_MILLIMETRES, True)
t = open(rep).read()
print(re.findall(r"\*\* Found \d+ [^*]*", t))
