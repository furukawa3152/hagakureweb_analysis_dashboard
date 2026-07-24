---
name: hagakure-web-analysis
description: >-
  Runs the HAGAKURE programming community monthly web analysis in Cursor:
  collect GA4/GSC data, inspect LP and blog, write the plan.md deliverable
  under reports/. Use when the user mentions 月次分析, RUN_ANALYSIS,
  plan.md に従って分析, or asks to execute prompts/RUN_ANALYSIS.md.
---

# HAGAKURE Web 月次分析

## いつ使うか

ユーザーが月次分析・`plan.md` に沿った分析・`@prompts/RUN_ANALYSIS.md` の実行を求めたとき。

## やること

1. **必読**: リポジトリの `prompts/RUN_ANALYSIS.md` を開き、その手順を一字一句の作業指示として実行する。詳細・原則・成果物構成はすべてそこ（と `plan.md`）に従う。
2. **データ**: `python scripts/collect_analysis_data.py` をリポジトリルートで実行し、`reports/<run_id>/raw/` を読む。
3. **実査**: https://hagakurepgm.net と https://hagakurepgm.net/blog/ を確認し、`content-notes.md` を書く。
4. **成果物**: `reports/<run_id>/report.md` に plan.md §7 の 15 章を書く。
5. **禁止**: 秘密鍵の出力、データ不足の断定、急成長・売上前提の施策、レポートに不要な大規模リファクタ。

## ユーザーへの返し方

- 短いエグゼクティブサマリー
- 保存したパス（`report.md` / `content-notes.md` / `raw/`）
- 計測できなかった点があれば一行で

## 参照

- 実行プロンプト: [prompts/RUN_ANALYSIS.md](../../../prompts/RUN_ANALYSIS.md)
- 依頼書: [plan.md](../../../plan.md)
- 収集スクリプト: [scripts/collect_analysis_data.py](../../../scripts/collect_analysis_data.py)
