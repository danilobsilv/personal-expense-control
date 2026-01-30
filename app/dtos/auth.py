from pydantic import  EmailStr
from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class RegisterIn:
    email: EmailStr
    name: str
    password: str


@dataclass(frozen=True)
class TokenOut:
    access_token: str
    token_type: str = "bearer"
