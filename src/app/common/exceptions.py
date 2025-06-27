"""
小型食品公司庫存訂單管理系統 - 基礎異常處理模組

此模組定義了系統的基礎例外類別：
1. 應用程式基礎例外類別
2. 資源未找到例外
3. 未授權存取例外
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
from datetime import datetime

# 設定日誌記錄器
logger = logging.getLogger(__name__)


# ==================== 基礎例外類別 ====================

class AppException(Exception):
    """應用程式自訂錯誤的基礎例外類別"""
    pass


class NotFoundException(AppException):
    """資源未找到例外"""

    def __init__(self, message="資源未找到"):
        self.message = message
        super().__init__(self.message)


class UnauthorizedException(AppException):
    """未授權存取例外"""

    def __init__(self, message="未授權存取"):
        self.message = message
        super().__init__(self.message)


# ==================== 統一錯誤回應格式 ====================

def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """建立統一格式的錯誤回應"""

    return {
        "success": False,
        "timestamp": timestamp or datetime.now().isoformat(),
        "error": {
            "code": error_code,
            "message": message,
            "status_code": status_code
        }
    }


# ==================== 例外處理器 ====================

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """處理應用程式自訂例外"""

    # 根據例外類型決定狀態碼和錯誤代碼
    if isinstance(exc, NotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
        error_code = "NOT_FOUND"
        logger.info(f"Resource not found: {exc.message}")
    elif isinstance(exc, UnauthorizedException):
        status_code = status.HTTP_401_UNAUTHORIZED
        error_code = "UNAUTHORIZED"
        logger.warning(f"Unauthorized access: {exc.message}")
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        error_code = "BAD_REQUEST"
        logger.error(f"Application error: {exc.message}")

    return JSONResponse(
        status_code=status_code,
        content=create_error_response(
            status_code=status_code,
            error_code=error_code,
            message=exc.message
        )
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """處理資料驗證錯誤"""

    logger.warning(f"Validation error on {request.url.path}: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message="輸入資料格式錯誤"
        )
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """處理標準 HTTP 例外"""

    logger.info(f"HTTP Exception {exc.status_code} on {request.url.path}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            error_code="HTTP_ERROR",
            message=str(exc.detail) if exc.detail else "HTTP 請求錯誤"
        )
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """處理未預期的一般例外"""

    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            message="系統內部錯誤，請稍後再試"
        )
    )


# ==================== 便利函數 ====================

def raise_not_found(message: str = "資源未找到") -> None:
    """便利函數：拋出資源未找到例外"""
    raise NotFoundException(message)


def raise_unauthorized(message: str = "未授權存取") -> None:
    """便利函數：拋出未授權例外"""
    raise UnauthorizedException(message)
