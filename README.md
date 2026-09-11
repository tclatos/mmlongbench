# MMLongBench-Doc Benchmark (`mmlongbench`)

This repository evaluates the **Document Graph (DocGraph) + Autonomous Deep Agent** stack against **MMLongBench-Doc** ([Homepage](https://mayubo2333.github.io/MMLongBench-Doc/) · [GitHub](https://github.com/mayubo2333/MMLongBench-Doc) · [Hugging Face](https://huggingface.co/datasets/yubo2333/MMLongBench-Doc) · [Paper](https://arxiv.org/abs/2407.01523) · [Leaderboard](https://huggingface.co/spaces/OpenIXCLab/mmlongbench-doc)).

> **Note on Benchmark Distinction:**  
> This project specifically targets **MMLongBench-Doc** (*Ma et al.*, 135 long PDF documents, 1,091 expert-annotated questions, average length ~47.5 pages / 21,214 tokens), not the broader 13k-sample multimodal benchmark suite *MMLongBench (Wang et al.)*.

---

## 🌟 Benchmark Overview & Highlights

[MMLongBench-Doc](https://mayubo2333.github.io/MMLongBench-Doc/) is an authoritative benchmark designed to evaluate long-context document understanding (DU) with multi-modal visualizations (tables, charts, infographics, diagrams, and layout structures).

- **135 Long PDF Documents**: Across 7 diverse domains (research reports, financial filings, guidelines, papers, technical manuals, administrative documents).
- **1,091 Questions with Deterministic Ground Truth**: Each accompanied by gold answer, evidence pages, and source annotations.
- **Cross-Page Reasoning (33.0%)**: Requires synthesizing evidence dispersed across multiple non-consecutive pages.
- **Unanswerable / Anti-Hallucination Questions (22.5%)**: Tests the model's resistance to hallucinating facts not grounded in the source documents.
- **Baseline Challenge**: Commercial multimodal models face substantial challenges on this benchmark (e.g. GPT-4o achieves ~44.9% overall F1).

---

## 🚀 Quick Start

### 1. Installation & Environment Setup

```bash
# Clone the repository
git clone https://github.com/tclatos/mmlongbench.git
cd mmlongbench

# Install all dependencies with uv
uv sync
```

### 2. Download Dataset & PDF Documents

Fetch the 1,091 question annotations and the 135 raw PDF documents directly from Hugging Face:

```bash
# Download question dataset and all 135 PDF files
uv run cli bench download --docs

# Or download metadata + first N documents for quick experimentation
uv run cli bench download --docs -n 10
```

### 3. Inspect Questions & Ground Truth

```bash
# List first 20 questions in a formatted table
uv run cli bench questions -n 20

# View single question details, evidence pages, and justification
uv run cli bench questions -q docqa_0001

# Launch the interactive Textual TUI browser
uv run cli bench questions --tui
```

### 4. Run Evaluation

```bash
# Dry-run execution plan
uv run cli bench run -p mistral_glm --dry-run

# Run agent on a single question
uv run cli bench run -p mistral_glm -q docqa_0001

# Run full benchmark evaluation profile
uv run cli bench run -p mistral_glm
```

---

## 🏗️ Architecture & Pipeline

```
[1. Dataset Fetch] (Hugging Face: yubo2333/MMLongBench-Doc)
       │
       ▼
[2. Multi-modal Markdownize & OCR] (Mistral OCR / MarkItDown / Docling)
       │
       ▼
[3. Hierarchical Document Graph Ingestion] (Ladybug DB + BM25 & Vector Index)
       │
       ▼
[4. Autonomous Deep Agent Execution] (Document Tree navigation, TOC inspection, Table slicing)
       │
       ▼
[5. LLM-as-Judge Evaluation] (MMLongBench-Doc grading rubric + Mafin 2.5 numeric tolerance)
       │
       ▼
[6. Metrics & TUI Observability] (Accuracy, error breakdown, trajectory replay)
```

---

## 📁 Repository Structure

```
mmlongbench/
  adapter.py            # MMLongBench-Doc dataset adapter (yubo2333/MMLongBench-Doc)
  commands/             # Typer CLI command group (cli bench ...)
  skills/custom/        # Domain QA skill (mmlongbench-qa) for agent guidance
config/
  bench.yaml            # Benchmark run profiles (agent LLM, judge LLM, build settings)
  app_conf.yaml         # GenAI Toolkit application configuration & CLI registry
data/
  mmlongbench/          # Cached question JSONL & Parquet files
  pdfs/                 # Downloaded raw PDF documents (135 files)
  markdown_multi/       # OCR & hierarchical Markdown trees
  kg/                   # Ingested Ladybug Document Graph database
```

---

## 🔗 Official Links & Resources

- **Project Homepage**: [https://mayubo2333.github.io/MMLongBench-Doc/](https://mayubo2333.github.io/MMLongBench-Doc/)
- **Hugging Face Dataset**: [https://huggingface.co/datasets/yubo2333/MMLongBench-Doc](https://huggingface.co/datasets/yubo2333/MMLongBench-Doc)
- **Hugging Face Leaderboard**: [https://huggingface.co/spaces/OpenIXCLab/mmlongbench-doc](https://huggingface.co/spaces/OpenIXCLab/mmlongbench-doc)
- **Official GitHub**: [https://github.com/mayubo2333/MMLongBench-Doc](https://github.com/mayubo2333/MMLongBench-Doc)
- **Paper**: [MMLongBench-Doc: Benchmarking Long-context Document Understanding with Visualizations](https://arxiv.org/abs/2407.01523) (*arXiv:2407.01523*)

---

## 📖 Citation

```bibtex
@misc{ma2024mmlongbenchdocbenchmarkinglongcontextdocument,
      title={MMLongBench-Doc: Benchmarking Long-context Document Understanding with Visualizations}, 
      author={Yubo Ma and Yuhang Zang and Liangyu Chen and Meiqi Chen and Yizhu Jiao and Xinze Li and Xinyuan Lu and Ziyu Liu and Yan Ma and Xiaoyi Dong and Pan Zhang and Liangming Pan and Yu-Gang Jiang and Jiaqi Wang and Yixin Cao and Aixin Sun},
      year={2024},
      eprint={2407.01523},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2407.01523}, 
}
```

