# src/app/orders/crud.py

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from . import models, schemas, enums
from ..common.exceptions import NotFoundException, DatabaseException


def get_order_by_id(db: Session, order_id: int) -> models.Order:
    """從 Order 資料表中根據 id 過濾出指定的訂單資料，回傳該筆完整資料記錄。"""
    try:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise NotFoundException(resource_name="Order", resource_id=order_id)
        return order
    except SQLAlchemyError as e:
        # 在真實應用中，應該記錄錯誤日誌
        # logger.error(f"Database error while fetching order {order_id}: {e}")
        raise DatabaseException(f"查詢訂單資料 (ID: {order_id}) 時發生錯誤")


def get_all_orders(
    db: Session,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Order]:
    """從 Order 資料表中篩選並導出訂單清單，可依照建立時間過濾、並支援分頁查詢。"""
    try:
        query = db.query(models.Order)
        if date_start:
            query = query.filter(models.Order.created_at >= date_start)
        if date_end:
            query = query.filter(models.Order.created_at <= date_end)
        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise DatabaseException(f"查詢所有訂單時發生錯誤: {e}")


def create_order(db: Session, order: schemas.OrderCreate, order_id: str) -> models.Order:
    """根據使用者輸入的訂單資料（包含顧客資訊與品項），將其轉換為資料庫格式並插入 Order 資料表中，回傳建立完成的訂單資料。"""
    try:
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
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"建立新訂單時發生錯誤: {e}")


def update_order_by_id(db: Session, order_id: str, update_data: schemas.OrderCreate) -> models.Order:
    """從 Order 資料表中根據 id 找到對應的訂單，依照傳入的 JSON 資料進行同層欄位更新，若無此訂單則拋出異常。"""
    db_order = get_order_by_id(db, order_id)
    try:
        update_data_dict = update_data.model_dump()
        for key, value in update_data_dict.items():
            if hasattr(db_order, key):
                if key == 'item':
                    setattr(db_order, key, [item.model_dump() for item in value])
                else:
                    setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)
        return db_order
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"更新訂單資料 (ID: {order_id}) 時發生錯誤: {e}")


def update_order_status(db: Session, order_id: int, status: enums.OrderStatus) -> models.Order:
    """從 Order 資料表中根據 id 找到對應的訂單，並更新其狀態欄位為新的 status，回傳更新後的訂單資料。若無此訂單則拋出異常。"""
    db_order = get_order_by_id(db, order_id)
    try:
        db_order.status = status
        db.commit()
        db.refresh(db_order)
        return db_order
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"更新訂單狀態 (ID: {order_id}) 時發生錯誤: {e}")


def update_payment_status(db: Session, order_id: int, payment_status: enums.PaymentStatus) -> models.Order:
    """從 Order 資料表中根據 id 找到對應的訂單，並更新其付款狀態欄位為新的 payment_status，回傳更新後的訂單資料。若無此訂單則拋出異常。"""
    db_order = get_order_by_id(db, order_id)
    try:
        db_order.payment_status = payment_status
        db.commit()
        db.refresh(db_order)
        return db_order
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"更新訂單付款狀態 (ID: {order_id}) 時發生錯誤: {e}")


def delete_order_by_id(db: Session, order_id: int):
    """
    根據訂單編號刪除訂單

    Args:
        db (Session): 資料庫連線
        order_id (int): 訂單編號
    """
    order = get_order_by_id(db, order_id)
    try:
        db.delete(order)
        db.commit()
        return order  # 回傳被刪除的訂單物件
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"刪除訂單 (ID: {order_id}) 時發生錯誤: {e}")


def get_latest_order_id_number(db: Session) -> int:
    """從 Order 資料表中取得最新的訂單編號，並回傳該編號。"""
    try:
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
        last_number = int(latest_order.id.split('-')[-1])
        return last_number
    except (SQLAlchemyError, ValueError, IndexError) as e:
        # 捕獲所有可能的錯誤
        raise DatabaseException(f"取得最新訂單編號時發生錯誤: {e}")
