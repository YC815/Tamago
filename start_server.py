#!/usr/bin/env python3
"""
Tamago API 服務器啟動腳本

使用方式:
    python start_server.py          # 開發模式 (熱重載)
    python start_server.py --prod   # 生產模式
"""

import sys
import subprocess
import argparse


def main():
    parser = argparse.ArgumentParser(description="啟動 Tamago API 服務器")
    parser.add_argument(
        "--prod",
        action="store_true",
        help="以生產模式運行 (無熱重載)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="主機地址 (預設: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="端口號 (預設: 8000)"
    )

    args = parser.parse_args()

    # 基本指令
    cmd = [
        sys.executable, "-m", "uvicorn",
        "src.app.main:app",
        "--host", args.host,
        "--port", str(args.port)
    ]

    # 開發模式添加熱重載
    if not args.prod:
        cmd.extend(["--reload"])
        print(f"🚀 啟動開發服務器於 http://{args.host}:{args.port}")
        print(f"📝 API 文件：http://{args.host}:{args.port}/docs")
    else:
        print(f"🏭 啟動生產服務器於 http://{args.host}:{args.port}")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 服務器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 啟動失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
