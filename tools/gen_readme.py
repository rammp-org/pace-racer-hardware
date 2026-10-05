#!/usr/bin/env python3
"""Regenerate the machine-derived sections of README.md from the KiCad netlist.

    tools/gen_readme.py --netlist pace-core/output/meta/pace-core.net --readme README.md
    tools/gen_readme.py --netlist ... --check      # exit 1 if README is stale (CI)

Sections are delimited by:
    <!-- BEGIN GENERATED: pinmap -->  ...  <!-- END GENERATED: pinmap -->
Anything outside the markers is left untouched.

Local netlist export without KiBot:
    kicad-cli sch export netlist --format kicadsexpr -o /tmp/pace.net pace-core/pace-core.kicad_sch
"""
import argparse, re, sys, pathlib

MCU_REF = 'U1'

def parse_sexpr(s):
    tok = re.findall(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()"]+', s); st = [[]]
    for t in tok:
        if t == '(': st.append([])
        elif t == ')': x = st.pop(); st[-1].append(x)
        else: st[-1].append(t[1:-1] if t.startswith('"') else t)
    return st[0][0]

def find(node, name):
    return [n for n in node if isinstance(n, list) and n and n[0] == name]

def kv(node, key):
    for n in node:
        if isinstance(n, list) and n and n[0] == key: return n[1] if len(n) > 1 else None
    return None

def pin_map(net_root):
    """Return rows (pin_number, pin_name, net_name, other_refs) for the MCU."""
    rows = []
    # pin names from the libpart definition of the MCU
    comp = next(c for c in find(find(net_root, 'components')[0], 'comp') if kv(c, 'ref') == MCU_REF)
    ls = find(comp, 'libsource')[0]; lib, part = kv(ls, 'lib'), kv(ls, 'part')
    lp = next(p for p in find(find(net_root, 'libparts')[0], 'libpart') if kv(p, 'lib') == lib and kv(p, 'part') == part)
    names = {kv(p, 'num'): kv(p, 'name') for p in find(find(lp, 'pins')[0], 'pin')}
    for net in find(find(net_root, 'nets')[0], 'net'):
        name = kv(net, 'name'); nodes = find(net, 'node')
        mine = [n for n in nodes if kv(n, 'ref') == MCU_REF]
        if not mine or name.startswith('unconnected-'): continue
        others = sorted({kv(n, 'ref') for n in nodes if kv(n, 'ref') != MCU_REF})
        for n in mine:
            num = kv(n, 'pin'); rows.append((num, names.get(num, ''), name.split('/')[-1], ', '.join(others)))
    def key(r):
        m = re.search(r'(\d+)', r[1]); return (0, int(m.group(1))) if m else (1, r[1])
    return sorted(rows, key=key)

def render_pinmap(rows):
    out = ['| MCU pin | Net | Connected to |', '| :-- | :-- | :-- |']
    for num, pname, net, others in rows:
        if pname in ('GND', '3V3', 'EPAD') or net in ('GND', '+3V3'): continue
        out.append(f'| {pname} (pin {num}) | `{net}` | {others} |')
    return '\n'.join(out)

def splice(readme, section, body):
    b, e = f'<!-- BEGIN GENERATED: {section} -->', f'<!-- END GENERATED: {section} -->'
    if b not in readme or e not in readme:
        sys.exit(f'README is missing markers for section {section!r}')
    pre, rest = readme.split(b, 1); _, post = rest.split(e, 1)
    return f'{pre}{b}\n{body}\n{e}{post}'

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--netlist', required=True); ap.add_argument('--readme', default='README.md'); ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    net = parse_sexpr(pathlib.Path(a.netlist).read_text())
    readme = pathlib.Path(a.readme).read_text()
    new = splice(readme, 'pinmap', render_pinmap(pin_map(net)))
    if a.check:
        if new != readme: sys.exit('README.md generated sections are stale. Run tools/gen_readme.py and commit.')
        print('README generated sections are current.'); return
    pathlib.Path(a.readme).write_text(new); print('README updated.')

if __name__ == '__main__':
    main()
