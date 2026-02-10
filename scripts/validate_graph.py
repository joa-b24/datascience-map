#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from typing import Any, Dict, List, Set

import yaml


def yload(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def die(msgs: List[str]) -> None:
    print("\n❌ Validation failed:\n")
    for m in msgs:
        print(f"- {m}")
    print()
    sys.exit(1)


def warn(msgs: List[str]) -> None:
    if not msgs:
        return
    print("\n⚠️  Warnings:\n")
    for m in msgs:
        print(f"- {m}")
    print()


def main() -> None:
    required = [
        "schema/node_types.yaml",
        "schema/relation_types.yaml",
        "schema/constraints.yaml",
        "index/nodes.yaml",
        "index/edges.yaml",
    ]
    missing = [p for p in required if not os.path.exists(p)]
    if missing:
        die([f"Missing required file: {p}" for p in missing])

    node_types = yload("schema/node_types.yaml") or {}
    rel_types = yload("schema/relation_types.yaml") or {}
    constraints = yload("schema/constraints.yaml") or {}

    allowed_types: Set[str] = set(node_types.keys())
    allowed_rels: Set[str] = set(rel_types.keys())

    conv = constraints.get("conventions", {}) or {}
    id_pattern = conv.get("id_pattern", r"^[a-z0-9_]+$")
    status_values = set(conv.get("status_values", []))

    rx_id = re.compile(id_pattern)

    nodes_doc = yload("index/nodes.yaml") or {}
    edges_doc = yload("index/edges.yaml") or {}

    if not isinstance(nodes_doc, dict) or "nodes" not in nodes_doc or not isinstance(nodes_doc["nodes"], list):
        die(["index/nodes.yaml must be a dict with key 'nodes' as a list"])

    if not isinstance(edges_doc, dict) or "edges" not in edges_doc or not isinstance(edges_doc["edges"], list):
        die(["index/edges.yaml must be a dict with key 'edges' as a list"])

    errors: List[str] = []
    warnings: List[str] = []

    # --- Validate nodes ---
    node_by_id: Dict[str, Dict[str, Any]] = {}
    type_by_id: Dict[str, str] = {}

    for i, n in enumerate(nodes_doc["nodes"]):
        if not isinstance(n, dict):
            errors.append(f"Node #{i} is not an object")
            continue

        nid = (n.get("id") or "").strip()
        ntype = (n.get("type") or "").strip()
        name = (n.get("name") or "").strip()
        path = (n.get("path") or "").strip()
        status = (n.get("status") or "").strip()

        if not nid:
            errors.append(f"Node #{i} missing 'id'")
            continue
        if not rx_id.match(nid):
            errors.append(f"Node id '{nid}' does not match pattern {id_pattern}")
            continue
        if nid in node_by_id:
            errors.append(f"Duplicate node id '{nid}' in index/nodes.yaml")
            continue
        if ntype not in allowed_types:
            errors.append(f"Node '{nid}' has unknown type '{ntype}'")
            continue
        if not name:
            warnings.append(f"Node '{nid}' has empty 'name' (recommended)")
        if status and status_values and status not in status_values:
            errors.append(f"Node '{nid}' has invalid status '{status}' (allowed: {sorted(status_values)})")

        if not path:
            errors.append(f"Node '{nid}' missing 'path'")
        else:
            if not os.path.exists(path):
                warnings.append(f"Node '{nid}' path does not exist: {path}")
            else:
                # filename should be <id>.md
                expected = f"{nid}.md"
                actual = os.path.basename(path)
                if actual != expected:
                    warnings.append(f"Node '{nid}' path filename '{actual}' != expected '{expected}'")

        node_by_id[nid] = n
        type_by_id[nid] = ntype

    # --- Validate edges ---
    edges = edges_doc["edges"]
    out_edges = defaultdict(list)
    in_edges = defaultdict(list)

    for i, e in enumerate(edges):
        if not isinstance(e, dict):
            errors.append(f"Edge #{i} is not an object")
            continue

        src = (e.get("from") or "").strip()
        rel = (e.get("relation") or "").strip()
        dst = (e.get("to") or "").strip()

        if not src or not rel or not dst:
            errors.append(f"Edge #{i} must have 'from', 'relation', 'to'")
            continue
        if src not in node_by_id:
            errors.append(f"Edge #{i} references unknown 'from' id '{src}'")
            continue
        if dst not in node_by_id:
            errors.append(f"Edge #{i} references unknown 'to' id '{dst}'")
            continue
        if rel not in allowed_rels:
            errors.append(f"Edge #{i} has unknown relation '{rel}'")
            continue

        # type compatibility
        rel_def = rel_types.get(rel, {}) or {}
        allowed_from = set(rel_def.get("from", []) or [])
        allowed_to = set(rel_def.get("to", []) or [])
        src_type = type_by_id[src]
        dst_type = type_by_id[dst]
        if allowed_from and src_type not in allowed_from:
            errors.append(f"Edge #{i}: relation '{rel}' cannot start from type '{src_type}'")
            continue
        if allowed_to and dst_type not in allowed_to:
            errors.append(f"Edge #{i}: relation '{rel}' cannot point to type '{dst_type}'")
            continue

        out_edges[src].append((rel, dst))
        in_edges[dst].append((rel, src))

    if errors:
        die(errors)

    # --- Apply minimal constraints ---
    rules = constraints.get("rules", {}) or {}
    limits = constraints.get("limits", {}) or {}

    def count_out(nid: str, rel: str) -> int:
        return sum(1 for r, _ in out_edges.get(nid, []) if r == rel)

    def get_out_targets(nid: str, rel: str) -> List[str]:
        return [t for r, t in out_edges.get(nid, []) if r == rel]

    # topic_must_belong_to_one_domain
    if rules.get("topic_must_belong_to_one_domain", False):
        for nid, t in type_by_id.items():
            if t == "Topic":
                c = count_out(nid, "BELONGS_TO")
                if c != 1:
                    errors.append(f"Topic '{nid}' must have exactly 1 BELONGS_TO edge (has {c})")

    # project_must_use_at_least_one_tool
    if rules.get("project_must_use_at_least_one_tool", False):
        for nid, t in type_by_id.items():
            if t == "Project":
                c = count_out(nid, "USES")
                if c < 1:
                    errors.append(f"Project '{nid}' must have at least 1 USES edge")

    # project_must_cover_something
    if rules.get("project_must_cover_something", False):
        for nid, t in type_by_id.items():
            if t == "Project":
                c = count_out(nid, "COVERS")
                if c < 1:
                    errors.append(f"Project '{nid}' must have at least 1 COVERS edge")

    # artifact_must_be_attached_or_cover
    if rules.get("artifact_must_be_attached_or_cover", False):
        for nid, t in type_by_id.items():
            if t == "Artifact":
                incoming_has = sum(1 for r, _ in in_edges.get(nid, []) if r == "HAS")
                outgoing_covers = count_out(nid, "COVERS")
                if incoming_has < 1 and outgoing_covers < 1:
                    errors.append(f"Artifact '{nid}' must have incoming HAS or outgoing COVERS")

    # PREREQ max out degree
    max_prereq = int(limits.get("prereq_max_out_degree_per_topic", 3))
    for nid, t in type_by_id.items():
        if t == "Topic":
            prereqs = get_out_targets(nid, "PREREQ")
            if len(prereqs) > max_prereq:
                warnings.append(f"Topic '{nid}' has {len(prereqs)} PREREQ edges (limit {max_prereq})")

    if errors:
        die(errors)

    warn(warnings)
    print("✅ Validation OK")
    print(f"   Nodes: {len(node_by_id)}")
    print(f"   Edges: {len(edges)}")


if __name__ == "__main__":
    main()
