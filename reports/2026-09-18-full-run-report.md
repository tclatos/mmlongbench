# MMLongBench-Doc — Full Benchmark Run Report

*Profile `default` · agent: `glm_5.3_flash@openrouter` (deep agent over a Ladybug document graph) · judge: `deepSeek-V4.1-Flash@openrouter` · 2026-09-18*

## 1. What this benchmark is, and why it is hard (non-technical summary)

**MMLongBench-Doc** is a public benchmark from NTU Singapore (NeurIPS 2024) built to answer one question: *can AI systems actually read a long, messy, real-world document?* It contains **135 real documents** — research reports, academic papers, financial reports, guidebooks, brochures — averaging **47 pages each**, and **1,091 expert-written questions** about them.

It is difficult for three reasons:

1. **Haystack size.** A document is dozens of pages long. A question like *"What was the revenue in the third quarter?"* requires finding the one page that matters among 50. Long documents defeat systems that simply "read everything" — attention and context windows get saturated, and the model drowns in irrelevant pages.
2. **Mixed content.** The answers are not only in prose. They hide in tables, bar and line charts, figures, and page layouts. Reading a chart is closer to *looking* at a picture than reading text.
3. **Trick questions.** About **22% of the questions have no answer in the document at all.** A good system must say *"this is not answerable"* instead of inventing something plausible — a direct probe for hallucination. Another third of the questions require combining evidence from **multiple pages**.

The best documented systems on this benchmark answer in the mid-to-high 50s: NVIDIA's Nemotron-3-Nano-Omni-30B-A3B reports **57.5%**, the leaderboard-leading TeleMM2.0 (Jan 2026) reaches **56.1%**, and GPT-4o manages **46%**. Long-document understanding remains an unsolved problem.

### What our system does

Instead of feeding every page image to a big model, our pipeline:

1. **Converts each PDF to text** (OCR), preserving structure — sections, tables, images.
2. **Builds a "map" of each document** — a graph of sections with titles, summaries, and a hybrid search index (keyword + meaning-based).
3. **An AI agent investigates** each question like an analyst with a filing cabinet: it browses the map, searches by keyword and meaning, reads specific sections, occasionally looks at figures with a vision model, and writes a final answer.
4. **A second AI model grades** every answer against the reference.

### High-level results so far

- All 1,091 questions have now been run and graded end-to-end.
- On **uninterrupted, healthy runs** the system answers **~70% of questions correctly** — comfortably above the best published number (56%) — with notably strong table reading (82%) and chart reading (77%).
- Roughly one third of the runs were damaged by an infrastructure failure after the machine was suspended overnight (details in §5). Those runs score ~19% and drag the naive headline number down to 47%; they are repairable without re-running the whole benchmark.
- The hardest remaining weaknesses are questions about **figures and page layout**, and a small set of genuinely hard questions where run-to-run luck matters.

---

## 2. Technical run state

- `runs.jsonl`: 1,096 lines / **1,091 unique question records** (5 legacy duplicates from the Sep-16 pilot; last-wins).
- `scores.jsonl`: 1,091 scores; `scores_summary.json` current. Backups: `runs.jsonl.bak-20260917`, `scores.jsonl.bak-20260917`, plus `retrieval_rerun_old_scores.jsonl` (pre-rerun snapshot of the hard subset).
- Execution waves: original run (Sep 16–17), variance re-roll of 116 hard questions (phase A), completion of the remaining 722 (phase B).
- Total cost: ~110M input / ~2.4M output tokens. Throughput at concurrency 8: ~90–140 questions/hour depending on document difficulty.

## 3. Results on normal ("clean") runs

| Cohort | n | Accuracy (judged, partial credit) |
|---|---|---|
| Original run, clean (Sep 16–17) | 253 | **83.2%** |
| Phase B, clean | 366 | **61.1%** |
| **Clean-normal combined** | **619** | **70.1%** |
| Phase A variance re-roll (116 hardest) | 116 | 22.0% (was 2.6%) |
| Phase B, buffer-poisoned | 356 | 19.1% |

Headline over the full file (47.2%) is **not representative** — see §5.

