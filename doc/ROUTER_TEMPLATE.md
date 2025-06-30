# 路由器模板使用指南

這個文件提供了建立新功能模組路由器的模板和指南。

## 模板結構

### 1. 基本設定

```python
# src/app/{module_name}/router.py

# ==================== 匯入必要的套件 ====================
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session  # 資料庫會話類型
from typing import List, Optional    # 型別提示
from datetime import datetime        # 時間處理

# ==================== 匯入專案內的模組 ====================
from src.app.common.deps import get_db                    # 資料庫依賴注入
from src.app.common.exceptions import raise_not_found     # 統一異常處理
from . import schemas, crud, models                       # 同層級的模組

# ==================== 建立路由器實例 ====================
router = APIRouter(
    prefix="/{module_name}",      # API 路徑前綴，例如：/products, /inventory
    tags=["{模組名稱}管理"],       # 在 Swagger 文件中的分組標籤
    responses={                   # 預設的錯誤回應格式
        404: {"description": "{資源}未找到"},
        400: {"description": "請求資料錯誤"},
    }
)
```

### 2. 基本 CRUD 操作

#### 建立資源

```python
# ==================== POST：建立新資源 ====================
@router.post("/",                                    # HTTP POST 方法，路徑為根路徑
            response_model=schemas.{Resource}Out,     # 回傳的資料格式（用於文件生成）
            status_code=status.HTTP_201_CREATED,      # 成功時回傳 201 狀態碼
            summary="建立新{資源}",                    # API 文件中的簡短說明
            description="建立新的{資源}記錄")          # API 文件中的詳細說明
async def create_{resource}(
    {resource}_data: schemas.{Resource}Create,        # 請求體：使用 Pydantic 模型驗證輸入
    db: Session = Depends(get_db)                     # 依賴注入：取得資料庫會話
) -> schemas.{Resource}Out:                           # 回傳類型提示
    """
    建立新{資源}

    這個函數會：
    1. 接收客戶端傳來的{資源}資料
    2. 驗證資料格式是否正確
    3. 呼叫 CRUD 函數將資料存入資料庫
    4. 回傳建立成功的{資源}資料

    參數說明：
    - **field1**: 欄位1說明
    - **field2**: 欄位2說明
    """
    try:
        # 呼叫 CRUD 層的函數，將 Pydantic 模型轉換為資料庫模型並儲存
        db_{resource} = crud.create_{resource}(db=db, {resource}={resource}_data)

        # 將資料庫模型轉換為回應用的 Pydantic 模型
        return schemas.{Resource}Out.from_orm(db_{resource})

    except Exception as e:
        # 如果發生任何錯誤，回傳 400 錯誤和錯誤訊息
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"建立{資源}失敗: {str(e)}"
        )
```

#### 查詢單一資源

```python
# ==================== GET：查詢單一資源 ====================
@router.get("/{{{resource}_id}}",                    # HTTP GET 方法，路徑包含 ID 參數
           response_model=schemas.{Resource}Out,      # 回傳的資料格式
           summary="查詢指定{資源}",                   # API 文件簡短說明
           description="根據 ID 查詢{資源}詳細資訊")   # API 文件詳細說明
async def get_{resource}(
    {resource}_id: int,                               # 路徑參數：{資源} ID（自動轉換為整數）
    db: Session = Depends(get_db)                     # 依賴注入：資料庫會話
) -> schemas.{Resource}Out:                           # 回傳類型提示
    """
    查詢指定{資源}

    這個函數會：
    1. 接收路徑中的{資源} ID
    2. 在資料庫中查詢對應的{資源}
    3. 如果找到就回傳{資源}資料
    4. 如果找不到就拋出 404 錯誤
    """
    # 呼叫 CRUD 函數查詢資料庫
    db_{resource} = crud.get_{resource}(db=db, {resource}_id={resource}_id)

    # 檢查是否找到{資源}
    if not db_{resource}:
        # 使用統一的異常處理函數拋出 404 錯誤
        raise_not_found(f"找不到 ID 為 {{resource}_id} 的{資源}")

    # 將資料庫模型轉換為回應格式並回傳
    return schemas.{Resource}Out.from_orm(db_{resource})
```

#### 查詢資源清單

