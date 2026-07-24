# コンテンツ実査メモ（2026-07）

- 実査日: 2026-07-24 JST
- 取得方法: HTTP で HTML を取得して構造を確認（実ブラウザの見た目・表示速度は未計測）

## LP（https://hagakurepgm.net）

| 項目 | 確認内容 |
| --- | --- |
| タイトル | `HAGAKUREプログラミング塾｜佐賀でプログラミングを学ぶ人達のコミュニティです。` |
| メタディスクリプション | `佐賀のプログラミングコミュニティ。HAGAKURE PROGRAMMING塾のWebページ` |
| 主な見出し | About us / アウトプットで学びを共有 / こんな方におすすめ / 受講者の声 / 入塾までの流れ / Dojo / makimono |
| CTA・参加導線 | ナビ「参加フォーム」→ `https://forms.gle/N8ipEt2RFSs8bt4a9`。本文にも参加フォームリンク。画像ボタンは別 URL の Google Form（`docs.google.com/forms/d/e/1FAIpQLS...`）へ |
| 内部リンク | `/blog/`（Scroll）、`/term_use/`（参加規約）、`/saga_bot` など |
| 外部リンク | Facebook、Google Form |
| 計測タグ | **あり**（`G-PQMQ82P18K`、`GTM-WLK68MXV` / gtag・GTM） |
| モバイル | HTML 上はレスポンシブ想定。実機確認は未実施 |

所見（実査ベース）:

- コミュニティ趣旨・入塾フロー・受講者の声があり、外部者向けの説明は一通り揃っている。
- ヘッダの参加導線と画像ボタンで **フォーム URL が2系統**ある（同一フォームの短縮/正式か、別フォームかは未確認）。
- ナビからブログへは行ける。

## ブログ（https://hagakurepgm.net/blog/）

| 項目 | 確認内容 |
| --- | --- |
| タイトル（一覧） | `HAGAKUREプログラミング塾\|Scroll` |
| メタディスクリプション | **なし**（一覧・個別記事とも未確認範囲では未設定） |
| 位置づけ文言 | 「Scrollは、HAGAKUREプログラミング塾の参加者が運営するブログサイトです。」 |
| 投稿の様子 | 一覧に複数の最近記事（例: 2026-07 前後の JAWS-UG・RunCat・Cursor・v0 など）。参加者アウトプットの場として機能している様子 |
| 記事を書く | `https://hagakurepgm.net/accounts/google/login/`（Google ログイン） |
| LP への戻り | フッタ相当に「HAGAKURE PROGRAMMING塾のWebサイトはこちらでござる」→ `/`。ガイドライン → `/blog_guidelines/` |
| 参加フォーム導線 | 一覧 HTML 上では **参加フォームへの直接 CTA は目立たない**（LP に戻るリンクはある） |
| 個別記事の title | **全記事とも `<title>` がサイト共通**（`HAGAKUREプログラミング塾\|Scroll`）。記事固有名は `og:title` / `h1` にある |
| 計測タグ | **なし**（一覧・個別とも gtag / GTM / G- を検出できず） |

個別記事サンプル（検索上位ページ）:

| path | h1 / og:title |
| --- | --- |
| `/blog/124/` | RunCat NeoでAIコーディングツールの使用量を表示 |
| `/blog/107/` | Gemma4 vs Gemma3 |
| `/blog/97/` | Moonshine Voiceを実行してみる |
| `/blog/94/` | vibe-local を触ってみた |
| `/blog/ollamallm/` | OllamaでローカルLLM動作が爆速になった話 |
| `/blog/gpt-oss-vs-gemma3/` | gpt-oss vs gemma3 |

## 未確認

- 実ブラウザでのモバイル表示・表示速度（Core Web Vitals）
- 2つの Form URL が同一か別か
- フォーム送信数（GA4 / フォーム側の実数）
- ブログ投稿者数の正確な人数（一覧からの推定のみ）
