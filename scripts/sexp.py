"""Tiny S-expression helpers for reading KiCad library files."""
import re

_tok = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+')


def parse(text):
    stack = [[]]
    for m in _tok.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append([])
        elif t == ")":
            done = stack.pop()
            stack[-1].append(done)
        else:
            stack[-1].append(t)
    return stack[0]


def dump(x, ind=0):
    if not isinstance(x, list):
        return x
    if all(not isinstance(e, list) for e in x):
        return "(" + " ".join(x) + ")"
    pad = "\n" + "  " * (ind + 1)
    parts = []
    for e in x:
        parts.append(pad + dump(e, ind + 1) if isinstance(e, list) else " " + e)
    return "(" + "".join(parts).lstrip() + ")"


def find_symbol(lib_path, name):
    tree = parse(open(lib_path).read())[0]
    for e in tree:
        if isinstance(e, list) and e[:2] == ["symbol", f'"{name}"']:
            return e
    raise KeyError(name)
