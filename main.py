from typing import Union
from fastapi import FastAPI, Depends, HTTPException  # type: ignore
from src.config.db_config import create_db_and_tables
from src.modules.user.model import User, create_user_table
from src.modules.user.router import user_router
from src.utils.security import authenticate_user
from src.utils.security import authenticate_user, create_access_token, get_current_user
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()


# Create the database and tables
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    create_user_table()
    

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Register the routers
app.include_router(user_router, prefix="/api/v1/user", tags=["User"])
