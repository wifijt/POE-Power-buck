"""Compare a KiCad netlist export against design.py. Usage: check_netlist.py file.net"""
import re, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
import design
t = open(sys.argv[1]).read()
got = {}
for blk in t.split("(net (code")[1:]:
    name = re.search(r'\(name "([^"]*)"', blk).group(1).lstrip("/")
    for ref, pin in re.findall(r'\(node \(ref "([^"]*)"\) \(pin "([^"]*)"', blk):
        got[(ref, pin)] = name
want = {(r, p): n for n, nodes in design.nets().items() for r, p in nodes}
bad = 0
for k, n in want.items():
    g = got.get(k)
    if g != n:
        print("MISMATCH", k, "want", n, "got", g); bad += 1
for k, g in got.items():
    if k not in want and not g.startswith("unconnected"):
        print("EXTRA", k, g); bad += 1
print("netlist check:", "OK" if not bad else f"{bad} problems", f"({len(want)} pin-net pairs)")
sys.exit(1 if bad else 0)
