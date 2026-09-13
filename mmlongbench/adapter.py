"""MMLongBench-Doc dataset adapter for multi-modal long-document understanding.

Reference:
- GitHub: https://github.com/mayubo2333/MMLongBench-Doc
- Hugging Face: https://huggingface.co/datasets/yubo2333/MMLongBench-Doc
- Paper: "MMLongBench-Doc: Benchmarking Long-context Document Understanding with Visualizations" (arXiv:2407.01523)
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path
from typing import Any

from genai_graph.bench.adapters.base import (
    BaseBenchmarkAdapter,
    download_hf_file,
    download_http_file,
)
from genai_graph.bench.models import BenchQuestion
from loguru import logger

HF_DATASET_ID = "yubo2333/MMLongBench-Doc"
# Authoritative mirror of the document PDFs (the Hub copy of some documents
# serves bytes that do not match the repo's recorded LFS OIDs).
GITHUB_DOCUMENTS_URL = "https://raw.githubusercontent.com/mayubo2333/MMLongBench-Doc/main/data/documents"

MMLONGBENCH_DOC_JUDGE_RUBRIC = """\
You are a strict-but-fair grader for MMLongBench-Doc, a benchmark evaluating multi-modal comprehension of very long documents (PDF reports, financial disclosures, academic papers, administrative guidelines, and technical publications).
Compare the agent's answer to the gold answer using the provided evidence and justification.

Return ONLY a JSON object with exactly these keys:
{
  "correctness": "correct" | "partial" | "incorrect",
  "numeric_match": true | false | null,
  "groundedness": "grounded" | "partial" | "ungrounded",
  "error_category": "missing_ocr_or_visual_chart" | "calculation_or_math_error" | "retrieval_or_lookup_error" | "halted_or_empty_response" | null,
  "rationale": "<one sentence>"
}

Equivalence and grading rules (MMLongBench-Doc evaluation protocol):
- Numerical accuracy: rounding differences are IGNORED when they do not change the conclusion (e.g. 18.3% is equivalent to 18.29%, 0.1829, or 18%). Fractions, percentages, and decimals are equivalent.
- Text & Categorical answers: Case-insensitive, punctuation-insensitive string matching. If the gold answer is a name, title, category, or entity, and the agent includes the key entity name or synonymous formulation, it is correct.
- List answers: The agent answer is correct if it covers all or the majority of the required items without hallucinations.
- Unanswerable questions: 22.5% of questions in MMLongBench-Doc are designed to be unanswerable to test hallucination detection. If the gold answer states 'Not answerable', 'Unanswerable', or 'N/A', the agent is correct if it explicitly determines that the document does not provide the requested information.
- Superset answers: If the agent answer is a superset of the gold answer and conveys the exact factual answer clearly, it is correct.

Tiers:
- "correct" = agent answer matches gold answer substance and requirements under the equivalence rules above.
- "partial" = right direction or correct document located, but contains minor calculation/rounding errors or omitted secondary list items.
- "incorrect" = wrong fact, hallucinated response, or completely missing answer.
- "numeric_match" = true if a numeric value was expected and matches; false if expected but does not match; null if non-numeric.
- "groundedness" = "grounded" if supported by the document text/figures; "ungrounded" if facts are hallucinated or fabricated.
- "error_category" = when correctness is "partial" or "incorrect", categorize the primary root cause:
  * "missing_ocr_or_visual_chart": question requires reading a visual chart, line plot, graph, or diagram missing/unreadable in text OCR transcript.
  * "calculation_or_math_error": agent found the relevant figures, but made an arithmetic, formula, or rounding calculation mistake.
  * "retrieval_or_lookup_error": agent retrieved or referenced the wrong section, table, or failed to find the relevant document page.
  * "halted_or_empty_response": agent timed out, looped, hit tool recursion limits, or returned an empty/aborted response.
