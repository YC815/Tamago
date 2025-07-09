import psycopg2

# 替換成你提供的連線字串
conn_str = (
    "postgresql://supabase_admin:78pnI3DXM1UVOfP9i6c5RJ2T0GWhHax4"
    "@tpe1.clusters.zeabur.com:31509/postgres"
)

try:
    # 加上 connect_timeout=5，避免卡住
    conn = psycopg2.connect(conn_str, connect_timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print("✅ 成功連線到 Supabase PostgreSQL！")
    cur.close()
    conn.close()
except Exception as e:
    print("❌ 連線失敗：", e)
