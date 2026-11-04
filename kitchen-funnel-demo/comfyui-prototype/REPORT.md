# ComfyUI Photorealization Prototype — Test Report

**Date:** 2026-10-31 · **Tester:** Arlo (subagent) · **Status:** DEMO ONLY — nothing published, sent, or spent ($0, no signups, no paid APIs)
**Input:** SolidCraft block-kitchen render `kitchen-iso-open.png` (L-layout, sink centred on the long run, 30″ range, fridge at the return end, wall cabinets, no island, no window)

## Verdict up front
**BLOCKED on a rented GPU — the approach is not falsified; the local hardware is.**
The full pipeline was installed, licence-verified, and driven end-to-end through the conditioning stage on this VM: the depth and canny control maps generated from the real SolidCraft render are excellent (see §4). But **zero generations completed**: the ComfyUI server process was silently SIGKILLed during model loading or early sampling in **7 out of 7 attempts**, at every configuration tried (fp32/fp16/forced-fp16, dual/single ControlNet, 768→448 px). A co-tenant inference job held 2.0–2.6 GB RSS throughout, and a controlled probe showed a 3.0 GB process is killed on this VM while 2.4 GB survives. SDXL + dual ControlNet needs a ~7 GB working set — it cannot fit here, and SD 1.5's ~2.7–3.1 GB peak sits exactly in the kill zone.
**Recommendation:** run the identical, already-built workflows on a rented 24 GB GPU (≈ $0.30–$1.80 for the whole test — §7). Do not judge the AI path by this VM.

## 1. Resources measured on this VM
| Item | Value |
|---|---|
| vCPUs | 4 (`nproc`) — shared; a co-tenant CPU inference job (SadTalker, another project) ran the entire session |
| RAM | 7.7 GiB total, **no swap** (creating swap is not permitted in this container) |
| Disk | 200 GB, 174 GB free |
| GPU | **none** |
| Gotcha | `/tmp` is a 512 MB tmpfs — the first pip install died with "No space left on device" until `TMPDIR` was pointed at disk |
| Survival probe | anonymous 2.4 GB allocation survived 100 s; 3.0 GB allocation was killed before 150 s |

## 2. Install manifest (all official sources, licences recorded)
| Component | Source | Version / file | Size | Licence (commercial use) | Status |
|---|---|---|---|---|---|
| ComfyUI | github.com/Comfy-Org/ComfyUI | **0.43.0**, commit `7c4390a6f70cd8eb41014d6af52969397a752fc4` (2026-10-31) | — | GPL-3.0 (tool; outputs unaffected) | ✅ installed, API ran headless (`--cpu`) |
| comfyui_controlnet_aux | github.com/Fannovel16/comfyui_controlnet_aux | master @ 2026-10-31 | — | Apache-2.0 | ✅ loaded (only dwpose/pose nodes failed — missing matplotlib; not needed) |
| PyTorch | download.pytorch.org/whl/cpu | 2.15.0+cpu, Python 3.12.3 | — | BSD-style | ✅ |
| SDXL base | HF `stabilityai/stable-diffusion-xl-base-1.0` | `sd_xl_base_1.0.safetensors` | 6,938,078,334 expected / **3,896,069,096 downloaded** | CreativeML OpenRAIL++-M ✅ | ⚠️ partial — download loops were killed in a mass process-kill at ~17:42 UTC; never completed, never loaded |
| ControlNet Union ProMax (SDXL) | HF `xinsir/controlnet-union-sdxl-1.0` | `diffusion_pytorch_model_promax.safetensors` | 2,513,342,408 expected / **1,758,161,378 downloaded** | Apache-2.0 (repo card) ✅ | ⚠️ partial, same cause |
| SD 1.5 base (fp16) | HF `Comfy-Org/stable-diffusion-v1-5-archive` | `v1-5-pruned-emaonly-fp16.safetensors` | **2,132,696,762 ✓ exact** (1,145 tensors verified) | CreativeML OpenRAIL-M ✅ | ✅ complete |
| ControlNet 1.5 depth (fp16) | HF `comfyanonymous/ControlNet-v1-1_fp16_safetensors` | `control_v11f1p_sd15_depth_fp16.safetensors` | **722,601,100 ✓ exact** (340 tensors) | OpenRAIL-M (SD1.5 derivative) ✅ | ✅ complete |
| ControlNet 1.5 canny (fp16) | same repo | `control_v11p_sd15_canny_fp16.safetensors` | **722,601,100 ✓ exact** (340 tensors) | OpenRAIL-M ✅ | ✅ complete |
| Depth Anything V2 Small | HF `depth-anything/Depth-Anything-V2-Small` | `depth_anything_v2_vits.pth` | **99,218,434 ✓ exact** | Apache-2.0 (ViT-S variant) ✅ | ✅ complete (fetched by curl — the HF hub xet downloader hangs through this proxy) |

