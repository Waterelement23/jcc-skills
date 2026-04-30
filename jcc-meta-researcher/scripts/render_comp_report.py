#!/usr/bin/env python3
import argparse
import html
import json
import math
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "report_template.html"
RATING_ORDER = ["成型难度", "成型战力", "经济要求", "装备要求", "运营难度", "抗同行", "烂分能力", "吃鸡上限"]


def esc(value):
    return html.escape(str(value), quote=True)


def stars(count):
    return "★" * int(count or 1)


def item_img(item, size_class="item"):
    return (
        f'<img class="{size_class}" title="{esc(item.get("name", item.get("alt", "")))}" '
        f'alt="{esc(item.get("alt", item.get("name", "")))}" src="{esc(item["icon"])}">'
    )


def item_label(item):
    if item.get("name") == "破防者":
        return "破防者"
    return item.get("alt") or item.get("name", "")


def render_unit(unit):
    if not unit:
        return '<div class="grid-hex"></div>'

    item_names = " / ".join(item_label(item) for item in unit.get("items", []))
    title = f'{unit["unit"]} {stars(unit.get("stars", 1))}'
    if item_names:
        title = f"{title}：{item_names}"

    items = "".join(item_img(item) for item in unit.get("items", []))
    badge = f'<div class="captain">{esc(unit["badge"])}</div>' if unit.get("badge") else ""
    role = unit.get("role", "utility")
    return (
        '<div class="grid-hex">'
        f'<div class="unit-card" title="{esc(title)}">'
        f'<div class="stars">{esc(stars(unit.get("stars", 1)))}</div>'
        f'<div class="avatar-frame {esc(role)}"><img class="avatar" alt="{esc(unit["unit"])}" src="{esc(unit["avatar"])}"></div>'
        f"{badge}"
        f'<div class="unit-items">{items}</div>'
        "</div></div>"
    )


def render_board(rows):
    rendered = []
    for index, row in enumerate(rows):
        cls = "grid-row offset" if index % 2 else "grid-row"
        cells = "".join(render_unit(unit) for unit in row)
        rendered.append(f'<div class="{cls}">{cells}</div>')
    return "\n".join(rendered)


def render_traits(traits):
    return "\n".join(
        f'<div class="trait"><span class="trait-icon">{esc(trait["count"])}</span>{esc(trait["name"])}</div>'
        for trait in traits
    )


def render_priority_items(items):
    return "\n".join(item_img(item) for item in items)


def render_augments(augments):
    return "\n".join(
        f'<div class="icon-chip"><img alt="{esc(augment["name"])}" src="{esc(augment["icon"])}"><span>{esc(augment["name"])}</span></div>'
        for augment in augments
    )


def render_gods(gods):
    return "\n".join(
        f'<div class="icon-chip"><i class="god-icon">{esc(god.get("short", god["name"][:1]))}</i><span>{esc(god["name"])}</span></div>'
        for god in gods
    )


def radar_point(index, score, radius=72):
    angle = -math.pi / 2 + index * (2 * math.pi / len(RATING_ORDER))
    scaled = radius * (float(score) / 5.0)
    return round(math.cos(angle) * scaled, 2), round(math.sin(angle) * scaled, 2)


def render_radar(ratings):
    points = " ".join(f"{x},{y}" for x, y in [radar_point(i, ratings[label]) for i, label in enumerate(RATING_ORDER)])
    label_positions = [
        (150, 22), (238, 51), (278, 131), (238, 213),
        (150, 234), (62, 213), (22, 131), (62, 51),
    ]
    labels = []
    for (x, y), label in zip(label_positions, RATING_ORDER):
        labels.append(f'<text class="radar-label" x="{x}" y="{y}" text-anchor="middle">{esc(label)}</text>')
        labels.append(f'<text class="radar-score" x="{x}" y="{y + 13}" text-anchor="middle">{esc(ratings[label])}/5</text>')
    label_html = "\n".join(labels)
    return f'''
        <svg class="radar-chart" viewBox="0 0 300 250" role="img" aria-label="多维评分雷达图">
          <g transform="translate(150 128)">
            <polygon points="0,-72 51,-51 72,0 51,51 0,72 -51,51 -72,0 -51,-51" fill="none" stroke="rgba(255,255,255,.24)"/>
            <polygon points="0,-54 38,-38 54,0 38,38 0,54 -38,38 -54,0 -38,-38" fill="none" stroke="rgba(255,255,255,.16)"/>
            <polygon points="0,-36 25,-25 36,0 25,25 0,36 -25,25 -36,0 -25,-25" fill="none" stroke="rgba(255,255,255,.11)"/>
            <line x1="0" y1="0" x2="0" y2="-82" stroke="rgba(255,255,255,.12)"/>
            <line x1="0" y1="0" x2="58" y2="-58" stroke="rgba(255,255,255,.12)"/>
            <line x1="0" y1="0" x2="82" y2="0" stroke="rgba(255,255,255,.12)"/>
            <line x1="0" y1="0" x2="58" y2="58" stroke="rgba(255,255,255,.12)"/>
            <line x1="0" y1="0" x2="0" y2="82" stroke="rgba(255,255,255,.12)"/>
            <line x1="0" y1="0" x2="-58" y2="58" stroke="rgba(255,255,255,.12)"/>
            <line x1="0" y1="0" x2="-82" y2="0" stroke="rgba(255,255,255,.12)"/>
            <line x1="0" y1="0" x2="-58" y2="-58" stroke="rgba(255,255,255,.12)"/>
            <polygon points="{points}" fill="rgba(255,217,102,.24)" stroke="#f7d774" stroke-width="2"/>
          </g>
          {label_html}
        </svg>
    '''


