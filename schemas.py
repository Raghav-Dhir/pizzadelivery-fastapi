from pydantic import BaseModel, BaseSettings
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            "example" : {
                "username" : "tapu",
                "email" : "tapu@tmkoc.com",
                "password" : "secret",
                "is_staff" : False,
                "is_active" : True
            }
        }

class Settings(BaseSettings):
    authjwt_secret_key: str = '82eb37fbb1954d5e538b4f9ac20ca6974f0837171af7c78de3e4dbb710a2d367'

class LoginModel(BaseModel):
    username: str
    password: str