from pydantic import BaseModel, Field
from typing import Optional, Dict
from enum import Enum
from fastapi import Form


class UserIn(BaseModel):
    name:str = Field(...)
    username:str = Field(...)
    email:str = Field(...)
    password:str = Field(...)
    phone:str = Field(...)
    userType:str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "username": "johndoe",
                "email": "johndoe@gmail.com",
                "password":"psswd",
                "phone": "07453535454",
                "userType": "Admin"
            }
        }


class LogIn(BaseModel):
    grant_type:Optional[str] = ""
    username:str = Form(...)
    password:str = Form(...)
    scopes:Optional[str] = ""
    client_id:Optional[str] = ""
    client_secret:Optional[str] = ""

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "username": "John Doe",
                "password": "johndoepsswd",
            }
        }


class TypeModel(str, Enum):
    Customer = "Customer"
    Visitor = "Visitor"
    Agent = "Agent"
    Admin = "Admin"

#fix last step
class Allow(BaseModel):
    current_user:Dict = Field(...)
    user:Dict = Field(...)
    record:Dict = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "user": {
                    "created_by": "c01357257c514060b1f70a7cba886076",
                },
                "current_user": {
                    "_id": "c01357257c514060b1f70a7cba886076",
                    "userType": "Admin",
                },
                "record": {
                    "owner": "c01357257c514060b1f70a7cba886076",
                    "created_by": "c01357257c514060b1f70a7cba886076",
                },
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
