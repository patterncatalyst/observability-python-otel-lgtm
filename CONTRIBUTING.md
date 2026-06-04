# Contributing

Thanks for your interest. This repo is a teaching artifact — a talk plus a
companion tutorial — so contributions are weighed against whether they keep the
four deliverables (site, deck, demo app, stack) coherent and in sync.

## Ground rules

- **One source of truth for diagrams.** Never hand-edit an SVG or a deck PNG.
  Edit `scripts/diagrams.py`, then regenerate:
  ```bash
  python scripts/diagrams.py
  bash scripts/render_pngs.sh
  ```
  The `.excalidraw` files are the editable source; the `.svg` and `.png` are
  build outputs.

- **The site chapter and the example stay in lockstep.** If you change a
  chapter under `_docs/`, update its sibling under `examples/NN-*/` (and the
  example's `README.md`) so the prose and the runnable code never drift.

- **Honesty about verification.** Anything not actually executed end-to-end is
  marked `unverified` in its front matter and in the reconciliation plan. Don't
  promote something to `verified` you haven't run. If you *do* run a demo
  successfully, update [`_plans/reconciliation-plan.md`](_plans/reconciliation-plan.md).

- **Pin versions deliberately.** New dependencies go in `app/pyproject.toml`
  with an explicit version, and into the versions-to-pin table in the
  reconciliation plan.

## Local checks before a PR

```bash
# Python sources compile
python -m compileall app/app

# Shell drivers parse
for f in $(find examples scripts -name '*.sh'); do bash -n "$f"; done

# YAML is well-formed
python -c "import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob('stack/**/*.yaml', recursive=True)]"

# Diagrams regenerate cleanly
python scripts/diagrams.py
```

## Iteration model

Work lands in numbered iterations (r0.1, r1.0, r2.0, …) tracked in
[`_plans/iteration-plan.md`](_plans/iteration-plan.md). If you're adding a whole
new chapter + demo, align it to a planned iteration rather than scattering it.
