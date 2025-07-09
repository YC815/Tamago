from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 匯入路由器 - 使用相對導入
from app.orders import router as orders_router
from app.common.exceptions import app_exception_handler, AppException

# 建立 FastAPI 應用程式實例
app = FastAPI(
    title="Tamago - 小型食品商店管理系統",
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
        "message": "Tamago API 系統正常運行",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }
