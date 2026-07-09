"""Search Console API から検索パフォーマンスを取得する。"""
from __future__ import annotations

from urllib.parse import urlparse

import pandas as pd
from googleapiclient.discovery import build

from config import load_settings
from data_sources.auth import get_credentials

_METRICS = ["clicks", "impressions", "ctr", "position"]


def _service():
    return build("searchconsole", "v1", credentials=get_credentials(), cache_discovery=False)


def _query(dimensions: list[str], start_date: str, end_date: str, row_limit: int = 25000) -> pd.DataFrame:
    settings = load_settings()
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    response = (
        _service()
        .searchanalytics()
        .query(siteUrl=settings.gsc_site_url, body=body)
        .execute()
    )

    rows = []
    for row in response.get("rows", []):
        record = {dim: key for dim, key in zip(dimensions, row["keys"])}
        for metric in _METRICS:
            record[metric] = row.get(metric, 0.0)
        rows.append(record)

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=[*dimensions, *_METRICS])
    # ctr は 0〜1 の割合で返るため、%表示に合わせて 0〜100 に変換
    if "ctr" in df.columns and not df.empty:
        df["ctr"] = df["ctr"] * 100
    return df


def _to_path(url: str) -> str:
    """GSC の完全URL（https://domain/path）を GA4 と同じパス表記に正規化。"""
    parsed = urlparse(url)
    path = parsed.path or "/"
    return path


def fetch_by_page(start_date: str, end_date: str) -> pd.DataFrame:
    """ページ別の検索パフォーマンス。GA4 と突き合わせる page 列を正規化して付与。"""
    df = _query(["page"], start_date, end_date)
    if not df.empty:
        df["page"] = df["page"].apply(_to_path)
    return df


def fetch_by_query(start_date: str, end_date: str) -> pd.DataFrame:
    """検索クエリ別のパフォーマンス。"""
    return _query(["query"], start_date, end_date)


def fetch_by_date(start_date: str, end_date: str) -> pd.DataFrame:
    """日別の検索パフォーマンス（推移グラフ用）。"""
    df = _query(["date"], start_date, end_date)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
    return df
