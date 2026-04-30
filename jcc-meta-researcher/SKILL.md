---
name: jcc-meta-researcher
description: Research current-version 金铲铲之战 / 金铲铲 / JCC team compositions with a maintained local meta knowledge base. Use only when the user explicitly mentions 金铲铲, 铲铲, 金铲铲之战, or JCC and asks about阵容, 羁绊, 弈子, 装备, 海克斯, D牌, 拉人口, 当前版本强势阵容, or ranked climbing recommendations.
---

# JCC Meta Researcher

Use this skill to answer version-aware 金铲铲 composition questions.

## Core Rule

Before giving a meta recommendation, check the local knowledge base version and verify whether the live game version changed. If the version or hotfix state changed, update the knowledge base first, then answer.

## Reference Files

- Read `references/current-version.md` first for the local knowledge base state.
- Read `references/season-overview.md` for season systems and stable context.
- Read the relevant file in `references/versions/` for current meta tiers.
- Read relevant files in `references/comps/` for detailed comp cards.
- Append to `references/update-log.md` when updating knowledge.

## Workflow

1. Confirm the request is explicitly about 金铲铲.
2. Read `references/current-version.md`.
3. Search online for the current official game version or hotfix state.
4. Compare online version facts with the local knowledge base.
5. If unchanged, answer from local references.
6. If changed, update `current-version.md`, create or update `versions/<version>.md`, update affected comp cards, and append `update-log.md`.
7. If online checking fails, answer from local references and clearly say `未完成联网版本复核，以下基于本地知识库`.
8. Answer in concise, actionable Chinese.

## Source Priority

Use this priority order:

1. Official announcements, official sites, Tencent-related publishing channels, and official update notes.
2. Mainstream comp lists and guide sites for meta heat and consensus.
3. Video and community content as supporting evidence only.
4. Model reasoning only to explain likely effects, not as standalone evidence for high-confidence recommendations.

Official updates decide factual changes. Multi-source agreement decides meta confidence. Single-source recommendations belong in 有争议可玩 or 观察名单 unless strongly supported by official changes and reasoning.

## Output Tiers

Separate recommendations into:

- 高置信推荐
- 有争议可玩
- 观察名单
- 已削弱 / 不推荐

When sources disagree, keep the disagreement visible instead of forcing a single certainty.

## Required Output

Every answer must include:

- 当前知识库版本
- 联网复核结果
- 使用来源 or source summary
- 不确定性

For each重点阵容, include:

- 评级
- 适合输入条件
- 不推荐条件
- 成型阵容
- 默认站位
- 推荐装备
- 推荐海克斯
- D牌节奏
- 拉人口节奏
- 多维评分
- 一句话判断

## Visual Reports

When the user asks for a webpage, visual display, chart, board, or rendered阵容页:

1. Build structured composition JSON with board rows, units, traits, priority items, augments, 星神, notes, and ratings.
2. Run `scripts/render_comp_report.py --input <composition.json> --output <report.html>`.
3. The renderer validates unit avatar, item icon, and augment icon URLs before writing HTML. If any image cannot load, fix the URL or replace the asset and rerun.
4. Return the generated HTML path or browser URL to the user.

The visual report renderer uses:

- A 7-column hex board with each unit inside its owning hex cell.
- Current-season square unit avatars from CommunityDragon when available.
- Real item icons instead of color blocks.
- Recommended海克斯 and 星神 under priority items.
- A radar chart with dimension labels and scores directly on the chart.

Do not use generic LoL champion portraits or `splash_centered` art as the primary unit avatar when current-season square icons are available. Do not show unit names on the board; keep names in `title` and `alt` text.

## Input Handling

When the user gives a trait or core champion:

- Prefer comps that meaningfully use that trait or champion.
- If no high-confidence comp exists, say the current version does not recommend forcing it.
- If the champion is only a utility unit, do not present it as a core carry.
- If the trait is mainly transitional, explain realistic transition paths.

When the user asks for current-version strong comps:

- Return 3 高置信推荐 comps.
- Return 2 有争议可玩 comps.
- Add 观察名单 when useful.

## Knowledge Base Updates

When updating references:

- Update `references/current-version.md` with version, season, check date, update date, source summary, and force-recheck status.
- Create or update `references/versions/<version>.md` with official changes, meta trend, tiered recommendations, downgraded comps, and source disagreements.
- Create or update only affected `references/comps/<comp-slug>.md` files.
- Append one concise entry to `references/update-log.md`.
- Keep official facts separate from meta interpretation.

## Boundaries

Do not claim an answer is current when version recheck failed. Do not treat a single guide as enough for T0 status. Do not present entertainment comps as ranked meta comps. Do not ignore item mismatch, contesting players, low HP, or broken economy. Do not promise guaranteed ranking gains.
