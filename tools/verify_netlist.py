#!/usr/bin/env python3
"""Compare two KiCad XML netlists (kicad-cli sch export netlist --format kicadxml)
and report any difference in connectivity, ignoring net *names*.

Usage: tools/verify_netlist.py before.xml after.xml

Each net is reduced to its frozenset of (ref, pin) nodes; the two netlists
must contain exactly the same set of node-sets. Exit code 1 on mismatch.
"""
import sys, xml.etree.ElementTree as ET

def nodes(path):
    r = ET.parse(path).getroot()
    out = {}
    for n in r.find('nets'):
        key = frozenset((x.get('ref'), x.get('pin')) for x in n)
        out[key] = n.get('name')
    return out

a, b = nodes(sys.argv[1]), nodes(sys.argv[2])
only_a = [a[k] for k in a if k not in b]
only_b = [b[k] for k in b if k not in a]
if only_a or only_b:
    print('CONNECTIVITY CHANGED'); print(' nets only in before:', only_a); print(' nets only in after: ', only_b); sys.exit(1)
renamed = [(a[k], b[k]) for k in a if a[k] != b[k]]
print(f'OK: {len(a)} nets, identical connectivity. {len(renamed)} renamed:')
for o, n in sorted(renamed): print(f'  {o:44} -> {n}')
