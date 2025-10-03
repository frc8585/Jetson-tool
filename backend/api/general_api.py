from fastapi import APIRouter
from fastapi.responses import JSONResponse

# 為這個檔案下的所有路由設定共同的前綴
# 例如：prefix="/general"，則路由將變成 /general/test
router = APIRouter(prefix="/general", tags=["general"])


@router.get("/test")
async def test_get():
    return JSONResponse(content={"message": "Hello World!!"})

