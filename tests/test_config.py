import pytest
import os
from unittest.mock import patch, MagicMock
from src.app.core.config import Settings, get_settings


class TestSettings:
    """Settings 類別的測試"""

    def test_settings_init_success(self):
        """測試 Settings 正常初始化"""
        # 模擬環境變數
        env_vars = {
            'PG_HOST': 'localhost',
            'PG_PORT': '5432',
            'PG_USER': 'testuser',
            'PG_PASSWORD': 'testpass',
            'PG_DATABASE': 'testdb'
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()

            # 驗證屬性設定正確
            assert settings.PG_HOST == 'localhost'
            assert settings.PG_PORT == '5432'
            assert settings.PG_USER == 'testuser'
            assert settings.PG_PASSWORD == 'testpass'
            assert settings.PG_DATABASE == 'testdb'

    def test_settings_missing_single_env_var(self):
        """測試缺少單一環境變數時拋出錯誤"""
        # 只設定部分環境變數，缺少 PG_HOST
        env_vars = {
            'PG_PORT': '5432',
            'PG_USER': 'testuser',
            'PG_PASSWORD': 'testpass',
            'PG_DATABASE': 'testdb'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Settings()

            # 驗證錯誤訊息包含缺少的變數
            assert "必須設定環境變數: PG_HOST" in str(exc_info.value)

    def test_settings_missing_multiple_env_vars(self):
        """測試缺少多個環境變數時拋出錯誤"""
        # 只設定部分環境變數，缺少多個
        env_vars = {
            'PG_PORT': '5432',
            'PG_USER': 'testuser'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Settings()

            error_message = str(exc_info.value)
            # 驗證錯誤訊息包含所有缺少的變數
            assert "必須設定環境變數:" in error_message
            assert "PG_HOST" in error_message
            assert "PG_PASSWORD" in error_message
            assert "PG_DATABASE" in error_message

    def test_settings_missing_all_env_vars(self):
        """測試完全沒有設定環境變數時拋出錯誤"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Settings()

            error_message = str(exc_info.value)
            # 驗證錯誤訊息包含所有必要的變數
            required_vars = ['PG_HOST', 'PG_PORT', 'PG_USER', 'PG_PASSWORD', 'PG_DATABASE']
            for var in required_vars:
                assert var in error_message

    def test_db_uri_property(self):
        """測試 db_uri 屬性建構正確的連線字串"""
        env_vars = {
            'PG_HOST': 'db.example.com',
            'PG_PORT': '5433',
            'PG_USER': 'admin',
            'PG_PASSWORD': 'secret123',
            'PG_DATABASE': 'production'
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            expected_uri = "postgresql://admin:secret123@db.example.com:5433/production"
            assert settings.db_uri == expected_uri

    def test_db_uri_with_special_characters(self):
        """測試包含特殊字元的資料庫連線字串"""
        env_vars = {
            'PG_HOST': 'localhost',
            'PG_PORT': '5432',
            'PG_USER': 'user@domain',
            'PG_PASSWORD': 'p@ssw0rd!',
            'PG_DATABASE': 'test-db'
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            expected_uri = "postgresql://user@domain:p@ssw0rd!@localhost:5432/test-db"
            assert settings.db_uri == expected_uri


class TestGetSettings:
    """get_settings 函數的測試"""

    def test_get_settings_returns_settings_instance(self):
        """測試 get_settings 回傳 Settings 實例"""
        env_vars = {
            'PG_HOST': 'localhost',
            'PG_PORT': '5432',
            'PG_USER': 'testuser',
            'PG_PASSWORD': 'testpass',
            'PG_DATABASE': 'testdb'
        }

        with patch.dict(os.environ, env_vars):
            settings = get_settings()
            assert isinstance(settings, Settings)
            assert settings.PG_HOST == 'localhost'

    def test_get_settings_creates_new_instance_each_time(self):
        """測試 get_settings 每次呼叫都建立新實例"""
        env_vars = {
            'PG_HOST': 'localhost',
            'PG_PORT': '5432',
            'PG_USER': 'testuser',
            'PG_PASSWORD': 'testpass',
            'PG_DATABASE': 'testdb'
        }

        with patch.dict(os.environ, env_vars):
            settings1 = get_settings()
            settings2 = get_settings()

            # 驗證是不同的實例
            assert settings1 is not settings2
            # 但屬性值相同
            assert settings1.PG_HOST == settings2.PG_HOST

    def test_get_settings_propagates_init_errors(self):
        """測試 get_settings 會傳播初始化錯誤"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_settings()

            assert "必須設定環境變數:" in str(exc_info.value)


class TestSettingsIntegration:
    """Settings 類別的整合測試"""

    def test_load_dotenv_integration(self):
        """測試與 load_dotenv 的整合"""
        # 這個測試驗證 load_dotenv 被正確呼叫
        with patch('dotenv.load_dotenv') as mock_load_dotenv:
            # 重新匯入模組以觸發 load_dotenv 呼叫
            import importlib
            import src.app.core.config
            importlib.reload(src.app.core.config)

            # 驗證 load_dotenv 被呼叫
            mock_load_dotenv.assert_called_once()

    def test_complete_workflow(self):
        """測試完整的工作流程"""
        env_vars = {
            'PG_HOST': 'prod-db.company.com',
            'PG_PORT': '5432',
            'PG_USER': 'app_user',
            'PG_PASSWORD': 'super_secure_password',
            'PG_DATABASE': 'cheflink_prod'
        }

        with patch.dict(os.environ, env_vars):
            # 建立設定
            settings = get_settings()

            # 驗證所有屬性
            assert settings.PG_HOST == 'prod-db.company.com'
            assert settings.PG_PORT == '5432'
            assert settings.PG_USER == 'app_user'
            assert settings.PG_PASSWORD == 'super_secure_password'
            assert settings.PG_DATABASE == 'cheflink_prod'

            # 驗證資料庫連線字串
            expected_uri = "postgresql://app_user:super_secure_password@prod-db.company.com:5432/cheflink_prod"
            assert settings.db_uri == expected_uri