def render_card(comp):
    notes = comp["notes"]
    return f'''
    <section class="jcc-shell">
      <div class="jcc-topbar">
        <div class="brand"><span class="brand-mark"></span><span>{esc(comp["name"])}</span></div>
        <div class="stage-pill">{esc(comp["stage"])}</div>
      </div>
      <div class="jcc-main">
        <div class="left-area">
          <div class="board-stage"><div class="board-grid">{render_board(comp["board"]["rows"])}</div></div>
          <div class="traits">{render_traits(comp["traits"])}</div>
          <div class="priority"><span>优先装备</span><div class="priority-items">{render_priority_items(comp["priority_items"])}</div></div>
          <div class="visual-section"><div class="visual-section-title">推荐海克斯</div><div class="icon-list">{render_augments(comp["augments"])}</div></div>
          <div class="visual-section"><div class="visual-section-title">推荐星神</div><div class="icon-list">{render_gods(comp["gods"])}</div></div>
        </div>
        <div class="right-area">
          <div class="note-title">过渡思路</div><p class="note">{esc(notes["过渡思路"])}</p>
          <div class="note-title">装备分析</div><p class="note">{esc(notes["装备分析"])}</p>
          <div class="note-title">搜牌节奏</div><p class="note">{esc(notes["搜牌节奏"])}</p>
          <div class="radar-mini">{render_radar(comp["ratings"])}</div>
        </div>
      </div>
    </section>
    '''


def normalize_input(data):
    if "comps" in data:
        return data["comps"]
    return [data]


def collect_image_refs(data):
    refs = []
    for comp in normalize_input(data):
        comp_name = comp.get("name", "unknown comp")
        for row in comp.get("board", {}).get("rows", []):
            for unit in row:
                if not unit:
                    continue
                if unit.get("avatar"):
                    refs.append((f'{comp_name} / {unit.get("unit", "unknown unit")} avatar', unit["avatar"]))
                for item in unit.get("items", []):
                    if item.get("icon"):
                        label = item.get("alt") or item.get("name") or "unknown item"
                        refs.append((f"{comp_name} / {unit.get('unit', 'unknown unit')} item {label}", item["icon"]))

        for item in comp.get("priority_items", []):
            if item.get("icon"):
                label = item.get("alt") or item.get("name") or "unknown item"
                refs.append((f"{comp_name} / priority item {label}", item["icon"]))

        for augment in comp.get("augments", []):
            if augment.get("icon"):
                refs.append((f'{comp_name} / augment {augment.get("name", "unknown augment")}', augment["icon"]))
    return refs


def image_url_loads(url, timeout):
    request = urllib.request.Request(url, headers={"User-Agent": "jcc-meta-researcher/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", response.getcode())
            content_type = response.headers.get("Content-Type", "")
            if status >= 400:
                return False, f"HTTP {status}"
            if content_type and not content_type.lower().startswith("image/"):
                return False, f"not an image ({content_type})"
            response.read(1)
            return True, ""
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, str(exc)


def validate_image_urls(data, timeout=5):
    failures = []
    seen = {}
    for label, url in collect_image_refs(data):
        if url in seen:
            ok, reason = seen[url]
        else:
            ok, reason = image_url_loads(url, timeout)
            seen[url] = (ok, reason)
        if not ok:
            failures.append(f"- {label}: {url} ({reason})")
    if failures:
        raise RuntimeError("Image validation failed:\n" + "\n".join(failures))


def render_report(data):
    comps = normalize_input(data)
    cards = "\n".join(render_card(comp) for comp in comps)
    title = f"金铲铲阵容报告 - {comps[0]['name']}" if comps else "金铲铲阵容报告"
    return TEMPLATE.read_text(encoding="utf-8").format(title=esc(title), cards=cards)


def main():
    parser = argparse.ArgumentParser(description="Render a JCC visual composition report.")
    parser.add_argument("--input", required=True, help="Path to structured composition JSON.")
    parser.add_argument("--output", required=True, help="Path to write HTML report.")
    parser.add_argument("--image-timeout", type=float, default=5, help="Seconds to wait for each remote image.")
    parser.add_argument("--skip-image-check", action="store_true", help="Skip remote image validation.")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    try:
        if not args.skip_image_check:
            validate_image_urls(data, timeout=args.image_timeout)
        html_text = render_report(data)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(html_text, encoding="utf-8")
        print(output)
    except Exception as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
