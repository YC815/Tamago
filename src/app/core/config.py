# src/app/core/config.py

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


def get_required_env(key: str) -> str:
    """取得必須的環境變數，如果不存在則拋出明確的錯誤訊息

    Args:
        key (str): 環境變數的名稱

    Returns:
        str: 環境變數的值

    Raises:
        ValueError: 當環境變數不存在時
    """
    value = os.environ.get(key)
    if value is None:
        raise ValueError(
            f"必須設定環境變數 {key}！\n"
            f"請在 .env 檔案中設定 {key}=your_value\n"
            f"或在系統環境變數中設定此值。"
        )
    return value


class Settings:
    """應用程式設定類別"""

    # PostgreSQL 設定（必須提供，無預設值）
    PG_HOST: str = get_required_env("PG_HOST")
    PG_PORT: str = get_required_env("PG_PORT")
    PG_USER: str = get_required_env("PG_USER")
    PG_PASSWORD: str = get_required_env("PG_PASSWORD")
    PG_DATABASE: str = get_required_env("PG_DATABASE")

    @property
    def db_uri(self) -> str:
        """建構資料庫連線字串"""
        return f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DATABASE}"


# 建立全域設定實例
settings = Settings()
