# STEPBACK Single-Doc Rerun — Validation of the Table/Image Rework

Date: 2026-09-14 · Profile: `mistral_glm` · Doc: `STEPBACK` (8 questions) · Agent: `glm_5.3_flash@openrouter` · Judge: `deepSeek-V4.1-Flash@openrouter`

## What was validated

The graph-schema/tool rework (commits `51efc14`, `98d6dd0` in genai-graph; `b3fe994`, `a711fd4` in genai-tk; `8656c7a` in mmlongbench) plus three follow-up fixes made this session:

1. **`config/markdownize.yaml`**: enabled `describe_uncaptioned_images: true` for `mistral_ocr` (the rework's VLM image-description feature shipped default-off, leaving generically-named images unfindable — critical now that Image nodes and image embeddings are gone).
2. **`config/agents.yaml`**: system prompt still listed the removed `search_images` / `search_tables` tools; replaced with the new discipline (TOC-first, tables read inline via `get_section_content`, `query_image` last-resort with sentence-form questions, budget 3) and added `excluded_tools: [grep]`.
3. **Prep fix**: stale STEPBACK run records blocked re-execution (`run_questions_flow` reuses existing records). Filtering must key on top-level `doc_name`, not `doc_id`.

Test setup: STEPBACK-only pathspec; cached markdown (OneDrive + staged), old-schema graph DB, and staged KG dirs deleted so the new conversion/ingestion path actually ran; old records backed up (`runs.pre_stepback2.*.bak`).

## Results (real agent run) vs previous STEPBACK run

| Metric | Previous run | This run | Δ |
|---|---|---|---|
| Strict Accuracy | 75% (6/8) | 75% (6/8) | = |
| Groundedness | 59.6% (3-doc smoke) / 87.5% (regraded old) | 81.2% | mixed |
| Avg Tool Calls / question | 28.5 | **9.75** | −66% |
| Input tokens | 2,747,754 | **744,974** | −73% |
| Output tokens | 265,672 | 157,250 | −41% |
| `grep` calls | 158 (3-doc smoke) | **0** | eliminated |
| Ground-truth file access | yes (grep on questions.jsonl etc.) | **none** | eliminated |
| Recursion-limit halts | 4 (3-doc smoke) | 0 | fixed |

Tool mix (8 questions): `get_section_content` 20 · `search_sections` 15 · `query_image` 11 · `list_documents` 8 · `get_document_toc` 8 · `glob` 6 · `ls` 5 · `read_file` 4 · `get_folder_toc` 1.

## Trace analysis

- **grep exclusion enforced in the harness**: all 8 deep agents logged `excluded 1 built-in tool(s): ['grep']`. File middleware retained; remaining `ls`/`glob`/`read_file` usage was legitimate (SKILL.md reads, workspace markdown paging, image globs). No benchmark ground-truth paths touched.
- **query_image budget enforced**: docqa_0460's 4th attempt was rejected with "Maximum image query limit (3) reached"; effective VLM calls ≤3/question. Questions 0457, 0459, 0456 answered with zero image calls (pure text/table navigation) — the last-resort discipline from the prompt is working.
- **Skills staged in isolated per-question workspaces** (`/tmp/docgraph-ws-*`) — the file-tool surface is bounded to skill docs; no more whole-workspace exposure.
- **Failures (2)** are perception limits, not discipline failures:
  - docqa_0455 (gold 73.2%): VLM read the bar-chart label as 71.8 — chart-text misread.
  - docqa_0460 (gold 5 pie charts): answered 10 — counted sub-charts inside composite figures; the 3-call budget prevents exhaustive visual enumeration (accepted tradeoff).
- **Build path validated end-to-end** on the new schema: OCR reconversion → `process_markdown_tables` → 2 uncaptioned-image VLM descriptions (exactly the 2 images >10 KB; the other 9 are 4–6 KB, below the 10 KB threshold by design) → outline pre-pass (7 LLM calls) → ingest (45 sections, 47 chunks, FTS + 1024-dim chunk embeddings, ~4 s).

## Notes & minor issues

- STEPBACK's "tables" (Table 1–6) are rendered chart images in the PDF; with `table_format: html` Mistral emitted prose + figures instead of the old useless `tbl-N.html` links (29 bare refs → 0). Table conversion is wired but **not exercised** by this doc — needs a table-heavy enterprise doc to truly verify.
- docqa_0461 ran 26 min wall-clock (12 tool calls, 3 VLM queries) — VLM latency dominates; consider a faster VLM for `query_image`.
- Cosmetic: `RuntimeError: Event loop is closed` noise from httpx `aclose()` after the grade flow's loop closes; grading completes fine.
- Process gotcha: `uv run cli bench run` silently reuses existing run records — delete/relocate matching records in `runs.jsonl` to force re-execution. And `uv run` may reinstall editable packages mid-session (observed once).

## VLM A/B (second session): query_image/description VLM switched to Gemini 2.5 Flash

Isolated A/B on the failing docqa_0455 chart (Figure 1, MMLU Physics group, gold 73.2%):

| VLM | native image | 3× upscale |
|---|---|---|
| glm_5.3_flash | 71.2 ✗ (flaky: 71.8 in agent run) | 0.732 ✓ |
| gemini-2.5-flash | 0.729 (closest) | 0.732 ✓ |
| qwen3-vl-32b | 78.4 + scrambled bars ✗ | 73.2 ✓ (other bars confabulated) |

Findings: **image resolution is the dominant failure mode** — all VLMs read correctly once the image is upscaled. Changes made:
1. `genai_tk/extra/markdownize/image_describer.py`: new `upscale_small_image()` — 3× LANCZOS for JPEG/PNG below 2000 px, used by `describe_image_with_vlm`.
2. `genai_graph/kg/query/document_graph_tools.py`: `execute_image_query` now upscales small images before the VLM call; default VLM → `gemini-2.5-flash@openrouter` (fallback `glm_5.3_flash@openrouter`).
3. `MistralOCRConverter.vlm_model` default → `gemini-2.5-flash@openrouter`.

Full-bench rerun with the new VLM: 62.5% (5/8, +1 partial) — within run-to-run noise, **not** an improvement over 75%. docqa_0455 remains incorrect (Gemini estimated 72.1/72.9/73.2 across three reads — the paper prose never states the value and the chart label is borderline-legible; gold comes from chart reading). docqa_0460 (pie counting) hit the recursion limit burning 2.88M tokens (88% of the run) by looping searches against the query_image budget. Verdict: keep Gemini (best-calibrated reader, never hallucinated wildly), treat visual-enumeration and unlabelled-chart questions as expected misses.

### Post-budget loop damping (implemented & validated)

Two changes end the runaway-loop failure mode:
1. **`genai_graph/agent/middleware/wrap_up.py` (new)** — `WrapUpMiddleware` counts tool calls per question: at `soft_limit` (24) it injects a converge-now SystemMessage; at `hard_limit` (32) it strips ALL tools from the model request and forces a plain-text final answer — the run can no longer die at `recursion_limit` without an answer. Wired in `config/agents.yaml`.
2. **Directive budget-rejection message** — `query_image` over-budget now orders: no further image queries or repeated searches; synthesize now.

Validated on the exact pathological question (docqa_0460 rerun): **54 calls / 2.88M in-tokens / recursion crash → 11 calls / 102K in-tokens / clean answer** (−96% tokens). The middleware safety net did not need to fire — the hardened budget message alone triggered convergence. Still graded incorrect (answered 4, gold 5) — visual-enumeration questions remain expected misses.

## Remaining risks

1. Chart data-point reading accuracy (docqa_0455-type failures) — bounded by VLM vision quality; the ≤3 budget caps burn but can't fix misreads.
2. Visual-enumeration questions (count figures) conflict with the 3-call budget — expect misses; acceptable for enterprise-doc usage. Agents may also loop after budget rejection (docqa_0460 burned 2.88M tokens to recursion limit).
3. Table pipeline unverified on a real table-heavy document.
4. Markdown cache invalidation is manual: whenever the converter changes, cached `*.md` in `~/OneDrive/prj/bench/markdown/` must be deleted or the old conversion is reused silently.
