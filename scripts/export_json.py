#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import yaml


def yload(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    nodes_doc = yload("index/nodes.yaml") or {}
    edges_doc = yload("index/edges.yaml") or {}
    meta = yload("graph/graph.meta.yaml") if False else None  # optional future
    # We'll export minimal meta for now
    graph_out = {
        "meta": {
            "name": "knowledge-map",
            "exported_at": datetime.utcnow().isoformat() + "Z",
        },
        "nodes": nodes_doc.get("nodes", []) or [],
        "edges": edges_doc.get("edges", []) or [],
    }

    out_path = "build/graph.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph_out, f, ensure_ascii=False, indent=2)

    print(f"✅ Exported: {out_path}")
    print(f"   Nodes: {len(graph_out['nodes'])} | Edges: {len(graph_out['edges'])}")


if __name__ == "__main__":
    main()
