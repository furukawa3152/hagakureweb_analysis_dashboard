---
name: hagakure-web-analysis
description: >-
  Runs the HAGAKURE programming community monthly web analysis in Cursor:
  collect analysis context and GA4/GSC data, inspect the public LP/blog and
  local site source, and write the plan.md deliverable under reports/. Use
  when the user mentions 月次分析, RUN_ANALYSIS, plan.md に従って分析, or
  asks to execute prompts/RUN_ANALYSIS.md.
---

# HAGAKURE Web 月次分析

## いつ使うか

ユーザーが月次分析・`plan.md` に沿った分析・`@prompts/RUN_ANALYSIS.md` の実行を求めたとき。

## やること

1. **必読**: リポジトリの `prompts/RUN_ANALYSIS.md` を開き、その手順を一字一句の作業指示として実行する。詳細・原則・成果物構成はすべてそこ（と `plan.md`）に従う。
2. **事前確認**: データ収集を始める前に、分析対象期間の結果へ影響し得るイベントがあったかユーザーに必ず確認し、回答を `reports/<run_id>/context.md` に保存する。回答を得るまでは分析を開始しない。
3. **実施記録**: `reports/action-log.md` を必ず読み、分析対象期間中に実施されたサイト・計測・運用上の改善を評価へ反映する。
4. **データ**: `python scripts/collect_analysis_data.py` をリポジトリルートで実行し、`reports/<run_id>/raw/` を読む。GA4 の `googleform_click` を参加フォームへの到達を示す代替指標として必ず集計し、当期・前期のクリック数を比較する。
5. **公開サイト実査**: https://hagakurepgm.net と https://hagakurepgm.net/blog/ を確認する。
6. **サイトソース実査**: `/Users/itaru/cursor_project/hagakure_blog/` を読み、公開サイトの観察結果と照合する。特にテンプレート、ページモデル、URL、メタデータ・OGP、構造化データ、CTA・内部リンク、レスポンシブ対応、アクセシビリティ、計測コード、表示性能に関係する実装を確認する。記事本文のデータベースがないため、個別記事の内容や本番データは公開サイトを正とし、ソースだけから推測しない。
7. **実査メモ**: `content-notes.md` に「公開サイトで確認した事実」「サイトソースで確認した事実」「両者を照合した改善候補」を分けて書く。ソース根拠には可能な範囲でファイルパスを付ける。
8. **成果物**: `reports/<run_id>/report.md` に plan.md §7 の 15 章を書く。改善アクションには、該当する場合は実装対象のファイルまたは機能領域を記載する。
9. **解釈**: `action-log.md` と `context.md` の出来事は確認された事実として記載できるが、数値変化との因果関係は断定せず、原因仮説の根拠として扱う。
10. **指標の区別**: `googleform_click` はフォームを開いた回数であり、フォーム送信完了数や新規参加者数そのものではない。plan.md の年次 KGI「新規参加者10名」に対する代替指標として扱い、送信・参加実績が別途確認できない場合は未計測と明記する。
11. **禁止**: 秘密鍵・環境変数・認証情報の読み取りや出力、データ不足の断定、急成長・売上前提の施策、レポート作成中のサイトソース変更、レポートに不要な大規模リファクタ。

## 実施記録の形式

`reports/action-log.md` は次の形式だけを使う。

```markdown
# 実施記録

- 2026-07-25: 参加フォームリンクのクリックをGA4 APIで取得する処理を追加
```

改善を実際に完了したときだけ追記する。予定・提案・状態・担当者・効果などは書かない。

## 分析コンテキストの形式

`reports/<run_id>/context.md` には、イベントの日付と内容だけを書く。

```markdown
# 分析コンテキスト

- 2026-07-10: HAGAKUREのイベントを開催
- 2026-07-15: SNSで特定記事が紹介された
```

イベントが無い場合も確認済みであることを残す。

```markdown
# 分析コンテキスト

- 2026-06-26 .. 2026-07-23: 特記事項なし
```

## ユーザーへの返し方

- 短いエグゼクティブサマリー
- 保存したパス（`report.md` / `content-notes.md` / `raw/`）
- 計測できなかった点があれば一行で

## 参照

- 実行プロンプト: [prompts/RUN_ANALYSIS.md](../../../prompts/RUN_ANALYSIS.md)
- 依頼書: [plan.md](../../../plan.md)
- 収集スクリプト: [scripts/collect_analysis_data.py](../../../scripts/collect_analysis_data.py)
