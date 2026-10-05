#!/usr/bin/env python3
"""Rename nets/labels across a KiCad project from a JSON mapping.

Usage: tools/rename_nets.py <project_dir> <map.json> [--dry-run]

Touches, in place:
  *.kicad_sch  label / global_label / hierarchical_label / sheet pin names,
               bus-member labels (bus.member), group-bus labels ({a, b}),
               netclass directive "Net Class" properties, and free text notes.
  *.kicad_pcb  (net "...") and (net_name "...") references, including
               hierarchical "/Sheet/name" forms.
  *.kicad_pro  bus alias members and net class patterns.

Matching is whole-token: a name is only replaced when the characters either
side are not part of a net-name token ([A-Za-z0-9_+-]). Embedded image data
blocks are skipped. Connectivity must be verified afterwards with
tools/verify_netlist.py.
"""
import json, re, sys, pathlib

TOKEN = r'[A-Za-z0-9_+\-]'

def build_regex(mapping):
    keys = sorted(mapping, key=len, reverse=True)
    alt = '|'.join(re.escape(k) for k in keys)
    return re.compile(rf'(?<!{TOKEN})({alt})(?!{TOKEN})')

# Only rename inside these s-expression heads in schematics.
SCH_HEADS = ('label', 'global_label', 'hierarchical_label', 'pin', 'text', 'netclass_flag')
PCB_HEADS = ('net', 'net_name')

def rename_quoted_in_context(text, rx, mapping, heads):
    """Replace inside quoted strings that directly follow one of `heads`.
    Skips (data "...") image blocks."""
    out, changed = [], 0
    pos = 0
    pattern = re.compile(r'\((' + '|'.join(heads) + r')\s+"((?:[^"\\]|\\.)*)"')
    for m in pattern.finditer(text):
        head, val = m.group(1), m.group(2)
        new = rx.sub(lambda mm: mapping[mm.group(1)], val)
        if new != val:
            changed += 1
            out.append(text[pos:m.start(2)]); out.append(new); pos = m.end(2)
    out.append(text[pos:])
    return ''.join(out), changed

def rename_property(text, rx, mapping, prop_name):
    pat = re.compile(r'\(property\s+"' + re.escape(prop_name) + r'"\s+"((?:[^"\\]|\\.)*)"')
    changed = 0
    def sub(m):
        nonlocal changed
        new = rx.sub(lambda mm: mapping[mm.group(1)], m.group(1))
        if new != m.group(1): changed += 1
        return m.group(0)[:m.start(1)-m.start(0)] + new + '"'
    return pat.sub(sub, text), changed

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    proj = pathlib.Path(args[0]); mapping = json.load(open(args[1]))
    mapping = {k: v for k, v in mapping.items() if not k.startswith('_')}
    rx = build_regex(mapping)
    report = {}
    for f in sorted(proj.glob('*.kicad_sch')):
        t = f.read_text()
        t2, c1 = rename_quoted_in_context(t, rx, mapping, SCH_HEADS)
        t2, c2 = rename_property(t2, rx, mapping, 'Net Class')
        report[f.name] = c1 + c2
        if not dry and t2 != t: f.write_text(t2)
    for f in sorted(proj.glob('*.kicad_pcb')):
        t = f.read_text()
        t2, c = rename_quoted_in_context(t, rx, mapping, PCB_HEADS)
        report[f.name] = c
        if not dry and t2 != t: f.write_text(t2)
    for f in sorted(proj.glob('*.kicad_pro')):
        p = json.loads(f.read_text()); c = 0
        ba = p.get('schematic', {}).get('bus_aliases', {})
        for k, members in ba.items():
            new = [mapping.get(m, m) for m in members]
            c += sum(a != b for a, b in zip(members, new)); ba[k] = new
        for pat in p.get('net_settings', {}).get('netclass_patterns', []):
            new = rx.sub(lambda mm: mapping[mm.group(1)], pat['pattern'])
            c += new != pat['pattern']; pat['pattern'] = new
        report[f.name] = c
        if not dry: f.write_text(json.dumps(p, indent=2) + '\n')
    for k, v in report.items(): print(f'{k:36} {v} replacements')
    if dry: print('(dry run, nothing written)')

if __name__ == '__main__':
    main()
