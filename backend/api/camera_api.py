from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from backend.utils.camera import get_all_connected_cameras

router = APIRouter(prefix="/camera", tags=["camera"])

# TODO 整理各種API呼叫與需要甚麼工具函式
@router.get("/cameras")
async def get_cameras():
    # TODO 撰寫API註解
    return JSONResponse(content=jsonable_encoder(get_all_connected_cameras()))