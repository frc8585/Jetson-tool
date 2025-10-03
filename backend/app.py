from fastapi import FastAPI

# 將應用建立與 router 註冊移到此檔案，以保持 main.py 乾淨
from backend.api import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(title="Jetson-tool API")
    # 在此集中註冊 package-level router（所有子路由由 backend.api 聚合）
    app.include_router(api_router, prefix="/api")
    return app


# 預先建立一個 app 實例，uvicorn 或其他啟動程式可以直接匯入這個變數
app = create_app()
