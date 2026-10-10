#!/usr/bin/env python3
"""Rebuild generated book content from the commits in chapters.json."""
import html
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'
REPO = 'https://github.com/Giotyp/pie-book'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def read_blobs(commit, names):
    refs = [commit + ':' + name for name in names]
    data = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=ROOT,
                                   input=('\n'.join(refs) + '\n').encode())
    position = 0
    for name in names:
        end = data.index(b'\n', position)
        header = data[position:end].split()
        if len(header) != 3 or header[1] != b'blob':
            raise ValueError(f'Not a source blob: {commit}:{name}')
        size = int(header[2])
        position = end + 1
        yield name, data[position:position + size]
        position += size + 1


def resolve(label, files, aliases):
    if label in aliases:
        return aliases[label]
    if label in files:
        return label
    matches = [p for p in files if p.endswith('/' + label)]
    if len(matches) == 1:
        return matches[0]
    children = [p for p in files if p.startswith(label.rstrip('/') + '/')]
    if children:
        for suffix in ('/src/main.rs', '/src/lib.rs', '/__init__.py'):
            target = label.rstrip('/') + suffix
            if target in children:
                return target
        return sorted(children)[0]
    return None


def link_sources(text, chapter, files):
    """Only rewrite inline code outside fenced blocks; retain symbols as code."""
    fenced = False
    output = []
    references = []
    for line in text.splitlines():
        if line.lstrip().startswith(('```', '~~~')):
            fenced = not fenced
        if not fenced and not line.lstrip().startswith(('```', '~~~')):
            def replace(match):
                label = match.group(1)
                target = resolve(label, files, chapter['aliases'])
                if not target:
                    return match.group(0)
                references.append({'label': label, 'path': target})
                url = '../assets/source/' + chapter['slug'] + '/' + quote(target) + '.txt'
                return (f'<a class="source-link" href="{url}" '
                        f'data-source="{html.escape(target, quote=True)}">'
                        f'<code>{html.escape(label)}</code></a>')
            line = re.sub(r'`([^`\n]+)`', replace, line)
        output.append(line)
    return '\n'.join(output) + '\n', references


def main():
    manifest = json.loads((ROOT / 'chapters.json').read_text())
    chapters = manifest['chapters']
    if [c['number'] for c in chapters] != list(range(1, len(chapters) + 1)):
        raise ValueError('Chapter numbers must be consecutive and ordered')
    for directory in ('chapters', 'assets/source', 'assets/catalog'):
        (DOCS / directory).mkdir(parents=True, exist_ok=True)
    intro = git('show', manifest['introduction_commit'] + ':README.md').decode()
    for c in chapters:
        intro = intro.replace('../../tree/' + c['branch'] + ')', 'chapters/' + c['slug'] + '.md)')
    intro += ('\n## Reading this book\n\n'
              'Follow the chapters in order. Each chapter describes a separate, pinned Git commit. '
              'Click a source filename to read that version in the source panel; on a small screen, '
              'the panel opens over the chapter. Directory links open an entry file, and the file '
              'selector lets you browse the rest of that chapter.\n\n'
              'To run a chapter, clone this repository and check out the commit shown on its page. '
              'The chapter commands require Rust and the `wasm32-wasip2` target; the macOS examples '
              'use Metal and download model weights. Source files are reading examples, not '
              'standalone Rust Playground programs.\n\n'
              'Descriptions of missing reference features refer to the tutorial stage where they '
              'appear; later chapters may add them. The current Pie implementation may have evolved '
              'beyond these tutorial snapshots.\n')
    (DOCS / 'introduction.md').write_text(intro)
    parts = {1: 'Inferlets and KV memory', 6: 'Generation techniques and conversations',
             12: 'Serving and execution performance', 15: 'Reference architecture and runtime services',
             24: 'GPU execution and advanced capabilities'}
    summary = ['# Summary', '', '[Introduction](introduction.md)', '']
    for c in chapters:
        if c['number'] in parts:
            summary += ['# ' + parts[c['number']], '']
        summary.append(f"- [{c['title']}](chapters/{c['slug']}.md)")
        names = git('ls-tree', '-r', '--name-only', c['commit']).decode().splitlines()
        files = {}
        names = [p for p in names if p != 'README.md' and not p.endswith('Cargo.lock')]
        for path, data in read_blobs(c['commit'], names):
            try:
                content = data.decode('utf-8')
            except UnicodeDecodeError:
                continue
            if '\x00' in content:
                continue
            files[path] = content
            dest = DOCS / 'assets/source' / c['slug'] / (path + '.txt')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content)
        for alias, target in c['aliases'].items():
            if target not in files:
                raise ValueError(f"Invalid alias {c['slug']}: {alias} -> {target}")
        text = git('show', c['commit'] + ':README.md').decode()
        text = re.sub(r'^# Chapter #\d+:', '#', text, count=1)
        text, references = link_sources(text, c, files)
        metadata = (f"\n> Source: [{c['branch']}]({REPO}/tree/{c['commit']}) · "
                    f"Commit: `{c['commit'][:12]}`\n\n"
                    f"```bash\ngit checkout {c['commit']}\n```\n\n"
                    f'<span class="source-catalog" data-catalog="../assets/catalog/{c["slug"]}.json"></span>\n')
        heading, rest = text.split('\n', 1)
        (DOCS / 'chapters' / (c['slug'] + '.md')).write_text(heading + '\n' + metadata + rest)
        catalog = dict(chapter=c['title'], commit=c['commit'], slug=c['slug'],
                       repository=REPO, files=sorted(files), references=references)
        (DOCS / 'assets/catalog' / (c['slug'] + '.json')).write_text(json.dumps(catalog, indent=2) + '\n')
    (DOCS / 'SUMMARY.md').write_text('\n'.join(summary) + '\n')
    print(f'Imported {len(chapters)} chapters and introduction')


if __name__ == '__main__':
    main()
