#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple

import yaml


def yload(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    nodes_doc = yload("index/nodes.yaml") or {}
    edges_doc = yload("index/edges.yaml") or {}
    nodes = nodes_doc.get("nodes", []) or []
    edges = edges_doc.get("edges", []) or []

    type_by_id: Dict[str, str] = {}
    status_by_id: Dict[str, str] = {}
    for n in nodes:
        type_by_id[n["id"]] = n["type"]
        status_by_id[n["id"]] = n.get("status", "unknown")

    print("\n📌 Node counts:")
    c = Counter(n["type"] for n in nodes)
    for t, k in sorted(c.items()):
        print(f"  - {t}: {k}")

    print("\n✅ Status counts:")
    cs = Counter(status_by_id.values())
    for s, k in sorted(cs.items()):
        print(f"  - {s}: {k}")

    print("\n🔗 Edge counts:")
    ce = Counter(e["relation"] for e in edges)
    for r, k in sorted(ce.items()):
        print(f"  - {r}: {k}")

    # Most used tools (USES -> Tool)
    tool_use = Counter()
    for e in edges:
        if e["relation"] == "USES" and type_by_id.get(e["to"]) == "Tool":
            tool_use[e["to"]] += 1

    print("\n🧰 Most used tools (USES -> Tool):")
    for tid, k in tool_use.most_common(10):
        print(f"  - {tid}: {k}")

    # Orphan topics (no incoming COVERS)
    covered_topics = set()
    for e in edges:
        if e["relation"] == "COVERS" and type_by_id.get(e["to"]) == "Topic":
            covered_topics.add(e["to"])

    topic_ids = {n["id"] for n in nodes if n["type"] == "Topic"}
    orphans = sorted(topic_ids - covered_topics)
    print("\n🕳️ Orphan topics (no incoming COVERS):")
    print(f"  Count: {len(orphans)}")
    for tid in orphans[:25]:
        print(f"  - {tid}")
    if len(orphans) > 25:
        print(f"  ... +{len(orphans) - 25} more")

    # Projects with no artifacts
    out_edges = defaultdict(list)
    for e in edges:
        out_edges[e["from"]].append(e)

    projects = [n["id"] for n in nodes if n["type"] == "Project"]
    no_art = []
    for pid in projects:
        if not any(e["relation"] == "HAS" for e in out_edges.get(pid, [])):
            no_art.append(pid)

    print("\n📦 Projects with no HAS->Artifact edges:")
    print(f"  Count: {len(no_art)}")
    for pid in no_art[:25]:
        print(f"  - {pid}")
    if len(no_art) > 25:
        print(f"  ... +{len(no_art) - 25} more")

    print()


if __name__ == "__main__":
    main()
