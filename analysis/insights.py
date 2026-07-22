"""初心者向けの自動分析ロジック。

- 健康診断：期間比較でKPIの増減を出す
- 伸び/落ちページ：ページ別のクリック増減
- 改善のヒント：数字を解釈して日本語アドバイスに変換
- ことば地図：検索クエリを意図でグルーピング
"""
from __future__ import annotations

import pandas as pd

# 増減が±この%未満なら「横ばい」とみなす
FLAT_THRESHOLD = 5.0


def summarize_totals(gsc_page: pd.DataFrame, ga4_page: pd.DataFrame) -> dict:
    """ページ別データを合計して主要KPIを算出。"""
    impr = float(gsc_page["impressions"].sum()) if not gsc_page.empty else 0.0
    clicks = float(gsc_page["clicks"].sum()) if not gsc_page.empty else 0.0
    ctr = (clicks / impr * 100) if impr else 0.0
    sessions = float(ga4_page["sessions"].sum()) if not ga4_page.empty else 0.0
    users = float(ga4_page["totalUsers"].sum()) if not ga4_page.empty else 0.0
    return {
        "impressions": impr,
        "clicks": clicks,
        "ctr": ctr,
        "sessions": sessions,
        "totalUsers": users,
    }


def pct_delta(current: float, previous: float) -> float | None:
    """前期比（%）。前期が0なら比較不能でNoneを返す。"""
    if previous == 0:
        return None
    return (current - previous) / previous * 100


def status_of(delta: float | None) -> str:
    """増減率から状態を返す: up / flat / down / unknown。指標はすべて多いほど良い前提。"""
    if delta is None:
        return "unknown"
    if abs(delta) < FLAT_THRESHOLD:
        return "flat"
    return "up" if delta > 0 else "down"


def build_health(current: dict, previous: dict) -> list[dict]:
    """健康診断カードのデータを組み立てる。"""
    metrics = [
        ("impressions", "検索での表示"),
        ("clicks", "検索からのクリック"),
        ("ctr", "クリック率(CTR)"),
        ("sessions", "サイト訪問"),
        ("totalUsers", "訪問者数"),
    ]
    cards = []
    for key, label in metrics:
        cur = current.get(key, 0.0)
        prev = previous.get(key, 0.0)
        delta = pct_delta(cur, prev)
        cards.append(
            {
                "key": key,
                "label": label,
                "current": cur,
                "delta": delta,
                "status": status_of(delta),
            }
        )
    return cards


def page_movers(cur_gsc: pd.DataFrame, prev_gsc: pd.DataFrame, top: int = 5):
    """クリック数がもっとも伸びた/落ちたページを返す (risers, fallers)。"""
    empty = pd.DataFrame(columns=["page", "clicks_now", "clicks_prev", "change"])
    if cur_gsc.empty and prev_gsc.empty:
        return empty, empty

    cur = (cur_gsc[["page", "clicks"]] if not cur_gsc.empty
           else pd.DataFrame(columns=["page", "clicks"]))
    prev = (prev_gsc[["page", "clicks"]] if not prev_gsc.empty
            else pd.DataFrame(columns=["page", "clicks"]))
    cur = cur.rename(columns={"clicks": "clicks_now"})
    prev = prev.rename(columns={"clicks": "clicks_prev"})

    merged = pd.merge(cur, prev, on="page", how="outer").fillna(0)
    merged["change"] = merged["clicks_now"] - merged["clicks_prev"]

    risers = merged[merged["change"] > 0].sort_values("change", ascending=False).head(top)
    fallers = merged[merged["change"] < 0].sort_values("change").head(top)
    return risers.reset_index(drop=True), fallers.reset_index(drop=True)


