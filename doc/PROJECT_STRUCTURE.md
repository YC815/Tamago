```
chef_link/
├── README.md
├── poetry.lock / requirements.txt
└── src/
    └── app/                       # 核心基礎設施
        ├── core/
        │   ├── config.py          # 讀 .env、存全域設定
        │   ├── database.py        # SessionLocal, engine
        │   └── security.py        # (日後) JWT & 密碼雜湊
        ├── common/
        │   ├── deps.py            # 依賴：get_db
        │   └── exceptions.py      # 共用自定義錯誤
        ├── users/                 # 功能模組 #1
        │   ├── models.py
        │   ├── schemas.py
        │   ├── crud.py
        │   └── router.py
        ├── products/              # 功能模組 #2
        │   ├── models.py
        │   ├── schemas.py
        │   ├── crud.py
        │   └── router.py
        ├── inventory/             # 功能模組 #3
        │   ├── models.py
        │   ├── schemas.py
        │   ├── crud.py
        │   └── router.py
        └── main.py
```
