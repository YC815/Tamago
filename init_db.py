# init_db.py

from src.app.core.database import engine
from src.app.orders.models import Order  # 先 import 你要建的 model
from src.app.core.database import Base


def init():
    print("📦 正在建立資料表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 資料表已建立完成！")


if __name__ == "__main__":
    init()
