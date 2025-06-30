# src/app/orders/crud.py

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas, enums
from ..common.exceptions import raise_not_found


def get_order_by_id(db: Session, order_id: int) -> Optional[models.Order]:
    """從 Order 資料表中根據 id 過濾出指定的訂單資料，回傳該筆完整資料記錄。"""
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def get_all_orders(
    db: Session,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Order]:
    """從 Order 資料表中篩選並導出訂單清單，可依照建立時間過濾、並支援分頁查詢。"""
    query = db.query(models.Order)
    if date_start:
        query = query.filter(models.Order.created_at >= date_start)
    if date_end:
        query = query.filter(models.Order.created_at <= date_end)
    return query.offset(skip).limit(limit).all()


def create_order(db: Session, order: schemas.OrderCreate, order_id: str) -> models.Order:
    """根據使用者輸入的訂單資料（包含顧客資訊與品項），將其轉換為資料庫格式並插入 Order 資料表中，回傳建立完成的訂單資料。"""
    items_json = [item.model_dump() for item in order.item]
    db_order = models.Order(
        id=order_id,
        customer_name=order.customer_name,
        phone=order.phone,
        email=order.email,
        item=items_json
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order_data(db: Session, order_id: int, update_data: dict) -> models.Order:
    """從 Order 資料表中根據 id 找到對應的訂單，依照傳入的 JSON 資料進行同層欄位更新，若無此訂單則拋出異常。"""
    db_order = get_order_by_id(db, order_id)
    if not db_order:
        raise_not_found("資料不存在")
    for key, value in update_data.items():
        if hasattr(db_order, key):
            setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order_status(db: Session, order_id: int, status: enums.OrderStatus) -> models.Order:
    """從 Order 資料表中根據 id 找到對應的訂單，並更新其狀態欄位為新的 status，回傳更新後的訂單資料。若無此訂單則拋出異常。"""
    db_order = get_order_by_id(db, order_id)
    if not db_order:
        raise_not_found("資料不存在")
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order


def update_payment_status(db: Session, order_id: int, payment_status: enums.PaymentStatus) -> models.Order:
    """從 Order 資料表中根據 id 找到對應的訂單，並更新其付款狀態欄位為新的 payment_status，回傳更新後的訂單資料。若無此訂單則拋出異常。"""
    db_order = get_order_by_id(db, order_id)
    if not db_order:
        raise_not_found("資料不存在")
    db_order.payment_status = payment_status
    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> models.Order:
    """從 Order 資料表中根據 id 找到對應的訂單，並將其刪除。刪除後回傳該筆原始訂單資料。若無此訂單則拋出異常。"""
    db_order = get_order_by_id(db, order_id)
    if not db_order:
        raise_not_found("資料不存在")
    db.delete(db_order)
    db.commit()
    return db_order


def get_latest_order_id_number(db: Session) -> int:
    """從 Order 資料表中取得最新的訂單編號，並回傳該編號。"""
    # 獲取今日的訂單 ID 來計算下一個序號
    today = datetime.now().strftime('%Y%m%d')
    prefix = f"ORD-{today}-"

    # 查詢今日最新的訂單
    latest_order = db.query(models.Order).filter(
        models.Order.id.like(f"{prefix}%")
    ).order_by(models.Order.id.desc()).first()

    if not latest_order:
        return 0  # 今日第一筆訂單

    # 從訂單 ID 中提取序號 (例如: "ORD-20231201-0001" -> 1)
    try:
        last_number = int(latest_order.id.split('-')[-1])
        return last_number
    except (ValueError, IndexError):
        return 0
