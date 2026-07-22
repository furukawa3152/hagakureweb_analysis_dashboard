"""GA4 × Search Console 統合ダッシュボード（Streamlit）。

初心者にもわかりやすいよう、専門用語をやさしく翻訳し、
数字を「次の行動」に変換したビューを用意している。
"""
from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analysis import insights
from analysis.glossary import GLOSSARY, channel_ja, device_ja
from analysis.merge import merge_by_page
from config import load_settings
from data_sources import ga4, gsc

st.set_page_config(page_title="Hagakure Web 分析ダッシュボード", layout="wide")
st.title("Hagakure Web 分析ダッシュボード")
st.caption(
    "佐賀でプログラミングを学びたい非エンジニア／エンジニアに届いているかを、"
    "Search Console × GA4 で観察する"
)

# --- 設定チェック ---
settings = load_settings()
missing = settings.validate()
if missing:
    st.error("以下の設定が未完了です。`.env` を確認してください：\n\n- " + "\n- ".join(missing))
    st.stop()

# --- 期間選択 ---
with st.sidebar:
    st.header("期間")
    default_end = date.today() - timedelta(days=1)  # 前日まで（当日は集計が不安定）
    default_start = default_end - timedelta(days=27)
    start_date, end_date = st.date_input(
        "対象期間",
        value=(default_start, default_end),
        max_value=date.today(),
    )
    run = st.button("データ取得", type="primary")
    st.caption("※ 前の同じ日数の期間と自動で比較します（健康診断・伸び落ち用）")

s = start_date.isoformat()
e = end_date.isoformat()

# 直前の同じ長さの期間（比較用）
span_days = (end_date - start_date).days
prev_end = start_date - timedelta(days=1)
prev_start = prev_end - timedelta(days=span_days)
ps = prev_start.isoformat()
pe = prev_end.isoformat()


@st.cache_data(ttl=3600, show_spinner="データ取得中...")
def load_all(start: str, end: str, prev_s: str, prev_e: str):
    return {
        "page_ga4": ga4.fetch_by_page(start, end),
        "page_gsc": gsc.fetch_by_page(start, end),
        "prev_page_ga4": ga4.fetch_by_page(prev_s, prev_e),
        "prev_page_gsc": gsc.fetch_by_page(prev_s, prev_e),
        "date_ga4": ga4.fetch_by_date(start, end),
        "date_gsc": gsc.fetch_by_date(start, end),
        "query_gsc": gsc.fetch_by_query(start, end),
        "prev_query_gsc": gsc.fetch_by_query(prev_s, prev_e),
        "channel_ga4": ga4.fetch_by_channel(start, end),
        "device_ga4": ga4.fetch_by_device(start, end),
    }


if not run and "data" not in st.session_state:
    st.info("サイドバーで期間を選び、「データ取得」を押してください。")
    st.stop()

if run:
    st.session_state["data"] = load_all(s, e, ps, pe)

data = st.session_state["data"]
# 旧キャッシュ（prev_query_gsc なし）は再取得を促す
if "prev_query_gsc" not in data:
    st.warning("データ形式が更新されました。サイドバーの「データ取得」を再度押してください。")
    st.stop()

gsc_page = data["page_gsc"]
ga4_page = data["page_ga4"]
merged = merge_by_page(ga4_page, gsc_page)

# 数値列の日本語表示設定（統合ビュー等で共通利用）
_COLCFG = {
    "page": st.column_config.TextColumn("ページ"),
    "impressions": st.column_config.NumberColumn("表示回数", help=GLOSSARY["impressions"], format="%d"),
    "clicks": st.column_config.NumberColumn("クリック", help=GLOSSARY["clicks"], format="%d"),
    "ctr": st.column_config.NumberColumn("CTR", help=GLOSSARY["ctr"], format="%.2f%%"),
    "position": st.column_config.NumberColumn("平均順位", help=GLOSSARY["position"], format="%.1f"),
    "sessions": st.column_config.NumberColumn("訪問", help=GLOSSARY["sessions"], format="%d"),
    "totalUsers": st.column_config.NumberColumn("訪問者数", help=GLOSSARY["totalUsers"], format="%d"),
    "screenPageViews": st.column_config.NumberColumn("ページ表示", help=GLOSSARY["screenPageViews"], format="%d"),
    "averageSessionDuration": st.column_config.NumberColumn("平均滞在(秒)", help=GLOSSARY["averageSessionDuration"], format="%.0f"),
    "engagementRate": st.column_config.NumberColumn("エンゲージ率", help=GLOSSARY["engagementRate"], format="%.1f%%"),
}

