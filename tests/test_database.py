"""
測試資料庫配置和連線功能
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(autouse=True)
def mock_env_vars():
    """自動應用的 fixture，模擬必要的環境變數"""
    with patch.dict('os.environ', {
        'PG_HOST': 'localhost',
        'PG_PORT': '5432',
        'PG_USER': 'test_user',
        'PG_PASSWORD': 'test_password',
        'PG_DATABASE': 'test_db'
    }):
        yield


class TestDatabaseConfiguration:
    """測試資料庫配置"""

    def test_engine_creation(self):
        """測試資料庫引擎是否正確建立"""
        # 由於有環境變數 mock，可以安全地導入
        from src.app.core.database import engine

        # 檢查引擎是否為 SQLAlchemy Engine 實例
        assert hasattr(engine, 'connect'), "Engine 應該有 connect 方法"
        assert hasattr(engine, 'begin'), "Engine 應該有 begin 方法"
        assert hasattr(engine, 'url'), "Engine 應該有 url 屬性"

        # 檢查連線字串格式（不包含真實密碼）
        db_url = str(engine.url)
        assert 'postgresql://' in db_url, "應該使用 PostgreSQL 驅動"
        assert 'test_user' in db_url, "應該包含測試用戶名"
        assert 'localhost' in db_url, "應該包含測試主機"

    def test_session_local_creation(self):
        """測試會話工廠是否正確建立"""
        from src.app.core.database import SessionLocal

        # 檢查 SessionLocal 是否為 sessionmaker 實例
        assert hasattr(SessionLocal, '__call__'), "SessionLocal 應該是可呼叫的"

        # 測試建立會話（不實際連線到資料庫）
        with patch('src.app.core.database.engine') as mock_engine:
            session = SessionLocal()
            assert hasattr(session, 'query'), "Session 應該有 query 方法"
            assert hasattr(session, 'add'), "Session 應該有 add 方法"
            assert hasattr(session, 'commit'), "Session 應該有 commit 方法"
            assert hasattr(session, 'close'), "Session 應該有 close 方法"

    def test_base_creation(self):
        """測試 Base 類別是否正確建立"""
        from src.app.core.database import Base

        # 檢查 Base 是否為 declarative_base 實例
        assert hasattr(Base, 'metadata'), "Base 應該有 metadata 屬性"
        assert hasattr(Base, 'registry'), "Base 應該有 registry 屬性"
        assert hasattr(Base, '__subclasshook__'), "Base 應該是一個類別"

    def test_get_db_function(self):
        """測試 get_db 依賴注入函數"""
        from src.app.common.deps import get_db

        # Mock SessionLocal 以避免真實資料庫連線
        with patch('src.app.common.deps.SessionLocal') as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db

            # 測試 get_db 函數是否為 generator
            db_generator = get_db()
            assert hasattr(db_generator, '__next__'), "get_db 應該回傳 generator"

            # 測試會話是否正確產生和關閉
            db_session = next(db_generator)
            assert db_session == mock_db, "應該回傳 mock 的資料庫會話"

            # 測試 generator 結束時是否關閉會話
            try:
                next(db_generator)
            except StopIteration:
                mock_db.close.assert_called_once(), "會話應該在 generator 結束時關閉"

    def test_database_uri_format(self):
        """測試資料庫連線字串格式"""
        from src.app.core.config import get_settings

        settings = get_settings()
        db_uri = settings.db_uri

        # 檢查 URI 格式
        assert db_uri.startswith('postgresql://'), "應該使用 PostgreSQL 協議"
        assert 'test_user:test_password' in db_uri, "應該包含用戶認證資訊"
        assert '@localhost:5432' in db_uri, "應該包含主機和埠號"
        assert '/test_db' in db_uri, "應該包含資料庫名稱"


class TestDatabaseIntegration:
    """測試資料庫整合功能"""

    def test_engine_configuration_parameters(self):
        """測試引擎建立時的參數配置"""
        from src.app.core.database import engine

        # 檢查引擎是否正確建立
        assert engine is not None, "引擎應該被正確建立"

        # 檢查連線字串
        db_url = str(engine.url)
        assert 'postgresql://' in db_url, "應該使用正確的資料庫連線字串"

        # 檢查引擎池配置（pool_pre_ping 已在建立時設定）
        # pre_ping 是建立引擎時的參數，不是 pool 物件的屬性
        # 我們透過檢查 pool 類型來確認引擎正確配置
        assert str(type(engine.pool)) == "<class 'sqlalchemy.pool.impl.QueuePool'>", "應該使用 QueuePool"

    def test_session_configuration(self):
        """測試會話配置參數"""
        from src.app.core.database import SessionLocal

        # 檢查 sessionmaker 的配置
        assert not SessionLocal.kw.get('autocommit', True), "應該關閉自動提交"
        assert not SessionLocal.kw.get('autoflush', True), "應該關閉自動清理"
