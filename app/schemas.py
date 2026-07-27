from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class CreateAdvRequest(BaseModel):
    title: str
    description: str
    price: int
    #author: str

class CreateAdvResponse(BaseModel):
    id: int

class UpdateAdvRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    #author: Optional[str] = None

class UpdateAdvResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    author: Optional[str]
    created_at: Optional[str] = None

class OKResponse(BaseModel):
    status: str = "ok"

class GetAdvResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    author: str
    created_at: Optional[str] = None    

class SearchAdvRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    #author: Optional[str] = None
    created_at: Optional[str] = None

class SearchAdvResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    author: str
    created_at: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    id: int
    token: UUID

    class Config:
        from_attributes = True

class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = "role_user"

class IdResponse(BaseModel):
    id: int

class GetUserResponse(BaseModel):
    id: int
    name: str

class UpdateUserRequest(BaseModel):
    name: str
    password: str
    role: Optional[str]

class UpdateUserResponse(BaseModel):
    id: int
    name: str
    status: str = "ok"
