# src/app/core/config.py

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


class Settings:
    """應用程式設定類別"""

    def __init__(self):
        """初始化設定，驗證必要的環境變數"""
        required_vars = ['PG_HOST', 'PG_PORT', 'PG_USER', 'PG_PASSWORD', 'PG_DATABASE']
        missing_vars = []

        for var in required_vars:
            if var not in os.environ:
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"必須設定環境變數: {', '.join(missing_vars)}")

        # 設定屬性
        self.PG_HOST = os.environ["PG_HOST"]
        self.PG_PORT = os.environ["PG_PORT"]
        self.PG_USER = os.environ["PG_USER"]
        self.PG_PASSWORD = os.environ["PG_PASSWORD"]
        self.PG_DATABASE = os.environ["PG_DATABASE"]

    @property
    def db_uri(self) -> str:
        """建構資料庫連線字串"""
        return f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DATABASE}"


# 移除這行：settings = Settings()
# 改為在需要時才建立實例
def get_settings() -> Settings:
    """取得設定實例"""
    return Settings()