Licence traps from the research were avoided: no FLUX [dev] / FLUX ControlNets, no Qwen-Image-2.1, no SD 3.5. SDXL-Lightning/LCM accelerators were **not** used (no time to verify their licences to the required standard).
Install lives at `~/workspace/comfyui-lab/` (ComfyUI + venv + models) if a future window re-opens. Note ComfyUI's current `requirements.txt` bundles ~500 MB of workflow-template *media* packages — pure overhead for headless API use.

## 3. Benchmark log — 7 attempts, 0 completions
All attempts: prompt accepted by the API (`queued` + prompt id), then the server died with **no traceback** (SIGKILL signature) at the heavy stage. Co-tenant RSS 2.0–2.6 GB throughout.

| # | Config | Size / steps | ControlNet | Furthest stage reached | Server RSS at last sighting |
|---|---|---|---|---|---|
| 1 | `--cpu` (fp32 default) | 768×720 / 20 | depth+canny (SD1.5) | died at checkpoint load | — (log ends at model load, dtype fp32) |
| 2 | `--cpu --fp16-unet/vae/text-enc` | 768×720 / 20 | depth+canny | **preprocessors done, maps saved**; died in sampling (bar 0/20) | **4.81 GB** |
| 3 | #2 + `--use-split-cross-attention` | 640×600 / 20 | depth+canny | died ~sampling start | — |
| 4 | #3 + `--cache-none` | 512×480 / 20 | depth+canny | died loading 2nd ControlNet | 2.68 GB |
| 5 | #4 flags, server inside tracked session | 512×480 / 20 | depth+canny | died in load phase | — |
| 6 | `--force-fp16`, depth-only | 512×480 / 20 | depth | died after ControlNet load | 3.12 GB |
| 7 | `--force-fp16`, depth-only | 512×480 / 20 → then 448×416 / 16 | depth | died after CLIP load (both sizes) | 2.74 GB |

Other measured timings: server boot 3–4 min; Depth-Anything-V2 + canny preprocessing of the 768×720 input ≈ 2–4 min including model fetch; checkpoint load ≈ 1–2 min. **No sampling step completed inside any surviving window** (longest sampling survival ≈ 5 min at 512×480 without step 1 finishing) — consistent with multi-minute CPU step times on 4 shared vCPUs, but not separately provable because every run was killed.
**SDXL benchmark gate: never reached.** Its two files (9.45 GB combined) were still partial when the download processes were killed, and its working set could not have fit regardless. Per the task's pivot rule, the SD 1.5 tier above *is* the Tier B attempt — it was blocked by the same wall, one stage later than conditioning.