tabs = st.tabs([
    "🎯 目的達成",
    "🩺 健康診断",
    "💡 改善のヒント",
    "📄 ページ別 統合ビュー",
    "📊 伸び / 落ち",
    "📈 推移",
    "🔍 検索キーワード",
    "🌐 流入経路・デバイス",
])

_STATUS_ICON = {"up": "🟢", "flat": "🟡", "down": "🔴", "unknown": "⚪"}

# =====================================================================
# タブ1: 目的達成ボード（誰に届いたか）
# =====================================================================
with tabs[0]:
    st.subheader("狙った人に届いているか")
    st.caption(
        f"検索クエリから「誰向けの検索か」を推定し、"
        f"対象期間 {s} 〜 {e} を直前の {ps} 〜 {pe} と比較します。"
        "指標はクリック数の前期比です。"
    )

    persona_cards = insights.build_persona_scorecard(
        data["query_gsc"], data["prev_query_gsc"]
    )
    pcols = st.columns(len(persona_cards))
    for col, card in zip(pcols, persona_cards):
        delta_txt = None if card["delta"] is None else f"{card['delta']:+.1f}%"
        col.metric(
            f"{_STATUS_ICON[card['status']]} {card['label']}",
            f"{int(card['current_clicks']):,} クリック",
            delta=delta_txt,
            help=(
                f"表示 {int(card['current_impressions']):,}回 / "
                f"CTR {card['current_ctr']:.2f}% / "
                f"平均順位 {card['current_position']:.1f} / "
                f"キーワード {card['current_queries']}件"
            ),
        )
        col.caption(
            f"表示 {int(card['current_impressions']):,}　"
            f"CTR {card['current_ctr']:.1f}%　"
            f"順位 {card['current_position']:.1f}"
        )

    st.divider()
    st.markdown("#### 各ペルソナの代表キーワード")
    persona_keys = [("local", "📍 佐賀ローカル"),
                    ("beginner", "🌱 非エンジニア・学び始め"),
                    ("engineer", "🧑‍💻 エンジニア・実務寄り")]
    qcols = st.columns(3)
    for col, (pkey, plabel) in zip(qcols, persona_keys):
        with col:
            st.markdown(f"**{plabel}**")
            top_q = insights.top_queries_for_persona(data["query_gsc"], pkey, top=6)
            if top_q.empty:
                st.info("該当キーワードなし")
            else:
                st.dataframe(
                    top_q,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "query": st.column_config.TextColumn("キーワード"),
                        "clicks": st.column_config.NumberColumn("クリック", format="%d"),
                        "impressions": st.column_config.NumberColumn("表示", format="%d"),
                        "ctr": st.column_config.NumberColumn("CTR", format="%.1f%%"),
                        "position": st.column_config.NumberColumn("順位", format="%.1f"),
                    },
                    height=260,
                )

    st.divider()
    st.markdown(
        "**信号の見方**　🟢 前より良くなった（+5%超）／🟡 ほぼ横ばい／"
        "🔴 前より下がった（−5%超）／⚪ 比較データなし  \n"
        "※「佐賀 プログラミング 初心者」のように複数に当てはまる語は、"
        "スコアカードではそれぞれのペルソナに計上します。"
    )

