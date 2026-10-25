#!/usr/bin/env python3
"""Check the local Markdown documentation without third-party dependencies."""

import argparse
import json
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from urllib.parse import unquote, urlparse

from render_progress import stale_outputs


REPOSITORIES = (
    "documentation",
    "motion-tennis-camera-tracking",
    "motion-tennis-game-engine",
    "motion-tennis-physics-engine",
    "motion-tennis-controller",
    "debug-units",
)
REQUIRED_DOCS = (
    "overview.md",
    "requirements.md",
    "architecture.md",
    "hardware.md",
    "controller.md",
    "tracking.md",
    "physics.md",
    "game-engine.md",
    "protocol.md",
    "coordinates-and-time.md",
    "timing.md",
    "development.md",
    "testing.md",
    "troubleshooting.md",
    "roadmap.md",
    "adr/README.md",
    "master-plan.md",
    "networking.md",
    "tracking-stack.md",
    "debugging.md",
)
EXCLUDED_DIRECTORIES = {".git", ".venv", "node_modules", "__pycache__"}
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_LINK = re.compile(r"!?\[[^\]\n]*\]\((<[^>\n]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)")
REFERENCE_DEFINITION = re.compile(r"^ {0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)")
HTML_LINK = re.compile(r"\b(?:href|src)=[\"']([^\"']+)[\"']", re.IGNORECASE)
HEADING = re.compile(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$")
EXPLICIT_ANCHOR = re.compile(r"\b(?:id|name)=[\"']([^\"']+)[\"']", re.IGNORECASE)


def slugify(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = text.replace("`", "").replace("*", "")
    text = re.sub(r"[^\w\-\s]", "", text.lower())
    return text.replace(" ", "-")


def reject_json_constant(value):
    raise ValueError("Non-finite JSON constant: " + value)


def finite_json_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Non-finite JSON number: " + value)
    return number


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(source):
    return json.loads(source, parse_constant=reject_json_constant,
                      parse_float=finite_json_float, object_pairs_hook=unique_json_object)


def github_remote(path):
    """Read only the remote URL, never credentials or the full Git configuration."""
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode:
        return None
    remote = result.stdout.strip()
    match = re.fullmatch(r"git@github\.com:([^/]+)/(.+?)(?:\.git)?", remote)
    if match:
        return match.group(1), match.group(2)
    parsed = urlparse(remote)
    if parsed.hostname == "github.com":
        parts = parsed.path.strip("/").removesuffix(".git").split("/")
        if len(parts) == 2:
            return tuple(parts)
    return None


class Checker:
    def __init__(self, documentation, workspace):
        self.documentation = documentation
        self.workspace = workspace
        self.errors = []
        self.skips = set()
        self.counts = Counter()
        self.anchors = {}
        self.links = defaultdict(set)
        self.markdown = []
        self.repo_paths = {}
        self.github_paths = {}
        for name in REPOSITORIES:
            path = documentation if name == "documentation" else workspace / name
            if not path.is_dir():
                self.skips.add("Sibling checkout is unavailable: " + name)
                continue
            self.repo_paths[name] = path
            remote = github_remote(path)
            if remote:
                self.github_paths[remote] = path
            else:
                self.skips.add("Cannot map GitHub links without an origin remote: " + name)
            self.markdown.extend(
                item
                for item in path.rglob("*.md")
                if not any(part in EXCLUDED_DIRECTORIES for part in item.relative_to(path).parts)
            )

    def label(self, path):
        try:
            return str(path.relative_to(self.workspace))
        except ValueError:
            return str(path)

    def error(self, path, line, message):
        self.errors.append("{}:{}: {}".format(self.label(path), line, message))

    def blocks(self, path, source):
        plain = []
        active = None
        contents = []
        start = 0
        language = ""
        for line_number, line in enumerate(source.splitlines(), 1):
            match = FENCE.match(line)
            if active:
                if match and match[1][0] == active[0] and len(match[1]) >= len(active) and not match[2].strip():
                    self.check_block(path, start, language, "\n".join(contents))
                    active = None
                else:
                    contents.append(line)
                plain.append("")
            elif match:
                active = match[1]
                language = match[2].strip().split(maxsplit=1)[0] if match[2].strip() else ""
                contents = []
                start = line_number
                plain.append("")
            else:
                plain.append(line)
        if active:
            self.error(path, start, "Unclosed code fence")
        return plain

    def check_block(self, path, line, language, content):
        self.counts["code fences"] += 1
        if language == "json":
            self.counts["JSON examples"] += 1
            try:
                read_json(content)
            except (json.JSONDecodeError, ValueError) as exc:
                self.error(path, line, "Invalid JSON example: " + str(exc))
        elif language == "mermaid":
            self.counts["Mermaid blocks"] += 1
            lines = [item.strip() for item in content.splitlines() if item.strip() and not item.lstrip().startswith("%%")]
            if not lines:
                self.error(path, line, "Empty Mermaid block")
                return
            declaration = lines[0].split()[0]
            accepted = {"flowchart", "graph", "sequenceDiagram", "stateDiagram-v2", "stateDiagram"}
            if declaration not in accepted:
                self.error(path, line, "Unsupported Mermaid declaration for this lightweight checker: " + declaration)
                return
            if declaration in {"flowchart", "graph", "sequenceDiagram"}:
                starters = {"subgraph"} if declaration in {"flowchart", "graph"} else {"loop", "alt", "opt", "par", "critical", "break", "rect", "box"}
                depth = 0
                for offset, item in enumerate(lines[1:], 1):
                    keyword = item.split()[0]
                    if keyword in starters:
                        depth += 1
                    elif item == "end":
                        depth -= 1
                        if depth < 0:
                            self.error(path, line + offset, "Mermaid end has no opening block")
                            depth = 0
                if depth:
                    self.error(path, line, "Mermaid has unclosed structural blocks")

    def scan(self, path):
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.error(path, 1, "Cannot read UTF-8 Markdown: " + str(exc))
            return []
        if not source.endswith("\n"):
            self.error(path, max(1, len(source.splitlines())), "Missing final newline")
        for line_number, line in enumerate(source.splitlines(), 1):
            if line.rstrip("\t ") != line:
                self.error(path, line_number, "Trailing whitespace")
        plain = self.blocks(path, source)
        anchors = set()
        heading_counts = Counter()
        for line in plain:
            anchors.update(EXPLICIT_ANCHOR.findall(line))
            heading = HEADING.match(line)
            if heading:
                slug = slugify(heading[1])
                count = heading_counts[slug]
                heading_counts[slug] += 1
                anchors.add(slug + ("-" + str(count) if count else ""))
        self.anchors[path.resolve()] = anchors
        found_links = []
        for line_number, line in enumerate(plain, 1):
            found_links.extend((line_number, match[1].strip("<>")) for match in INLINE_LINK.finditer(line))
            reference = REFERENCE_DEFINITION.match(line)
            if reference:
                found_links.append((line_number, reference[1].strip("<>")))
            found_links.extend((line_number, target) for target in HTML_LINK.findall(line))
        return found_links

    def check_link(self, source, line, target):
        parsed = urlparse(target)
        fragment = unquote(parsed.fragment)
        target_path = None
        if parsed.scheme or parsed.netloc:
            if parsed.hostname != "github.com":
                self.counts["external links not fetched"] += 1
                return
            parts = unquote(parsed.path).strip("/").split("/")
            if len(parts) < 2:
                self.counts["external links not fetched"] += 1
                return
            key = tuple(parts[:2])
            local_root = self.github_paths.get(key)
            if local_root is None:
                if parts[1] in self.repo_paths and any(name == parts[1] for _, name in self.github_paths):
                    self.error(source, line, "Project GitHub URL does not match the checkout's origin: " + target)
                    return
                if parts[1] in REPOSITORIES:
                    self.skips.add("Project URL cannot be checked locally: " + "/".join(parts[:2]))
                self.counts["external links not fetched"] += 1
                return
            if len(parts) == 2:
                target_path = local_root / "README.md" if fragment else local_root
            elif len(parts) >= 5 and parts[2] in {"blob", "tree"}:
                # Branch names with slashes need a full Git-aware URL resolver.
                if parts[3] != "main":
                    self.skips.add("Non-main GitHub path is outside this checker's scope: " + target)
                    return
                target_path = local_root.joinpath(*parts[4:])
            else:
                self.counts["external links not fetched"] += 1
                return
        elif parsed.path:
            target_path = source.parent / unquote(parsed.path)
        else:
            target_path = source
        target_path = target_path.resolve()
        self.counts["local links"] += 1
        if not target_path.exists():
            self.error(source, line, "Missing link target: " + target)
            return
        if target_path.suffix.lower() == ".md":
            self.links[source.resolve()].add(target_path)
            if fragment and fragment not in self.anchors.get(target_path, set()):
                self.error(source, line, "Missing heading anchor: " + target)

    def required_content(self):
        root = self.documentation
        for name in REQUIRED_DOCS:
            if not (root / "docs" / name).is_file():
                self.error(root / "README.md", 1, "Required documentation page is missing: docs/" + name)
        for path in self.repo_paths.values():
            for name in ("README.md", "LICENSE"):
                if not (path / name).is_file():
                    self.error(path / name, 1, "Required repository file is missing")
        terms = {
            "architecture.md": ("ball_state_request", "ball_state_response"),
            "protocol.md": ("ball_state_request", "ball_state_response", "controller_input", "feedback_result"),
            "timing.md": ("t0", "tr", "t1"),
        }
        for name, required_terms in terms.items():
            path = root / "docs" / name
            if not path.exists():
                continue
            source = path.read_text(encoding="utf-8")
            for term in required_terms:
                if not re.search(r"\b" + re.escape(term) + r"\b", source):
                    self.error(path, 1, "Required specification term is missing: " + term)
        reachable = set()
        queue = deque([(root / "README.md").resolve()])
        while queue:
            path = queue.popleft()
            if path in reachable:
                continue
            reachable.add(path)
            queue.extend(self.links[path] - reachable)
        for path in self.markdown:
            if path.is_relative_to(root / "docs") and path.resolve() not in reachable:
                self.error(path, 1, "Documentation page is not reachable from the central README")

    def reference_profile(self):
        path = self.documentation / "spec" / "reference-profile.json"
        protobuf = self.documentation / "spec" / "motion.proto"
        if not protobuf.is_file():
            self.error(protobuf, 1, "Required proposed Protobuf contract is missing")
        try:
            profile = read_json(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            self.error(path, 1, "Cannot read finite, unambiguous profile JSON: " + str(exc))
            return
        if not isinstance(profile, dict):
            self.error(path, 1, "Reference profile must be a JSON object")
            return
        self.counts["reference profiles"] += 1

        def value(section, key):
            parent = profile if section is None else profile.get(section)
            candidate = parent.get(key) if isinstance(parent, dict) else None
            if type(candidate) is not int or candidate <= 0:
                self.error(path, 1, "Expected positive integer: " + ".".join(filter(None, (section, key))))
                return None
            return candidate

        def require(condition, message):
            if not condition:
                self.error(path, 1, message)

        names = {
            "rates": ("controller_hz", "physics_tick_us", "camera_target_hz", "pose_minimum_hz"),
            "limits": ("udp_payload_bytes", "batch_transactions", "batch_transactions_per_controller",
                       "physics_queue_per_controller", "controller_pending_transactions",
                       "dedup_retention_us", "dedup_batches"),
            "timing_us": ("response_p99_target", "electrical_p99_target", "controller_expiry",
                          "ball_query_retry", "ball_query_expiry", "commit_retry_1", "commit_retry_2",
                          "commit_ambiguity_pause", "clock_mapping_refresh", "clock_mapping_maximum_age"),
        }
        settings = {key: value(section, key) for section, keys in names.items() for key in keys}
        players = value(None, "players")
        if players is None or any(item is None for item in settings.values()):
            return
        s = settings
        require(players <= 4, "Reference profile supports at most four players")
        require(s["udp_payload_bytes"] <= 1200, "UDP payload exceeds the 1200-byte contract limit")
        wire_integer_maximum = profile["limits"].get("maximum_wire_uint64")
        require(wire_integer_maximum == str(2**56 - 1),
                "Wire uint64 maximum must preserve the eight-byte varint size bound")
        normal_per_controller = (s["controller_hz"] * s["physics_tick_us"] + 999999) // 1000000
        require(normal_per_controller <= s["batch_transactions_per_controller"],
                "Per-controller batch cannot carry the normal samples arriving in one tick")
        require(players * normal_per_controller <= s["batch_transactions"],
                "Batch cannot carry the normal player input load per tick")
        require(s["batch_transactions_per_controller"] <= s["physics_queue_per_controller"],
                "Per-controller batch limit exceeds its input queue")
        require(s["batch_transactions"] <= players * s["batch_transactions_per_controller"],
                "Batch maximum exceeds the sum of its per-controller limits")
        require(s["controller_pending_transactions"] * 1000000 > s["controller_expiry"] * s["controller_hz"],
                "Controller pending-table duration must exceed controller expiry")
        require(s["response_p99_target"] <= s["electrical_p99_target"] <= s["controller_expiry"],
                "Response target must not exceed electrical target or controller expiry")
        require(s["ball_query_retry"] < s["ball_query_expiry"], "Query retry must precede query expiry")
        require(s["commit_retry_1"] < s["commit_retry_2"] < s["commit_ambiguity_pause"],
                "Commit retry times must increase and precede ambiguity pause")
        require(s["clock_mapping_refresh"] <= s["clock_mapping_maximum_age"],
                "Clock mapping refresh interval exceeds its validity age")
        require(s["pose_minimum_hz"] <= s["camera_target_hz"],
                "Minimum pose rate exceeds the camera target rate")
        require(s["dedup_retention_us"] >= s["controller_expiry"],
                "Deduplication retention is shorter than controller expiry")
        require(s["dedup_batches"] * s["physics_tick_us"] >= s["dedup_retention_us"],
                "Deduplication cache cannot retain nominal-rate batches for its declared duration")
        ports = profile.get("ports")
        if not isinstance(ports, dict) or not ports:
            self.error(path, 1, "Reference profile must declare transport ports")
        else:
            valid_ports = all(type(port) is int and 1 <= port <= 65535 for port in ports.values())
            require(valid_ports, "Ports must be integers in 1..65535")
            if valid_ports:
                require(len(set(ports.values())) == len(ports), "Reference service ports must be distinct")
        acceptance = profile.get("acceptance")
        fraction = acceptance.get("maximum_late_or_failed_fraction") if isinstance(acceptance, dict) else None
        require(type(fraction) in (int, float) and 0 <= fraction <= 1,
                "Acceptance failure fraction must be a finite number in 0..1")

    def run(self):
        collected = [(path, self.scan(path)) for path in sorted(set(self.markdown))]
        for path, links in collected:
            for line, target in links:
                self.check_link(path, line, target)
        self.required_content()
        self.reference_profile()
        try:
            for path in stale_outputs(self.documentation):
                self.error(path, 1, "Stale project progress view; run python3 scripts/render_progress.py")
            self.counts["project progress views"] += 2
        except (OSError, UnicodeError, ValueError) as exc:
            self.error(self.documentation / "docs/project-status.md", 1, "Invalid project progress source: " + str(exc))
        print("Checked {} Markdown files in {} available repositories.".format(len(collected), len(self.repo_paths)))
        for key, value in sorted(self.counts.items()):
            print("  {}: {}".format(key, value))
        for skip in sorted(self.skips):
            print("SKIP: " + skip)
        print("LIMIT: no network checks, complete Markdown parser, Mermaid parser/renderer, Protobuf compilation, runtime schema or hardware validation.")
        for error in self.errors:
            print("ERROR: " + error, file=sys.stderr)
        if self.errors:
            print("FAIL: {} documentation error(s).".format(len(self.errors)))
            return 1
        print("PASS: all supported local documentation checks passed.")
        return 0


def main():
    documentation = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=documentation.parent, help="Parent containing optional sibling component checkouts")
    args = parser.parse_args()
    return Checker(documentation, args.workspace.resolve()).run()


if __name__ == "__main__":
    sys.exit(main())
