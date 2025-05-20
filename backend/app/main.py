from fastapi import FastAPI
from app.api.routes import router
from app.core.config import setup_cors

app = FastAPI()

setup_cors(app)         # Habilita CORS
app.include_router(router)
