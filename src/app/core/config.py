# src/app/core/config.py

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


class Settings:
    """應用程式設定類別"""

    def __init__(self):
        """初始化設定，驗證必要的環境變數"""
        self.db_uri = os.getenv("SUPABASE_DB_URL")
        if not self.db_uri:
            raise ValueError("必須設定環境變數: SUPABASE_DB_URL")


# 改為在需要時才建立實例
def get_settings() -> Settings:
    """取得設定實例"""
    return Settings()
