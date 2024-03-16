# auth.py
# Importing necessary modules for type hinting, security, and API routing
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, APIRouter
from passlib.context import CryptContext
from starlette import status
# Importing custom modules for database and models
from fastapi_todo_app import database, models
from pydantic import BaseModel
from sqlmodel import Session, select
# Importing modules for handling authentication tokens and environment variables
from datetime import timedelta, datetime
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve secret key, algorithm, and access token expiry time from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# Alias for the Users model to make the code shorter
Users = models.Users

# Create an API router with a specific path prefix and tags for organization
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# Setup password hashing context and OAuth2 bearer token handling
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

# Pydantic models to define request and response data structures
class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Dependency function to get the database session
def get_db():
    with Session(database.engine) as session:
        yield session

# Annotated dependency for injecting the database session
db_dependency = Annotated[Session, Depends(get_db)]

# Route for user signup with status code for successful creation
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(create_user_request: CreateUserRequest, db: db_dependency):
    # Create a new user model and hash the password
    create_user_model = Users(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        email=create_user_request.email,
    )
    # Add the new user to the database and commit the changes
    db.add(create_user_model)
    db.commit()

# Route to obtain a token for authenticated access
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    # Authenticate the user and raise an exception if authentication fails
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User validation failed",
        )
    # Create an access token and return it
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}

# Helper function to authenticate a user
def authenticate_user(username: str, password: str, db: db_dependency):
    # Query the database for the user by username
    statement = select(Users).where(Users.username == username)
    results = db.exec(statement)
    user = results.first()
    # Verify the user's password and return the user object if authentication is successful
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

# Helper function to create an access token
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    # Prepare the token payload with the username, user ID, and expiry time
    encode = {"sub": username, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    # Encode and return the token
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency function to retrieve the current user from the token
def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        # Decode the token and extract the username and user ID
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        # Raise an exception if the token is invalid
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User validation failed")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User validation failed")
