from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 匯入路由器
from src.app.orders import router as orders_router
from src.app.common.exceptions import app_exception_handler, AppException

# 建立 FastAPI 應用程式實例
app = FastAPI(
    title="ChefLink - 小型食品商店管理系統",
    description="提供庫存、訂單等管理功能的 API 系統",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 文件路徑
    redoc_url="/redoc"  # ReDoc 文件路徑
)

# 設定 CORS（跨域請求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該設定具體的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊例外處理器
app.add_exception_handler(AppException, app_exception_handler)

# 註冊路由器
app.include_router(orders_router.router)

# 基本的測試類別（保留原有的）


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None

# 根路徑 - 系統健康檢查


@app.get("/", tags=["系統"])
async def root():
    """
    系統健康檢查

    回傳系統基本資訊和狀態
    """
    return {
        "message": "ChefLink API 系統正常運行",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }

# 系統資訊


@app.get("/info", tags=["系統"])
async def get_system_info():
    """
    取得系統資訊

    回傳 API 系統的詳細資訊
    """
    return {
        "name": "ChefLink",
        "description": "小型食品商店管理系統",
        "version": "1.0.0",
        "features": [
            "訂單管理",
            "庫存管理（規劃中）",
            "商品管理（規劃中）",
            "客戶管理（規劃中）"
        ],
        "endpoints": {
            "orders": "/orders",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# 測試端點（保留原有的）


@app.post("/test-item", tags=["測試"])
async def create_test_item(item: Item):
    """
    測試端點 - 建立測試商品

    用於測試 Pydantic 模型驗證
    """
    return {
        "message": "測試商品建立成功",
        "item": item,
        "total_price": item.price * (0.8 if item.is_offer else 1.0)
    }
