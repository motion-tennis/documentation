#!/usr/bin/env python3
"""Render the README project dashboard from the canonical Markdown ledger."""

import argparse
from datetime import date
from html import escape
from pathlib import Path
import re
import sys
from textwrap import wrap


START = "<!-- project-progress:start -->"
END = "<!-- project-progress:end -->"
STAGES = tuple("S" + str(i) for i in range(8))
STATES = {
    "Active, incomplete": ("ACTIVE", "#a7f36b", "#183b32"),
    "Blocked": ("BLOCKED", "#ffc775", "#3c3023"),
    "Not released": ("NOT RELEASED", "#a8b9c6", "#152832"),
    "Accepted": ("ACCEPTED", "#73e0c3", "#183b32"),
    "Deferred": ("SEPARATE SCOPE", "#a8b9c6", "#152832"),
}


def section(source, heading):
    """Read one named H2 section, rejecting missing or repeated headings."""
    parts = re.split(r"^## " + re.escape(heading) + r"\s*$", source, flags=re.M)
    if len(parts) != 2:
        raise ValueError("Expected exactly one section: " + heading)
    return re.split(r"^## ", parts[1], maxsplit=1, flags=re.M)[0]


def snapshot(ledger, definitions):
    active = re.findall(r"^\*\*Active stage: (S[0-7]) — (.+)\.\*\*$", ledger, re.M)
    reviewed = re.findall(r"^\*\*Last evidence review: (\d{4}-\d{2}-\d{2})\.\*\*", ledger, re.M)
    if len(active) != 1 or len(reviewed) != 1:
        raise ValueError("Expected one active stage and one evidence-review date")
    date.fromisoformat(reviewed[0])
    rows = re.findall(r"^\| (S\d+) \| ([^|]+) \|[^\n]+\|$",
                      section(ledger, "Stage state"), re.M)
    names = re.findall(r"^\| \*\*(S\d+) — (.+?)\*\* \|",
                       section(definitions, "Stage sequence and acceptance gates"), re.M)
    if sorted(key for key, _ in rows) != list(STAGES):
        raise ValueError("Stage state must contain each of S0–S7 exactly once")
    if sorted(key for key, _ in names) != list(STAGES):
        raise ValueError("Stage definitions must contain each of S0–S7 exactly once")
    states = {key: value.strip() for key, value in rows}
    names = dict(names)
    if any(state not in STATES for state in states.values()):
        raise ValueError("Unknown stage state; use the vocabulary in project-status.md")
    selected, title = active[0]
    if names[selected] != title:
        raise ValueError("Active-stage title differs from the shared stage definition")
    if states[selected] not in {"Active, incomplete", "Blocked", "Accepted"}:
        raise ValueError("Selected stage must be active, blocked or accepted")
    if any(key != selected and value in {"Active, incomplete", "Blocked"}
           for key, value in states.items()):
        raise ValueError("Only the selected stage may be active or blocked")
    if any(states[key] == "Deferred" for key in STAGES[:7]):
        raise ValueError("Deferred is reserved for S7; unreleased core stages use Not released")
    if selected != "S7" and states["S7"] != "Deferred":
        raise ValueError("S7 must stay deferred until it is explicitly selected")
    core = [states[key] == "Accepted" for key in STAGES[:7]]
    if core != sorted(core, reverse=True):
        raise ValueError("Core stage acceptance must follow the shared sequence")
    index = STAGES.index(selected)
    if not all(core[:index]) or any(core[index + 1:]):
        raise ValueError("Selected stage conflicts with the accepted stage sequence")
    checklist = section(ledger, "Active gate checklist")
    binding = re.findall(r"^\*\*Checklist stage: (S\d+)\.\*\*$", checklist, re.M)
    if binding != [selected]:
        raise ValueError("Checklist stage must match the selected active stage")
    tasks = re.findall(r"^- \[([ xX])\] (.+)$", checklist, re.M)
    if not tasks:
        raise ValueError("The active gate checklist must contain at least one item")
    done = sum(mark.lower() == "x" for mark, _ in tasks)
    if states[selected] == "Accepted" and done != len(tasks):
        raise ValueError("An accepted stage cannot have unchecked gate items")
    return {"active": selected, "names": names, "states": states, "reviewed": reviewed[0],
            "accepted": sum(core), "done": done, "total": len(tasks),
            "next": next((text for mark, text in tasks if mark == " "), None)}


def svg_text(x, y, content, size=18, color="#e7f0f2", weight=400):
    return ('<text x="{}" y="{}" font-size="{}" fill="{}" font-weight="{}">{}</text>'
            .format(x, y, size, color, weight, escape(content)))


