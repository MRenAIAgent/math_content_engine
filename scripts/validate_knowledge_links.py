#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from math_content_engine.knowledge_graph import load_algebra_knowledge_graph, build_concept_index
from math_content_engine.templates.registry import get_registry


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    links_path = repo_root / "curriculum" / "algebra1" / "content_textbook_exercise_links.json"
    graph_path = repo_root / "curriculum" / "algebra1" / "algebra_knowledge_graph.json"

    links = json.loads(links_path.read_text(encoding="utf-8"))
    graph = load_algebra_knowledge_graph(graph_path)
    concept_index = build_concept_index(graph)

    registry = get_registry()
    ok = True

    # Validate template ids + concept ids
    for item in links.get("content_templates", []):
        template_id = item.get("template_id")
        if template_id not in registry:
            print(f"[ERROR] Unknown template_id: {template_id}", file=sys.stderr)
            ok = False

        for cid in item.get("concept_ids", []):
            if cid not in concept_index:
                print(f"[ERROR] Unknown concept_id '{cid}' referenced by template '{template_id}'", file=sys.stderr)
                ok = False

        for ref in item.get("textbook_refs", []):
            ref_path = repo_root / ref
            if not ref_path.exists():
                print(f"[ERROR] Missing textbook ref '{ref}' for template '{template_id}'", file=sys.stderr)
                ok = False

    if ok:
        print("[OK] knowledge links look consistent")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

