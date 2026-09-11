---
name: mmlongbench-qa
description: Answer MMLongBench-Doc multi-modal long-document questions across research papers, financial reports, technical manuals, guidelines, and slide documents by navigating the Document Graph.
---

# MMLongBench-Doc Multi-Modal Long-Document Question Answering

You answer complex multi-modal and long-document questions from **research reports, financial filings, academic papers, administrative guidelines, and technical manuals** by navigating a Document Graph (Folders → Documents → Markdown sections).

---

## 1. Document Characteristics & Structure Discovery

[MMLongBench-Doc](https://github.com/mayubo2333/MMLongBench-Doc) comprises 135 PDF documents with an average length of 47.5 pages (~21,214 tokens), spanning 7 diverse domains with rich multi-modal components (tables, charts, infographics, and text).

### Key Dataset Traits to Keep in Mind:
- **Cross-Page Reasoning (33.0% of questions)**: Many answers require synthesizing information across multiple non-consecutive pages (e.g. demographic charts on page 3 combined with survey totals on page 12).
- **Unanswerable Questions (22.5% of questions)**: A significant portion of questions cannot be answered from the document to test hallucination resistance. When the required evidence is genuinely absent, answer explicitly: `Not answerable.`
- **Rich Multi-Modal Tables & Figures**: Inspect table layouts, column labels, date headers, and chart captions carefully in the section Markdown.

---

## 2. Document Graph Navigation Workflow

1. **Orient with `get_folder_toc(folder_id=None)`**:
   - List available documents to identify the target report or filing matching the question.
2. **Inspect Outline with `get_document_toc(document_id=<id>, max_level=2)`**:
   - View the complete section tree, titles, page spans, and descriptions.
   - Use the TOC to identify the exact section, heading, or table before reading raw content.
3. **Targeted Search with `search_sections(query="<query>", document_id="<id>")`**:
   - Use keyword-rich queries (e.g., `"Demographic Breakdown"`, `"Table 4"`, `"Revenue Growth"`, `"Methodology"`).
   - Constrain search with `document_id` when the document is known.
4. **Read Section Markdown with `get_section_content(section_ids="<id>", start_line=..., max_lines=...)`**:
   - Read tables, text transcripts, and visual descriptions.
   - Use `start_line` and `max_lines` pagination for large tables or multi-page sections.
5. **Multi-Step Continuity & Tool Calling Discipline**:
   - Always invoke the next tool call directly in each turn during multi-step investigations.
   - Do NOT emit intermediate conversational status updates without a tool call.
   - Emit plain text only when delivering your final answer.

---

## 3. Grounded Answering & Equivalence Rules

- **Numerical Precision & Units**:
  - Percentages, decimals, and fractions are equivalent ($18.29\% \equiv 0.1829 \equiv 18.3\%$).
  - Always verify whether numbers are in units of thousands, millions, or billions.
  - Use `python_interpreter` for exact arithmetic, rounding, and ratio calculations.
- **Categorical & Entity Answers**:
  - State the exact entity name, category, or classification as given in the source text.
- **Unanswerable Questions**:
  - If a question asks for information not present anywhere in the document, explicitly conclude: `Not answerable.`
- **Citations**:
  - Always cite the section ID `[hash::sequence]` and document filename.

