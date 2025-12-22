from contextlib import asynccontextmanager
from fastapi import FastAPI


# 將應用建立與 router 註冊移到此檔案，以保持 main.py 乾淨
from backend.api import router as api_router
from backend.services.camera_manager_service import CameraManager
from backend.services.pipeline_manager_service import PipelineManager
from backend.services.field_manager_service import FieldManager
from backend.services.calibration_service import CalibrationService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    
    """
    # --- 
    print("Application startup: Initializing Services...")
    
    # 初始化 CameraManager 並啟動
    camera_manager = CameraManager()
    camera_manager.start()
    app.state.camera_manager = camera_manager
    print("CameraManager started.")

    # 初始化 FieldManager
    field_manager = FieldManager()
    app.state.field_manager = field_manager
    print("FieldManager initialized.")
    
    # 初始化 CalibrationService
    calibration_service = CalibrationService(camera_manager)
    app.state.calibration_service = calibration_service
    print("CalibrationService initialized.")
    
    # 初始化 PipelineManager 並啟動
    pipeline_manager = PipelineManager(camera_manager, field_manager)
    pipeline_manager.start()
    app.state.pipeline_manager = pipeline_manager
    print("PipelineManager started.")
    
    try:
        yield # 
    finally:
        # --- 
        print("Application shutdown: Stopping CameraManager...")
        # 6. 
        if hasattr(app.state, "camera_manager"):
            app.state.camera_manager.stop_all()
        print("CameraManager stopped gracefully.")


def create_app() -> FastAPI:
    app = FastAPI(title="Jetson-tool API", lifespan=lifespan)
    # 在此集中註冊 package-level router（所有子路由由 backend.api 聚合）
    app.include_router(api_router, prefix="/api")
    return app


# 預先建立一個 app 實例，uvicorn 或其他啟動程式可以直接匯入這個變數
app = create_app()
