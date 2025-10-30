from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production-use-openssl-rand-hex-32"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False

class UserInDB(User):
    hashed_password: str

# Generate password hashes
def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

# Pre-hashed passwords (generated with bcrypt)
ADMIN_PASSWORD_HASH = get_password_hash("admin123")
DEMO_PASSWORD_HASH = get_password_hash("demo123")

# Fake database of users (in production, use a real database)
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": ADMIN_PASSWORD_HASH,
        "disabled": False,
    },
    "demo": {
        "username": "demo",
        "full_name": "Demo User",
        "email": "demo@example.com",
        "hashed_password": DEMO_PASSWORD_HASH,
        "disabled": False,
    }
}

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str) -> Optional[UserInDB]:
    """Get user from database"""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user"""
    print(f"🔐 Authenticating user: {username}")
    user = get_user(username)
    if not user:
        print(f"❌ User not found: {username}")
        return None
    if not verify_password(password, user.hashed_password):
        print(f"❌ Invalid password for user: {username}")
        return None
    print(f"✅ Authentication successful for: {username}")
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Test the authentication when running directly
if __name__ == "__main__":
    print("Testing authentication module...")
    print("\n✅ Password hashes generated successfully")
    print(f"Admin hash: {ADMIN_PASSWORD_HASH[:50]}...")
    print(f"Demo hash: {DEMO_PASSWORD_HASH[:50]}...")
    
    # Test authentication
    print("\n🧪 Testing authentication:")
    test_user = authenticate_user("admin", "admin123")
    if test_user:
        print(f"✅ Admin authentication works!")
    else:
        print(f"❌ Admin authentication failed!")
    
    test_user2 = authenticate_user("demo", "demo123")
    if test_user2:
        print(f"✅ Demo authentication works!")
    else:
        print(f"❌ Demo authentication failed!")
    
    # Test wrong password
    test_user3 = authenticate_user("admin", "wrongpassword")
    if not test_user3:
        print(f"✅ Wrong password correctly rejected!")
    else:
        print(f"❌ Wrong password was accepted!")