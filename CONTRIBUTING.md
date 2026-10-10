# Maintaining the Pie book

The `mdbook` branch assembles the book. Tutorial branch READMEs remain the
narrative source; `chapters.json` pins the introduction and each chapter to a
commit. The generated `docs/` content and `book/` output are ignored by Git.

Install mdBook 0.5.4, then run from the repository root:

```sh
git fetch origin
python3 scripts/import-book.py
python3 scripts/validate-book.py
mdbook build
mdbook serve --open
```

To update a chapter, edit its tutorial branch README/code, fetch the new
commit, and update `commit` in `chapters.json`. Keep `number` and `slug` stable
so published URLs survive updates. Add an `aliases` entry when an inline file
reference is ambiguous, mapping the text in backticks to a complete source
path. The importer resolves exact paths, unique suffixes, and directory entry
files. Symbols remain inline code. All tracked UTF-8 source files except the
README and Cargo.lock are exported per chapter and available in the viewer's
file selector. Git commits must be available locally; CI fetches full history.

The chapter 15 layout illustration is a fenced block and is preserved. Add
explicit source links in its branch README if a guided read order is desired.
Future line-range annotations and draggable panel sizing are enhancements;
the initial reader uses a fixed desktop width and full-screen mobile drawer.

The introduction is generated from the pinned main README. Book-specific
reading guidance and link conversion live in `scripts/import-book.py`.
Do not hand-edit generated pages or source snapshots. The raw `.txt` links
remain usable when JavaScript is disabled.

## GitHub Pages

In repository Settings → Pages, select **GitHub Actions** as the build source.
Allow `mdbook` in the `github-pages` environment's deployment branch rules.
Push this branch to run the build and deploy workflow. Pull requests build
and validate the book and upload a preview artifact without deploying.
The expected project URL is https://giotyp.github.io/pie-book/.

The workflow pins mdBook 0.5.4. Update the local and CI versions together.
