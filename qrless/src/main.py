from fastapi import FastAPI
from qrless.src import models
from qrless.src.database import engine
from qrless.src.router import router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)