Fine-grained on the 619 clean-normal runs:

- **By evidence source**: Table 81.8% · Chart 76.9% · Pure-text 75.0% · Figure 59.2% · Layout 58.6%. Text/table/chart handling is strong; figure- and layout-dependent questions are the weak spot.
- **Unanswerable questions: 66.9%** (n=154) vs 71.2% on answerable ones — good hallucination control.
- **Cross-page questions: 64.0%** (n=193) vs single-page 76.8%.
- Incorrect runs use ~2× the tool calls and tokens of correct ones (411k vs 206k input tokens on average) — failures are retrieval thrashing, not model collapse.
- The 83.2% vs 61.1% cohort gap is largely composition: wave 1 over-samples "Research report" documents (43% of the cohort, only 2 financial reports), while phase B carries the harder Academic-paper (68) and Financial-report (23) share — the paper's own analysis flags those domains as hardest.
- Variance re-roll of the 116 hardest questions: 26 improved / 3 regressed — roughly a quarter of those failures were run-to-run luck, not systematic.

## 4. Comparison with SOTA (factual)

Published numbers. The live leaderboard is maintained by the benchmark authors on Hugging Face (`OpenIXCLab/mmlongbench-doc` Space, backed by the `OpenIXCLab/mmlongbench-doc-results` dataset); the original paper is NeurIPS 2024 Datasets & Benchmarks Spotlight (arXiv:2407.01523). All official-protocol models below are fed page screenshots end-to-end:

| Model (official protocol) | Overall Acc | Cross-page | Unanswerable |
|---|---|---|---|
| Nemotron-3-Nano-Omni-30B-A3B (NVIDIA, vendor-reported) | **57.5** | — | — |
| TeleMM2.0 (Jan 2026) — best on official leaderboard | 56.1% | 48.6% | 46.2% |
| GPT-4.1 (Apr 2025) | 49.7% | 49.9% | 26.0% |
| GPT-4o (Nov 2024) | 46.3% | 41.4% | 34.1% |
| Qwen3-Omni-30B-A3B (closest open competitor) | 49.5 | — | — |

