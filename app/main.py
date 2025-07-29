from fastapi import FastAPI
from .routers import users, assessments, dashboard
from .dependencies import Base, engine

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(assessments.router)
app.include_router(dashboard.router)
