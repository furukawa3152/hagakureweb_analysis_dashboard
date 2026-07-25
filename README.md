# Hagakure Web 分析ダッシュボード

Search Console（流入前：表示・クリック・CTR・順位）と GA4（流入後：セッション・滞在・行動）を
**ページURLで突き合わせて1画面で見る**ための、自分用ローカルダッシュボード。

GA4 と Search Console を行き来せず、ページごとの「検索で見られているか」と
「来たあとどうか」を同時に確認できる。

## セットアップ

[SETUP.md](./SETUP.md) を参照（Google Cloud の認証準備 → `.env` 設定 → 起動）。

## 起動

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 月次Web分析スキル

このリポジトリには Cursor 用の
[`hagakure-web-analysis`](./.cursor/skills/hagakure-web-analysis/SKILL.md)
スキルが含まれている。月次分析を依頼すると、[`plan.md`](./plan.md) と
[`prompts/RUN_ANALYSIS.md`](./prompts/RUN_ANALYSIS.md) に従って次を実行する。

- GA4 / Search Console の当月・前期データを収集する
- 分析前に対象期間のイベントを確認し、分析コンテキストとして保存する
- 実施済みの改善記録を読み、数値変化の解釈へ反映する
- LP とブログの公開サイトを実査する
- `/Users/itaru/cursor_project/hagakure_blog/` のサイトソースを読み、公開状態と照合する
- 対象者への到達状況、LP・ブログの役割、KGI / KPI、計測上の問題を分析する
- 事実と仮説を分け、A / B / C 分類と優先順位を付けた改善アクションを作る
- `reports/YYYY-MM/` に実測データ、実査メモ、最終レポートを保存する

サイトソースからは、テンプレート、ページモデル、URL、SEO・OGP、CTA・内部リンク、
レスポンシブ対応、アクセシビリティ、計測、表示性能を確認する。記事本文の
データベースは含まれないため、個別記事の内容と本番状態は公開サイトを正とする。
月次分析ではサイトソース自体を変更しない。

### 実施記録と分析コンテキスト

- `reports/action-log.md`: 実際に完了した改善を、`- YYYY-MM-DD: 実施したこと` の形式で記録する。予定や提案は書かない。
- `reports/YYYY-MM/context.md`: 分析対象期間の数値へ影響し得るイベントを、`- YYYY-MM-DD: イベント` の形式で記録する。

`action-log.md` はサイト・計測・運用上の変更履歴、`context.md` はイベント開催、
SNS・メディア掲載、障害、季節要因などの分析背景を残すためのファイル。
月次分析では両方を読むが、イベントと数値変化の因果関係は断定せず、原因仮説の
根拠として扱う。

### 実行方法

Cursor で次のように依頼する。

```text
このプロンプトどおりに月次Web分析を実行し、成果物を reports/ に保存して
@prompts/RUN_ANALYSIS.md
```

期間を指定する場合は、依頼に次を加える。

```text
期間: --days 28 --end YYYY-MM-DD --run-id YYYY-MM
```

指定しない場合は、分析実行日の前日までの28日間と、その直前の同日数を比較する。
初回実行前に [`SETUP.md`](./SETUP.md) に沿って認証と `.env` を設定しておく。

### 毎月実行すること

1. 分析対象月と終了日を確認する。
2. 対象期間の結果へ影響し得るイベントを共有し、`context.md` に保存する。
3. `action-log.md` と `context.md` を読んでから、データ収集とサイト実査を行う。
4. `reports/YYYY-MM/report.md` の事実、仮説、改善アクションを確認する。
5. 実施した改善は `action-log.md` に追記する。
6. 翌月、同じ指標で変化と施策結果を確認する。

成果物の詳細は [`reports/README.md`](./reports/README.md) を参照。

## 構成

```
app.py                 Streamlit のダッシュボード画面
config.py              .env の読み込み・設定検証
data_sources/
  auth.py              サービスアカウント認証（GA4/GSC共通）
  ga4.py               GA4 Data API 取得（ページ別・日別）
  gsc.py               Search Console API 取得（ページ別・クエリ別・日別）
analysis/
  merge.py             ページURLで GA4×GSC を突き合わせる中核ロジック
  insights.py          健康診断・伸び落ち・改善ヒント・クエリ分類の分析
  glossary.py          専門用語のやさしい翻訳・チャネル/デバイス名の和訳
```

## 画面

- **🩺 健康診断**：主要KPIを前期間と比較し、信号機（🟢🟡🔴）で増減を表示
- **💡 改善のヒント**：数字を自動で読み解き「あと一歩／タイトル改善／コンテンツ改善」を提案
- **📄 ページ別 統合ビュー**：検索パフォーマンス × サイト内行動を1行で比較
- **📊 伸び / 落ち**：クリック数が伸びた/落ちたページのランキング
- **📈 推移**：クリック・表示回数・訪問の日別推移
- **🔍 検索キーワード**：検索意図でグルーピングした「ことば地図」＋クエリ一覧
- **🌐 流入経路・デバイス**：どこから来たか／PC・スマホの内訳を円グラフで
