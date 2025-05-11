from fastapi import HTTPException  # type: ignore
from fastapi.encoders import jsonable_encoder # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from datetime import timedelta
from src.utils.security import create_access_token

def getResponse(data, model_name):
    item = {"message": f"{ model_name} get successfully",  "data": jsonable_encoder(data)}
    # return item
    return JSONResponse(
        status_code=404,
        content=item,
    )

def notFoundResponse():
    return JSONResponse(
        status_code=404,
        content={"message": f"Item not found"},
    )

def createSuccessResponse(data, model_name):
    item = {"message":  f"{model_name} created successfully" ,"data": jsonable_encoder(data)}
    # return item
    return JSONResponse(status_code=201, content=item)

def updateSuccessResponse(data, model_name):
    item = {"message": f"{model_name} data updated successfully" ,"data": jsonable_encoder(data)}
    # return item
    return JSONResponse(status_code=200, content=item)

def deleteResponse(model_name):
    item = {"message": f"{model_name} data deleted successfully" }
    return JSONResponse(status_code=200, content=item)

def loginResponse(data):
    if not data:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        user={"sub": data.username},
        expires_delta = timedelta(minutes=30)
    )
    return {"access_token": access_token, "user": data.dict(exclude={"password"}), "token_type": "Bearer", "token_expires_in": 1800}

def messageResponse(message):
    return JSONResponse(status_code=200, content={"message": message})