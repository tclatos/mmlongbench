---
name: mmlongbench-qa
description: Answer MMLongBench-Doc multi-modal long-document questions across research papers, financial reports, technical manuals, guidelines, and slide documents by navigating the Document Graph and querying images with VLM.
---

# MMLongBench-Doc Multi-Modal Long-Document Question Answering

You answer complex multi-modal and long-document questions from **research reports, financial filings, academic papers, administrative guidelines, and technical manuals** by navigating a Document Graph (Folders → Documents → Markdown sections → Images).

---

## 1. Dataset Foundations & Scientific Characteristics

Based on the [MMLongBench-Doc](https://github.com/mayubo2333/MMLongBench-Doc) benchmark (arXiv:2407.01523), documents average 47.5 pages (~21,214 tokens) and span 7 diverse domains.

### Key Benchmark Traits & Strategic Guidelines:

1. **Unanswerable Questions (~22.5% of questions — Anti-Hallucination Probe)**:
   - MMLongBench-Doc intentionally modifies key query predicates to evaluate hallucination resistance.
   - **Predicate Mismatches to Systematically Check**:
     * **Time / Year Mismatch**: e.g., the document reports on an *April 2018* survey, but the query asks about *April 2022*.
     * **Subject / Entity Mismatch**: e.g., the document discusses *Donald Trump*, but the query asks about *Joe Biden*.
     * **Population / Geography Mismatch**: e.g., the document surveys *U.S. adults*, but the query asks about *Chinese adults*.
     * **Unmeasured Demographics**: e.g., the survey breaks data down by *Gender*, but the query asks for *Race / Ethnicity (Black vs White)*.
   - **Action Rule**: If ANY key predicate (year, entity, population, or variable) is not supported by the document, immediately state: `Not answerable.` Do not extrapolate or substitute a different year/entity.

2. **Visual Charts, Plots & Infographics Understanding**:
   - Many questions require reading exact numerical values, bar heights, line endpoints, time series trajectories, or categories from visual figures that are NOT fully transcribed into Markdown text tables.
   - **Action Rule**: When a question refers to a chart, line plot, figure, or visual distribution:
     * Call `search_images(query="<chart topic or figure label>", document_id="<id>")` to locate the image.
     * Call `query_image(image="<image_id or path>", question="<specific visual query>")` to read the chart via the VLM.

3. **Cross-Page Reasoning (~33.0% of questions)**:
   - Frequently requires combining information across non-adjacent pages:
     * e.g., Total survey sample size $N = 1,503$ on Methodology (Page 3/4) combined with a $36\%$ response on Page 12: $1503 \times 0.36 = 541$.
     * e.g., Identifying the leading political party on Page 11, then checking that specific party's media attention rate on Page 13.
   - **Action Rule**: Look for sample sizes, definitions, and overall totals in the introduction/methodology sections when calculating absolute counts from percentages.

4. **Exact Format Compliance**:
   - **Alphabetical List**: When asked for a list in alphabetical order (e.g. `["A", "B"]`), sort the items alphabetically.
   - **Float Format**: When asked for float format (e.g. `7.0`), format the numeric answer as a float.
   - **List Format**: When asked for e.g. `["3", "2"]` or list of values, output the values in the requested list structure.

---

## 2. Document Graph Navigation Workflow

1. **Orient with `get_folder_toc(folder_id=None)` or `list_documents()`**:
   - Identify the target document filename and content hash matching the query topic.
2. **Inspect Outline with `get_document_toc(document_id=<id>, max_level=2)`**:
   - Examine the section hierarchy, page spans, and routing descriptions.
   - Identify the relevant sections and figures before reading raw text.
3. **Inspect Visual Figures with `search_images` and `query_image`**:
   - For chart, line plot, diagram, or graphical questions, find the image and query it with the VLM.
4. **Read Section Content with `get_section_content(section_ids="<id>", start_line=..., max_lines=...)`**:
   - Read tables, text paragraphs, and footnotes.
   - Use pagination (`start_line`, `max_lines`) for extensive tables.
5. **Targeted Search with `search_sections(query="<query>", document_id="<id>")`**:
   - Use compact keyword queries (e.g., `"Methodology Sample Size"`, `"Table 2"`, `"Mudslinging"`) when the TOC does not directly reveal the location.
6. **Tool Discipline**:
   - Always emit the next tool call directly in each step.
   - Do NOT emit intermediate conversational status messages without tool calls.
   - Emit plain text only when delivering your final answer.

---

## 3. Grounded Answering & Equivalence Rules

- **Numerical Precision & Units**:
  - Percentages, decimals, and fractions are equivalent ($18.29\% \equiv 0.1829 \equiv 18.3\%$).
  - Always check units (thousands vs millions vs billions, percentage points vs percentages).
  - Use `python_interpreter` when available for exact arithmetic.
- **Unanswerable Questions**:
  - State clearly: `Not answerable.` (or `The document does not provide information about ...`).
- **Citations**:
  - Cite the section ID `[hash::sequence]` and document filename or image ID.

