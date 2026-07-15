from fastapi import FastAPI

from src.api.routes import router


app = FastAPI(

    title="Document Intelligence API",

    version="1.0.0"

)

app.include_router(router)