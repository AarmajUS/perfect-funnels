# SolidCraft Prototype Test — One Sample Kitchen
**Date:** 2026-10-31 · **Tester:** Arlo (subagent) · **Status:** DEMO ONLY — nothing published, sent, or spent ($0, no paid APIs, no LLM calls; the tool was driven by scripted JSON commands only)

## Verdict up front
**(a) Usable now as a back-office HOT-lead design-consult layer** — with a narrow, honest scope: after a lead comes in, an agent builds a to-scale block model like this one in seconds, and the contractor's brief gets (1) verified quantities for the price book and (2) a clean plan view + 3D view of the proposed layout. It is **not** ready to be the homeowner-facing live configurator (no finishes/photoreal look, version churn) — that stays with the photo-restyle funnel front end, exactly as the doctrine already has it.

## 1. Install route + version (what actually worked)
- **Tool:** SolidCraft **v0.28.0** (released 2026-10-31), repo `tangency-labs/solidcraft` (the reel's `bherbruck/solvecraft`; renamed SolveCraft → SolidCraft at v0.6). Licence MIT OR Apache-2.0.
- **Route:** prebuilt release tarball `solidcraft-0.28.0-linux-x86_64.tar.gz` (~100 MB) from GitHub Releases → extracted → `bin/solidcraft-cli`. No Rust toolchain needed (none on this VM), no source build.
- **Headless on this VM:** CLI works fully. `solidcraft-cli gpu` → **no GPU adapter; falls back to the CPU rasterizer** for snapshots (warning issued, images still produced). The photoreal path-tracer (`render`) is **blocked here**: `HostUnavailable: the GPU path tracer requires a Vulkan driver… no Vulkan or Metal adapter satisfies SOLIDCRAFT_GPU=auto`.
- **Sanity test first:** the project's own `examples/bracket.json` built in ~2 s → STEP + native `.sc` + an 800×600 snapshot PNG. Then the kitchen.
- **MCP path also proven live:** a small Python JSON-RPC driver (saved as `mcp-drive-example.py`) started `solidcraft-cli mcp --headless --in kitchen.sc`, initialized (server "SolidCraft 0.28.0"), called `measure` (totals identical to the CLI's) and `screenshot` (wrote `kitchen-top-mcp.png`). No LLM was involved.
- **Docs-drift note:** the online MCP docs describe a `summary` argument for `measure`; the 0.28.0 server rejects it (`unknown argument 'summary'; its arguments are: body, items`). Trust the binary, not the docs.

## 2. What was built
One JSON command script (25 commands, saved as `kitchen-commands.json`) of `solid.box` / `solid.cylinder` primitives — **unit system: millimetres internally** (SolidCraft native), specified in inches (1 in = 25.4 mm). Origin at the room's SW interior corner; X east along the 12-ft wall, Y north, Z up.

**Layout (L-shape):** base cabinets run the full 12-ft south wall — 54 in cabinet, 36 in sink base, 30 in range, 24 in cabinet — and return 60 in up the west wall (the 24×24 in corner belongs to the south run and is counted once). Fridge (36 wide × 30 deep × 70 high) closes the return at the north end. No doorway was needed (east side is open). Only the two L walls are modelled, so the model stays readable; ceiling height 8 ft.

| Body | Size (in) | Position / notes |
|---|---|---|
| Floor | 144 × 120 × 2 | top at Z 0; driven by parameters `room_x` / `room_y` |
| Wall_South / Wall_West | 144 / 120 long × 6 thick × 96 high | driven by `room_x` / `room_y` / `ceiling_h` |
| Base_South_West | 54 × 24 × 34.5 | south run, west segment |
| Base_Sink | 36 × 24 × 34.5 | sink centre at X = 72 in = **centre of the 144 in wall run** |
| Base_South_East | 24 × 24 × 34.5 | east of the range |
| Base_Return | 24 × 60 × 34.5 | west-wall return, north of the corner |
| Countertops (4 bodies) | 25 deep × 1.5 thick, top at 36 in | corner + south (with sink cutout) + south-east + return segments, no overlaps |
| Sink_Basin | 30 × 16 × 9 | top flush with counter at 36 in; opening boolean-cut into Counter_South first |
| Range | 30 × 25 × 36 | + 4 burner cylinders (6 in / 4.5 in dia) on top |
| Fridge | 30 deep × 36 wide × 70 high | end of return run |
| Wall cabinets (3 bodies) | 12 deep × 30 high, bottom at 54 in | 54 in south-west, 24 in south-east, 60 in return; none over sink or range |

**Parametric proof:** re-running the saved design with `room_x` changed 3657.6 → 4267.2 mm rebuilt Floor and Wall_South to exactly **168.00 in** (measured). Room size is a parameter, not a redraw.

## 3. Tool-extracted vs hand-calculated quantities
Measurements from SolidCraft itself (`solidcraft-cli eval` on the saved design → `kitchen-measure.json`; 21 bodies, all closed solids). **Every bounding box matched the spec to 0.01 in.**

| Quantity | Hand calc (from spec) | Tool-extracted | Match |
|---|---|---|---|
| Room footprint | 12 ft × 10 ft = **120 sq ft** | Floor bbox 144.00 × 120.00 in | ✅ exact |
| Base cabinet run | south 54+36+24 = 114 in; return 60 in | bboxes 54 / 36 / 24 / 60 in | ✅ exact |
| Countertop, gross | segments 600+1625+600+1500 = **4325 in² = 30.03 sq ft** | segment bboxes 25×24, 65×25, 24×25, 25×60 in | ✅ exact |
| Countertop, net of sink cut | 4325 − (30×16) = **3845 in² = 26.70 sq ft** | Counter_South volume 0.994 ft³ ÷ 1.5 in thick = **1145 in²** = 1625 − 480; it also gained faces 6 → 10 (the cut) | ✅ exact |
| Ceiling height | 96 in | wall bbox dz 96.00 in | ✅ exact |
| Sink position | centre X = 72 in | basin bbox X 57–87 in → centre 72 in | ✅ exact |
| Range / fridge | 30 in / 36 in wide | bboxes 30.00 / 36.00 in (fridge 70.00 high) | ✅ exact |

**Funnel quantities a price book needs (derived per-body, as a brief would carry):**
- **Base cabinets: 14.5 linear ft** (9.5 ft south + 5 ft return; corner counted once)
- **Wall cabinets: 11.5 linear ft** (54 + 24 + 60 in) → **26 linear ft of cabinets total**
- **Countertop: 30.0 sq ft gross / 26.7 sq ft net** of the sink cutout (state which one the owner's book bills — most bill gross)
- **Appliances/fixtures: 2 appliances** (30 in range, 36 in fridge) **+ 1 sink** (30×16, centred on the long run)
- **Placement list:** L-layout; sink centred on 12-ft run; range between sink base and east cabinet; fridge at return end; wall cabinets over west + east base segments and the return, none over sink/range.
- ⚠️ Derive quantities **per body, never from the design total volume** — bodies can sit inside each other (the basin lives inside the sink-base cabinet's volume), so the grand total double-counts overlaps. Per-body numbers above are exact.

## 4. Screenshots — quality judgement for a contractor brief
All rendered headless on this VM by the tool itself (CPU rasterizer, ~2 s each):
- `kitchen-top.png` — **plan view: genuinely brief-grade.** Reads like a floor plan: L runs, sink, range with 4 burners, fridge, wall-cabinet outlines. A contractor can verify the layout at a glance.
- `kitchen-iso-open.png` — **3D view: brief-grade after camera craft.** Custom camera from the open NE side + walls set to 12% opacity + per-body colours (navy cabinets, cream counters, grey appliances). Layout, proportions and placements are unambiguous. It is a clean technical block rendering — **not** a homeowner "wow" image and not photoreal (and the path-traced render needs a GPU this VM doesn't have).
- `kitchen-iso.png` — the naive default iso: walls hide the kitchen entirely. Lesson banked: default views are useless for rooms; the ghost-wall + inside camera recipe above is the standard shot.
- Colours are flat per-body tints set at snapshot time (the design file itself carries no finishes).

## 5. Effort / time
- Download + extract: ~2 min (100 MB at ~1.2 MB/s). Bracket sanity build: ~2 s. Kitchen script authoring: ~10 min. Kitchen build: **0.2 s wall clock (21.8 ms of model time)** for all 25 commands. Measure: instant. Each snapshot: ~2 s. MCP session incl. screenshot: ~1.6 s. Total agent time end-to-end incl. research and this report: **~35 min**. Rebuilding a *variant* kitchen from this template (new room size, moved appliances) is a minutes-level edit of one JSON file, not a new build.

## 6. Hard limitations for room/kitchen work (vs mechanical parts)
1. **Blocks, not cabinetry.** Cabinets are solid boxes: no doors, frames, toe-kicks, fillers, handles, or interiors unless each is modelled as more boxes. Fine for layout + quantities; not a shop drawing.
2. **No architectural vocabulary.** Walls are boxes; windows/doors/openings need manual boolean cuts; no plumbing, electrical, clearances, or code checks. Nothing validates that a layout is buildable — the contractor still does that on the site visit (which the funnel already promises).
3. **No finishes or photorealism here.** Flat snapshot colours only on this VM; the photoreal renderer requires a Vulkan GPU. Homeowner-facing beauty shots still belong to the AI photo-restyle step.
4. **Young, fast-moving project.** First commit Oct 2026; v0.28.0 writes design **format 45** (v0.27 wrote 44) — old designs open in new versions, but any production use must **pin one version** and re-test on upgrades. Docs already drift from the binary (see the `measure` argument above).
5. **Overlap blindness.** The kernel happily lets bodies intersect (basin inside cabinet). Totals must be read per body — see §3 warning.
6. **mm-native.** Inches work as expressions (`"54 in"`-style values and parameters), but every report out of the tool is mm and needs converting for a US contractor brief (done in the table above).

## 7. Files in this folder
- `kitchen.sc` — native SolidCraft design (format 45, opens in v0.28.0)
- `kitchen.json` — same design as plain JSON (parameters + timeline)
- `kitchen.step` / `kitchen.stl` — exports (STEP header verified; STL 4,416 triangles)
- `kitchen-commands.json` — the 25-command build script (replayable: `solidcraft-cli run kitchen-commands.json`)
- `kitchen-measure.json` — full tool measurement dump (per-body volume / bbox / topology)
- `kitchen-iso-open.png` (hero 3D), `kitchen-top.png` (plan), `kitchen-iso.png` (default view, kept as evidence), `kitchen-top-mcp.png` (same plan via the MCP server)
- `mcp-drive-example.py` — the JSON-RPC driver that proved the MCP path with no LLM

**Bottom line for the funnel:** the pattern from the house-planner reel + this CAD layer combine cleanly — photo restyle sells the dream up front, and for HOT leads this produces a dimensioned layout + verified quantities (cabinet lin ft, counter sq ft, placements) behind the ballpark, feeding the owner's price book exactly the structured inputs the doctrine requires. Recommended next step (on Rafiq's go, not done here): template 2–3 standard layouts (L, U, galley) as parameterised scripts so a new lead's model is a form-fill, and pin v0.28.0.
