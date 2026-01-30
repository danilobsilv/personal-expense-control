from pydantic import EmailStr
from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class UserOut:
    id: int
    email: EmailStr
    name: str
