from fastapi import FastAPI, HTTPException, Depends, status
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from database import SessionLocal, engine
import models
from models import Base
import os
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from dotenv import load_dotenv 
from datetime import timedelta 
from jose import JWTError, jwt

app = FastAPI()

# Load environment variables
load_dotenv()

# OAuth2 setup
"""oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")"""

SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


# Confirm the values are loaded
print("SECRET_KEY:", SECRET_KEY)
print("ALGORITHM:", ALGORITHM)
print("ACCESS_TOKEN_EXPIRE_MINUTES:", ACCESS_TOKEN_EXPIRE_MINUTES)

origins = [
    "http://localhost:3000",  # your frontend URL
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # This specifies the allowed origins for CORS
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# -------------------- Password Hashing Utilities --------------------
# Set up the password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Verify the password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


plain_password = "password"
STORED_HASHED_PASSWORD="$2b$12$W1DBvzcp3jQvat6sKHLIE.2jC5rNTLeWFq450h701zB.CyMNjvdMS"


print(f"New hashed password: {STORED_HASHED_PASSWORD}")


result = pwd_context.verify(plain_password,STORED_HASHED_PASSWORD )
print(f"Password matches: {result}")


# Models for authentication (Pydantic models)
class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

# Password utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

"""def get_password_hash(password):
    return pwd_context.hash(password)"""

# Create JWT access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get the current authenticated user
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



# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication routes
@app.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Attempting login for user: {form_data.username}")  # DebuggingSTORED_HASHED_PASSWORD
    if form_data.username != "testuser" or not verify_password(form_data.password, STORED_HASHED_PASSWORD):


        print("Password verification failed.")  # Debugging
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Pydantic models
class ActivityBase(BaseModel):
    Activity_Name: str
    Description: str
    Duration: str

class ActivityModel(ActivityBase):
    Activity_ID: int
    class Config:
        orm_mode = True

class DestinationBase(BaseModel):
    Site_Name: str
    Description: str
    Region: str
    Best_Time_to_Visit: str

class DestinationModel(DestinationBase):
    Site_ID: int
    class Config:
        orm_mode = True

# Routes for activities (GET is public, POST, PUT, DELETE are protected)
@app.get("/activities/", response_model=List[ActivityModel])
async def read_activities(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 100):
    return db.query(models.Activity).offset(skip).limit(limit).all()

@app.post("/activities/", response_model=ActivityModel)
async def create_activity(activity: ActivityBase, db: Annotated[Session, Depends(get_db)], current_user: User = Depends(get_current_user)):
    db_activity = models.Activity(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@app.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(activity_id: int, db: Annotated[Session, Depends(get_db)], current_user: User = Depends(get_current_user)):
    db_activity = db.query(models.Activity).filter(models.Activity.Activity_ID == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(db_activity)
    db.commit()

@app.put("/activities/{activity_id}", response_model=ActivityModel)
async def update_activity(activity_id: int, activity: ActivityBase, db: Annotated[Session, Depends(get_db)], current_user: User = Depends(get_current_user)):
    db_activity = db.query(models.Activity).filter(models.Activity.Activity_ID == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    for key, value in activity.dict().items():
        setattr(db_activity, key, value)
    db.commit()
    db.refresh(db_activity)
    return db_activity

# Destinations routes (GET is public, POST, PUT, DELETE are protected)
@app.get("/destinations/", response_model=List[DestinationModel])
async def read_destinations(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 100):
    return db.query(models.Destination).offset(skip).limit(limit).all()

@app.post("/destinations/", response_model=DestinationModel)
async def create_destination(destination: DestinationBase, db: Annotated[Session, Depends(get_db)], current_user: User = Depends(get_current_user)):
    db_destination = models.Destination(**destination.dict())
    db.add(db_destination)
    db.commit()
    db.refresh(db_destination)
    return db_destination

@app.delete("/destinations/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_destination(destination_id: int, db: Annotated[Session, Depends(get_db)], current_user: User = Depends(get_current_user)):
    db_destination = db.query(models.Destination).filter(models.Destination.Site_ID == destination_id).first()
    if not db_destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    db.delete(db_destination)
    db.commit()

@app.put("/destinations/{destination_id}", response_model=DestinationModel)
async def update_destination(destination_id: int, destination: DestinationBase, db: Annotated[Session, Depends(get_db)], current_user: User = Depends(get_current_user)):
    db_destination = db.query(models.Destination).filter(models.Destination.Site_ID == destination_id).first()
    if not db_destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    for key, value in destination.dict().items():
        setattr(db_destination, key, value)
    db.commit()
    db.refresh(db_destination)
    return db_destination

# Protected route, requires authentication
@app.get("/protected-data")
async def read_protected_data(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}, you have access to protected data!"}

@app.get("/")
async def root():
    return {"message": "Welcome to the Ecotourism API. Check the Swagger at http://localhost:8001/docs"}
