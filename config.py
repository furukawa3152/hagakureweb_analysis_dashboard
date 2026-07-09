"""環境変数の読み込みと設定値の一元管理。"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# GA4 と GSC の両方を読み取り専用で使うためのスコープ
SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
]


@dataclass(frozen=True)
class Settings:
    credentials_path: str
    ga4_property_id: str
    gsc_site_url: str

    def validate(self) -> list[str]:
        """未設定の項目名を返す。空なら設定OK。"""
        missing = []
        if not self.credentials_path or not os.path.exists(self.credentials_path):
            missing.append("GOOGLE_APPLICATION_CREDENTIALS（JSONキーのパス）")
        if not self.ga4_property_id:
            missing.append("GA4_PROPERTY_ID")
        if not self.gsc_site_url:
            missing.append("GSC_SITE_URL")
        return missing


def load_settings() -> Settings:
    return Settings(
        credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
        ga4_property_id=os.getenv("GA4_PROPERTY_ID", ""),
        gsc_site_url=os.getenv("GSC_SITE_URL", ""),
    )
