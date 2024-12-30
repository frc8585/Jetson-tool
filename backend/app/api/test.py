from fastapi import APIRouter

test_routes = APIRouter()

@test_routes.get("/hello")
async def say_hello():
    return {"message": "Hello, FastAPI!"}
