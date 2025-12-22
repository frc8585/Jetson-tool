from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Tuple, Optional

router = APIRouter(prefix="/calibration", tags=["calibration"])

class CalibrationStartRequest(BaseModel):
    camera_id: str
    board_size: Tuple[int, int] = (9, 6)
    square_size: float = 0.025

class CalibrationCaptureResponse(BaseModel):
    success: bool
    sample_count: int
    message: Optional[str] = None

@router.post("/start")
async def start_calibration(request: Request, body: CalibrationStartRequest):
    """Start a new calibration session."""
    try:
        # Assuming calibration_service is initialized in app.state
        service = request.app.state.calibration_service
        service.start_session(body.camera_id, body.board_size, body.square_size)
        return JSONResponse(content={"message": f"Calibration started for {body.camera_id}"})
    except RuntimeError as e:
        return JSONResponse(content={"error": str(e)}, status_code=409) # Conflict
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/capture")
async def capture_sample(request: Request, camera_id: str):
    """Capture a sample frame for the active session."""
    try:
        service = request.app.state.calibration_service
        success, count = service.add_sample(camera_id)
        
        if success:
            return JSONResponse(content={"success": True, "sample_count": count})
        else:
            return JSONResponse(content={"success": False, "sample_count": count, "message": "Failed to detect corners"}, status_code=400)
            
    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except RuntimeError as e:
        return JSONResponse(content={"error": str(e)}, status_code=409)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/compute")
async def compute_calibration(request: Request, camera_id: str):
    """Compute calibration parameters."""
    try:
        service = request.app.state.calibration_service
        result = service.compute_calibration(camera_id)
        return JSONResponse(content=result)
    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except RuntimeError as e:
        return JSONResponse(content={"error": str(e)}, status_code=409)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/cancel")
async def cancel_calibration(request: Request):
    """Cancel the current calibration session."""
    service = request.app.state.calibration_service
    service.cancel_session()
    return JSONResponse(content={"message": "Calibration session cancelled"})

@router.get("/status")
async def get_status(request: Request):
    """Get current session status."""
    service = request.app.state.calibration_service
    return JSONResponse(content=service.get_session_info())
