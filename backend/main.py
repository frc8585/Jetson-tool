# backend/main.py
from backend.app import app


if __name__ == "__main__":
    import uvicorn

    # 只負責啟動，所有 app 與路由設定都放在 backend.app
    uvicorn.run(app, host="0.0.0.0", port=8000)
