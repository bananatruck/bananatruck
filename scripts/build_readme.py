#!/usr/bin/env python3
"""Build a compact terminal-style SVG profile README with a real profile image.

This layout is tuned to mimic the Andrew6rant reference spacing:
- compact 20px terminal row rhythm
- right text block starts close to the image
- section rules start after the heading text, so they never overlap
- only the main profile image is shown on the left
"""

from __future__ import annotations

import base64
import calendar
import datetime as dt
import html
import json
import mimetypes
import textwrap
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.json"
FONT = "Consolas, Menlo, Monaco, 'Courier New', monospace"
CHAR_W = 9.6

LIGHT = {
    "page": "#ffffff",
    "card": "#f6f8fa",
    "border": "#d0d7de",
    "text": "#24292f",
    "muted": "#8c959f",
    "key": "#bc4c00",
    "value": "#0969da",
    "green": "#1a7f37",
    "red": "#cf222e",
}

DARK = {
    "page": "#0d1117",
    "card": "#161b22",
    "border": "#30363d",
    "text": "#c9d1d9",
    "muted": "#6e7681",
    "key": "#ffa657",
    "value": "#a5d6ff",
    "green": "#3fb950",
    "red": "#f85149",
}


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def plural(value: int, word: str) -> str:
    return f"{value} {word}{'' if value == 1 else 's'}"


def date_diff(birthday: str) -> str:
    born = dt.date.fromisoformat(birthday)
    today = dt.date.today()

    years = today.year - born.year
    months = today.month - born.month
    days = today.day - born.day

    if days < 0:
        previous_month = today.month - 1 or 12
        previous_month_year = today.year if today.month != 1 else today.year - 1
        days += calendar.monthrange(previous_month_year, previous_month)[1]
        months -= 1

    if months < 0:
        months += 12
        years -= 1

    cake = " birthday" if today.month == born.month and today.day == born.day else ""
    return f"{plural(years, 'year')}, {plural(months, 'month')}, {plural(days, 'day')}{cake}"


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def wrap_text(value: str, width: int) -> list[str]:
    clean = " ".join(str(value).split())
    return textwrap.wrap(clean, width=width, break_long_words=False, break_on_hyphens=False) or [clean]


def clip_def(x: int, y: int, w: int, h: int, clip_id: str, radius: int = 12) -> str:
    return f'<clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" ry="{radius}"/></clipPath>'


def image_element(path: Path, x: int, y: int, w: int, h: int, clip_id: str) -> str:
    return (
        f'<image href="{data_uri(path)}" x="{x}" y="{y}" width="{w}" height="{h}" '
        f'preserveAspectRatio="xMidYMid slice" clip-path="url(#{clip_id})"/>'
    )


def rule_after_text(x: int, y: int, text: str, x2: int, colors: dict[str, str], font_size: int = 18) -> str:
    # Start the horizontal rule after the rendered heading text, with padding.
    start = int(x + (len(text) * CHAR_W * (font_size / 16)) + 28)
    start = min(start, x2 - 80)
    return f'<line x1="{start}" y1="{y}" x2="{x2}" y2="{y}" stroke="{colors["text"]}" stroke-width="1.2" opacity="0.78"/>'


def heading(text: str, y: int, colors: dict[str, str], x: int = 485, x2: int = 1088) -> str:
    shown = f"- {text}"
    return (
        f'<text x="{x}" y="{y}" font-size="18" font-family="{FONT}" fill="{colors["text"]}">{html.escape(shown)}</text>\n'
        f'{rule_after_text(x, y - 6, shown, x2, colors, 18)}'
    )


def terminal_row(label: str, value: str, y: int, colors: dict[str, str]) -> tuple[str, int]:
    """One Andrew-style label/dot/value row with fixed readable alignment."""
    label_x = 485
    value_x = 745
    right_x = 1088
    font_size = 16
    line_height = 20
    after_gap = 0
    approx_char_w = CHAR_W

    wrapped = wrap_text(value, 36)
    label_end = label_x + 21 + int(len(label) * approx_char_w) + 12
    dots_x1 = min(value_x - 32, label_end)
    dots_x2 = value_x - 18

    parts = [
        f'<text x="{label_x}" y="{y}" font-size="{font_size}" font-family="{FONT}">'
        f'<tspan fill="{colors["muted"]}">. </tspan>'
        f'<tspan fill="{colors["key"]}">{html.escape(label)}</tspan>'
        f'<tspan fill="{colors["muted"]}">:</tspan>'
        f'</text>',
    ]

    if dots_x2 > dots_x1 + 8:
        parts.append(
            f'<line x1="{dots_x1}" y1="{y - 6}" x2="{dots_x2}" y2="{y - 6}" '
            f'stroke="{colors["muted"]}" stroke-width="1.5" stroke-linecap="round" '
            f'stroke-dasharray="1 8" opacity="0.72"/>'
        )

    for i, line in enumerate(wrapped):
        parts.append(
            f'<text x="{value_x}" y="{y + i * line_height}" font-size="{font_size}" '
            f'font-family="{FONT}" fill="{colors["value"]}">{html.escape(line)}</text>'
        )

    return "\n".join(parts), y + max(1, len(wrapped)) * line_height + after_gap


