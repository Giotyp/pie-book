# Maintaining the Pie book

The `mdbook` branch assembles the book. Tutorial branch READMEs remain the
narrative source; `chapters.json` pins each chapter to a commit and holds its
contents-page description and recommended-reading flag. The generated `docs/`
content and `book/` output are ignored by Git.

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

The introduction uses the maintained `templates/introduction.md` template.
Edit its opening, recommended path, and reading guidance there. The importer
fills its chapter index from `chapters.json`; section headings are shared with
the sidebar in `scripts/import-book.py`. Contents-page styling lives in
`theme/contents.css`. Keep the recommended path consistent with the manifest
flags when changing recommendations.
Do not hand-edit generated pages or source snapshots. The raw `.txt` links
remain usable when JavaScript is disabled.

The standalone **Inspecting an Inferlet** chapter is maintained in
`templates/inspecting-an-inferlet.md`. Its manifest entry specifies a
`source_dir` of checked-in reference files, their upstream repository and
commit, and SHA-256 checksums. This lets CI build without a sibling Pie
checkout. To update it, copy the listed files from a clean checkout of the
new upstream commit and update the commit and checksums together.
`templates/inspecting-an-inferlet.json` defines inclusive source line ranges
for each `{{compare:name}}` block. The importer renders Rust, Python, and
JavaScript columns from those files, omits whole comment lines, and removes common
indentation. Update
the ranges and explanations when changing the sources, then inspect the
rendered chapter. Complete files remain available in the source panel.
Comparison styling lives in `theme/inspection.css` and stacks on mobile.

## GitHub Pages

In repository Settings → Pages, select **GitHub Actions** as the build source.
Allow `mdbook` in the `github-pages` environment's deployment branch rules.
Push this branch to run the build and deploy workflow. Pull requests build
and validate the book and upload a preview artifact without deploying.
The expected project URL is https://giotyp.github.io/pie-book/.

The workflow pins mdBook 0.5.4. Update the local and CI versions together.