def generate_hints(merged: pd.DataFrame) -> list[dict]:
    """統合データ（merge_by_page の結果）から改善のヒントを自動生成。"""
    if merged.empty:
        return []

    df = merged.copy()
    for col in ["impressions", "clicks", "ctr", "position",
                "sessions", "engagementRate", "averageSessionDuration"]:
        if col not in df.columns:
            df[col] = float("nan")

    total_impr = df["impressions"].sum()
    total_clicks = df["clicks"].sum()
    avg_ctr = (total_clicks / total_impr * 100) if total_impr else 0.0
    median_impr = df["impressions"].median()
    median_sessions = df["sessions"].median()
    eng = df["engagementRate"].dropna()
    avg_eng = float(eng.mean()) if not eng.empty else 0.0

    hints: list[dict] = []

    # 🎯 あと一歩ページ：検索結果2ページ目（11〜20位）で表示が多い
    almost = df[(df["position"] >= 11) & (df["position"] <= 20)
                & (df["impressions"] >= median_impr)]
    for _, r in almost.sort_values("impressions", ascending=False).head(5).iterrows():
        hints.append({
            "type": "あと一歩ページ",
            "icon": "🎯",
            "page": r["page"],
            "message": (f"検索順位 {r['position']:.0f}位（検索結果の2ページ目あたり）。"
                        "あと少しで1ページ目に届きます。ここを強化すると流入が伸びやすい。"),
            "detail": f"表示 {int(r['impressions'])}回 / クリック {int(r['clicks'])}回",
        })

    # ✏️ タイトル改善候補：上位表示なのにクリック率が低い
    title = df[(df["position"] <= 10) & (df["impressions"] >= median_impr)
               & (df["ctr"] < avg_ctr)]
    for _, r in title.sort_values("impressions", ascending=False).head(5).iterrows():
        hints.append({
            "type": "タイトル改善候補",
            "icon": "✏️",
            "page": r["page"],
            "message": (f"上位に表示されているのにクリック率が低め"
                        f"（CTR {r['ctr']:.1f}% < 平均 {avg_ctr:.1f}%）。"
                        "タイトルや説明文を見直すとクリックが増えるかも。"),
            "detail": f"表示 {int(r['impressions'])}回 / 順位 {r['position']:.0f}位",
        })

    # 📝 コンテンツ改善候補：訪問は多いが、しっかり読まれていない
    content = df[(df["sessions"] >= median_sessions) & (df["sessions"] > 0)
                 & (df["engagementRate"] < avg_eng)]
    for _, r in content.sort_values("sessions", ascending=False).head(5).iterrows():
        hints.append({
            "type": "コンテンツ改善候補",
            "icon": "📝",
            "page": r["page"],
            "message": (f"訪問は多いのに、しっかり読まれた割合が低め"
                        f"（エンゲージ率 {r['engagementRate']:.0f}% < 平均 {avg_eng:.0f}%）。"
                        "導入文や記事の中身を見直すと改善しやすい。"),
            "detail": (f"訪問 {int(r['sessions'])} / "
                       f"平均滞在 {r['averageSessionDuration']:.0f}秒"),
        })

    return hints


# クエリの意図分類に使うキーワード（補助表示用）
_QUESTION_KW = ["とは", "方法", "やり方", "使い方", "なぜ", "どう", "どうやって",
                "できない", "意味", "理由", "手順", "？", "?"]
_COMPARE_KW = ["おすすめ", "オススメ", "比較", "違い", "ランキング", "vs",
               "選び方", "どっち", "人気"]

# 目的達成ボード用：誰に届いたかのペルソナキーワード
# 1クエリが複数ペルソナに該当し得る（スコアカードは重複カウント可）
_LOCAL_KW = [
    "佐賀", "唐津", "鳥栖", "武雄", "伊万里", "多久", "鹿島", "嬉野",
    "小城", "神埼", "基山", "有田",
]
_BEGINNER_KW = [
    "初心者", "未経験", "入門", "始め方", "はじめ方", "はじめて", "初めて",
    "独学", "学びたい", "習い事", "教室", "スクール", "プログラミング教室",
    "プログラミングスクール", "わかりやすく", "簡単", "子ども", "子供", "キッズ",
]
_ENGINEER_KW = [
    "エンジニア", "転職", "実務", "フレームワーク", "フロントエンド", "バックエンド",
    "インフラ", "キャリア", "案件", "実装", "API", "アルゴリズム", "コーディング",
    "SES", "フルスタック", "サーバーサイド",
]

# 円グラフ用の排他分類の優先順（先にマッチした方を採用）
_PERSONA_PRIORITY = [
    ("local", "📍 佐賀ローカル", _LOCAL_KW),
    ("beginner", "🌱 非エンジニア・学び始め", _BEGINNER_KW),
    ("engineer", "🧑‍💻 エンジニア・実務寄り", _ENGINEER_KW),
]
_PERSONA_OTHER = ("other", "🔎 その他", [])


def classify_query(query: str) -> str:
    for kw in _QUESTION_KW:
        if kw in query:
            return "❓ 知りたい・困りごと"
    for kw in _COMPARE_KW:
        if kw in query:
            return "⚖️ 比較・検討"
    return "🔎 その他のことば"


