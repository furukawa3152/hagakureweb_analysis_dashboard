"""サービスアカウント認証情報の生成（GA4 / GSC 共通）。"""
from __future__ import annotations

from functools import lru_cache

from google.oauth2 import service_account

from config import SCOPES, load_settings


@lru_cache(maxsize=1)
def get_credentials() -> service_account.Credentials:
    settings = load_settings()
    return service_account.Credentials.from_service_account_file(
        settings.credentials_path, scopes=SCOPES
    )
