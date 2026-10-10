#!/usr/bin/env python3
"""Check imported chapter order, snapshot identity, and local source targets."""
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

root = Path(__file__).resolve().parent.parent
manifest = json.loads((root / 'chapters.json').read_text())
summary = (root / 'docs/SUMMARY.md').read_text()
expected = [f"chapters/{c['slug']}.md" for c in manifest['chapters']]
actual = re.findall(r'^- \[[^\]]+\]\(([^)]+)\)', summary, re.M)
assert actual == expected, 'Summary chapter order differs from manifest'
count = 0
snapshots = []
for chapter in manifest['chapters']:
    page = root / 'docs/chapters' / (chapter['slug'] + '.md')
    text = page.read_text()
    catalog = json.loads((root / 'docs/assets/catalog' / (chapter['slug'] + '.json')).read_text())
    assert catalog['commit'] == chapter['commit']
    for file in catalog['files']:
        snapshot = root / 'docs/assets/source' / chapter['slug'] / (file + '.txt')
        snapshots.append((chapter['commit'] + ':' + file, snapshot))
    for href in re.findall(r'class="source-link" href="([^"]+)"', text):
        assert (page.parent / unquote(href)).is_file(), f'Missing source target: {href}'
        count += 1
    assert catalog['references'] or chapter['number'] == 15, f'No source links: {page}'
for link in re.findall(r'\]\((chapters/[^)]+)\)', (root / 'docs/introduction.md').read_text()):
    assert (root / 'docs' / link).is_file(), f'Missing intro target: {link}'
print(f"Validated {len(expected)} chapters, exact source snapshots, and {count} source links")

# Read all pinned Git blobs in one process rather than spawning per file.
blobs = subprocess.check_output(['git', 'cat-file', '--batch'],
    input=('\n'.join(ref for ref, _ in snapshots) + '\n').encode(), cwd=root)
position = 0
for ref, snapshot in snapshots:
    end = blobs.index(b'\n', position)
    header = blobs[position:end].split()
    assert len(header) == 3 and header[1] == b'blob', f'Missing Git blob: {ref}'
    size = int(header[2])
    position = end + 1
    assert snapshot.read_bytes() == blobs[position:position + size], f'Snapshot mismatch: {snapshot}'
    position += size + 1
print(f'Verified {len(snapshots)} source files against their pinned Git blobs')