```python
# ==================== GET：查詢資源清單（支援分頁） ====================
@router.get("/",                                     # HTTP GET 方法，根路徑
           response_model=List[schemas.{Resource}Out], # 回傳格式：{資源}清單
           summary="查詢{資源}清單",                   # API 文件簡短說明
           description="查詢{資源}清單，支援分頁和篩選") # API 文件詳細說明
async def get_{resource}s(
    skip: int = Query(0, ge=0, description="跳過的記錄數"),           # 查詢參數：分頁偏移量
    limit: int = Query(100, ge=1, le=1000, description="每頁最大記錄數"), # 查詢參數：每頁數量限制
    db: Session = Depends(get_db)                                    # 依賴注入：資料庫會話
) -> List[schemas.{Resource}Out]:                                    # 回傳類型：{資源}清單
    """
    查詢{資源}清單

    這個函數會：
    1. 接收分頁參數（skip 和 limit）
    2. 從資料庫查詢{資源}清單
    3. 支援分頁功能，避免一次回傳太多資料
    4. 將每個{資源}轉換為回應格式

    分頁說明：
    - skip: 跳過前面幾筆記錄（用於翻頁）
    - limit: 最多回傳幾筆記錄（限制每頁大小）
    """
    # 呼叫 CRUD 函數查詢{資源}清單
    {resource}s = crud.get_{resource}s(db=db, skip=skip, limit=limit)

    # 將每個資料庫模型轉換為回應格式，並組成清單回傳
    return [schemas.{Resource}Out.from_orm({resource}) for {resource} in {resource}s]
```

#### 更新資源

```python
# ==================== PATCH：部分更新資源 ====================
@router.patch("/{{{resource}_id}}",                  # HTTP PATCH 方法，用於部分更新
             response_model=schemas.{Resource}Out,    # 回傳更新後的{資源}資料
             summary="更新{資源}",                     # API 文件簡短說明
             description="更新{資源}的部分欄位")        # API 文件詳細說明
async def update_{resource}(
    {resource}_id: int,                               # 路徑參數：要更新的{資源} ID
    update_data: schemas.{Resource}Update,            # 請求體：包含要更新的欄位
    db: Session = Depends(get_db)                     # 依賴注入：資料庫會話
) -> schemas.{Resource}Out:                           # 回傳類型：更新後的{資源}
    """
    更新{資源}

    這個函數會：
    1. 接收{資源} ID 和要更新的資料
    2. 檢查{資源}是否存在
    3. 只更新提供的欄位（部分更新）
    4. 回傳更新後的{資源}資料

    注意：
    - 使用 PATCH 方法，只更新提供的欄位
    - 未提供的欄位保持原值不變
    - 如果{資源}不存在會回傳 404 錯誤
    """
    # 呼叫 CRUD 函數更新{資源}
    db_{resource} = crud.update_{resource}(
        db=db,
        {resource}_id={resource}_id,
        update_data=update_data
    )

    # 檢查{資源}是否存在（CRUD 函數會在找不到時回傳 None）
    if not db_{resource}:
        raise_not_found(f"找不到 ID 為 {{resource}_id} 的{資源}")

    # 回傳更新後的{資源}資料
    return schemas.{Resource}Out.from_orm(db_{resource})
```

#### 刪除資源

```python
# ==================== DELETE：刪除資源 ====================
@router.delete("/{{{resource}_id}}",                 # HTTP DELETE 方法
              status_code=status.HTTP_204_NO_CONTENT, # 成功時回傳 204（無內容）
              summary="刪除{資源}",                    # API 文件簡短說明
              description="刪除指定的{資源}")           # API 文件詳細說明
async def delete_{resource}(
    {resource}_id: int,                               # 路徑參數：要刪除的{資源} ID
    db: Session = Depends(get_db)                     # 依賴注入：資料庫會話
):                                                    # 無回傳值（204 狀態碼）
    """
    刪除{資源}

    這個函數會：
    1. 接收要刪除的{資源} ID
    2. 檢查{資源}是否存在
    3. 從資料庫中刪除{資源}
    4. 回傳 204 狀態碼（表示成功但無內容）

    注意：
    - 刪除是永久性的，無法復原
    - 如果{資源}不存在會回傳 404 錯誤
    - 成功刪除回傳 204 狀態碼而非 200
    """
    # 呼叫 CRUD 函數刪除{資源}
    deleted_{resource} = crud.delete_{resource}(db=db, {resource}_id={resource}_id)

    # 檢查{資源}是否存在（CRUD 函數會在找不到時回傳 None）
    if not deleted_{resource}:
        raise_not_found(f"找不到 ID 為 {{resource}_id} 的{資源}")

    # 成功刪除，回傳空內容（FastAPI 會自動設定 204 狀態碼）
    return
```