## 4. What DID work — the conditioning stage (real outputs in this folder)
- `input-kitchen-iso-crop.png` — the SolidCraft iso render cropped to the room (790×742).
- `control-depth-from-input.png` — Depth Anything V2 (small) map: clean 3-D structure — fridge reads nearest, wall cabinets and both counter runs in correct perspective, corner depth continuous. This is a strong layout-lock signal.
- `control-canny-from-input.png` — Canny map: crisp line art with the 4 range burners, the sink rectangle, every cabinet outline. Also strong.
These were produced by the actual ComfyUI server on this VM from the actual funnel input (attempt #2), and both maps are saved as workflow inputs so the GPU run skips preprocessing entirely.

## 5. Scoring vs the pre-set pass bars
**Not scoreable — no generated images exist.** For the record, the bars were: (a) L-shape preserved; (b) sink/range/fridge positions preserved; (c) no invented windows/islands/appliances; (d) requested finish honoured; (e) reads as a real kitchen photo at thumbnail size; overall ≥ 80% on finish + layout. The 36-image spec matrix (3 finishes × 4 seeds × SDXL, + 1 photo restyle) was **not run** — scope cut is total for generation, for the measured reason in §3, not for lack of pipeline readiness: workflows for all of it are built and saved (§6).

## 6. Workflows saved (API format, reproducible)
In `workflows/` (builders `build_workflow.py` / `build_wf2.py` + runner `run_wf.py` included):
- `workflow-sdxl-dual-controlnet.json` — **the spec workflow**: SDXL + ControlNet Union (depth 0.8 + canny 0.6), 1024×960, 25 steps, in-graph DAv2 + canny preprocessors. Run this first on a GPU.
- `workflow-sd15-dual-controlnet.json` — same recipe on SD 1.5 (768×720, 20 steps).
- `workflow-sd15-depth-only.json` / `workflow-sd15-canny-only.json` — the single-ControlNet variants actually attempted locally, using the pre-computed maps in this folder as inputs.
- `workflow-sd15-photo-restyle-img2img.json` — homeowner-photo lane: `k-before.jpg` (768×512) img2img, denoise 0.65, depth ControlNet from a depth map of the photo (generate the map on the GPU host with the DAv2 node — it was not produced locally because every server died before a second job could run).
Finishes baked into the builders: (1) white shaker + white quartz + subway tile; (2) navy + butcher block + brass; (3) warm oak + grey marble. Negative prompt explicitly bans islands, windows, extra appliances, and render/cartoon looks.

## 7. The unblock — rented GPU options (researched 2026-10-31, no signup, no spend)
| Option | Card | Published rate | Notes |
|---|---|---|---|
| **RunPod Pod** | RTX A5000 24 GB | **$0.27/hr** | Per-second billing; official ComfyUI pod template exists; + storage ≈ $0.07/GB/mo (network volume). RTX 4090 24 GB is $0.74/hr community / $0.89 secure cloud if more speed is wanted. |
| **Vast.ai** | RTX 4090 24 GB | **≈ $0.33/hr** | Marketplace — price/availability fluctuate (rate seen 2026-10-31). |
| **Modal** (serverless) | L4 24 GB / A10G 24 GB | **≈ $0.80 / $1.10 per hr equiv.** | Per-second, scale-to-zero; Starter tier reported to include $30 free credit — best fit for an API-driven funnel long-term. |

**Cost of the full test on a rental (estimate):** setup + the 36-image SDXL matrix + photo restyle ≈ 1–2 GPU-hours (SDXL + dual ControlNet renders in ~10–30 s/image on a 24 GB card) → **roughly $0.30 (RunPod A5000) to $1.80 (Modal A10G)** all-in. The workflows in §6 run unchanged; expect the whole matrix in under an hour of wall time.

## 8. Bottom line for the funnel
- The **recipe is wired and validated as far as this machine allows**: licence-clean models, exact-byte downloads, API-driven ComfyUI, and control maps that genuinely encode the SolidCraft layout (fridge, sink, range all legible in both maps). Nothing in the evidence suggests the layout-lock approach fails — it was never allowed to generate.
- **Do not** read this as "AI photorealization doesn't work." Read it as: **this shared, GPU-less, memory-capped VM is the wrong computer for it** — the same wall SolidCraft's own path-tracer hit (needs Vulkan GPU) in the earlier prototype.
- Decision for Rafiq: approve ~$1–2 of RunPod/Modal time and the identical test runs to a scored verdict (36 images against the §5 bars) in one short session. If the bars pass there, the funnel's homeowner-facing "inspiration preview" is a per-lead GPU-seconds cost on Modal-style serverless, not a local workload.