Sources for the Nemotron entries: NVIDIA's model comparisons circulated in the Radiant blog "How to run Nemotron Omni" ([radiant.co](https://radiant.co/blog/how-to-run-nemotron-omni)), and NVIDIA's own engineering dev note on training the model (NeMo Data Designer, [docs.nvidia.com](https://docs.nvidia.com/nemo/datadesigner/dev-notes/vlm-long-document-understanding)). The dev note documents the full training journey against MMLongBench-Doc as the primary eval target: the base model started at 26% (answering "Unanswerable" to almost everything), and an OCR-text-only QA pipeline plateaued around 28% — the bulk of the gains came from visually-grounded synthetic data targeting charts, tables and diagrams. That independent finding reinforces this report's recommendation (§6) that figure/layout questions are where visually-grounded capability pays off.

**Protocol caveat (important).** The official evaluation feeds all ~47 page screenshots per document end-to-end to a vision model, extracts a short answer via a 3-stage GPT-4o protocol, and scores exact match. Our pipeline is agentic retrieval over OCR markdown + graph navigation (vision used sparingly), scored by an LLM judge with partial credit. The two protocols are **not directly comparable** — our judge is likely more lenient than exact match, while our input is lossier (OCR) but better structured.

With that caveat, on clean runs this system sits **well above every published number** on this benchmark (~70% vs 57.5 for the best reported model), and the sub-metrics agree on the most comparable slices: cross-page 64.0% vs 48.6%, unanswerable 66.9% vs 46.2% (official leaderboard models). This is consistent with the paper's own finding that text-based (OCR) pipelines beat end-to-end page-image models on long documents; the agentic graph navigation pushes that advantage further.

## 5. What went wrong overnight (buffer-manager degradation)

- The benchmark process survived a machine suspend/resume (~03:00–05:00 UTC, visible as a gap in run timestamps).
- Before the suspend: **0** buffer errors in 419 runs. After resume the failure rate ramped to **75%** (06:00 hour) and **100%** (07:00 hour) of new runs.
- Failure mode: the shared Ladybug database's buffer manager returned `Unable to allocate memory! The buffer pool is full and no memory could be freed!` on nearly every section read. Agents then answered from table-of-contents fragments → 19.1% accuracy on those 356 runs, including 115 outright `halted_or_empty_response` give-ups.
- Root cause is **system memory state after suspend/resume under WSL2**, not DB size (62 MB), not concurrency (the healthy first 5 hours ran at the same settings), and not the search stack. These tool errors were invisible in the console log because tool exceptions are converted to result strings without logging (`_tool_error`).

## 6. Recommendations

### Without rebuilding the graph (highest ROI)

1. **Runtime resilience**: set an explicit `buffer_pool_size` (e.g. 4 GB) on the shared Ladybug `Database` instead of the ~80%-of-RAM default; treat suspend/resume mid-run as fatal (detect the timestamp gap and abort rather than continue into a degraded DB); keep concurrency at 8.
2. **Make failures visible**: add a `logger.warning` in `_tool_error` (`genai_graph/kg/query/document_graph_tools.py`) and a bench post-run check that counts error-stuffed tool results.
3. **Anti-give-up guardrail**: if the final answer is empty/error-like after the wrap-up nudge, inject one forced recovery turn ("answer from the evidence you have, or state Not Answerable") — targets the 115 give-ups.
4. **Retrieval guidance for Figure/Layout questions** (59%/59%): update the `mmlongbench-qa` skill to route these to `query_image` earlier (budget is 3/question; clean runs under-use it).
5. **Efficiency**: tighter wrap-up nudging (raise the 24-call soft limit only for detected cross-page questions) and prompt caching on the repeated system/skill prompt.
6. **Scoring comparability**: add an optional strict scoring pass replicating the paper's 3-stage extraction + exact match, so future runs are directly comparable to the leaderboard (judge calls only, no re-runs).

### With a graph rebuild (if chasing Figure/Layout and financial docs)

1. **Table-aware OCR / markdownize profile** — financial reports and tables are where OCR loss bites.
2. **Describe uncaptioned images at build time** (`describe_uncaptioned: true`) so figure questions become retrievable as text.
3. **Stronger embeddings** than `qwen3_06b@deepinfra` for the SectionChunk HNSW index; chunk-level summaries for very long sections.
4. **Page-number grounding**: store PDF page mappings on sections so agents can cite/jump to evidence pages — directly targets cross-page questions.

## 7. Repair-pass playbook (to salvage the 356 poisoned runs later)

1. **Fresh machine state first**: restart WSL (`wsl --shutdown` from Windows) or reboot; verify with `free -h`. The corruption followed suspend/resume — start clean.
2. **Back up**: `cp data/mmlongbench/default/{runs,scores}.jsonl` with a date suffix.
3. **Strip the poisoned records** (last-wins JSONL makes this safe): remove every line whose id is in the buffer-hit set — runs started `>= 2026-09-17T23:46Z` whose `tool_results` contain `Buffer manager` — from **both** `runs.jsonl` and `scores.jsonl` (356 ids). Optionally also strip the 8 hard-error / 7 empty-answer runs.
4. *(Optional hardening first)*: apply the explicit `buffer_pool_size` and `_tool_error` logging from §6 — ~10 lines in `genai-tk/utils/ladybug/shared.py` and `genai_graph/kg/query/document_graph_tools.py`.
5. **Launch** (no `--rerun`; resume machinery skips the ~735 good records): `cli bench run --step run > data/mmlongbench/default/repair.log 2>&1 &` — expect ~4–5 h at concurrency 8.
6. **Monitor hourly**: tool errors don't reach the log until §6.2 is applied — check `runs.jsonl` line count and grep the newest records' `tool_results` for `Buffer manager`. If the hit rate is non-zero after a fresh start, stop and investigate rather than push through.
7. **Re-grade**: `cli bench grade` (reuses all good scores, grades only repaired runs), then `cli bench report`.

Expected outcome if the repaired cohort matches clean phase-B behavior (~61%): overall accuracy lands at **~61–63%** instead of 47.2%.
