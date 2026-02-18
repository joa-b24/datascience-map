#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set

import yaml

NODES_DIR = Path("nodes")
INDEX_DIR = Path("index")
INDEX_NODES = INDEX_DIR / "nodes.yaml"
INDEX_EDGES = INDEX_DIR / "edges.yaml"

TYPE_BY_FOLDER = {
    "domains": "Domain",
    "topics": "Topic",
    "tools": "Tool",
    "projects": "Project",
    "artifacts": "Artifact",
    "courses": "Course",
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def parse_frontmatter(md: str) -> Tuple[Dict[str, Any], str]:
    m = FRONTMATTER_RE.match(md)
    if not m:
        return {}, md
    fm = yaml.safe_load(m.group(1)) or {}
    body = md[m.end():]
    return fm, body

def infer_name_from_body(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.strip().startswith("# "):
            return line.strip()[2:].strip()
    return fallback

def stem_id(p: Path) -> str:
    return p.stem.strip()

def normalize_tags(tags: Any) -> List[str]:
    if tags is None:
        return []
    if isinstance(tags, list):
        return [str(t).strip() for t in tags if str(t).strip()]
    if isinstance(tags, str):
        return [tags.strip()] if tags.strip() else []
    return []

def add_edge(edges: List[Dict[str, str]], edge_set: Set[Tuple[str,str,str]], frm: str, rel: str, to: str):
    if not frm or not rel or not to:
        return
    key = (frm, rel, to)
    if key in edge_set:
        return
    edges.append({"from": frm, "relation": rel, "to": to})
    edge_set.add(key)

def main():
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, str]] = []
    edge_set: Set[Tuple[str,str,str]] = set()

    if not NODES_DIR.exists():
        raise SystemExit("nodes/ directory not found.")

    md_files = list(NODES_DIR.rglob("*.md"))

    # First pass: collect nodes
    for p in md_files:
        folder = p.parent.name
        ntype = TYPE_BY_FOLDER.get(folder, None)
        if not ntype:
            # Unknown folder; skip
            continue

        md = read_text(p)
        fm, body = parse_frontmatter(md)

        nid = str(fm.get("id") or stem_id(p)).strip()
        name = str(fm.get("name") or infer_name_from_body(body, nid)).strip()
        status = str(fm.get("status") or "planned").strip()
        tags = normalize_tags(fm.get("tags"))

        nodes.append({
            "id": nid,
            "type": ntype,
            "name": name,
            "status": status,
            "path": str(p.as_posix()),
            "tags": tags,
        })

    node_ids = {n["id"] for n in nodes}

    # Second pass: collect edges from frontmatter
    for p in md_files:
        folder = p.parent.name
        ntype = TYPE_BY_FOLDER.get(folder, None)
        if not ntype:
            continue

        md = read_text(p)
        fm, _ = parse_frontmatter(md)
        frm = str(fm.get("id") or stem_id(p)).strip()

        # belongs_to -> BELONGS_TO
        for dom in (fm.get("belongs_to") or []):
            to = str(dom).strip()
            add_edge(edges, edge_set, frm, "BELONGS_TO", to)

        # shortcut lists
        for to in (fm.get("covers") or []):
            add_edge(edges, edge_set, frm, "COVERS", str(to).strip())
        for to in (fm.get("uses") or []):
            add_edge(edges, edge_set, frm, "USES", str(to).strip())
        for to in (fm.get("has") or []):
            add_edge(edges, edge_set, frm, "HAS", str(to).strip())
        for to in (fm.get("prereq") or []):
            add_edge(edges, edge_set, frm, "PREREQ", str(to).strip())

        # generic relations list
        for r in (fm.get("relations") or []):
            if not isinstance(r, dict):
                continue
            rel = str(r.get("relation") or "").strip()
            to = str(r.get("to") or "").strip()
            add_edge(edges, edge_set, frm, rel, to)

    # Optional sanity: warn about edges to unknown nodes
    unknown_targets = []
    for e in edges:
        if e["to"] not in node_ids:
            unknown_targets.append(e)
    if unknown_targets:
        print(f"⚠️ Warning: {len(unknown_targets)} edges point to unknown node ids (create stubs or fix ids).")
        # print first few
        for e in unknown_targets[:10]:
            print("  ", e)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_NODES, "w", encoding="utf-8") as f:
        yaml.safe_dump({"nodes": nodes}, f, sort_keys=False, allow_unicode=True)
    with open(INDEX_EDGES, "w", encoding="utf-8") as f:
        yaml.safe_dump({"edges": edges}, f, sort_keys=False, allow_unicode=True)

    print(f"✅ Wrote {INDEX_NODES} with {len(nodes)} nodes")
    print(f"✅ Wrote {INDEX_EDGES} with {len(edges)} edges")

if __name__ == "__main__":
    main()
