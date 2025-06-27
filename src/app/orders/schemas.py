# src/app/orders/schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from src.app.orders.enums import OrderStatus, PaymentStatus


# 品項結構定義
class OrderItem(BaseModel):
    product_id: str = Field(..., description="商品 ID")
    name: str = Field(..., description="商品名稱")
    quantity: int = Field(..., description="數量")
    price: int = Field(..., description="單價")

    class Config:
        schema_extra = {
            "example": {
                "product_id": "cake001",
                "name": "草莓蛋糕",
                "quantity": 2,
                "price": 150
            }
        }


# 建立訂單時使用
class OrderCreate(BaseModel):
    customer_name: str
    phone: str
    email: EmailStr
    item: List[OrderItem]  # 這邊會轉成 JSON 存入資料庫

    class Config:
        schema_extra = {
            "example": {
                "customer_name": "王小明",
                "phone": "0912345678",
                "email": "xiao.ming@example.com",
                "item": [
                    {
                        "product_id": "cake001",
                        "name": "草莓蛋糕",
                        "quantity": 2,
                        "price": 150
                    },
                    {
                        "product_id": "pudding002",
                        "name": "焦糖布丁",
                        "quantity": 1,
                        "price": 80
                    }
                ]
            }
        }


# 查詢或回傳時使用
class OrderOut(OrderCreate):
    id: int
    created_at: datetime
    status: OrderStatus
    payment_status: PaymentStatus

    class Config:
        orm_mode = True  # ⬅️ 這行很重要，讓 SQLAlchemy 資料可以轉成 schema