# =====================================================================
# タブ2: 健康診断
# =====================================================================
with tabs[1]:
    st.subheader("今週の健康診断")
    st.caption(f"対象期間 {s} 〜 {e} を、直前の {ps} 〜 {pe} と比較しています。")

    cur_totals = insights.summarize_totals(gsc_page, ga4_page)
    prev_totals = insights.summarize_totals(data["prev_page_gsc"], data["prev_page_ga4"])
    cards = insights.build_health(cur_totals, prev_totals)

    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        if card["key"] == "ctr":
            value = f"{card['current']:.2f}%"
        else:
            value = f"{int(card['current']):,}"
        if card["delta"] is None:
            delta_txt = None
        else:
            delta_txt = f"{card['delta']:+.1f}%"
        col.metric(
            f"{_STATUS_ICON[card['status']]} {card['label']}",
            value,
            delta=delta_txt,
            help=GLOSSARY.get(card["key"], ""),
        )

    st.divider()
    st.markdown(
        "**信号の見方**　🟢 前より良くなった（+5%超）／🟡 ほぼ横ばい／"
        "🔴 前より下がった（−5%超）／⚪ 比較データなし"
    )

# =====================================================================
# タブ3: 改善のヒント
# =====================================================================
with tabs[2]:
    st.subheader("改善のヒント（自動アドバイス）")
    st.caption("数字を自動で読み解いて、次に手を打つとよさそうな場所を提案します。")

    hints = insights.generate_hints(merged)
    if not hints:
        st.info("ヒントを出せるだけのデータがまだありません。期間を広げてみてください。")
    else:
        order = ["あと一歩ページ", "タイトル改善候補", "コンテンツ改善候補"]
        for group in order:
            group_hints = [h for h in hints if h["type"] == group]
            if not group_hints:
                continue
            st.markdown(f"### {group_hints[0]['icon']} {group}")
            for h in group_hints:
                with st.container(border=True):
                    st.markdown(f"**{h['page']}**")
                    st.write(h["message"])
                    st.caption(h["detail"])

# =====================================================================
# タブ4: ページ別 統合ビュー
# =====================================================================
with tabs[3]:
    st.subheader("ページ別：検索パフォーマンス × サイト内行動")
    st.dataframe(merged, use_container_width=True, column_config=_COLCFG)
    st.caption(
        "見方の例：表示が多いのにCTRが低い→タイトル/説明の改善余地。"
        "クリックは多いが滞在が短い→コンテンツの改善余地。"
    )

# =====================================================================
# タブ5: 伸び / 落ち
# =====================================================================
with tabs[4]:
    st.subheader("伸びてる / 落ちてるページ")
    st.caption(f"クリック数の増減で比較（{s}〜{e} vs {ps}〜{pe}）。")

    risers, fallers = insights.page_movers(gsc_page, data["prev_page_gsc"])
    mover_cfg = {
        "page": st.column_config.TextColumn("ページ"),
        "clicks_now": st.column_config.NumberColumn("今回クリック", format="%d"),
        "clicks_prev": st.column_config.NumberColumn("前回クリック", format="%d"),
        "change": st.column_config.NumberColumn("増減", format="%+d"),
    }
    left, right = st.columns(2)
    with left:
        st.markdown("#### 📈 伸びてるページ")
        if risers.empty:
            st.info("伸びたページはありませんでした。")
        else:
            st.dataframe(risers, use_container_width=True, hide_index=True, column_config=mover_cfg)
    with right:
        st.markdown("#### 📉 落ちてるページ")
        if fallers.empty:
            st.info("落ちたページはありませんでした。")
        else:
            st.dataframe(fallers, use_container_width=True, hide_index=True, column_config=mover_cfg)

