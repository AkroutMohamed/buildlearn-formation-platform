from fastapi import APIRouter, Depends
from app.dependencies.auth import get_auth_service
from app.middleware.auth_middleware import get_current_user
from app.schemas.user import UserCreate, UserResponse
from app.schemas.common import TokenResponse
from app.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    return service.register_user(user)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    return service.login_user(
        {
            "email": form_data.username,
            "password": form_data.password,
        }
    )

