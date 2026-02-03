from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import TokenOut
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.services.user_service import create_user, authenticate_user
from app.auth.jwt import create_access_token
from app.auth.rate_limit import rate_limit

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    _rl=rate_limit("auth:register"),
):
    return create_user(db, user.name, user.email, user.password, user.role)

@router.post(
    "/login", status_code=status.HTTP_200_OK,
    openapi_extra={
        # We accept both JSON and form at runtime.
        # OpenAPI can't represent both for a single operation in a way that
        # Swagger UI always renders nicely, so we document the JSON body here.
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {"schema": UserLogin.model_json_schema()},
            },
        }
    },
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
    _rl=rate_limit("auth:login"),
)-> TokenOut:
    """JSON login endpoint.

    Use this if you want to send a JSON request body:
    {"email": "...", "password": "..."}
    """
    user = authenticate_user(db, str(credentials.email), str(credentials.password))
    token_value = create_access_token({"user_id": user.id, "role": user.role})
    return TokenOut(access_token=token_value)
