# presentations/

Built slide decks (`.pptx`), one file per talk or cut. These are **committed** —
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
node deck.js          # → ../presentations/otel-lgtm-python-r01.0.pptx
```

## Adding a second deck

When there's more than one talk (e.g. a workshop cut), copy the source and point
its output here:

```bash
cp deck/deck.js deck/deck-workshop.js
# edit deck-workshop.js: change OUT to "../presentations/otel-lgtm-python-workshop-r01.0.pptx"
cd deck && node deck-workshop.js
```

Both decks share the same `deck/assets` and `deck/png`, so diagrams and branding
stay consistent across every presentation.

## Current decks

| File | Covers |
|------|--------|
| `otel-lgtm-python-r01.0.pptx` | Foundations — Sections 0–3 (20 slides) |
