# Batch 2 Funnel Packs — Manifest

Built 2026-10-31 on the kitchen-funnel chassis. All prices are SAMPLE ranges (demo only) — owner's price book goes in before launch. Lead capture / GHL wiring is a later phase (not built).

| # | Slug | Trade | Default range | Premium range | Hot score | Images | Status |
|---|------|-------|---------------|---------------|-----------|--------|--------|
| 1 | roofing | Roofing | $5,600 – $8,400 | $35,150 – $56,700 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed |
| 2 | flooring | Flooring | $8,000 – $14,000 | $11,600 – $22,000 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed |
| 3 | windows-doors | Windows & Doors | $8,950 – $14,550 | $18,550 – $31,000 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed |
| 4 | deck-porch | Deck & Porch | $8,800 – $14,350 | $20,750 – $31,750 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed |
| 5 | basement-finishing | Basement Finishing | $23,800 – $39,200 | $44,900 – $75,000 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed |
| 6 | gutters | Gutters | $1,450 – $2,500 | $6,200 – $10,550 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed |
| 7 | fence | Fencing | $3,600 – $5,850 | $9,900 – $15,550 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed |
| 8 | pool | Pool Installation | $62,100 – $97,000 | $111,400 – $176,500 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed |
| 9 | landscaping-hardscaping | Landscaping & Hardscaping | $6,000 – $11,000 | $18,000 – $34,500 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed |
| 10 | garage | Garage Makeover | $2,200 – $3,800 | $11,000 – $19,350 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed (size check fixed in QA harness) |
| 11 | power-washing | Power Washing | $450 – $750 | $1,500 – $2,750 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed |
| 12 | full-house-renovation | Full-House Renovation | $72,000 – $144,000 | $278,000 – $529,000 | 95 HOT | 4 generated (before + 3 looks) | DONE — QA passed |
| 13 | addition-adu | Home Addition & ADU | $100,000 – $160,000 | $177,000 – $300,000 | 95 HOT | 4 generated (before + 3 concept looks) | DONE — QA passed |
| 14 | foundation-waterproofing | Foundation & Waterproofing (diagnostic) | $3,600 – $6,100 | $4,200 – $7,200 | 95 HOT | 4 generated (symptom photo + repaired photo + 2 method diagrams) | DONE — QA passed; URGENCY line verified on horizontal-crack/active-water path |
| 15 | hvac-replacement | HVAC Replacement (sizing) | $9,000 – $14,000 | $18,850 – $32,050 | 95 HOT | 4 generated (old unit + new furnace/AC edit + heat-pump + dual-fuel cards) | DONE — QA passed |

## Notes
- All 15 packs: QA run at 390px in headless Chromium — default range displays, premium path moves the range up, size input changes the range, hot path scores 95 / HOT with the design-consult flag shown, both brand skins (Offshore / white-label) render, zero JS errors. QA screenshots in each pack folder (qa-top.png, qa-brief.png, qa-whitelabel-top.png).
- Every pack carries the DEMO ribbon and the ballpark watermark: "SAMPLE RANGES — DEMO ONLY · owner's price book goes here before launch". Lead forms are demo-mode (nothing is sent). Price always comes from structured inputs x sample price rows, never from the preview image; structural choices flag a design consult in the brief instead of being faked in the preview.
- Derivations shown on-page where the brief asked: roofing (footprint x pitch factor -> roofing squares), gutters (footprint -> linear ft), HVAC (sq ft / 500 -> tonnage estimate), windows (large = 1.5x), deck (railing LF on 3 sides).
- Pool brief always carries the permits-vary-by-town row; addition/ADU is consult-by-nature (flag always on) with a zoning/permit row; foundation brief carries an URGENCY row (TOP PRIORITY wording + urgent callback opener for horizontal cracks / active water — verified); power-washing look cards preset the service selects and the pack subtitle notes the small-ticket speed point.
- One QA-harness fix during the run: the size-change check moved to a fresh page (the premium greedy-max pass could pre-set a select-driven size control, e.g. garage 3-car, masking the change). No pack code was at fault.
- packs/index.html (lineup page) intentionally NOT touched — owned by the Batch-1 build.
