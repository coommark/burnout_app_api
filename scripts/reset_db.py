from fastapi import FastAPI
from app.routers import users, assessments, dashboard
from app.dependencies import Base, engine

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ⚠️ ONLY for development — drop and recreate all tables
logger.warning("Dropping and recreating all tables")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(assessments.router)
app.include_router(dashboard.router)
