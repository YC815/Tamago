from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import get_settings

# 取得設定實例
settings = get_settings()

# 資料庫引擎（透過 .env 設定）
engine = create_engine(settings.db_uri, pool_pre_ping=True)

# 建立 session factory，每次 get_db() 都會用這個
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有 models 要繼承這個 Base
Base = declarative_base()
