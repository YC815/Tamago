# src/app/orders/router.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

# 匯入相關模組 - 使用相對導入
from ..common.deps import get_db
from ..common.exceptions import raise_not_found
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


@router.get("/get_all_orders", response_model=List[schemas.OrderOut])
async def get_all_orders(
    db: Session = Depends(get_db),
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    orders = crud.get_all_orders(db, date_start, date_end, skip, limit)
    return orders


@router.get("/get_order_by_id/{order_id}", response_model=schemas.OrderOut)
async def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order_by_id(db, order_id)
    if not order:
        raise_not_found()
    return order


@router.post("/create_order", response_model=schemas.OrderOut)
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{crud.get_latest_order_id_number(db) + 1:04d}"
    return crud.create_order(db, order, order_id)