def stat_pair_row(left_label: str, left_value: str, right_label: str, right_value: str, y: int, colors: dict[str, str]) -> str:
    """Two compact stats in one continuous Andrew-style row."""
    font_size = 16
    x = 485
    if right_label:
        return (
            f'<text x="{x}" y="{y}" font-size="{font_size}" font-family="{FONT}" xml:space="preserve">'
            f'<tspan fill="{colors["muted"]}">. </tspan>'
            f'<tspan fill="{colors["key"]}">{html.escape(left_label)}</tspan>'
            f'<tspan fill="{colors["muted"]}">: </tspan>'
            f'<tspan fill="{colors["value"]}">{html.escape(left_value)}</tspan>'
            f'<tspan fill="{colors["muted"]}"> | </tspan>'
            f'<tspan fill="{colors["key"]}">{html.escape(right_label)}</tspan>'
            f'<tspan fill="{colors["muted"]}">: </tspan>'
            f'<tspan fill="{colors["value"]}">{html.escape(right_value)}</tspan>'
            f'</text>'
        )
    return (
        f'<text x="{x}" y="{y}" font-size="{font_size}" font-family="{FONT}" xml:space="preserve">'
        f'<tspan fill="{colors["muted"]}">. </tspan>'
        f'<tspan fill="{colors["key"]}">{html.escape(left_label)}</tspan>'
        f'<tspan fill="{colors["muted"]}">: </tspan>'
        f'<tspan fill="{colors["value"]}">{html.escape(left_value)}</tspan>'
        f'</text>'
    )


def build_svg(config: dict[str, Any], mode: str) -> str:
    colors = LIGHT if mode == "light" else DARK
    birthday = config.get("birthday", "2004-01-10")
    uptime = date_diff(birthday)

    width = 1110
    height = 550
    card_x = 12
    card_y = 12
    card_w = width - 24
    card_h = height - 24

    hero_x = 28
    hero_y = 50
    hero_w = 430
    hero_h = 430

    photo_path = ROOT / config.get("photo", "assets/profile.jpg")
    title = html.escape(config.get("title", "keshav@jindal"))

    pieces: list[str] = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        clip_def(hero_x, hero_y, hero_w, hero_h, "heroClip", 10),
        "</defs>",
        f'<rect width="{width}" height="{height}" fill="{colors["page"]}"/>',
        f'<rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="16" fill="{colors["card"]}" stroke="{colors["border"]}"/>',
        image_element(photo_path, hero_x, hero_y, hero_w, hero_h, "heroClip"),
        f'<text x="485" y="40" font-size="18" font-family="{FONT}" fill="{colors["text"]}">{title}</text>',
        rule_after_text(485, 34, title, 1088, colors, 18),
    ]

    y = 70
    for label, raw_value in config.get("profile", []):
        value = str(raw_value).replace("__UPTIME__", uptime)
        row_svg, y = terminal_row(str(label), value, y, colors)
        pieces.append(row_svg)

    y += 16
    for label, raw_value in config.get("languages", []):
        value = str(raw_value).replace("__UPTIME__", uptime)
        row_svg, y = terminal_row(str(label), value, y, colors)
        pieces.append(row_svg)

    y += 16
    for label, raw_value in config.get("hobbies", []):
        value = str(raw_value).replace("__UPTIME__", uptime)
        row_svg, y = terminal_row(str(label), value, y, colors)
        pieces.append(row_svg)

    y += 14
    pieces.append(heading("Contact", y, colors))
    y += 26
    for label, raw_value in config.get("contact", []):
        value = str(raw_value).replace("__UPTIME__", uptime)
        row_svg, y = terminal_row(str(label), value, y, colors)
        pieces.append(row_svg)

    y += 12
    pieces.append(heading("GitHub Stats", y, colors))
    y += 26

    stats = [
        ("Repos", "Pretty impressive", "Contributed", "Also impressive"),
        ("Stars", "Pretty impressive", "Commits", "Pretty impressive"),
        ("Followers", "Pretty impressive", "LOC", "Way too many"),
    ]
    for left_label, left_value, right_label, right_value in stats:
        pieces.append(stat_pair_row(left_label, left_value, right_label, right_value, y, colors))
        y += 20

    pieces.append("</svg>")
    return "\n".join(pieces)


def write_readme(config: dict[str, Any]) -> None:
    username = config.get("username", "bananatruck")
    repo = config.get("repo", f"{username}/{username}")
    name = config.get("name", "Keshav Jindal")
    portfolio_url = config.get("portfolio_url", "https://bananatruck.site")

    readme = f'''<a href="{portfolio_url}">
  <img alt="{html.escape(name)}'s GitHub Profile README" src="https://raw.githubusercontent.com/{repo}/main/light_mode.svg">
</a>
'''
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    config = load_config()
    (ROOT / "light_mode.svg").write_text(build_svg(config, "light"), encoding="utf-8")
    (ROOT / "dark_mode.svg").write_text(build_svg(config, "dark"), encoding="utf-8")
    write_readme(config)
    print("Built README.md, light_mode.svg, and dark_mode.svg")


if __name__ == "__main__":
    main()
