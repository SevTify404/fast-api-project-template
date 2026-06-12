from fastapi import APIRouter

from app.globals.others_constants import OtherConstants

v1_api_router = APIRouter(prefix="/v1", responses=OtherConstants.COMMON_API_RESPONSES)


@v1_api_router.get("/hello")
async def hello():
    return {"message": "Hello World!"}
