from fastapi import FastAPI
from sqlmodel import SQLModel, Session

from database import engine
from routers import user, session

app = FastAPI()


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


app.include_router(user.router)
app.include_router(session.router)
