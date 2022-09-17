from fastapi import FastAPI
from app.api.endpoints.imports import router_imports
from app.api.endpoints.delete import router_delete
from app.api.endpoints.nodes import router_nodes

import uvicorn
from app.db.db_postgres import connect_db, disconnect_db, create_table, drop_table


def add_events(fastapi_app: FastAPI) -> None:

    @fastapi_app.on_event("startup")
    def startup_event() -> None:
        connect_db()
        try:
             create_table()
        except Exception as ex:
            print("[INFO] Таблица создана ранее.")

    @fastapi_app.on_event("shutdown")
    def shutdown_event() -> None:
        # drop_table()
        disconnect_db()


def create_app() -> FastAPI:
    """Создает FastAPI app."""

    fast_api_app = FastAPI()
    fast_api_app.include_router(router_imports)
    fast_api_app.include_router(router_delete)
    fast_api_app.include_router(router_nodes)

    add_events(fast_api_app)

    return fast_api_app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)