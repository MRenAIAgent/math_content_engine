from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple


def get_default_algebra_knowledge_graph_path() -> Path:
    """
    Return the default path to the shared Algebra knowledge graph JSON.

    This repo stores the canonical file under:
      math_content_engine/curriculum/algebra1/algebra_knowledge_graph.json

    We locate the repo root by walking up from this file until we find
    `pyproject.toml`.
    """
    here = Path(__file__).resolve()
    repo_root = next((p for p in here.parents if (p / "pyproject.toml").exists()), None)
    if repo_root is None:
        # best-effort fallback for src/ layout
        repo_root = here.parents[3]

    return repo_root / "curriculum" / "algebra1" / "algebra_knowledge_graph.json"


def load_algebra_knowledge_graph(path: Path | None = None) -> Dict[str, Any]:
    """
    Load the algebra knowledge graph JSON into a Python dict.
    """
    graph_path = path or get_default_algebra_knowledge_graph_path()
    return json.loads(graph_path.read_text(encoding="utf-8"))


def build_concept_index(graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Build an index {concept_id -> concept_dict}.
    """
    concepts = graph.get("concepts", [])
    return {c["id"]: c for c in concepts if isinstance(c, dict) and "id" in c}


def validate_concept_ids(
    concept_ids: Iterable[str],
    *,
    graph: Dict[str, Any] | None = None,
    graph_path: Path | None = None,
) -> Tuple[bool, list[str]]:
    """
    Validate that all concept_ids exist in the knowledge graph.

    Returns (ok, missing_ids).
    """
    g = graph or load_algebra_knowledge_graph(graph_path)
    index = build_concept_index(g)
    missing = [cid for cid in concept_ids if cid not in index]
    return (len(missing) == 0, missing)

