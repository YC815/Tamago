# 專案結構

## tree

```
[ ] chef_link/
[ ] ├── README.md
[ ] ├── poetry.lock / requirements.txt
[ ] └── src/
[ ]     └── app/                       # 核心基礎設施
[-]         ├── core/
[v]         │   ├── config.py          # 讀 .env、存全域設定
[v]         │   ├── database.py        # SessionLocal, engine
[ ]         │   └── security.py        # (日後) JWT & 密碼雜湊
[ ]         ├── common/
[v]         │   ├── deps.py            # 依賴：get_db
[ ]         │   └── exceptions.py      # 共用自定義錯誤
[ ]         ├── users/                 # 功能模組 #1
[ ]         │   ├── models.py
[ ]         │   ├── schemas.py
[ ]         │   ├── crud.py
[ ]         │   └── router.py
[ ]         ├── products/              # 功能模組 #2
[ ]         │   ├── models.py
[ ]         │   ├── schemas.py
[ ]         │   ├── crud.py
[ ]         │   └── router.py
[ ]         ├── inventory/             # 功能模組 #3
[ ]         │   ├── models.py
[ ]         │   ├── schemas.py
[ ]         │   ├── crud.py
[ ]         │   └── router.py
[ ]         ├── orders/             # 功能模組 #4
[ ]         │   ├── models.py
[ ]         │   ├── schemas.py
[ ]         │   ├── crud.py
[ ]         │   └── router.py
[ ]         └── main.py
```

## 功能模組檔案

| 檔案         | 功能說明                             |
| ------------ | ------------------------------------ |
| `models.py`  | 定義資料表格結構（SQLAlchemy）       |
| `schemas.py` | 定義輸入/輸出資料模型（Pydantic）    |
| `crud.py`    | 封裝資料庫邏輯（Create/Read...）     |
| `router.py`  | 定義 API 路徑與邏輯處理（呼叫 CRUD） |
