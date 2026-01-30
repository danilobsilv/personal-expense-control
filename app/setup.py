from app.api.routes.auth import router as auth_router
from app.api.routes.categories import router as categories_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.stats import router as stats_router
from app.config import cors_origins_list
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    application = FastAPI(title="Personal Expense Control API")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(auth_router)
    application.include_router(categories_router)
    application.include_router(transactions_router)
    application.include_router(stats_router)

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    return application

app = create_app()
