# src/app/orders/router.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

# 匯入相關模組
from src.app.common.deps import get_db
from src.app.common.exceptions import raise_not_found
from . import schemas, crud, models
from .enums import OrderStatus, PaymentStatus

# 建立路由器
router = APIRouter(
    prefix="/orders",
    tags=["訂單管理"],
    responses={
        404: {"description": "訂單未找到"},
        400: {"description": "請求資料錯誤"},
    }
)
