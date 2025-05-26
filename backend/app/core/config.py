from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # o ["http://localhost:3000"] para limitar
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
