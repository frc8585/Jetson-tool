"""API package: 聚合並暴露所有子模組的 routers。

把各個路由模組的 router include 到這裡，讓外部只需匯入
`from backend.api import router` 來獲得整個 API 的 router。
"""

from fastapi import APIRouter

from . import camera_api, general_api


# package-level router，聚合各子模組的 routers
router = APIRouter()

# 把 general_api 的 router include 進來（不在此指定 prefix，留給 app 層）
router.include_router(general_api.router)
router.include_router(camera_api.router)

__all__ = ["router"]