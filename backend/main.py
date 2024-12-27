import sys
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

# 動態設置 PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services import image_processing

from app.api import register_routes  # 將 API 路由註冊為獨立函數
from app.utils import startup_tasks, shutdown_tasks  # 啟動/關閉時的輔助任務
from config import settings  # 配置文件

# 創建 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,  # 從配置中讀取應用名稱
    version=settings.APP_VERSION  # 從配置中讀取應用版本
)

# 使用 Lifespan 事件處理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_tasks(app)  # 可初始化資料庫連接池等資源
    yield
    await shutdown_tasks(app)  # 可關閉資料庫連接或清理資源

app.router.lifespan_context = lifespan

# 註冊 API 路由
register_routes(app)





# 主函數 (若需要直接運行)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)