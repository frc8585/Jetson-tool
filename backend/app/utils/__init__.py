from app.services import image_processing

async def startup_tasks(app):
    print("app Start")
    image_processing.run()
    # 可初始化資料庫或其他服務

async def shutdown_tasks(app):
    print("app Close")
    image_processing.stop()
    print("app Close down")
    # 可清理資料庫或其他資源
