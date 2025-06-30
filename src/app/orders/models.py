# src/app/orders/models.py

from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON
from datetime import datetime, timezone, timedelta
from ..core.database import Base
from .enums import OrderStatus, PaymentStatus


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)  # 訂單 ID（系統自填）

    # 使用者輸入
    customer_name = Column(String, nullable=False)      # 姓名
    phone = Column(String, nullable=False)              # 聯絡電話
    email = Column(String, nullable=False)              # 電子郵件
    item = Column(JSON, nullable=False)               # 品項

    # 系統欄位
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))   # 建立時間
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)          # 訂單狀態
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID)  # 付款狀態
