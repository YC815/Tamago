from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依賴注入：取得一個資料庫 session，請求結束自動關閉

    這個函數使用 Python 的 generator 機制來管理資料庫連線的生命週期：
    1. 建立一個新的資料庫 session
    2. 透過 yield 將 session 提供給需要的函數
    3. 當請求處理完成後，自動關閉 session 釋放資源

    Returns:
        Generator[Session, None, None]: 資料庫 session 的生成器
    """
    db = SessionLocal()  # 建立新的資料庫 session
    try:
        yield db  # 將 session 提供給呼叫者使用
    finally:
        db.close()  # 確保 session 在使用完畢後被正確關閉
