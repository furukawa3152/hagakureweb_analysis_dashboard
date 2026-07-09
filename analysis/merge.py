"""GA4 と GSC をページURLで突き合わせる中核ロジック。"""
from __future__ import annotations

import pandas as pd


def merge_by_page(ga4_df: pd.DataFrame, gsc_df: pd.DataFrame) -> pd.DataFrame:
    """ページパスをキーに、検索(前)とサイト内行動(後)を1行に統合する。

    outer join で、GSCにしか無い/GA4にしか無いページも欠損なく残す。
    """
    merged = pd.merge(
        gsc_df,
        ga4_df,
        on="page",
        how="outer",
        suffixes=("_gsc", "_ga4"),
    )

    # 数値列の欠損は 0 埋め（順位だけは 0 埋めすると誤解を招くので除外）
    fill_zero = ["clicks", "impressions", "sessions", "totalUsers", "screenPageViews"]
    for col in fill_zero:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)

    # 見やすい列順に並べ替え（存在する列だけ）
    preferred = [
        "page",
        "impressions", "clicks", "ctr", "position",   # GSC: 流入前
        "sessions", "totalUsers", "screenPageViews",
        "averageSessionDuration", "engagementRate",     # GA4: 流入後
    ]
    ordered = [c for c in preferred if c in merged.columns]
    rest = [c for c in merged.columns if c not in ordered]
    merged = merged[ordered + rest]

    if "clicks" in merged.columns:
        merged = merged.sort_values("clicks", ascending=False)

    return merged.reset_index(drop=True)
