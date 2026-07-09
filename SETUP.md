# セットアップ手順

GA4 × Search Console 統合ダッシュボードを動かすまでの手順。

## 1. Google Cloud 側の準備（手作業）

> Cloud プロジェクトは GA4 を作った Google アカウントと**別アカウントでもOK**。
> データ閲覧権限は後述の「GA4 / GSC 側への追加」で制御されるため。

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成（既存でも可）
2. 以下の **2つの API** を有効化（「APIとサービス → ライブラリ」で検索）
   - **Google Analytics Data API** … レポート数値の取得用（本命）
   - **Google Search Console API** … 検索パフォーマンス取得用
   - ※ Analytics **Admin** API は不要（プロパティ管理用。今回はIDを直接指定するため）
3. サービスアカウントを作成
   - 「IAMと管理 → サービスアカウント → 作成」
   - ロールは付与不要（データ権限は GA4/GSC 側で付ける）
4. キーを発行：作成したサービスアカウント →「キー」→「鍵を追加 → JSON」でダウンロード
5. ダウンロードした JSON を、このリポジトリの `credentials/service-account.json` に置く
   （`credentials/` は `.gitignore` 済み。Git に上がりません）

## 2. サービスアカウントに閲覧権限を付与

JSON 内の `client_email`（`xxx@xxx.iam.gserviceaccount.com`）をコピーして：

- **GA4**：管理 → プロパティのアクセス管理 → ユーザー追加 → 上記メール、権限は「閲覧者」
- **Search Console**：設定 → ユーザーと権限 → ユーザーを追加 → 上記メール、権限は「制限付き」でOK

## 3. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集：

- `GOOGLE_APPLICATION_CREDENTIALS` … `credentials/service-account.json`（既定のまま）
- `GA4_PROPERTY_ID` … GA4 管理画面「プロパティの詳細」に出る数字ID
- `GSC_SITE_URL` … 対象サイト
  - URLプレフィックス型: `https://hagakure-web.com/`
  - ドメインプロパティ型: `sc-domain:hagakure-web.com`

## 4. 依存インストールと起動

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

ブラウザが開いたら、サイドバーで期間を選んで「データ取得」を押す。

## トラブルシュート

- **403 PERMISSION_DENIED** … サービスアカウントのメールを GA4 / GSC に追加したか確認。
- **API not enabled** … Cloud プロジェクトで Data API / Search Console API を有効化したか確認。
- **データが空** … 期間内にデータがあるか、`GA4_PROPERTY_ID` / `GSC_SITE_URL` が正しいか確認。
  当日分は集計が不安定なため、既定では前日までを表示。
