#!/usr/bin/env python3
"""Validate YAML examples in Beyla docs against docs/config-schema.json.

Beyla ignores unknown or misspelled YAML keys silently, so a doc example can look
valid and still do nothing. This checker finds those keys mechanically.

Usage:
  check_yaml_examples.py FILE.md [FILE.md ...] [--schema PATH] [--json] [--all]

Exit codes: 0 = no problems found, 1 = problems found, 2 = usage or tool error.

Read-only: reads the Markdown files and the schema, writes nothing.
"""
import argparse
import difflib
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("error: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

FENCE = re.compile(r"^\s*```\s*(ya?ml)\b", re.IGNORECASE)
ELLIPSIS = re.compile(r"^\s*(-\s*)?\.\.\.\s*$")
SHELL = re.compile(r"^\s*(\$ |sudo |cat >|curl |docker |kubectl |helm )|<<\s*'?EOF", re.MULTILINE)
CLOSE = re.compile(r"^\s*```\s*$")


def find_schema(md_path, explicit):
    if explicit:
        return explicit
    env = os.environ.get("BEYLA_CONFIG_SCHEMA")
    if env:
        return env
    d = os.path.dirname(os.path.abspath(md_path))
    while d != os.path.dirname(d):
        cand = os.path.join(d, "docs", "config-schema.json")
        if os.path.exists(cand):
            return cand
        d = os.path.dirname(d)
    return None


def extract_blocks(path):
    """Yield (first_content_line, text) for each fenced yaml block."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    i = 0
    while i < len(lines):
        if FENCE.match(lines[i]):
            start = i + 2  # 1-based line of first content line
            body = []
            i += 1
            while i < len(lines) and not CLOSE.match(lines[i]):
                body.append(lines[i])
                i += 1
            yield start, "\n".join(body)
        i += 1


class Validator:
    def __init__(self, schema):
        self.root = schema
        self.defs = schema.get("$defs", {})

    def resolve(self, node):
        seen = 0
        while isinstance(node, dict) and "$ref" in node and seen < 20:
            ref = node["$ref"]
            name = ref.rsplit("/", 1)[-1]
            node = self.defs.get(name, {})
            seen += 1
        return node

    def validate(self, value, node, path):
        node = self.resolve(node)
        if not isinstance(node, dict):
            return []
        for key in ("anyOf", "oneOf"):
            if key in node:
                best = None
                for branch in node[key]:
                    probs = self.validate(value, branch, path)
                    if not probs:
                        return []
                    if best is None or len(probs) < len(best):
                        best = probs
                return best or []
        out = []
        props = node.get("properties")
        addl = node.get("additionalProperties")
        items = node.get("items")
        enum = node.get("enum")
        if isinstance(value, dict):
            if props is not None:
                for k, v in value.items():
                    k = str(k)
                    sub = f"{path}.{k}" if path else k
                    if k in props:
                        out += self.validate(v, props[k], sub)
                    elif isinstance(addl, dict):
                        out += self.validate(v, addl, sub)
                    elif addl is True:
                        continue
                    else:
                        close = difflib.get_close_matches(k, list(props), n=1, cutoff=0.6)
                        hint = f" (did you mean '{close[0]}'?)" if close else ""
                        out.append((sub, "unknown-key", f"unknown key '{k}'{hint}"))
            elif isinstance(addl, dict):
                for k, v in value.items():
                    out += self.validate(v, addl, f"{path}.{k}" if path else str(k))
        elif isinstance(value, list):
            if items is not None:
                for n, v in enumerate(value):
                    out += self.validate(v, items, f"{path}[{n}]")
        elif value is not None:
            if enum and isinstance(value, (str, int, float, bool)):
                if str(value).lower() not in [str(e).lower() for e in enum]:
                    out.append((path, "enum", f"value '{value}' not in {enum}"))
            t = node.get("type")
            custom = props is not None and set(props) == {"Ranges"}
            if t == "object" and props is not None and not custom:
                out.append((path, "type-shape",
                            "schema expects a mapping here; Beyla may accept a scalar via custom "
                            "unmarshaling, so verify in source"))
        return out


def classify(doc, root_props):
    """Return (kind, payload, prefix). kind: beyla | skip."""
    if not isinstance(doc, dict):
        return "skip", None, ""
    keys = {str(k) for k in doc}
    if keys & root_props:
        return "beyla", doc, ""
    # Helm values: config.data holds the Beyla configuration
    cfg = doc.get("config")
    if isinstance(cfg, dict) and isinstance(cfg.get("data"), dict):
        if {str(k) for k in cfg["data"]} & root_props:
            return "beyla", cfg["data"], "config.data"
    return "skip", None, ""


def configmap_payloads(doc, root_props):
    """Yield (name, mapping) for ConfigMap data entries that hold Beyla YAML."""
    if isinstance(doc, dict) and doc.get("kind") == "ConfigMap" and isinstance(doc.get("data"), dict):
        for name, text in doc["data"].items():
            if isinstance(text, str):
                try:
                    inner = yaml.safe_load(text)
                except yaml.YAMLError:
                    continue
                if isinstance(inner, dict) and {str(k) for k in inner} & root_props:
                    yield name, inner


def check_file(path, schema_path, include_all):
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    root_props = set(schema.get("properties", {}))
    v = Validator(schema)
    results = []
    for start, text in extract_blocks(path):
        entry = {"file": path, "line": start, "status": "", "problems": []}
        try:
            docs = list(yaml.safe_load_all(text))
        except yaml.YAMLError as e:
            mark = getattr(e, "problem_mark", None)
            line = start + (mark.line if mark else 0)
            lines = text.split("\n")
            if SHELL.search(text):
                entry["status"] = "syntax-error"
                entry["problems"].append({"line": start, "path": "", "kind": "not-yaml",
                                          "message": "block looks like shell commands, not YAML; "
                                                     "check the fence language"})
            elif any(ELLIPSIS.match(ln) for ln in lines):
                entry["status"] = "skipped-partial-snippet"
            else:
                entry["status"] = "syntax-error"
                entry["problems"].append({"line": line, "path": "", "kind": "yaml-syntax",
                                          "message": str(getattr(e, "problem", e))})
            results.append(entry)
            continue
        checked = False
        for doc in docs:
            kind, payload, prefix = classify(doc, root_props)
            if kind == "beyla":
                checked = True
                for p, k, m in v.validate(payload, schema, prefix):
                    entry["problems"].append({"line": start, "path": p, "kind": k, "message": m})
            for name, inner in configmap_payloads(doc, root_props):
                checked = True
                for p, k, m in v.validate(inner, schema, f"ConfigMap.data.{name}"):
                    entry["problems"].append({"line": start, "path": p, "kind": k, "message": m})
        if not checked:
            entry["status"] = "skipped-not-beyla-config"
            if include_all:
                entry["status"] = "skipped"
        else:
            entry["status"] = "problems" if entry["problems"] else "ok"
        results.append(entry)
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="Markdown files to check")
    ap.add_argument("--schema", help="Path to docs/config-schema.json (default: search up from the file)")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    ap.add_argument("--all", action="store_true", help="List skipped (non-Beyla) blocks too")
    args = ap.parse_args()

    all_results = []
    for f in args.files:
        if not os.path.isfile(f):
            print(f"error: not a file: {f}", file=sys.stderr)
            return 2
        schema_path = find_schema(f, args.schema)
        if not schema_path or not os.path.isfile(schema_path):
            print("error: config-schema.json not found; pass --schema PATH", file=sys.stderr)
            return 2
        all_results += check_file(f, schema_path, args.all)

    problems = sum(len(r["problems"]) for r in all_results)
    if args.json:
        json.dump({"results": all_results, "problem_count": problems}, sys.stdout, indent=2)
        print()
    else:
        for r in all_results:
            if r["status"] == "ok":
                print(f"{r['file']}:{r['line']}: ok")
            elif r["status"] in ("problems", "syntax-error"):
                for p in r["problems"]:
                    where = f" [{p['path']}]" if p["path"] else ""
                    print(f"{r['file']}:{p['line']}:{where} {p['kind']}: {p['message']}")
            elif args.all:
                print(f"{r['file']}:{r['line']}: skipped (not Beyla config)")
        counts = {}
        for r in all_results:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        print(f"summary: {len(all_results)} yaml blocks, {problems} problems, statuses={counts}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
