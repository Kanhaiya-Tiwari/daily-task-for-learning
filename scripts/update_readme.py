#!/usr/bin/env python3
"""Refresh the generated daily section in README.md."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from random import SystemRandom


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
START_MARKER = "<!-- DAILY-DEVOPS-DOSE:START -->"
END_MARKER = "<!-- DAILY-DEVOPS-DOSE:END -->"

DEVOPS_QUOTES = (
    "Automation is not about replacing people; it is about freeing them for better work.",
    "You build it, you run it, you improve it.",
    "Reliable systems are designed, not wished into existence.",
    "Small, frequent improvements beat large, risky changes.",
    "Observability turns guessing into understanding.",
)

LINUX_COMMANDS = (
    ("find . -type f -name '*.log'", "Find all log files below the current directory."),
    ("du -sh *", "Show the size of each item in the current directory."),
    ("tail -f /var/log/syslog", "Follow new lines written to the system log."),
    ("ps aux --sort=-%mem | head", "Show the most memory-hungry processes."),
    ("grep -RIn 'TODO' .", "Recursively find TODOs with line numbers."),
)

PYTHON_TIPS = (
    "Use `pathlib.Path` instead of manually joining file-system strings.",
    "Prefer f-strings for clear, readable string interpolation.",
    "Use `enumerate()` when you need both an index and a value in a loop.",
    "Use `dict.get(key, default)` when a missing key is expected.",
    "Use a context manager (`with`) to close files reliably.",
)

MOTIVATIONAL_LINES = (
    "Progress compounds—ship the next small improvement.",
    "The best time to simplify a workflow is before it becomes urgent.",
    "Curiosity is a powerful debugging tool.",
    "Consistency turns good habits into durable systems.",
    "Every reliable release started as a thoughtful first step.",
)

EMOJIS = ("🚀", "🐧", "⚙️", "🛠️", "✨", "🔥", "💡", "🌱")


def render_daily_section(update_number: int | None, total_updates: int | None) -> str:
    """Return the Markdown that is owned by this script."""
    chooser = SystemRandom()
    command, command_description = chooser.choice(LINUX_COMMANDS)
    today = datetime.now(timezone.utc).date().isoformat()

    lines = [
        START_MARKER,
        "## Daily DevOps Dose",
        "",
        f"**Date (UTC):** {today}",
        "",
        f"> {chooser.choice(DEVOPS_QUOTES)}",
        "",
        f"**Linux command:** `{command}`  ",
        command_description,
        "",
        f"**Python tip:** {chooser.choice(PYTHON_TIPS)}",
        "",
        f"**Motivation:** {chooser.choice(MOTIVATIONAL_LINES)} {chooser.choice(EMOJIS)}",
    ]
    if update_number is not None and total_updates is not None:
        # This keeps each automated commit unique without displaying noisy metadata.
        lines.append(f"<!-- Daily refresh {update_number} of {total_updates} -->")
    lines.append(END_MARKER)
    return "\n".join(lines)


def update_readme(update_number: int | None = None, total_updates: int | None = None) -> None:
    """Replace the generated block without changing hand-written README content."""
    if not README.exists():
        README.write_text("# Project\n", encoding="utf-8")

    current = README.read_text(encoding="utf-8")
    section = render_daily_section(update_number, total_updates)

    start = current.find(START_MARKER)
    end = current.find(END_MARKER)
    if start != -1 and end != -1 and end >= start:
        end += len(END_MARKER)
        updated = current[:start] + section + current[end:]
    elif start != -1 or end != -1:
        raise RuntimeError(
            "README.md has only one daily-section marker. "
            "Restore both markers before running this script."
        )
    else:
        updated = current.rstrip() + "\n\n" + section + "\n"

    if updated != current:
        README.write_text(updated, encoding="utf-8")
        print(f"Updated {README.relative_to(ROOT)}")
    else:
        print("README.md is already current")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update-number", type=int, help="This update's 1-based position.")
    parser.add_argument("--total-updates", type=int, help="Number of updates in this run.")
    args = parser.parse_args()

    if (args.update_number is None) != (args.total_updates is None):
        parser.error("--update-number and --total-updates must be used together")
    if args.update_number is not None and (
        args.update_number < 1
        or args.total_updates < 1
        or args.update_number > args.total_updates
    ):
        parser.error("update numbers must be positive and within the total")

    update_readme(args.update_number, args.total_updates)
