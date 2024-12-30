from fastapi import FastAPI
from app.api.test import test_routes  # 示例的路由模組
from app.api.tag import tag_routes  # 示例的路由模組

def register_routes(app: FastAPI):
    app.include_router(test_routes, prefix="/api/test")
    app.include_router(tag_routes, prefix="/api/tag")

