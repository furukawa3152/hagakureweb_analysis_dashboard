"""GA4 Data API からページ別・日別の指標を取得する。"""
from __future__ import annotations

import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Filter,
    FilterExpression,
    Metric,
    RunReportRequest,
)

from config import load_settings
from data_sources.auth import get_credentials

# GA4 で取得する指標。CV(keyEvents)は環境により未設定だとエラーになり得るので、
# まずは安全な基本指標に絞る。必要になったら keyEvents を追加する。
_METRICS = [
    "sessions",
    "totalUsers",
    "screenPageViews",
    "averageSessionDuration",
    "engagementRate",
]
FORM_CLICK_EVENT = "googleform_click"


def _client() -> BetaAnalyticsDataClient:
    return BetaAnalyticsDataClient(credentials=get_credentials())


def _run(dimension: str, start_date: str, end_date: str) -> pd.DataFrame:
    settings = load_settings()
    request = RunReportRequest(
        property=f"properties/{settings.ga4_property_id}",
        dimensions=[Dimension(name=dimension)],
        metrics=[Metric(name=m) for m in _METRICS],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=100000,
    )
    response = _client().run_report(request)

    rows = []
    for row in response.rows:
        record = {dimension: row.dimension_values[0].value}
        for metric_name, metric_value in zip(_METRICS, row.metric_values):
            record[metric_name] = float(metric_value.value)
        rows.append(record)

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=[dimension, *_METRICS])
    # engagementRate は 0〜1 の割合で返るため %表示に合わせて変換
    if "engagementRate" in df.columns and not df.empty:
        df["engagementRate"] = df["engagementRate"] * 100
    return df


def fetch_by_page(start_date: str, end_date: str) -> pd.DataFrame:
    """ページパス別の指標。突き合わせ用に page 列（先頭スラッシュのパス）を付与。"""
    df = _run("pagePath", start_date, end_date)
    df = df.rename(columns={"pagePath": "page"})
    return df


def fetch_by_date(start_date: str, end_date: str) -> pd.DataFrame:
    """日別の指標（推移グラフ用）。"""
    df = _run("date", start_date, end_date)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
        df = df.sort_values("date")
    return df


def fetch_by_channel(start_date: str, end_date: str) -> pd.DataFrame:
    """流入経路（チャネル）別の指標。円グラフ用。"""
    df = _run("sessionDefaultChannelGroup", start_date, end_date)
    return df.rename(columns={"sessionDefaultChannelGroup": "channel"})


def fetch_by_device(start_date: str, end_date: str) -> pd.DataFrame:
    """デバイス（PC/スマホ/タブレット）別の指標。"""
    df = _run("deviceCategory", start_date, end_date)
    return df.rename(columns={"deviceCategory": "device"})


def fetch_form_clicks(start_date: str, end_date: str) -> pd.DataFrame:
    """参加フォームへのリンククリックを日付・リンク先別に取得。"""
    settings = load_settings()
    request = RunReportRequest(
        property=f"properties/{settings.ga4_property_id}",
        dimensions=[Dimension(name="date"), Dimension(name="linkUrl")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(
                    value=FORM_CLICK_EVENT,
                    match_type=Filter.StringFilter.MatchType.EXACT,
                ),
            )
        ),
        limit=100000,
    )
    response = _client().run_report(request)
    rows = [
        {
            "date": row.dimension_values[0].value,
            "linkUrl": row.dimension_values[1].value,
            "eventCount": float(row.metric_values[0].value),
        }
        for row in response.rows
    ]
    df = pd.DataFrame(rows, columns=["date", "linkUrl", "eventCount"])
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
        df = df.sort_values(["date", "linkUrl"])
    return df
