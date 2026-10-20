#!/usr/bin/env python3
"""Report link style and line-break style in Markdown docs. Read-only.

Checks two house conventions:
  1. Prefer reference-style links ([text][label] with a definition) over inline
     links ([text](url)).
  2. Prefer semantic line breaks: one sentence per line in the Markdown source.
     Reports lines that hold several sentences and lines that wrap mid-sentence.

Usage:
  check_source_format.py FILE.md [FILE.md ...] [--json] [--lines] [--links]

A third check covers reference links and admonitions: a reference-style link used
inside an admonition block must have its definition inside that same block.

Exit codes: 0 = no findings, 1 = findings, 2 = usage or tool error.

The sentence splitter is a heuristic. Treat counts as approximate and confirm a
line by reading it before you report it. It never modifies a file.
"""
import argparse
import json
import re
import sys

ABBREV = {"e.g", "i.e", "etc", "vs", "cf", "approx", "no", "fig", "inc", "ltd", "mr", "mrs", "dr", "st"}
INLINE_LINK = re.compile(r"(?<!\!)\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
REF_DEF = re.compile(r"^\s*\[[^\]]+\]:\s+\S+")
REF_USE = re.compile(r"(?<!\!)\[[^\]]+\]\[[^\]]*\]")
FENCE = re.compile(r"^\s*(```|~~~)")
ADM_OPEN = re.compile(r"\{\{[<%]\s*admonition\b")
ADM_CLOSE = re.compile(r"\{\{[<%]\s*/admonition\b")
LIST_START = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
LIST_PREFIX = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
BOUNDARY = re.compile(r"""([.!?])(["')\]*_]*)\s+(?=["'(\[*_`]*[A-Z0-9])""")


def mask(text):
    """Hide things that contain periods but aren't sentence ends."""
    text = re.sub(r"`[^`]*`", lambda m: "C" * len(m.group(0)), text)
    text = re.sub(r"\]\([^)]*\)", lambda m: "]" + "U" * (len(m.group(0)) - 1), text)
    text = re.sub(r"\]\[[^\]]*\]", lambda m: "]" + "U" * (len(m.group(0)) - 1), text)
    text = re.sub(r"\{\{[^}]*\}\}", lambda m: "S" * len(m.group(0)), text)
    text = re.sub(r"https?://\S+", lambda m: "U" * len(m.group(0)), text)
    return text


def sentence_count(line):
    body = LIST_PREFIX.sub("", line)
    masked = mask(body)
    count = 1
    for m in BOUNDARY.finditer(masked):
        before = masked[: m.start()]
        word = re.findall(r"[A-Za-z.]+$", before)
        last = word[0].rstrip(".").lower() if word else ""
        if m.group(1) == "." and (last in ABBREV or re.fullmatch(r"[a-z]\.?[a-z]?", last or "xx")):
            continue
        if m.group(1) == "." and re.search(r"\d$", before) and re.match(r"\s*\d", masked[m.end():]):
            continue
        count += 1
    return count


def analyze(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    out = {"file": path, "inline_links": [], "ref_defs": 0, "ref_uses": 0,
           "multi_sentence_lines": [], "wrapped_lines": [], "prose_lines": 0, "images_inline": 0}
    i = 0
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    in_code = False
    stack = []          # open admonition block ids; block 0 is the page itself
    block_counter = 0
    pending_pop = False
    defs = []           # (label, block, line)
    uses = []           # (label, block, line, explicit)
    for n in range(i, len(lines)):
        line = lines[n]
        if pending_pop and stack:
            stack.pop()
        pending_pop = False
        if FENCE.match(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        if ADM_OPEN.search(line) and not ADM_CLOSE.search(line):
            block_counter += 1
            stack.append(block_counter)
        cur = stack[-1] if stack else 0
        if ADM_CLOSE.search(line):
            pending_pop = True
        in_admonition = cur > 0
        out["images_inline"] += len(IMAGE.findall(line))
        d = REF_DEF.match(line)
        if d:
            out["ref_defs"] += 1
            defs.append((re.match(r"^\s*\[([^\]]+)\]", line).group(1).lower(), cur, n + 1))
            continue
        out["ref_uses"] += len(REF_USE.findall(line))
        for m in re.finditer(r"(?<!\!)\[([^\]]+)\]\[([^\]]*)\]", line):
            uses.append(((m.group(2) or m.group(1)).lower(), cur, n + 1, True))
        for m in re.finditer(r"(?<![\]\!])\[([^\]]+)\](?![\[(:])", line):
            uses.append((m.group(1).lower(), cur, n + 1, False))
        stripped = line.strip()
        for m in INLINE_LINK.finditer(line):
            out["inline_links"].append({"line": n + 1, "text": m.group(1), "dest": m.group(2),
                                        "in_admonition": in_admonition})
        if (not stripped or stripped.startswith("#") or stripped.startswith("|")
                or stripped.startswith("<!--") or stripped.startswith("{{")
                or stripped.startswith(">") or stripped.startswith("<")):
            continue
        out["prose_lines"] += 1
        nxt = lines[n + 1] if n + 1 < len(lines) else ""
        ns = nxt.strip()
        if ns and not LIST_START.match(nxt) and not ns.startswith(("#", "|", "<", ">", "{{", "```", "~~~", "![", "-", "*", "+")) \
                and not REF_DEF.match(nxt) and not re.search(r"[.!?:]$", stripped.rstrip("*_`\")]'\" ")) \
                and not stripped.endswith(("|", "-->")):
            out["wrapped_lines"].append({"line": n + 1, "text": stripped[:140]})
        k = sentence_count(line)
        if k > 1:
            out["multi_sentence_lines"].append({"line": n + 1, "sentences": k, "text": stripped[:140]})

    # Admonition bodies render on their own, so a reference link inside one needs its
    # definition inside that same block, and page text can't rely on a block's definitions.
    by_block = {}
    for label, block, _ in defs:
        by_block.setdefault(block, set()).add(label)
    all_defs = {label for label, _, _ in defs}
    problems = []
    for label, block, ln, explicit in uses:
        if not explicit and label not in all_defs:
            continue  # literal brackets, not a reference
        if block > 0 and label not in by_block.get(block, set()):
            where = "defined outside this block" if label in all_defs else "no definition found"
            problems.append({"line": ln, "label": label, "kind": "admonition-ref-" + where.replace(" ", "-"),
                             "message": f"reference [{label}] used inside an admonition, {where}"})
        elif block == 0 and label not in by_block.get(0, set()) and label in all_defs:
            problems.append({"line": ln, "label": label, "kind": "page-ref-defined-only-in-admonition",
                             "message": f"reference [{label}] on the page is defined only inside an admonition"})
    out["admonition_ref_problems"] = problems
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--lines", action="store_true", help="list each multi-sentence line")
    ap.add_argument("--links", action="store_true", help="list each inline link")
    args = ap.parse_args()
    results = []
    for f in args.files:
        try:
            results.append(analyze(f))
        except OSError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
    findings = sum(len(r["inline_links"]) + len(r["multi_sentence_lines"]) + len(r["wrapped_lines"]) + len(r["admonition_ref_problems"]) for r in results)
    if args.json:
        json.dump({"results": results, "findings": findings}, sys.stdout, indent=2)
        print()
    else:
        for r in results:
            print(f"{r['file']}: inline_links={len(r['inline_links'])} ref_uses={r['ref_uses']} "
                  f"ref_defs={r['ref_defs']} multi_sentence_lines={len(r['multi_sentence_lines'])} "
                  f"wrapped_lines={len(r['wrapped_lines'])} "
                  f"admonition_ref_problems={len(r['admonition_ref_problems'])}"
                  f"/{r['prose_lines']} prose lines")
            if args.links:
                for l in r["inline_links"]:
                    tag = " [in admonition]" if l["in_admonition"] else ""
                    print(f"  link {r['file']}:{l['line']}: [{l['text']}]({l['dest']}){tag}")
            for l in r["admonition_ref_problems"]:
                print(f"  admonition {r['file']}:{l['line']}: {l['message']}")
            if args.lines:
                for l in r["multi_sentence_lines"]:
                    print(f"  line {r['file']}:{l['line']}: ~{l['sentences']} sentences: {l['text']}")
                for l in r["wrapped_lines"]:
                    print(f"  wrap {r['file']}:{l['line']}: sentence continues on the next line: {l['text']}")
        tot_l = sum(len(r["inline_links"]) for r in results)
        tot_s = sum(len(r["multi_sentence_lines"]) for r in results)
        tot_w = sum(len(r["wrapped_lines"]) for r in results)
        tot_a = sum(len(r["admonition_ref_problems"]) for r in results)
        print(f"summary: {len(results)} files, {tot_l} inline links, {tot_s} multi-sentence lines, "
              f"{tot_w} lines wrapped mid-sentence, {tot_a} admonition reference problems")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
