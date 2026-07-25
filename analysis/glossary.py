"""専門用語を初心者向けのやさしい日本語に翻訳するための辞書。"""
from __future__ import annotations

# 各指標の「これは何？」説明。Streamlit の help ツールチップ等で使う。
GLOSSARY: dict[str, str] = {
    "impressions": "検索結果に表示された回数（見られたチャンスの数）",
    "clicks": "検索結果からクリックされてサイトに来た回数",
    "ctr": "表示されたうち、何%がクリックされたか（クリック率）",
    "position": "検索結果での平均の並び順。小さいほど上位（1に近いほど良い）",
    "sessions": "サイトへの訪問回数",
    "totalUsers": "サイトを訪れた人数（重複を除いた実人数）",
    "screenPageViews": "ページが表示された回数",
    "averageSessionDuration": "1回の訪問あたりの平均滞在時間（秒）",
    "engagementRate": "しっかり見てくれた訪問の割合（すぐ帰らなかった率）",
    "local": "「佐賀」など地域名を含む検索からのクリック（地元で学びたい人への到達度）",
    "beginner": "「初心者」「未経験」「教室」など学び始めの検索からのクリック",
    "engineer": "「エンジニア」「転職」「実務」など実務寄りの検索からのクリック",
    "formLinkClicks": "参加フォームのリンクをクリックして、フォームを開いた回数（送信完了数ではありません）",
}

# 表向きに出す日本語ラベル。
LABELS: dict[str, str] = {
    "impressions": "表示回数",
    "clicks": "クリック",
    "ctr": "クリック率(CTR)",
    "position": "平均順位",
    "sessions": "訪問(セッション)",
    "totalUsers": "訪問者数",
    "screenPageViews": "ページ表示",
    "averageSessionDuration": "平均滞在(秒)",
    "engagementRate": "エンゲージ率",
    "page": "ページ",
}

# GA4 のチャネル名（英語）を日本語に。
CHANNEL_JA: dict[str, str] = {
    "Organic Search": "検索（自然）",
    "Direct": "直接アクセス",
    "Referral": "他サイト経由",
    "Organic Social": "SNS（自然）",
    "Paid Search": "検索広告",
    "Paid Social": "SNS広告",
    "Display": "ディスプレイ広告",
    "Email": "メール",
    "Affiliates": "アフィリエイト",
    "Organic Video": "動画（自然）",
    "Unassigned": "不明",
}

# GA4 のデバイス名を日本語に。
DEVICE_JA: dict[str, str] = {
    "desktop": "パソコン",
    "mobile": "スマホ",
    "tablet": "タブレット",
    "smart tv": "テレビ",
}


def channel_ja(name: str) -> str:
    return CHANNEL_JA.get(name, name)


def device_ja(name: str) -> str:
    return DEVICE_JA.get(name, name)