def _matches_any(query: str, keywords: list[str]) -> bool:
    q = query or ""
    return any(kw in q for kw in keywords)


def classify_persona(query: str) -> str:
    """検索クエリをペルソナで排他分類（表示ラベルを返す）。"""
    for _, label, keywords in _PERSONA_PRIORITY:
        if _matches_any(query, keywords):
            return label
    return _PERSONA_OTHER[1]


def group_queries(query_df: pd.DataFrame) -> pd.DataFrame:
    """検索クエリを意図でグルーピングして集計。"""
    if query_df.empty:
        return pd.DataFrame(columns=["group", "clicks", "impressions", "件数"])
    df = query_df.copy()
    df["group"] = df["query"].apply(classify_query)
    grouped = (
        df.groupby("group")
        .agg(clicks=("clicks", "sum"),
             impressions=("impressions", "sum"),
             件数=("query", "count"))
        .reset_index()
        .sort_values("clicks", ascending=False)
    )
    return grouped.reset_index(drop=True)


def group_queries_by_persona(query_df: pd.DataFrame) -> pd.DataFrame:
    """検索クエリをペルソナで排他グルーピングして集計。"""
    if query_df.empty:
        return pd.DataFrame(columns=["group", "clicks", "impressions", "件数"])
    df = query_df.copy()
    df["group"] = df["query"].apply(classify_persona)
    grouped = (
        df.groupby("group")
        .agg(clicks=("clicks", "sum"),
             impressions=("impressions", "sum"),
             件数=("query", "count"))
        .reset_index()
        .sort_values("clicks", ascending=False)
    )
    return grouped.reset_index(drop=True)


def _persona_subset_totals(query_df: pd.DataFrame, keywords: list[str]) -> dict:
    """キーワードに該当するクエリの合計KPI。"""
    empty = {"impressions": 0.0, "clicks": 0.0, "ctr": 0.0, "position": 0.0, "queries": 0}
    if query_df.empty or "query" not in query_df.columns:
        return empty
    mask = query_df["query"].apply(lambda q: _matches_any(q, keywords))
    subset = query_df[mask]
    if subset.empty:
        return empty
    impr = float(subset["impressions"].sum())
    clicks = float(subset["clicks"].sum())
    ctr = (clicks / impr * 100) if impr else 0.0
    # 表示回数で重み付けした平均順位
    if impr > 0 and "position" in subset.columns:
        position = float((subset["position"] * subset["impressions"]).sum() / impr)
    else:
        position = 0.0
    return {
        "impressions": impr,
        "clicks": clicks,
        "ctr": ctr,
        "position": position,
        "queries": int(len(subset)),
    }


def build_persona_scorecard(
    cur_queries: pd.DataFrame, prev_queries: pd.DataFrame
) -> list[dict]:
    """目的達成ボード用：ペルソナ別の到達度カードを組み立てる。

    1クエリが複数ペルソナに該当する場合は両方に計上する
    （「佐賀 プログラミング 初心者」はローカルにも非エンジニアにも届いている、とみなす）。
    """
    cards = []
    for key, label, keywords in _PERSONA_PRIORITY:
        cur = _persona_subset_totals(cur_queries, keywords)
        prev = _persona_subset_totals(prev_queries, keywords)
        delta = pct_delta(cur["clicks"], prev["clicks"])
        cards.append(
            {
                "key": key,
                "label": label,
                "current_clicks": cur["clicks"],
                "current_impressions": cur["impressions"],
                "current_ctr": cur["ctr"],
                "current_position": cur["position"],
                "current_queries": cur["queries"],
                "prev_clicks": prev["clicks"],
                "delta": delta,
                "status": status_of(delta),
            }
        )
    return cards


def top_queries_for_persona(
    query_df: pd.DataFrame, persona_key: str, top: int = 8
) -> pd.DataFrame:
    """指定ペルソナに該当するクエリをクリック順で返す。"""
    kw_map = {key: kws for key, _, kws in _PERSONA_PRIORITY}
    keywords = kw_map.get(persona_key, [])
    empty_cols = ["query", "clicks", "impressions", "ctr", "position"]
    if query_df.empty or not keywords:
        return pd.DataFrame(columns=empty_cols)
    mask = query_df["query"].apply(lambda q: _matches_any(q, keywords))
    cols = [c for c in empty_cols if c in query_df.columns]
    return (
        query_df[mask][cols]
        .sort_values("clicks", ascending=False)
        .head(top)
        .reset_index(drop=True)
    )
