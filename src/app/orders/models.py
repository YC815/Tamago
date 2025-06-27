# src/app/orders/models.py

from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON
from datetime import datetime, timezone, timedelta
from enum import Enum as PyEnum
from src.app.core.database import Base

# 通用訂單狀態列舉


class OrderStatus(PyEnum):
    PENDING = "PENDING"         # 待確認／未處理
    CONFIRMED = "CONFIRMED"     # 已確認／待出貨
    SHIPPED = "SHIPPED"         # 已出貨
    DELIVERED = "DELIVERED"     # 已送達
    CANCELLED = "CANCELLED"     # 已取消
    RETURNED = "RETURNED"       # 已退貨

# 付款狀態列舉


class PaymentStatus(PyEnum):
    UNPAID = "UNPAID"           # 尚未付款
    PAID = "PAID"               # 已付款
    REFUNDED = "REFUNDED"       # 已退款


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)  # 訂單 ID（系統自填）

    # 使用者輸入
    customer_name = Column(String, nullable=False)      # 姓名
    phone = Column(String, nullable=False)              # 聯絡電話
    email = Column(String, nullable=False)              # 電子郵件
    item = Column(JSON, nullable=False)               # 品項（目前先用簡單字串表示）

    # 系統欄位
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))   # 建立時間
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)          # 訂單狀態
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID)  # 付款狀態
