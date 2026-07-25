#!/usr/bin/env python3
"""plan.md 月次分析用の GA4 / GSC データを収集し、reports/<run_id>/raw/ に保存する。

Python 3.14 + pandas の segfault を避けるため、標準ライブラリ中心で CSV 出力する。

使い方:
  source .venv/bin/activate
  python scripts/collect_analysis_data.py
  python scripts/collect_analysis_data.py --days 28 --run-id 2026-07
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from google.analytics.data_v1beta import BetaAnalyticsDataClient  # noqa: E402
from google.analytics.data_v1beta.types import (  # noqa: E402
    DateRange,
    Dimension,
    Filter,
    FilterExpression,
    Metric,
    RunReportRequest,
)
from googleapiclient.discovery import build  # noqa: E402

from config import load_settings  # noqa: E402
from data_sources.auth import get_credentials  # noqa: E402

GA4_METRICS = [
    "sessions",
    "totalUsers",
    "screenPageViews",
    "averageSessionDuration",
    "engagementRate",
]
GSC_METRICS = ["clicks", "impressions", "ctr", "position"]
FORM_CLICK_EVENT = "googleform_click"


def site_segment(page: str) -> str:
    path = (page or "").strip() or "/"
    if path == "/blog" or path.startswith("/blog/"):
        return "blog"
    return "lp"


def period_pair(end: date, days: int) -> tuple[date, date, date, date]:
    start = end - timedelta(days=days - 1)
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)
    return start, end, prev_start, prev_end


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def to_path(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path or "/"


def ga4_report(
    client: BetaAnalyticsDataClient,
    property_id: str,
    dimension: str,
    start: str,
    end: str,
) -> list[dict]:
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=dimension)],
        metrics=[Metric(name=m) for m in GA4_METRICS],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        limit=100000,
    )
    response = client.run_report(request)
    rows: list[dict] = []
    for row in response.rows:
        record = {dimension: row.dimension_values[0].value}
        for name, value in zip(GA4_METRICS, row.metric_values):
            num = float(value.value)
            if name == "engagementRate":
                num *= 100
            record[name] = num
        rows.append(record)
    return rows


def ga4_form_clicks(
    client: BetaAnalyticsDataClient,
    property_id: str,
    start: str,
    end: str,
) -> list[dict]:
    """参加フォームへのリンククリックを日付・リンク先別に取得する。"""
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date"), Dimension(name="linkUrl")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date=start, end_date=end)],
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
    response = client.run_report(request)
    return [
        {
            "date": row.dimension_values[0].value,
            "linkUrl": row.dimension_values[1].value,
            "eventCount": float(row.metric_values[0].value),
        }
        for row in response.rows
    ]


def gsc_query(service, site_url: str, dimensions: list[str], start: str, end: str) -> list[dict]:
    response = (
        service.searchanalytics()
        .query(
            siteUrl=site_url,
            body={
                "startDate": start,
                "endDate": end,
                "dimensions": dimensions,
                "rowLimit": 25000,
            },
        )
        .execute()
    )
    rows: list[dict] = []
    for row in response.get("rows", []):
        record = {dim: key for dim, key in zip(dimensions, row["keys"])}
        for metric in GSC_METRICS:
            val = float(row.get(metric, 0.0))
            if metric == "ctr":
                val *= 100
            record[metric] = val
        rows.append(record)
    return rows


def summarize_merged(rows: list[dict]) -> dict:
    impr = sum(float(r.get("impressions") or 0) for r in rows)
    clicks = sum(float(r.get("clicks") or 0) for r in rows)
    sessions = sum(float(r.get("sessions") or 0) for r in rows)
    users = sum(float(r.get("totalUsers") or 0) for r in rows)
    return {
        "pages": len(rows),
        "impressions": impr,
        "clicks": clicks,
        "ctr": (clicks / impr * 100) if impr else 0.0,
        "sessions": sessions,
        "totalUsers": users,
    }


def merge_by_page(ga4_rows: list[dict], gsc_rows: list[dict]) -> list[dict]:
    by_page: dict[str, dict] = {}
    for r in gsc_rows:
        page = r["page"]
        by_page[page] = {
            "page": page,
            "impressions": float(r.get("impressions") or 0),
            "clicks": float(r.get("clicks") or 0),
            "ctr": float(r.get("ctr") or 0),
            "position": float(r.get("position") or 0),
            "sessions": 0.0,
            "totalUsers": 0.0,
            "screenPageViews": 0.0,
            "averageSessionDuration": 0.0,
            "engagementRate": 0.0,
        }
    for r in ga4_rows:
        page = r["page"]
        base = by_page.get(page) or {
            "page": page,
            "impressions": 0.0,
            "clicks": 0.0,
            "ctr": 0.0,
            "position": 0.0,
        }
        base.update(
            {
                "sessions": float(r.get("sessions") or 0),
                "totalUsers": float(r.get("totalUsers") or 0),
                "screenPageViews": float(r.get("screenPageViews") or 0),
                "averageSessionDuration": float(r.get("averageSessionDuration") or 0),
                "engagementRate": float(r.get("engagementRate") or 0),
            }
        )
        by_page[page] = base
    merged = list(by_page.values())
    for r in merged:
        r["site"] = site_segment(r["page"])
    merged.sort(key=lambda x: x.get("clicks", 0), reverse=True)
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect GA4/GSC data for plan.md analysis")
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--end", type=str, default="")
    parser.add_argument("--run-id", type=str, default="")
    args = parser.parse_args()

    settings = load_settings()
    missing = settings.validate()
    if missing:
        print("設定不足:", ", ".join(missing), file=sys.stderr)
        return 1

    creds = get_credentials()
    print(f"credentials: OK ({creds.service_account_email})", flush=True)

    end = date.fromisoformat(args.end) if args.end else date.today() - timedelta(days=1)
    start, end, prev_start, prev_end = period_pair(end, args.days)
    run_id = args.run_id or end.strftime("%Y-%m")
    out_dir = ROOT / "reports" / run_id / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    s, e = start.isoformat(), end.isoformat()
    ps, pe = prev_start.isoformat(), prev_end.isoformat()
    print(f"period current: {s} .. {e}", flush=True)
    print(f"period previous: {ps} .. {pe}", flush=True)
    print(f"output: {out_dir}", flush=True)

    ga4_client = BetaAnalyticsDataClient(credentials=creds)
    gsc_service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    def ga4_pages(start_d: str, end_d: str) -> list[dict]:
        rows = ga4_report(ga4_client, settings.ga4_property_id, "pagePath", start_d, end_d)
        out = []
        for r in rows:
            page = r.pop("pagePath")
            r["page"] = page
            r["site"] = site_segment(page)
            out.append(r)
        return out

    def gsc_pages(start_d: str, end_d: str) -> list[dict]:
        rows = gsc_query(gsc_service, settings.gsc_site_url, ["page"], start_d, end_d)
        out = []
        for r in rows:
            page = to_path(r["page"])
            r["page"] = page
            r["site"] = site_segment(page)
            out.append(r)
        return out

    page_ga4 = ga4_pages(s, e)
    print(f"ga4 pages current: {len(page_ga4)}", flush=True)
    page_gsc = gsc_pages(s, e)
    print(f"gsc pages current: {len(page_gsc)}", flush=True)
    prev_ga4 = ga4_pages(ps, pe)
    prev_gsc = gsc_pages(ps, pe)
    print(f"prev pages ga4/gsc: {len(prev_ga4)}/{len(prev_gsc)}", flush=True)

    date_ga4_raw = ga4_report(ga4_client, settings.ga4_property_id, "date", s, e)
    date_ga4 = [{"date": r["date"], **{k: r[k] for k in GA4_METRICS}} for r in date_ga4_raw]
    date_gsc = gsc_query(gsc_service, settings.gsc_site_url, ["date"], s, e)
    query_gsc = gsc_query(gsc_service, settings.gsc_site_url, ["query"], s, e)
    channel_raw = ga4_report(
        ga4_client, settings.ga4_property_id, "sessionDefaultChannelGroup", s, e
    )
    channel = [
        {"channel": r["sessionDefaultChannelGroup"], **{k: r[k] for k in GA4_METRICS}}
        for r in channel_raw
    ]
    device_raw = ga4_report(ga4_client, settings.ga4_property_id, "deviceCategory", s, e)
    device = [
        {"device": r["deviceCategory"], **{k: r[k] for k in GA4_METRICS}} for r in device_raw
    ]
    form_clicks = ga4_form_clicks(ga4_client, settings.ga4_property_id, s, e)
    prev_form_clicks = ga4_form_clicks(ga4_client, settings.ga4_property_id, ps, pe)
    print(
        "form link clicks current/previous: "
        f"{sum(r['eventCount'] for r in form_clicks):.0f}/"
        f"{sum(r['eventCount'] for r in prev_form_clicks):.0f}",
        flush=True,
    )

    merged = merge_by_page(
        [{k: v for k, v in r.items() if k != "site"} for r in page_ga4],
        [{k: v for k, v in r.items() if k != "site"} for r in page_gsc],
    )
    prev_merged = merge_by_page(
        [{k: v for k, v in r.items() if k != "site"} for r in prev_ga4],
        [{k: v for k, v in r.items() if k != "site"} for r in prev_gsc],
    )

    ga4_fields = ["page", "site", *GA4_METRICS]
    gsc_page_fields = ["page", "site", *GSC_METRICS]
    merged_fields = [
        "page",
        "site",
        "impressions",
        "clicks",
        "ctr",
        "position",
        *GA4_METRICS,
    ]

    write_csv(out_dir / "page_ga4.csv", page_ga4, ga4_fields)
    write_csv(out_dir / "page_gsc.csv", page_gsc, gsc_page_fields)
    write_csv(out_dir / "page_merged.csv", merged, merged_fields)
    write_csv(out_dir / "prev_page_merged.csv", prev_merged, merged_fields)
    write_csv(out_dir / "date_ga4.csv", date_ga4, ["date", *GA4_METRICS])
    write_csv(out_dir / "date_gsc.csv", date_gsc, ["date", *GSC_METRICS])
    write_csv(out_dir / "query_gsc.csv", query_gsc, ["query", *GSC_METRICS])
    write_csv(out_dir / "channel_ga4.csv", channel, ["channel", *GA4_METRICS])
    write_csv(out_dir / "device_ga4.csv", device, ["device", *GA4_METRICS])
    write_csv(
        out_dir / "form_click_ga4.csv",
        form_clicks,
        ["date", "linkUrl", "eventCount"],
    )
    write_csv(
        out_dir / "prev_form_click_ga4.csv",
        prev_form_clicks,
        ["date", "linkUrl", "eventCount"],
    )
    print("csv files written", flush=True)

    by_site = {}
    for site in ("lp", "blog"):
        cur = [r for r in merged if r.get("site") == site]
        prev = [r for r in prev_merged if r.get("site") == site]
        by_site[site] = {"current": summarize_merged(cur), "previous": summarize_merged(prev)}

    meta = {
        "run_id": run_id,
        "collected_at": date.today().isoformat(),
        "days": args.days,
        "current_period": {"start": s, "end": e},
        "previous_period": {"start": ps, "end": pe},
        "ga4_property_id": settings.ga4_property_id,
        "gsc_site_url": settings.gsc_site_url,
        "totals": {
            "current": summarize_merged(merged),
            "previous": summarize_merged(prev_merged),
        },
        "by_site": by_site,
        "form_link_clicks": {
            "event_name": FORM_CLICK_EVENT,
            "current": sum(r["eventCount"] for r in form_clicks),
            "previous": sum(r["eventCount"] for r in prev_form_clicks),
        },
        "notes": [
            "site=blog は page が /blog または /blog/ で始まる行。それ以外は lp。",
            f"{FORM_CLICK_EVENT} は参加フォームへのリンククリック。フォーム送信完了ではない。",
            "フォーム送信完了数は本スクリプトでは取得しない。",
            "実測値のみ。推測はレポート本文で区別して書くこと。",
        ],
    }
    (out_dir / "summary.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("wrote summary.json", flush=True)
    print("RESULT: OK", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