def render_svg(data):
    selected = data["active"]
    label, accent, _ = STATES[data["states"][selected]]
    description = ("Selected stage {}: {}. {} of 7 core gates accepted. "
                   "{} of {} active gate checklist items complete. S7 is separate scope.")
    description = description.format(selected, data["names"][selected], data["accepted"],
                                     data["done"], data["total"])
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="592" viewBox="0 0 1120 592" role="img" aria-labelledby="title description">',
        '<title id="title">Motion Tennis project progress</title>',
        '<desc id="description">' + escape(description) + '</desc>',
        '<rect width="1120" height="592" rx="24" fill="#0b1c25"/>',
        '<g fill="none" stroke="#25434a" stroke-width="1.5" opacity="0.55">',
        '<path d="M855 0V132M1080 0V132M855 66H1080M967 0V132M855 22H1080M855 110H1080"/>',
        '</g>',
        '<g font-family="DejaVu Sans, Arial, sans-serif">',
        svg_text(32, 40, "MOTION TENNIS  /  PROJECT PROGRESS", 16, "#97adb7", 600),
        svg_text(32, 91, selected + "  " + data["names"][selected], 30, "#f2f7f8", 700),
        svg_text(32, 123, "Evidence reviewed " + data["reviewed"], 16, "#97adb7"),
        '<rect x="876" y="82" width="212" height="36" rx="18" fill="#152832"/>',
        svg_text(895, 106, label, 16, accent, 700),
    ]
    metrics = [("CORE GATES ACCEPTED", str(data["accepted"]) + " / 7", "S0 through S6"),
               ("ACTIVE GATE CHECKLIST", str(data["done"]) + " / " + str(data["total"]), selected + " review items"),
               ("EXTENSION TRACK", "S7", STATES[data["states"]["S7"]][0])]
    for i, (heading, value, detail) in enumerate(metrics):
        x = 32 + i * 360
        parts.extend([
            '<rect x="{}" y="152" width="336" height="94" rx="12" fill="#122a33"/>'.format(x),
            svg_text(x + 20, 179, heading, 13, "#97adb7", 600),
            svg_text(x + 20, 222, value, 30, "#f2f7f8", 700),
            svg_text(x + 125, 218, detail, 15, "#b6c9d0"),
        ])
    for i, key in enumerate(STAGES):
        x, y = 32 + (i % 4) * 270, 272 + (i // 4) * 126
        state, color, fill = STATES[data["states"][key]]
        border = color if key == selected or state == "ACCEPTED" else "#31464f"
        dashed = ' stroke-dasharray="6 5"' if key == "S7" else ""
        parts.extend([
            '<rect x="{}" y="{}" width="246" height="110" rx="12" fill="{}" stroke="{}" stroke-width="{}"{}/>'.format(
                x, y, fill, border, 2 if key == selected else 1, dashed),
            svg_text(x + 16, y + 25, key, 16, color, 700),
            svg_text(x + 54, y + 25, state, 11, color, 600),
        ])
        for line, content in enumerate(wrap(data["names"][key], width=24)):
            parts.append(svg_text(x + 16, y + 54 + line * 21, content, 17, "#e7f0f2", 500))
    parts.extend([
        svg_text(32, 550, "Reviewed gates and checklist items are separate counts, not an overall completion percentage.", 15, "#97adb7"),
        svg_text(32, 574, "SOURCE  docs/project-status.md   ·   Stage transitions require a recorded project decision.", 13, "#97adb7"),
        '</g>', '</svg>',
    ])
    return "\n".join(parts) + "\n"


def render_summary(data):
    next_item = data["next"] or "All selected-stage checklist items are complete; consult the recorded gate decision."
    # Link labels survive; document-relative targets belong to the source ledger.
    next_item = re.sub(r"!?\[([^\]\n]+)\]\([^\n)]+\)", r"\1", next_item)
    next_item = re.sub(r"\[([^\]\n]+)\]\[[^\]\n]*\]", r"\1", next_item)
    return "\n".join([
        START,
        '<!-- Generated by scripts/render_progress.py; edit the central ledger, not this block. -->',
        '',
        '[![Project stage dashboard](assets/project-progress.svg)](docs/project-status.md)',
        '',
        '**{} — {}** · {} · Evidence reviewed **{}**.'.format(
            data["active"], data["names"][data["active"]],
            data["states"][data["active"]], data["reviewed"]),
        '',
        '**Accepted core gates: {}/7** · **Active gate checklist: {}/{}**. These count reviewed gates and checklist items, not overall completion.'.format(
            data["accepted"], data["done"], data["total"]),
        '',
        '**Next checkpoint:** ' + next_item,
        '',
        '[Evidence and checklist](docs/project-status.md#active-gate-checklist) · [Stage plan](docs/project-stages.md) · [Take a bounded task](docs/contribution-workflow.md#task-brief)',
        '', END,
    ])


def expected_outputs(root):
    ledger = (root / "docs/project-status.md").read_text(encoding="utf-8")
    definitions = (root / "docs/project-stages.md").read_text(encoding="utf-8")
    data = snapshot(ledger, definitions)
    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1 or readme.index(START) >= readme.index(END):
        raise ValueError("README needs exactly one ordered project-progress marker pair")
    updated = readme[:readme.index(START)] + render_summary(data) + readme[readme.index(END) + len(END):]
    return {readme_path: updated, root / "assets/project-progress.svg": render_svg(data)}


def stale_outputs(root):
    return [path for path, content in expected_outputs(root).items()
            if not path.exists() or path.read_text(encoding="utf-8") != content]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail on stale generated views without writing files")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if args.check:
            stale = stale_outputs(root)
            if stale:
                print("STALE: " + ", ".join(str(path.relative_to(root)) for path in stale), file=sys.stderr)
                print("Run: python3 scripts/render_progress.py", file=sys.stderr)
                return 1
            print("PASS: README progress and SVG match the central status")
        else:
            for path, content in expected_outputs(root).items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
                print("Updated " + str(path.relative_to(root)))
    except (OSError, UnicodeError, ValueError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
