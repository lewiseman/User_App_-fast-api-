from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from user import schemas
from db import db
from fastapi.security import OAuth2PasswordRequestForm
from user import auth
from datetime import datetime, timedelta
from user import models


router = APIRouter(
    prefix="/auth",
    tags=["Users"],
)



@router.post('/login',
    response_description="login to your account",
    status_code=status.HTTP_202_ACCEPTED
    )
async def login(request:schemas.LogIn):
    logged_in = await models.login(request)
    return logged_in


#this router is only for fastapi swagger ui authorization can delete it 
@router.post('/login/swagger')
async def login(request:OAuth2PasswordRequestForm = Depends()):
    swagger_auth = await models.swagger_auth(request)
    return swagger_auth


@router.get('/check')
async def token_check(current_user: schemas.UserIn = Depends(auth.get_current_active_user)):
    return current_user


@router.get('/user-types')
def allowed_user_types(model_name:schemas.TypeModel):
    allowed = models.allowed_to_create(model_name)
    return allowed



@router.get(
    '/users',
    response_model= List[schemas.UserIn],
    response_description="Get all users"
    )
async def users(current_user:schemas.UserIn=Depends(auth.get_current_user)):
    users = await models.all_users()
    return users


@router.post(
    '/create-user', 
    status_code=status.HTTP_201_CREATED,
    response_description="create a new student",
    response_model=schemas.UserIn
    )
async def create_user(request :schemas.UserIn):
    created = await models.add_user(request)
    return created



@router.get(
    '/user/{id}',
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserIn
    )
async def user(id:str,current_user:schemas.UserIn=Depends(auth.get_current_user)):
    user = await models.find_user_by_id(id)
    return user


@router.put('/user/{id}',
    status_code=status.HTTP_200_OK,
    response_description="update user by id",
    )
async def user(id:str,request:schemas.UserIn):
    request = {k: v for k, v in request.dict().items() if v is not None}
    updated_user = await models.update_user(id,request)
    if updated_user:
        return updated_user
    return f"no such user"


@router.delete('/user/{id}',
    status_code=status.HTTP_200_OK,
    response_description="Delete a user"
    )
async def user(id:str):
    deleted_user = await models.delete_user(id)
    if deleted_user:
        return "Student removed successfully"
    return "no such user"



@router.post('/find-user/',
    response_model= List[schemas.UserIn],
    response_description = "Find user by name",
    status_code=status.HTTP_200_OK,
    )
async def get_user(name:str):
    user = await models.find_user(name)
    return user


#fix last step
@router.post('/authenticate')
def authorized(request:schemas.Allow):
    data = request.dict()
    try:
        allowed = models.allowed_to_edit(data["user"], data["user"], data["record"])
        if allowed:
            return ({"allowed": True})
        return ({'message': 'Unauthorized'})
    except Exception as e:
        return ({'message': f'{e}'})