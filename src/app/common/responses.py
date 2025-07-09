"""
小型食品公司庫存訂單管理系統 - 統一回應產生器

此模組提供函數來建立標準化的 API 回應格式。
"""

from typing import Any, Dict, Optional
from datetime import datetime


def create_success_response(
    data: Any,
    message: str = "請求成功",
    status_code: int = 200,
    timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """
    建立統一格式的成功回應。

    Args:
        data (Any): 要回傳的主要資料。
        message (str, optional): 成功訊息。預設為 "請求成功"。
        status_code (int, optional): HTTP 狀態碼。預設為 200。
        timestamp (Optional[str], optional): 時間戳。預設為當前時間。

    Returns:
        Dict[str, Any]: 格式化的成功回應字典。
    """
    return {
        "success": True,
        "timestamp": timestamp or datetime.now().isoformat(),
        "status_code": status_code,
        "message": message,
        "data": data
    }
