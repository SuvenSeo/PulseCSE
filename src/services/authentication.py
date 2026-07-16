import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

# Assuming these are defined elsewhere as per project structure
# For a real implementation, ensure these imports are valid:
from src.core.models import User  # Assuming User model has id (UUID), email (EmailStr), hashed_password (str)
from src.storage.user_repository import UserRepository  # Assuming UserRepository has methods like get_user_by_email, create_user
from src.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES  # Assuming these are defined in src/config.py

# --- Pydantic Models for Authentication ---

class Token(BaseModel):
    """Represents a JWT token response."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Represents the data contained within a JWT token payload."""
    email: Optional[EmailStr] = None
    user_id: Optional[str] = None # Stored as string in JWT, but original might be UUID

class UserCreate(BaseModel):
    """Model for creating a new user."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long.")

class UserLogin(BaseModel):
    """Model for user login credentials."""
    email: EmailStr
    password: str

# --- Password Hashing ---
# Using bcrypt for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

# --- JWT Token Utilities ---

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.

    Args:
        data: The payload data to encode in the token.
        expires_delta: Optional timedelta for token expiration. If None, uses default from config.

    Returns:
        The encoded JWT string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # Add expiration timestamp to payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes a JWT token and returns its payload.

    Args:
        token: The JWT string to decode.

    Returns:
        The decoded payload dictionary, or None if decoding fails (e.g., invalid token, expired).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# --- Authentication Service ---

class AuthenticationService:
    """
    Service responsible for user authentication, registration,
    password management, and JWT token handling within PulseCSE.
    """
    def __init__(self, user_repository: UserRepository):
        """
        Initializes the AuthenticationService.

        Args:
            user_repository: An instance of UserRepository for database interactions.
        """
        self.user_repository = user_repository

    async def authenticate_user(self, email: EmailStr, password: str) -> Optional[User]:
        """
        Authenticates a user by email and password.

        Args:
            email: The user's email address.
            password: The user's plain text password.

        Returns:
            The User object if authentication is successful, None otherwise.
        """
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            return None  # User not found
        if not verify_password(password, user.hashed_password):
            return None  # Incorrect password
        return user

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Registers a new user in the system.

        Args:
            user_data: Pydantic model containing user's email and plain text password.

        Returns:
            The newly created User object.

        Raises:
            ValueError: If a user with the given email already exists.
        """
        existing_user = await self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists.")

        hashed_password = get_password_hash(user_data.password)
        
        # Assuming user_repository.create_user expects email and hashed_password
        new_user = await self.user_repository.create_user(
            email=user_data.email,
            hashed_password=hashed_password
        )
        return new_user

    def generate_auth_tokens(self, user: User) -> Token:
        """
        Generates access tokens for an authenticated user.

        Args:
            user: The authenticated User object.

        Returns:
            A Token object containing the access token.
        """
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.email), "user_id": str(user.id)}, # 'sub' for subject, typically a unique user identifier
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token)
