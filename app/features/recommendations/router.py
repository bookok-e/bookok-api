from fastapi import APIRouter

from . import service
from .schemas import RecommendRequest, RecommendResponse

router = APIRouter(prefix="/api")


@router.post("/recommendations", response_model=RecommendResponse)
async def create_recommendation(req: RecommendRequest) -> RecommendResponse:
    return await service.recommend(req)
