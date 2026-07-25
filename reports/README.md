# 分析レポート出力先

月次分析の成果物をここに保存する。

```
reports/
  action-log.md          # 実施済みの改善記録
  YYYY-MM/
    context.md           # 分析結果に影響し得るイベント
    raw/                 # collect_analysis_data.py の出力（CSV / summary.json）
    report.md            # plan.md §7 の最終成果物
    content-notes.md     # 公開サイト / サイトソースの実査・照合メモ
```

`raw/` は再現用。人が読む本体は `report.md`。
`content-notes.md` には、公開サイトで確認した事実、サイトソースで確認した事実、
両者を照合した改善候補を分けて記録する。

`action-log.md` は `- YYYY-MM-DD: 実施したこと`、`context.md` は
`- YYYY-MM-DD: 結果に影響し得るイベント` の形式で記録する。
月次分析では両方を読むが、イベントと数値変化の因果関係は断定しない。

月次の実行方法と確認事項は、リポジトリ直下の
[`README.md`](../README.md#月次web分析スキル) を参照。
