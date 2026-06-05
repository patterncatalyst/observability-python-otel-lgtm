# presentations/

The built slide deck (`.pptx`). A single, current file — no revision number in
the name; git history carries the versions. Committed so it travels with the repo —
they're deliverables, not throwaway build scratch.

The tooling that produces them lives in [`../deck/`](../deck/): `deck.js` (the
slide source), `deck-helpers.js` (the Red Hat design system), `assets/` (cover
and section panels, logos), and `png/` (diagram images rasterized from
`../assets/diagrams/*.svg`).

## Building

Run from inside `deck/` so the relative asset and output paths resolve:

```bash
cd deck
export NODE_PATH=$(npm root -g)
node deck.js          # → ../presentations/otel-lgtm-python.pptx
```

## Adding a second deck

When there's more than one talk (e.g. a workshop cut), copy the source and point
its output here:

```bash
cp deck/deck.js deck/deck-workshop.js
# edit deck-workshop.js: change OUT to "../presentations/otel-lgtm-python-workshop.pptx"
cd deck && node deck-workshop.js
```

Both decks share the same `deck/assets` and `deck/png`, so diagrams and branding
stay consistent across every presentation.

## Current decks

| File | Covers |
|------|--------|
| `otel-lgtm-python.pptx` | The talk deck — Sections 0–9 (31 slides) |
