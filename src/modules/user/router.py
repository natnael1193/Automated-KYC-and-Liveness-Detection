from fastapi import FastAPI, Depends, HTTPException  # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from src.modules.user.model import User
from src.utils.router import router
from src.utils.requests.get_requests import GetAllData
from src.utils.security import authenticate_user, get_current_user
from src.utils.responses.responses import messageResponse, loginResponse

# Define the router for user-related endpoints
user_router = router


@user_router.get("/users")
async def get_users():
    model = User
    return GetAllData(model, "User")


@user_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    model = User
    user = authenticate_user(model, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return loginResponse(user)

@user_router.get("/welcome_user")
def welcome_user(current_user: dict = Depends(get_current_user)):
    return messageResponse(f"Welcome, {current_user['username']}!")