"""


def _clean_val(val: Any) -> Any:
    """Return JSON-safe value: pandas NaN -> None."""
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    return val


def _parse_list_field(val: Any) -> list[Any]:
    """Safely parse string representations of lists (e.g. '[3, 5]' or "['Chart']")."""
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        val_str = val.strip()
        if not val_str:
            return []
        if val_str.startswith("[") and val_str.endswith("]"):
            try:
                parsed = ast.literal_eval(val_str)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        return [val_str]
    return [val]


class MMLongBenchAdapter(BaseBenchmarkAdapter):
    """Adapter for MMLongBench and MMLongBench-Doc datasets."""

    name: str = "mmlongbench"

    def load_dataset(
        self, split: str | None = None, cache_dir: Path | None = None
    ) -> list[BenchQuestion]:
        """Load MMLongBench questions and convert to standard BenchQuestion items.

        Supports loading from local JSONL cache or downloading directly from Hugging Face Hub.
        """
        import pandas as pd

        target_dir = cache_dir or (Path.cwd() / "data" / "mmlongbench")
        target_dir.mkdir(parents=True, exist_ok=True)

        questions_jsonl = target_dir / "questions.jsonl"
        parquet_cache = target_dir / "mmlongbench_doc.parquet"

        # 1. If questions.jsonl exists, load directly
        if questions_jsonl.exists() and questions_jsonl.stat().st_size > 0:
            logger.info("Loading cached questions from {}", questions_jsonl)
            questions: list[BenchQuestion] = []
            with questions_jsonl.open(encoding="utf-8") as fh:
                for idx, line in enumerate(fh):
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    q_id = str(
                        item.get("id") or item.get("question_id") or f"docqa_{idx:04d}"
                    )
                    raw_doc = str(
                        item.get("doc_name")
                        or item.get("doc_id")
                        or item.get("file_name")
                        or "unknown"
                    )
                    doc_stem = self.resolve_doc_name(raw_doc)
                    questions.append(
                        BenchQuestion(
                            id=q_id,
                            doc_name=doc_stem,
                            doc_names=[doc_stem],
                            question=str(item.get("question", "")),
                            gold_answer=str(
                                item.get("answer") or item.get("gold_answer", "")
                            ),
                            evidence=_parse_list_field(
                                item.get("evidence") or item.get("evidence_pages")
                            ),
                            justification=_clean_val(item.get("justification")),
                            metadata=item,
                        )
                    )
            return questions

        # 2. If parquet cache exists or needs downloading from Hugging Face
        if parquet_cache.exists() and parquet_cache.stat().st_size > 0:
            logger.info("Loading questions from cached parquet: {}", parquet_cache)
            df = pd.read_parquet(parquet_cache)
        else:
            logger.info(
                "Fetching MMLongBench-Doc dataset from Hugging Face ({})", HF_DATASET_ID
            )
            hf_path = download_hf_file(
                repo_id=HF_DATASET_ID,
                filename="data/train-00000-of-00001.parquet",
                repo_type="dataset",
            )
            df = pd.read_parquet(hf_path)
            df.to_parquet(parquet_cache, index=False)
            logger.info(
                "Saved {} questions to parquet cache {}", len(df), parquet_cache
            )

        # 3. Parse DataFrame into BenchQuestion objects and save questions.jsonl
        questions = []
        with questions_jsonl.open("w", encoding="utf-8") as fh:
            for idx, row in df.iterrows():
                q_id = f"docqa_{idx + 1:04d}"
                raw_doc_id = str(row.get("doc_id", "unknown"))
                doc_stem = self.resolve_doc_name(raw_doc_id)
                q_text = str(row.get("question", ""))
                gold_ans = str(row.get("answer", ""))
                doc_type = _clean_val(row.get("doc_type"))
                ans_format = _clean_val(row.get("answer_format"))
                ev_pages = _parse_list_field(row.get("evidence_pages"))
                ev_sources = _parse_list_field(row.get("evidence_sources"))

                metadata = {
                    "id": q_id,
                    "doc_id": raw_doc_id,
                    "doc_name": doc_stem,
                    "doc_type": doc_type,
                    "answer_format": ans_format,
                    "evidence_pages": ev_pages,
                    "evidence_sources": ev_sources,
                }

                bq = BenchQuestion(
                    id=q_id,
                    doc_name=doc_stem,
                    doc_names=[doc_stem],
                    question=q_text,
                    gold_answer=gold_ans,
                    evidence=ev_pages,
                    justification=f"Doc Type: {doc_type}. Sources: {', '.join(map(str, ev_sources))}",
                    metadata=metadata,
                )
                questions.append(bq)
                fh.write(bq.model_dump_json() + "\n")

        logger.info(
            "Initialized {} MMLongBench-Doc questions in {}",
            len(questions),
            questions_jsonl,
        )
        return questions

    def fetch_document(self, doc_name: str, output_dir: Path) -> Path:
        """Download document PDF from Hugging Face Hub (yubo2333/MMLongBench-Doc)."""
        output_dir.mkdir(parents=True, exist_ok=True)
        norm_name = self.resolve_doc_name(doc_name)
        target = output_dir / f"{norm_name}.pdf"
        sub_target = output_dir / "documents" / f"{norm_name}.pdf"

        if target.exists() and target.stat().st_size > 1000:
            logger.debug("PDF already present: {}", target)
            return target
        if sub_target.exists() and sub_target.stat().st_size > 1000:
            logger.debug("PDF already present in documents/: {}", sub_target)
            return sub_target

        # 1. Download pre-built PDF directly from yubo2333/MMLongBench-Doc
        try:
            logger.info(
                "Downloading PDF for {} from {}/documents", norm_name, HF_DATASET_ID
            )
            downloaded = download_hf_file(
                repo_id=HF_DATASET_ID,
                filename=f"documents/{norm_name}.pdf",
                repo_type="dataset",
                output_dir=output_dir,
            )
            if downloaded.exists() and downloaded.stat().st_size > 1000:
                return downloaded
        except Exception as exc:
            logger.warning(
                "Could not download PDF from {} for {}: {}",
                HF_DATASET_ID,
                norm_name,
                exc,
            )

        # 2. Fall back to the benchmark authors' GitHub mirror of the documents.
        try:
            github_url = f"{GITHUB_DOCUMENTS_URL}/{norm_name}.pdf"
            logger.info("Downloading PDF for {} from {}", norm_name, github_url)
            part_path = sub_target.with_name(sub_target.name + ".part")
            download_http_file(url=github_url, output_path=part_path)
            if part_path.read_bytes()[:5] != b"%PDF-":
                raise ValueError(f"Downloaded {github_url} is not a valid PDF.")
            part_path.replace(sub_target)
            return sub_target
        except Exception as exc:
            logger.warning("Could not download PDF from GitHub for {}: {}", norm_name, exc)

        raise FileNotFoundError(
            f"Document {norm_name} could not be fetched from {HF_DATASET_ID}."
        )

    def get_judge_rubric(self) -> str:
        return MMLONGBENCH_DOC_JUDGE_RUBRIC


# Backward compatibility aliases
MMLongBenchDocAdapter = MMLongBenchAdapter
DefaultBenchmarkAdapter = MMLongBenchAdapter
DefaultBenchmarkAdapter = MMLongBenchAdapter
