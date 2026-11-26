from fastapi import FastAPI

from app.core.errors import register_error_handlers
from app.features.recommendations.router import router as recommendations_router

app = FastAPI(title="bookok-api")
register_error_handlers(app)
app.include_router(recommendations_router)
