# MMLongBench-Doc Multimodal Evaluation Report

**Evaluation Date:** September 12, 2026  
**Benchmark:** [MMLongBench-Doc](https://github.com/mayubo2333/MMLongBench-Doc) (arXiv:2407.01523)  
**Agent Architecture:** DeepAgent (`type: deep`) with Ladybug Document Graph & Multimodal VLM  
**Agent LLM:** `glm_5.3_flash@openrouter` (`z-ai/glm-5.3-flash`)  
**Judge LLM:** `DeepSeek-V4-Pro-0813@openrouter`  
**OCR / Conversion Pipeline:** Mistral OCR (`include_image_base64: true`) + Ladybug Image Node Ingestion  

---

## 1. Executive Summary

We evaluated the deep multimodal Document Graph agent on a representative subset of 8 questions across 2 diverse documents from MMLongBench-Doc:
1. `05-03-18-political-release.pdf` (May 2018 Pew Research survey on presidential ratings and ethics)
2. `11-21-16-Updated-Post-Election-Release.pdf` (November 2016 Pew Research post-election voter reactions and campaign evaluations)

The test evaluated key scientific dimensions of long-document multimodal comprehension:
- **Visual Chart & Line Plot Interpretation** (questions requiring pixel-level chart reasoning)
- **Anti-Hallucination & Unanswerable Question Detection** (questions with perturbed year, entity, or demographic predicates)
- **Cross-Page Reasoning & Arithmetic Synthesis** (combining sample sizes $N$ from methodology sections with survey percentages)
- **Document Graph Navigation** (`get_folder_toc`, `get_document_toc`, `get_section_content`, `search_sections`, `search_images`, `query_image`)

### Performance Metrics

| Metric | Score | Detail |
|---|---|---|
| **Strict Accuracy** | **87.5%** | **7 / 8 Questions Correct** |
| **Numeric Match Rate** | **100.0%** | **2 / 2 Numeric Questions Exactly Matched** |
| **Unanswerable Detection Rate** | **100.0%** | **3 / 3 Unanswerable Questions Identified** |
| **Groundedness Rate** | **87.5%** | **7 / 8 Responses Grounded with Exact Citations** |
| **Average Tool Calls / Turn** | **10.88** | Active multi-step navigation & VLM calls |
| **Token Consumption** | In: 867,864 \| Out: 107,699 | Full multi-turn graph navigation |

---

## 2. Detailed Question-by-Question Evaluation

| ID | Document | Question Type | Gold Answer | Agent Output | Judge Decision |
|---|---|---|---|---|---|
| `docqa_0684` | `11-21-16-Updated-Post-Election-Release` | Visual Chart / Line Plot | `92` | **92% (in 2016)** | **Correct (Grounded)** |
| `docqa_0685` | `11-21-16-Updated-Post-Election-Release` | Section Table / Demographics | `men` | **Men (81% vs 78%)** | **Correct (Grounded)** |
| `docqa_0686` | `11-21-16-Updated-Post-Election-Release` | Unanswerable (Demographic Mismatch) | `Not answerable` | **Not answerable.** (No Black/White breakdown) | **Correct (Grounded)** |
| `docqa_0688` | `11-21-16-Updated-Post-Election-Release` | Distribution / Grade Comparison | `Clinton` | **Clinton** (Average grade C vs C-) | **Correct (Grounded)** |
| `docqa_0207` | `05-03-18-political-release` | Cross-Page Arithmetic ($N \times \%$) | `541` | **541 adults** ($1503 \times 36\%$) | **Correct (Grounded)** |
| `docqa_0208` | `05-03-18-political-release` | Unanswerable (Year Mismatch) | `Not answerable` | **Not answerable.** (Survey was 2018, not 2022) | **Correct (Grounded)** |
| `docqa_0210` | `05-03-18-political-release` | Unanswerable (Entity Mismatch) | `Not answerable` | **Not answerable.** (Document covers Trump, not Biden) | **Correct (Grounded)** |
| `docqa_0209` | `05-03-18-political-release` | Table / Chart Comparison | `['Make good decisions about economic policy ', 'Make wise decisions about immigration policy ']` | `['Make wise decisions about immigration policy', 'Negotiate favorable trade agreements with other countries']` | **Incorrect (Retrieval / Column Misalignment)** |

---

## 3. Trajectory & Agent Behavior Analysis

### What Worked Exceptionally Well:

1. **Multimodal Visual Chart Reasoning (`search_images` + `query_image`)**:
   - In `docqa_0684`, the agent searched for mudslinging figures using `search_images(query="mudslinging")`, identified `image_id: 345c14f120035b1d::11::40980090`, and dispatched `query_image` to GLM-5.3-Flash.
   - The VLM accurately traced the line chart from 1992 to 2016, extracting the exact 92% peak and contrasting it with the 4% low for "Less mudslinging".
2. **Robust Anti-Hallucination on Unanswerable Questions**:
   - The agent demonstrated 100% precision on unanswerable questions across all perturbation types:
     * **Year perturbation** (`docqa_0208`): Immediately verified the survey dates in methodology ($2018 \neq 2022$) and refrained from hallucinating.
     * **Entity perturbation** (`docqa_0210`): Confirmed the document discussed Donald Trump and that Joe Biden was unmentioned.
     * **Demographic absence** (`docqa_0686`): Checked the gender/party breakdown table and accurately reported that race (Black vs. White) was not measured.
3. **Cross-Page Arithmetic Synthesis**:
   - In `docqa_0207`, the agent combined the 36% "poor" rating from Section 13 / Image `1fe49a31` with the sample size $N = 1,503$ from Section 25 (Methodology) to compute $1503 \times 0.36 = 541$.

### Root Cause Analysis of the Single Error (`docqa_0209`):
- **Issue**: For `docqa_0209`, the question asked for the domains with the highest "Very confident" and "Not at all confident" ratings.
- **Root Cause**: The Mistral OCR markdown table representation in Section 7 contained misaligned column headers for diverging bar charts (combining left-total and right-total percentages into the header row). As a result, the right-total 54% for trade agreements was read as the "Very confident" column instead of the sub-column value.
- **Lesson**: When reading complex multi-column survey tables with diverging bars, the agent should cross-validate ambiguous column headers by querying the corresponding figure image using `query_image`.

---

## 4. Key Recommendations for Full-Scale Benchmark Run

1. **Visual Cross-Validation Rule for Diverging Tables**:
   - Add a heuristic in the `mmlongbench-qa` skill prompting the agent to call `query_image` when survey tables contain ambiguous multi-level headers or diverging stacked bar formats.
2. **Multimodal Embeddings Integration**:
   - Enable multimodal embeddings (e.g. `amazon.nova-2-multimodal-embeddings-v1` via EdenAI) to allow direct semantic similarity search over image embeddings alongside text chunk embeddings.
3. **Structured Format Guardrails**:
   - Standardize post-processing or prompt formatting for questions requesting strict list outputs (`["A", "B"]`) to ensure exact alphabetical sorting and string cleanliness.
4. **Batch Execution & Concurrency Tuning**:
   - The full 135-document / 1,091-question benchmark can be scheduled with Prefect workers (`concurrency=10` or higher) with cached outlines and DB artifacts.
