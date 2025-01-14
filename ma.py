from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from models import Base, Activity, Destination, DestinationCreate
from database import engine, SessionLocal
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# -------------------- Initialize FastAPI App --------------------
app = FastAPI(
    title="Activities and Destinations API",
    description="API for managing activities and destinations",
    version="1.0.0",
    openapi_tags=[{"name": "Activities"}, {"name": "Destinations"}],
)

# -------------------- Load Environment Variables --------------------
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# -------------------- CORS Setup --------------------
origins = [
    "http://localhost:3000",  # your frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Create Tables --------------------
Base.metadata.create_all(bind=engine)

# -------------------- OAuth2 Setup --------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# -------------------- Password Hashing Utilities --------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hardcoded user credentials (for testing)
plain_password = "password"
STORED_HASHED_PASSWORD = "$2b$12$W1DBvzcp3jQvat6sKHLIE.2jC5rNTLeWFq450h701zB.CyMNjvdMS"  # Hashed password for "password"

print(f"New hashed password: {STORED_HASHED_PASSWORD}")
result = pwd_context.verify(plain_password,STORED_HASHED_PASSWORD )
print(f"Password matches: {result}")


# -------------------- User Model --------------------
class User(BaseModel):
    username: str

# -------------------- Password Verification --------------------
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# -------------------- JWT Token Creation --------------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# -------------------- Dependency to Get Current User --------------------
def get_current_user(token: str = Depends(oauth2_scheme)):
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
        return User(username=username)
    except JWTError:
        raise credentials_exception

# -------------------- Dependency to Get DB Session --------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------- Authentication Routes --------------------
@app.post("/token/", response_model=dict, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "testuser" or not verify_password(form_data.password, STORED_HASHED_PASSWORD):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# -------------------- Activities Endpoints --------------------
@app.get("/activities/", tags=["Activities"])
async def read_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).all()
    return activities

# -------------------- Destinations Endpoints --------------------
@app.get("/destinations/", response_model=List[Destination], tags=["Destinations"])
async def read_destinations(db: Session = Depends(get_db)):
    return db.query(models.Destination).all()

@app.post("/destinations/", response_model=Destination, tags=["Destinations"])
async def create_destination(destination: DestinationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_destination = Destination(**destination.dict())  # Make sure you're passing the Pydantic model's fields
    db.add(new_destination)
    db.commit()
    db.refresh(new_destination)
    return new_destination
# -------------------- Root Endpoint --------------------
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Activities and Destinations API. Check Swagger at http://localhost:8000/docs"}

"""# -------------------- OpenAPI Configuration for Swagger UI --------------------
@app.get("/openapi.json")
def get_openapi():
    openapi_schema = app.openapi()
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/token/",
                    "scopes": {}
                }
            }
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    return openapi_schema
"""