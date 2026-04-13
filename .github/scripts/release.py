#!/usr/bin/env python3
"""Semantic release: parse conventional commits, bump version, update changelog."""

import json
import os
import re
import subprocess
import sys
from datetime import date

COMMIT_RE = re.compile(
    r"^(feat|fix|refactor|perf|docs|chore|style|test|ci|build)"
    r"(\([^)]+\))?"
    r"(!)?:\s*(.+)$"
)

VERSION_FILES = [
    (".claude-plugin/plugin.json", ["version"]),
    (".claude-plugin/marketplace.json", ["plugins", 0, "version"]),
    ("package.json", ["version"]),
]

SECTION_MAP = {
    "feat": "Added",
    "fix": "Fixed",
    "refactor": "Changed",
    "perf": "Changed",
}

RELEASABLE = {"feat", "fix", "refactor", "perf"}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def get_latest_tag():
    r = run(["git", "describe", "--tags", "--abbrev=0"])
    return r.stdout.strip() if r.returncode == 0 else None


def get_commits_since(tag):
    cmd = ["git", "log", "--pretty=format:%s"]
    if tag:
        cmd.insert(2, f"{tag}..HEAD")
    r = run(cmd)
    return [l for l in r.stdout.strip().splitlines() if l] if r.returncode == 0 else []


def parse_commits(subjects):
    commits = []
    for subj in subjects:
        if subj.startswith("chore(release):"):
            continue
        m = COMMIT_RE.match(subj)
        if m:
            kind, scope, breaking, msg = m.groups()
            scope = scope[1:-1] if scope else None
            commits.append({
                "type": kind,
                "scope": scope,
                "breaking": bool(breaking),
                "message": msg,
            })
    return commits


def determine_bump(commits):
    if any(c["breaking"] for c in commits):
        return "major"
    types = {c["type"] for c in commits}
    if "feat" in types:
        return "minor"
    if types & RELEASABLE:
        return "patch"
    return None


def bump_version(version_str, bump):
    parts = [int(x) for x in version_str.lstrip("v").split(".")]
    if bump == "major":
        parts = [parts[0] + 1, 0, 0]
    elif bump == "minor":
        parts = [parts[0], parts[1] + 1, 0]
    else:
        parts = [parts[0], parts[1], parts[2] + 1]
    return ".".join(str(p) for p in parts)


def update_version_files(new_version):
    for filepath, keys in VERSION_FILES:
        with open(filepath) as f:
            data = json.load(f)
        obj = data
        for k in keys[:-1]:
            obj = obj[k]
        obj[keys[-1]] = new_version
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")


def build_changelog_section(new_version, commits):
    sections = {}
    for c in commits:
        section = SECTION_MAP.get(c["type"])
        if not section:
            continue
        entry = f"- **{c['scope']}:** {c['message']}" if c["scope"] else f"- {c['message']}"
        sections.setdefault(section, []).append(entry)

    lines = [f"## {new_version} ({date.today().isoformat()})", ""]
    for heading in ["Added", "Changed", "Fixed"]:
        if heading in sections:
            lines.append(f"### {heading}")
            lines.extend(sections[heading])
            lines.append("")
    return "\n".join(lines)


def update_changelog(section_text):
    changelog = "CHANGELOG.md"
    if os.path.exists(changelog):
        with open(changelog) as f:
            content = f.read()
        marker = "# Changelog\n\n"
        idx = content.find(marker)
        if idx >= 0:
            insert_at = idx + len(marker)
            content = content[:insert_at] + section_text + "\n" + content[insert_at:]
        else:
            content = f"# Changelog\n\n{section_text}\n{content}"
    else:
        content = f"# Changelog\n\n{section_text}\n"
    with open(changelog, "w") as f:
        f.write(content)


def set_output(key, value):
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"{key}={value}\n")
    else:
        print(f"{key}={value}")


def main():
    tag = get_latest_tag()
    base_version = tag.lstrip("v") if tag else "0.0.0"
    subjects = get_commits_since(tag)

    if not subjects:
        print("No new commits since last tag. Skipping release.")
        return

    commits = parse_commits(subjects)
    if not commits:
        print("No conventional commits found. Skipping release.")
        return

    bump = determine_bump(commits)
    if not bump:
        print("Only non-releasable commits (docs/chore/etc). Skipping release.")
        return

    new_version = bump_version(base_version, bump)
    print(f"Release: {base_version} → {new_version} ({bump})")

    section = build_changelog_section(new_version, commits)
    update_version_files(new_version)
    update_changelog(section)

    with open("/tmp/release_notes.md", "w") as f:
        f.write(section)

    set_output("new_version", new_version)


if __name__ == "__main__":
    main()