### 3. 統計和業務邏輯 API

#### 統計資訊

```python
@router.get("/stats/summary",
           summary="{資源}統計摘要",
           description="取得{資源}統計資訊")
async def get_{resource}_stats(
    db: Session = Depends(get_db)
) -> dict:
    """取得{資源}統計摘要"""
    stats = {
        "total_{resource}s": db.query(models.{Resource}).count(),
        # 根據需要加入其他統計
    }

    return {"statistics": stats, "timestamp": datetime.now().isoformat()}
```

#### 業務邏輯操作

```python
@router.post("/{{{resource}_id}}/action",
            response_model=schemas.{Resource}Out,
            summary="執行{資源}動作",
            description="對{資源}執行特定的業務動作")
async def perform_{resource}_action(
    {resource}_id: int,
    action_data: schemas.{Resource}ActionRequest,
    db: Session = Depends(get_db)
) -> schemas.{Resource}Out:
    """執行{資源}動作"""
    db_{resource} = crud.get_{resource}(db=db, {resource}_id={resource}_id)

    if not db_{resource}:
        raise_not_found(f"找不到 ID 為 {{resource}_id} 的{資源}")

    try:
        updated_{resource} = crud.perform_{resource}_action(
            db=db,
            {resource}_id={resource}_id,
            action_data=action_data
        )
        return schemas.{Resource}Out.from_orm(updated_{resource})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"執行動作失敗: {str(e)}"
        )
```

## 使用步驟

### 1. 建立新的功能模組

假設要建立商品管理模組：

1. 建立目錄：`src/app/products/`
2. 建立檔案：
   - `__init__.py`
   - `models.py` - 資料庫模型
   - `schemas.py` - API 資料結構
   - `crud.py` - 資料庫操作函數
   - `router.py` - API 路由

### 2. 替換模板變數

在複製模板時，需要將以下佔位符替換為實際的值：

| 佔位符          | 說明                       | 範例（商品模組） | 範例（庫存模組） |
| --------------- | -------------------------- | ---------------- | ---------------- |
| `{module_name}` | 模組名稱（小寫，用於路徑） | `products`       | `inventory`      |
| `{Resource}`    | 資源類別名（首字母大寫）   | `Product`        | `Inventory`      |
| `{resource}`    | 資源變數名（小寫）         | `product`        | `inventory`      |
| `{資源}`        | 中文資源名稱               | `商品`           | `庫存`           |
| `{模組名稱}`    | 中文模組名稱               | `商品`           | `庫存`           |

**替換範例**：

```python
# 模板中的程式碼
@router.get("/{{{resource}_id}}")
async def get_{resource}({resource}_id: int):
    db_{resource} = crud.get_{resource}(...)

# 替換後的商品模組程式碼
@router.get("/{product_id}")
async def get_product(product_id: int):
    db_product = crud.get_product(...)
```

### 3. 在主應用程式中註冊路由器

在 `src/app/main.py` 中：

```python
from src.app.products import router as products_router

app.include_router(products_router.router)
```

## 異常處理最佳實踐

### 使用統一的異常處理

我們的專案有統一的異常處理機制，請遵循以下原則：

```python
# ==================== 匯入異常處理函數 ====================
from src.app.common.exceptions import raise_not_found

# ==================== 資源未找到的標準處理方式 ====================
if not db_resource:
    # 使用統一的 raise_not_found 函數，而不是直接拋出 HTTPException
    raise_not_found(f"找不到 ID 為 {resource_id} 的{資源}")

    # ❌ 不要這樣做：
    # raise HTTPException(status_code=404, detail="...")
```

### 業務邏輯驗證

對於業務邏輯錯誤，使用 HTTPException：

