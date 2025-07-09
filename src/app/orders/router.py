# src/app/orders/router.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

# 匯入相關模組 - 使用相對導入
from ..common.deps import get_db
from ..common.responses import create_success_response
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


@router.get("/get_all_orders")
async def get_all_orders(
    db: Session = Depends(get_db),
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    取得所有訂單

    Args:
        db (Session, optional): 資料庫連線. Defaults to Depends(get_db).
        date_start (Optional[str], optional): 起始日期. Defaults to None.
        date_end (Optional[str], optional): 結束日期. Defaults to None.
        skip (int, optional): 跳過的筆數. Defaults to 0.
        limit (int, optional): 限制回傳的筆數. Defaults to 100.

    Returns:
        List[schemas.OrderOut]: 訂單列表
    """
    orders = crud.get_all_orders(db, date_start, date_end, skip, limit)
    return create_success_response(orders, message="成功取得所有訂單")


@router.get("/get_order_by_id/{order_id}")
async def get_order_by_id(order_id: str, db: Session = Depends(get_db)):
    """
    根據訂單編號取得訂單

    Args:
        order_id (str): 訂單編號
        db (Session, optional): 資料庫連線. Defaults to Depends(get_db).

    Returns:
        schemas.OrderOut: 訂單資料
    """
    # crud 函式會在上游處理好 not found 的情況
    order = crud.get_order_by_id(db, order_id)
    return create_success_response(schemas.OrderOut.model_validate(order).model_dump(), message=f"成功取得訂單 #{order_id}")


@router.post("/create_order", status_code=status.HTTP_201_CREATED)
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """
    建立一筆新的訂單

    - **order**: 訂單資料，包含顧客資訊與購買品項
    - **db**: 資料庫連線
    """
    # 產生訂單編號，格式為 ORD-YYYYMMDD-XXXX (當日流水號)
    order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{crud.get_latest_order_id_number(db) + 1:04d}"

    # 呼叫 CRUD 函式建立訂單並取得回傳的資料庫物件
    new_order = crud.create_order(db, order, order_id)

    # 回傳建立好的訂單資料
    return create_success_response(schemas.OrderOut.model_validate(new_order).model_dump(), message="訂單已成功建立", status_code=201)


@router.post("/delete_order_by_id/{order_id}")
async def delete_order_by_id(order_id: str, db: Session = Depends(get_db)):
    """
    刪除訂單

    Args:
        order_id (str): 訂單編號
        db (Session, optional): 資料庫連線. Defaults to Depends(get_db).
    """
    # crud 函式會處理找不到訂單的例外
    crud.delete_order_by_id(db, order_id)
    return create_success_response(None, message=f"訂單 #{order_id} 已成功刪除")


@router.post("/update_order_by_id/{order_id}")
async def update_order_by_id(order_id: str, order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """
    更新訂單
    """
    updated_order = crud.update_order_by_id(db, order_id, order)
    return create_success_response(schemas.OrderOut.model_validate(updated_order).model_dump(), message=f"訂單 #{order_id} 已成功更新")
