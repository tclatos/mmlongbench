# MMLongBench-Doc Benchmark (`mmlongbench`)

Evaluating **Document Graph + Deep Agent** on [MMLongBench-Doc](https://github.com/mayubo2333/MMLongBench-Doc) — a benchmark evaluating long-context multimodal document understanding across 135 lengthy PDF documents (averaging 47.5 pages / 21,214 tokens) and 1,091 expert-annotated questions.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Download MMLongBench-Doc questions and PDF documents
uv run cli bench download --docs

# 3. Inspect benchmark questions
uv run cli bench questions -n 20
uv run cli bench questions -q docqa_0001
uv run cli bench questions --tui               # Launch interactive Textual browser

# 4. Run end-to-end evaluation
uv run cli bench run -p mistral_glm -q docqa_0001
uv run cli bench run -p mistral_glm --dry-run
```

---

## 📊 Benchmark Overview

- **Source Dataset**: [`yubo2333/MMLongBench-Doc`](https://huggingface.co/datasets/yubo2333/MMLongBench-Doc)
- **Documents**: 135 PDF files across 7 diverse domains
- **Questions**: 1,091 total questions
  - **Cross-Page Reasoning**: 33.0%
  - **Unanswerable (Anti-Hallucination)**: 22.5%
- **Evaluation Engine**: `genai_graph.bench` with LLM-as-judge rubric

---

## 🛠️ Project Structure

```
mmlongbench/
  adapter.py            # MMLongBench-Doc dataset adapter
  commands/             # CLI commands (cli bench ...)
  skills/custom/        # mmlongbench-qa domain navigation skill
config/
  bench.yaml            # Benchmark profiles (agent LLM, judge LLM, paths)
  app_conf.yaml         # Application & CLI registration
data/
  mmlongbench/          # Cached questions & parquet
  pdfs/                 # Downloaded raw PDF documents
  markdown_multi/       # OCR & hierarchical Markdown trees
  kg/                   # Ingested Ladybug Document Graph
```

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