```python
# ==================== 業務規則檢查 ====================
# 檢查資源狀態是否允許操作
if resource.status == "LOCKED":
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="已鎖定的{資源}無法進行此操作"
    )

# 檢查權限
if not user.has_permission("delete_{resource}"):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="您沒有權限刪除{資源}"
    )

# 檢查資料完整性
if resource.has_dependencies():
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="此{資源}仍有相關資料，無法刪除"
    )
```

### 異常處理的層級

```python
# ==================== 三層異常處理 ====================

# 1. 資源不存在 → 使用統一函數
if not db_resource:
    raise_not_found("找不到指定的{資源}")

# 2. 業務邏輯錯誤 → 使用 HTTPException
if not business_rule_check():
    raise HTTPException(status_code=400, detail="業務規則錯誤")

# 3. 系統錯誤 → 在 try-catch 中處理
try:
    result = complex_operation()
except Exception as e:
    raise HTTPException(status_code=500, detail="系統內部錯誤")
```

## 文件化建議

### API 文件

- 每個端點都要有清楚的 `summary` 和 `description`
- 使用 docstring 說明參數和回傳值
- 提供範例資料

### 參數驗證

```python
from pydantic import Field

skip: int = Query(0, ge=0, description="跳過的記錄數（用於分頁）")
limit: int = Query(100, ge=1, le=1000, description="每頁最大記錄數")
```

## 測試建議

### 單元測試

```python
def test_create_resource():
    # 測試建立資源
    pass

def test_get_resource_not_found():
    # 測試資源未找到的情況
    pass
```

### 整合測試

```python
def test_resource_crud_workflow():
    # 測試完整的 CRUD 流程
    pass
```

## 完整範例：商品管理模組

以下是一個完整的商品管理路由器範例，展示如何應用上述模板：

```python
# src/app/products/router.py

# ==================== 匯入必要的套件 ====================
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

# ==================== 匯入專案內的模組 ====================
from src.app.common.deps import get_db
from src.app.common.exceptions import raise_not_found
from . import schemas, crud, models

# ==================== 建立路由器實例 ====================
router = APIRouter(
    prefix="/products",           # API 路徑前綴：/products
    tags=["商品管理"],            # Swagger 文件中的分組
    responses={
        404: {"description": "商品未找到"},
        400: {"description": "請求資料錯誤"},
    }
)

# ==================== POST：建立新商品 ====================
@router.post("/",
            response_model=schemas.ProductOut,
            status_code=status.HTTP_201_CREATED,
            summary="建立新商品",
            description="建立新的商品記錄")
async def create_product(
    product_data: schemas.ProductCreate,
    db: Session = Depends(get_db)
) -> schemas.ProductOut:
    """建立新商品"""
    try:
        db_product = crud.create_product(db=db, product=product_data)
        return schemas.ProductOut.from_orm(db_product)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"建立商品失敗: {str(e)}"
        )

# ==================== GET：查詢單一商品 ====================
@router.get("/{product_id}",
           response_model=schemas.ProductOut,
           summary="查詢指定商品",
           description="根據 ID 查詢商品詳細資訊")
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> schemas.ProductOut:
    """查詢指定商品"""
    db_product = crud.get_product(db=db, product_id=product_id)

    if not db_product:
        raise_not_found(f"找不到 ID 為 {product_id} 的商品")

    return schemas.ProductOut.from_orm(db_product)

# ==================== GET：查詢商品清單 ====================
@router.get("/",
           response_model=List[schemas.ProductOut],
           summary="查詢商品清單",
           description="查詢商品清單，支援分頁和篩選")
async def get_products(
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=1000, description="每頁最大記錄數"),
    category: Optional[str] = Query(None, description="商品分類篩選"),
    db: Session = Depends(get_db)
) -> List[schemas.ProductOut]:
    """查詢商品清單"""
    products = crud.get_products(
        db=db,
        skip=skip,
        limit=limit,
        category=category
    )
    return [schemas.ProductOut.from_orm(product) for product in products]
```

這個範例展示了：

- ✅ 正確的匯入和設定
- ✅ 詳細的註解說明每個部分的功能
- ✅ 統一的異常處理
- ✅ 完整的型別提示
- ✅ 清楚的 API 文件

這個模板提供了一個完整的 FastAPI 路由器結構，遵循最佳實踐並整合了統一的異常處理機制。
