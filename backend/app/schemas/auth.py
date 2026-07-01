from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class RoleRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    permissions: list[str] = []


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    roles: list[str] = []
    permissions: list[str] = []


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=64)
    description: str | None = None
    permissions: list[str] = []


class PermissionAssign(BaseModel):
    role_name: str
    permission_codes: list[str]

