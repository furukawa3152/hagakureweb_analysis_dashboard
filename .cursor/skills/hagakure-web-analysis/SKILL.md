---
name: hagakure-web-analysis
description: >-
  Runs the HAGAKURE monthly web analysis using GA4, Search Console and the
  public LP/blog, then creates practical web and community improvement actions.
  Use for RUN_ANALYSIS, 月次分析, or the step-by-step analysis prompts.
---

# HAGAKURE Web 月次分析

## 基準

1. `plan.md` を目的・範囲・成果物の正とする。
2. 一括実行は `prompts/RUN_ANALYSIS.md` に従う。
3. 2段階実行は `prompts/RUN_ANALYSIS_STEP_BY_STEP.md` に従う。
4. 分析・アクション品質は `prompts/RUN_ANALYSIS.md` の全要件に従う。

## 入力

- 対象期間: 利用者が自然文で指定する
- `inputs/external-events.md`: 今回分へ置き換える
- `inputs/action-log.md`: 完了済みアクションを累積する

利用者へID、連番、保存先、コマンド引数を入力させない。

## 分析段階

1. `prompts/01_ANALYZE.md` を実行する。
2. GA4・GSCデータを実行時に取得する。
3. LPとブログの公開ページを実査する。
4. `plan.md` の6つのWebサイト運営目的を分析する。
5. データ不足を課題の存在へ読み替えない。
6. 事実と仮説を分ける。
7. `reports/analysis.md` だけを作る。アクション案を書かない。

## アクション提案段階

1. 人が修正した場合は修正後の `reports/analysis.md` を正とする。
2. `prompts/02_PROPOSE_ACTIONS.md` を実行する。
3. データ、サイト実査、コミュニティとWebサイトの目的、実施済みアクション、
   外部イベント、広報・編集・運営の実務知見を組み合わせる。
4. 統計的有意差、大きなサンプル数、分析データとの直接対応を提案条件にしない。
5. 各案の主な起点を「データ」「サイト実査」「目的」「実務仮説」から明記する。
6. 各案について、対応目的、提案理由、実施内容、期待する変化、定量・定性の
   確認方法を説明する。
7. Webサイト内の改修だけでなく、広報、投稿・編集支援、地域連携、イベント、
   コミュニティ運営、開発・運営の学習機会も検討する。
8. すぐに行う対応、継続施策、中長期施策を目的と状況に応じて提案し、
   施策の規模や期間を一律に制限しない。
9. 対象者別の件数を固定せず、一般論の羅列ではなく実施可能な内容へ具体化する。
10. 計測上の前提を改善施策と分ける。
11. `inputs/action-log.md` と同じ完了済みアクションを再提案しない。
12. `reports/actions.md` には現在の改善アクション案だけを記載する。

## 指標

- LP外部者のKGIはGoogleフォーム経由の新規参加者10名/年。
- `googleform_click` はリンククリックであり、送信や参加ではない。
- ブログ外部者のKGIは未設定。
- ブログ参加者の記事作成件数は現在値・目標値とも未設定。
- 未設定値を勝手に決定しない。

## 保存

```text
reports/
  analysis.md
  actions.md

.analysis/current/
  raw/
  context.md
  manifest.json
  quality-report.md
  content-notes.md
  stage-status.md
```

過去版、月別成果物、実行IDを作らない。秘密鍵、トークン、認証情報を出力しない。

## 人との境界

分析エージェントは改善アクション案の作成まで行う。実行の最終判断、実装、公開、
現実世界での活動、`inputs/action-log.md` への追記は行わない。人とLLMは
`reports/actions.md` をもとに内容、優先順位、実施方法を調整できる。