# =====================================================================
# タブ6: 推移
# =====================================================================
with tabs[5]:
    st.subheader("日別の推移")
    date_gsc = data["date_gsc"]
    date_ga4 = data["date_ga4"]

    if not date_gsc.empty or not date_ga4.empty:
        fig = go.Figure()
        if not date_gsc.empty:
            fig.add_trace(go.Scatter(x=date_gsc["date"], y=date_gsc["clicks"],
                                     name="クリック（検索）", mode="lines"))
            fig.add_trace(go.Scatter(x=date_gsc["date"], y=date_gsc["impressions"],
                                     name="表示回数（検索）", mode="lines", yaxis="y2"))
        if not date_ga4.empty:
            fig.add_trace(go.Scatter(x=date_ga4["date"], y=date_ga4["sessions"],
                                     name="サイト訪問", mode="lines"))
        fig.update_layout(
            yaxis=dict(title="クリック / 訪問"),
            yaxis2=dict(title="表示回数", overlaying="y", side="right"),
            legend=dict(orientation="h"),
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("この期間のデータがありません。")

# =====================================================================
# タブ7: 検索キーワード（誰向けか）
# =====================================================================
with tabs[6]:
    st.subheader("検索キーワード：誰向けの検索か")
    query_gsc = data["query_gsc"]

    if query_gsc.empty:
        st.info("この期間の検索クエリデータがありません。")
    else:
        grouped = insights.group_queries_by_persona(query_gsc)
        st.markdown("#### クリックの内訳（ペルソナ）")
        gcol1, gcol2 = st.columns([1, 1])
        with gcol1:
            fig = go.Figure(data=[go.Pie(
                labels=grouped["group"], values=grouped["clicks"], hole=0.4)])
            fig.update_layout(height=320, legend=dict(orientation="h"))
            st.plotly_chart(fig, use_container_width=True)
        with gcol2:
            st.dataframe(
                grouped, use_container_width=True, hide_index=True,
                column_config={
                    "group": st.column_config.TextColumn("ペルソナ"),
                    "clicks": st.column_config.NumberColumn("クリック", format="%d"),
                    "impressions": st.column_config.NumberColumn("表示回数", format="%d"),
                    "件数": st.column_config.NumberColumn("キーワード数", format="%d"),
                },
            )
        st.caption(
            "円グラフは1キーワードを1ペルソナに分類"
            "（優先: 佐賀ローカル → 非エンジニア → エンジニア → その他）。"
            "目的達成タブのスコアカードとは数え方が少し異なります。"
        )

        st.divider()
        st.markdown("#### キーワード一覧")
        list_df = query_gsc.copy()
        list_df["persona"] = list_df["query"].apply(insights.classify_persona)
        st.dataframe(
            list_df, use_container_width=True, hide_index=True,
            column_config={
                "persona": st.column_config.TextColumn("ペルソナ"),
                "query": st.column_config.TextColumn("検索キーワード"),
                "clicks": st.column_config.NumberColumn("クリック", help=GLOSSARY["clicks"], format="%d"),
                "impressions": st.column_config.NumberColumn("表示回数", help=GLOSSARY["impressions"], format="%d"),
                "ctr": st.column_config.NumberColumn("CTR", help=GLOSSARY["ctr"], format="%.2f%%"),
                "position": st.column_config.NumberColumn("平均順位", help=GLOSSARY["position"], format="%.1f"),
            },
        )

# =====================================================================
# タブ8: 流入経路・デバイス
# =====================================================================
with tabs[7]:
    st.subheader("どこから来た？ 何で見てる？")

    channel = data["channel_ga4"].copy()
    device = data["device_ga4"].copy()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🌐 流入経路")
        if channel.empty:
            st.info("データがありません。")
        else:
            channel["表示名"] = channel["channel"].apply(channel_ja)
            fig = go.Figure(data=[go.Pie(
                labels=channel["表示名"], values=channel["sessions"], hole=0.4)])
            fig.update_layout(height=340, legend=dict(orientation="h"))
            st.plotly_chart(fig, use_container_width=True)
            st.caption("検索頼みか、SNSや直接アクセスも効いているかがわかります。")
    with c2:
        st.markdown("#### 📱 デバイス")
        if device.empty:
            st.info("データがありません。")
        else:
            device["表示名"] = device["device"].apply(device_ja)
            fig = go.Figure(data=[go.Pie(
                labels=device["表示名"], values=device["sessions"], hole=0.4)])
            fig.update_layout(height=340, legend=dict(orientation="h"))
            st.plotly_chart(fig, use_container_width=True)
            st.caption("スマホ中心なら、スマホでの見やすさが特に重要です。")
