# HAGAKURE Web分析 — 2段階実行

このファイルは、分析結果を確認してからアクション案を作るための共通入口である。
利用者の依頼は2回だけで、段階番号やIDを指定する必要はない。

## 1回目の依頼

```text
prompts/RUN_ANALYSIS_STEP_BY_STEP.mdを読み、段階実行を開始してください。
対象期間: 2026年7月
```

対象期間が指定された開始依頼では、`prompts/01_ANALYZE.md` だけを実行する。
`reports/analysis.md` を作成し、アクションを提案せず停止する。

## 2回目の依頼

分析結果を確認し、必要なら `reports/analysis.md` を修正してから次を送る。

```text
prompts/RUN_ANALYSIS_STEP_BY_STEP.mdを読み、次へ進めてください。
```

`.analysis/current/stage-status.md` が `phase: analysis_complete` であることを確認し、
`prompts/02_PROPOSE_ACTIONS.md` だけを実行する。`reports/actions.md` を作成して停止する。

## 自動判定

| 状態 | 実行すること |
| --- | --- |
| 対象期間付きの開始依頼 | データ収集と分析 |
| `phase: analysis_complete` で次へ進む依頼 | アクション提案 |
| `phase: actions_complete` | 2段階完了を案内し、再実行しない |
| 状態ファイルなしで次へ進む依頼 | 対象期間付きの開始依頼を案内する |

## 2段階完了後

次は実行段階ではなく、人とLLMによるアクション検討である。利用者は通常の文章で、
アクション案の比較、修正、優先順位付け、具体化を依頼できる。

例:

```text
reports/actions.mdのアクション案を、今月4時間以内で実行できる順に比較してください。
```

```text
記事末のコミュニティ紹介を今月実施する方向で、具体的な作業手順を作ってください。
```

何を実行するかの最終判断、サイト変更、公開、現実世界での活動は人が行う。
`inputs/action-log.md` には、実際に完了した内容だけを追記する。
