from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from backend.utils.camera import get_connected_cameras

router = APIRouter(prefix="/camera", tags=["camera"])


@router.get("/cameras")
async def get_cameras(encode_image: bool = False):
    """Return a list of connected cameras as JSON-serializable dicts.

    Query param `encode_image` controls whether camera image bytes are included
    as base64-encoded JPEG strings. Default: False.
    """
    cameras = get_connected_cameras()
    # Convert camera objects to plain dicts; avoid returning raw objects
    camera_dicts = [c.get_all(encode_image=encode_image) for c in cameras]
    return JSONResponse(content=jsonable_encoder(camera_dicts))