"""Benchmark CLI commands for MMLongBench-Doc."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from genai_graph.bench.adapters.base import get_benchmark_adapter
from genai_graph.bench.config import load_bench_profile, load_env
from genai_graph.core.commands_bench import BenchCommands as BaseBenchCommands
from loguru import logger
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

console = Console()


class BenchCommands(BaseBenchCommands):
    """Extended benchmark commands with MMLongBench-Doc dataset downloading."""

    def register_sub_commands(self, cli_app: typer.Typer) -> None:
        super().register_sub_commands(cli_app)

        @cli_app.command("download")
        def download_dataset(
            docs: Annotated[
                bool,
                typer.Option(
                    "--docs/--no-docs",
                    help="Download raw PDF documents for benchmark questions",
                ),
            ] = True,
            limit: Annotated[
                int | None,
                typer.Option(
                    "-n", "--limit", help="Limit number of PDF documents to download"
                ),
            ] = None,
            profile: Annotated[
                str | None,
                typer.Option("-p", "--profile", help="Bench run profile key"),
            ] = None,
            config_path: Annotated[
                str | None,
                typer.Option(
                    "-c", "--config", help="Path to bench YAML configuration file"
                ),
            ] = None,
        ) -> None:
            """Download MMLongBench-Doc questions and PDF documents from Hugging Face.

            Examples:
                cli bench download
                cli bench download --docs -n 10
                cli bench download --no-docs
            """
            load_env()
            cfg_p = Path(config_path) if config_path else None
            cfg = load_bench_profile(profile_name=profile, config_path=cfg_p)
            adapter = get_benchmark_adapter(cfg.dataset_adapter, project_root=cfg.project_root)

            dataset_dir = cfg.project_root / "data" / "mmlongbench"
            pdfs_dir = Path(cfg.docgraph.paths.sources_dir)

            console.print(
                "[bold cyan]Fetching MMLongBench-Doc questions from Hugging Face...[/bold cyan]"
            )
            questions = adapter.load_dataset(cache_dir=dataset_dir)
            console.print(
                f"[bold green]✓ Loaded {len(questions)} questions into {dataset_dir}[/bold green]"
            )

            if docs:
                all_docs = adapter.get_available_docs(cache_dir=dataset_dir)
                if limit and limit > 0:
                    all_docs = all_docs[:limit]

                console.print(
                    f"[bold cyan]Downloading {len(all_docs)} PDF documents to {pdfs_dir}...[/bold cyan]"
                )
                pdfs_dir.mkdir(parents=True, exist_ok=True)

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console,
                ) as progress:
                    task_id = progress.add_task("Fetching PDFs...", total=len(all_docs))
                    for doc_name in all_docs:
                        progress.update(
                            task_id, description=f"Fetching {doc_name[:30]}..."
                        )
                        try:
                            adapter.fetch_document(doc_name, pdfs_dir)
                        except Exception as exc:
                            logger.warning("Failed to fetch doc {}: {}", doc_name, exc)
                        progress.advance(task_id)

                console.print(
                    f"[bold green]✓ PDF documents ready in {pdfs_dir}[/bold green]"
                )


__all__ = ["BenchCommands"]


__all__ = ["BenchCommands"]
